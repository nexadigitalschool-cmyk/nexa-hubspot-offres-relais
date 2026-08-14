"""Orchestration de bout en bout — Étape 1 : socle national des lycées.

Usage :
    python -m ie_prospection.pipeline --config config/campuses.yml --source api
    python -m ie_prospection.pipeline --config config/campuses.yml --source fixture

La source ``fixture`` exécute le pipeline sur des données synthétiques (hors
ligne), utile quand l'accès réseau à l'API officielle n'est pas ouvert.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .config import AppConfig, load_config
from .fixtures import build_fixture_records
from .geocode import geocode_ban
from .logging_utils import get_logger, setup_logging
from .ods_client import ODSAPIError, ODSClient
from .reporting import (
    write_jsonl,
    write_quality_report,
    write_rejects,
    write_sample,
    write_socle,
    write_sources_manifest,
)
from .schema import AUX_FIELDS, FIELD_MAP, first_present
from .transform import _norm, transform_records


def build_where(aca_field: str, academie: str, nature_field: str | None,
                keep_natures: list[str]) -> str:
    """Construit une clause ODSQL narrowant par académie (+ nature si possible)."""
    esc = academie.replace('"', '\\"')
    clause = f'{aca_field}="{esc}"'
    if nature_field and keep_natures:
        values = ", ".join('"' + n.replace('"', '\\"') + '"' for n in keep_natures)
        clause += f" and {nature_field} in ({values})"
    return clause


def _iter_fixture_pages(records: list[dict], academie: str, page_size: int,
                        raw_dir: Path, log):
    """Simule la pagination ODS sur les données synthétiques (+ dump brut)."""
    subset = [r for r in records
              if _norm(first_present(r, FIELD_MAP["Académie"])[1]) == _norm(academie)]
    page_dir = raw_dir / _safe(academie)
    page_dir.mkdir(parents=True, exist_ok=True)
    log.info("[%s] (fixture) %d enregistrements", academie, len(subset))
    for offset in range(0, len(subset), page_size):
        page = subset[offset:offset + page_size]
        payload = {"total_count": len(subset), "results": page}
        (page_dir / f"page_{offset:06d}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        for rec in page:
            yield rec


def _iter_fixture_dept_pages(records: list[dict], dep_code: str, page_size: int,
                             raw_dir: Path, log):
    """Pagination synthétique par code département (tampons hors académie)."""
    def _dep(r):
        v = str((r.get("code_departement") or "")).strip()
        return v.zfill(3) if v.isdigit() else v
    subset = [r for r in records if _dep(r) == dep_code]
    page_dir = raw_dir / f"dep_{dep_code}"
    page_dir.mkdir(parents=True, exist_ok=True)
    log.info("[dep %s] (fixture) %d enregistrements", dep_code, len(subset))
    for offset in range(0, len(subset), page_size):
        page = subset[offset:offset + page_size]
        (page_dir / f"page_{offset:06d}.json").write_text(
            json.dumps({"total_count": len(subset), "results": page}, ensure_ascii=False),
            encoding="utf-8")
        for rec in page:
            yield rec


def _src_entry(source_label, config, base_url, where, url, extraction_date, volume):
    return {"source": source_label, "dataset_id": config.source.dataset_id,
            "base_url": base_url, "where": where, "url_exemple": url,
            "date_extraction": extraction_date, "volume_extrait": volume,
            "volume_conserve": ""}


def _safe(name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", name)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return "".join(ch if ch.isalnum() else "_" for ch in s).strip("_").lower()


def build_where_dept(dep_field: str, dep_code: str, nature_field: str | None,
                     keep_natures: list[str]) -> str:
    """Clause ODSQL narrowant par code département (+ nature si possible)."""
    clause = f'{dep_field}="{dep_code}"'
    if nature_field and keep_natures:
        values = ", ".join('"' + n.replace('"', '\\"') + '"' for n in keep_natures)
        clause += f" and {nature_field} in ({values})"
    return clause


def geocode_active_campuses(config: AppConfig, force: bool, log,
                            session=None) -> None:
    """Renseigne les coordonnées des campus actifs à partir de leur adresse via
    la BAN officielle. N'écrase jamais des coordonnées existantes en cas d'échec."""
    for c in config.active_campuses():
        need = force or not c.has_coordinates
        if not need or not c.address:
            continue
        coords = geocode_ban(c.address, session=session)
        if coords:
            c.latitude, c.longitude = coords
            c.coordinates_source = "BAN (api-adresse.data.gouv.fr)"
        elif not c.has_coordinates:
            log.warning("Campus %s : adresse non géocodée et pas de coordonnées "
                        "-> distance désactivée pour ce campus.", c.name)


def run(config: AppConfig, source: str, paths: dict, run_id: str,
        base_url_override: str | None = None, resume: bool = True,
        limit_per_academie: int | None = None, geocode: bool = False) -> dict:
    log = get_logger()
    extraction_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    active = config.active_campuses()
    academies: list[str] = []
    buffer_depts: list[str] = []
    national = False
    for c in active:
        academies.extend(c.academies)
        buffer_depts.extend(c.buffer_departments)
        national = national or c.national
    academies = list(dict.fromkeys(academies))
    buffer_depts = list(dict.fromkeys(buffer_depts))

    # Géocodage des campus (source officielle) — jamais de coordonnées inventées.
    geocode_active_campuses(config, force=geocode, log=log)
    for c in active:
        if c.has_coordinates:
            log.info("Campus %-12s : (%.5f, %.5f) source=%s | rayon=%.0f km",
                     c.name, c.latitude, c.longitude, c.coordinates_source, c.radius_km)
        else:
            log.info("Campus %-12s : sans coordonnées (distance désactivée)", c.name)

    log.info("IE Prospection v%s — étape 1 socle national", __version__)
    log.info("Source=%s | campus actifs=%s | académies=%s | tampons=%s | national=%s",
             source, [c.name for c in active], academies, buffer_depts, national)

    raw_dir = Path(paths["raw"])
    all_records: list[dict] = []
    source_entries: list[dict] = []

    if source == "fixture":
        source_label = "FIXTURE (données synthétiques — non officielles)"
        fixtures = build_fixture_records()
        for aca in academies:
            recs = list(_iter_fixture_pages(fixtures, aca, config.http.page_size, raw_dir, log))
            if limit_per_academie:
                recs = recs[:limit_per_academie]
            all_records.extend(recs)
            source_entries.append(_src_entry(source_label, config, "(local fixture)",
                                              f'academie="{aca}"', "(local fixture)",
                                              extraction_date, len(recs)))
        for dep in buffer_depts:
            recs = list(_iter_fixture_dept_pages(fixtures, dep, config.http.page_size,
                                                 raw_dir, log))
            all_records.extend(recs)
            source_entries.append(_src_entry(source_label, config, "(local fixture)",
                                              f'code_departement="{dep}"', "(local fixture)",
                                              extraction_date, len(recs)))
    elif source == "api":
        base_url = base_url_override or config.source.base_url
        source_label = f"Annuaire de l'éducation nationale — {config.source.dataset_id}"
        client = ODSClient(base_url, config.source.dataset_id, config.http, raw_dir)
        aca_field = client.resolve_field(FIELD_MAP["Académie"]) or "libelle_academie"
        dep_field = client.resolve_field(AUX_FIELDS["code_departement"]) or "code_departement"
        nature_field = client.resolve_field(AUX_FIELDS["libelle_nature"])
        log.info("Champs résolus — académie:%s département:%s nature:%s",
                 aca_field, dep_field, nature_field)

        targets = [("academie", aca, build_where(aca_field, aca, nature_field,
                                                 config.lycee_filter.keep_natures))
                   for aca in academies]
        targets += [("dep", dep, build_where_dept(dep_field, dep, nature_field,
                                                  config.lycee_filter.keep_natures))
                    for dep in buffer_depts]

        for kind, key, where in targets:
            try:
                client.count(where)
            except ODSAPIError as exc:
                log.warning("Clause 'where' avec nature rejetée (%s) — repli sans nature.", exc)
                where = (build_where(aca_field, key, None, []) if kind == "academie"
                         else build_where_dept(dep_field, key, None, []))
            label = key if kind == "academie" else f"dep_{key}"
            recs = list(client.iter_records(where, label=label, resume=resume))
            if limit_per_academie:
                recs = recs[:limit_per_academie]
            all_records.extend(recs)
            url = (f"{base_url}/catalog/datasets/{config.source.dataset_id}"
                   f"/records?where={where}&limit={config.http.page_size}&offset=0")
            source_entries.append(_src_entry(source_label, config, base_url, where, url,
                                             extraction_date, len(recs)))
    else:
        raise ValueError(f"source inconnue : {source}")

    # Sauvegarde intermédiaire (enregistrements bruts agrégés).
    inter_path = write_jsonl(Path(paths["intermediate"]) / "annuaire_records.jsonl",
                             all_records)
    log.info("Intermédiaire écrit : %s (%d enregistrements)", inter_path, len(all_records))

    # Transformation.
    result = transform_records(all_records, config, source_label, extraction_date, log)
    kept, rejected, stats = result["kept"], result["rejected"], result["stats"]

    # Sorties.
    out = Path(paths["output"])
    reports = Path(paths["reports"])
    socle_path = write_socle(out / "socle_national.csv", kept)
    rejects_path = write_rejects(out / "rejected.csv", rejected)
    sample_path = write_sample(reports / "echantillon_30.csv", kept, 30)

    per_campus: dict[str, dict] = {}
    for c in active:
        rows = [r for r in kept if r["Campus rattaché"] == c.name]
        cpath = out / f"campus_{_safe(c.name)}.csv"
        write_socle(cpath, rows)
        per_campus[c.name] = {"count": len(rows), "distance_enabled": c.has_coordinates,
                              "radius_km": c.radius_km, "buffer": c.buffer_departments,
                              "coordinates_source": c.coordinates_source, "file": str(cpath)}
        log.info("Campus %-12s : %4d lignes | distance=%s", c.name, len(rows),
                 "oui" if c.has_coordinates else "désactivée (coordonnées manquantes)")

    manifest_path = write_sources_manifest(reports / "sources.csv", source_entries)

    meta = {"run_id": run_id, "extraction_date": extraction_date,
            "source_label": source_label, "academies": academies, "version": __version__}
    quality_path = write_quality_report(reports / "data_quality_report.md", stats,
                                        result["field_presence"], result["drift"],
                                        per_campus, meta)

    log.info("=" * 60)
    log.info("RÉSUMÉ : extrait=%d | conservé=%d | rejeté=%d",
             stats["total_extrait"], stats["conserves"], stats["rejetes"])
    log.info("Rejets par motif : %s", stats["rejets_par_motif"])
    log.info("Fichiers : %s | %s | %s | %s | %s", socle_path, rejects_path,
             sample_path, manifest_path, quality_path)

    return {"stats": stats, "per_campus": per_campus,
            "files": {"socle": str(socle_path), "rejects": str(rejects_path),
                      "sample": str(sample_path), "manifest": str(manifest_path),
                      "quality": str(quality_path), "intermediate": str(inter_path)}}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="NEXA — socle national des lycées (étape 1)")
    p.add_argument("--config", default="config/campuses.yml")
    p.add_argument("--source", choices=["api", "fixture"], default="api")
    p.add_argument("--base-url", default=None, help="Surcharge de la base API (miroir)")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--reports-dir", default="reports")
    p.add_argument("--no-resume", action="store_true",
                   help="Ne pas relire les pages brutes déjà sauvegardées")
    p.add_argument("--limit-per-academie", type=int, default=None)
    p.add_argument("--geocode", action="store_true",
                   help="Forcer le (re)géocodage BAN des adresses de campus")
    p.add_argument("--run-id", default=None)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    reports_dir = Path(args.reports_dir)
    setup_logging(reports_dir, run_id)
    config = load_config(args.config)
    paths = {
        "raw": Path(args.data_dir) / "raw",
        "intermediate": Path(args.data_dir) / "intermediate",
        "output": Path(args.data_dir) / "output",
        "reports": reports_dir,
    }
    try:
        run(config, args.source, paths, run_id,
            base_url_override=args.base_url, resume=not args.no_resume,
            limit_per_academie=args.limit_per_academie, geocode=args.geocode)
    except ODSAPIError as exc:
        get_logger().error("Extraction interrompue (API) : %s", exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
