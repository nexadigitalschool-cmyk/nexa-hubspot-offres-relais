"""Normalisation, filtrage, déduplication et affectation campus.

Principes :
  * Aucune valeur d'origine n'est modifiée. Les identifiants (UAI, SIREN,
    SIRET, code postal) sont conservés en TEXTE, zéros initiaux inclus.
  * Aucune donnée absente n'est déduite : les champs vides restent vides et
    sont comptabilisés.
  * Aucun résultat n'est supprimé silencieusement : toute ligne écartée est
    versée au fichier des rejets avec un motif précis.
  * Aucune donnée nominative n'est produite (pas de nom de proviseur, pas
    d'email personnel reconstruit).
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter

from .config import AppConfig, Campus, LyceeFilter
from .geo import haversine_km, parse_coordinate
from .schema import AUX_FIELDS, FIELD_MAP, OUTPUT_COLUMNS, first_present

UAI_RE = re.compile(r"^[0-9]{7}[A-Z]$")

# Marqueurs d'établissements hors périmètre national (étranger / AEFE).
FOREIGN_MARKERS = ("ETRANGER", "AEFE", "HORS DE FRANCE", "MLF")


def _norm(value) -> str:
    s = unicodedata.normalize("NFKD", str(value or ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.upper()
    for ch in "-'’.,/()":
        s = s.replace(ch, " ")
    return " ".join(s.split())


def normalize_phone(raw) -> str:
    """Normalise un numéro français dans un champ séparé (format +33).
    Conserve une valeur vide si l'entrée est vide ou inexploitable.
    L'original reste présent dans les données brutes/intermédiaires."""
    if raw is None:
        return ""
    digits = re.sub(r"[^\d+]", "", str(raw))
    if not digits:
        return ""
    if digits.startswith("+33"):
        rest = re.sub(r"\D", "", digits[3:])
        return f"+33{rest}" if rest else ""
    if digits.startswith("0033"):
        rest = digits[4:]
        return f"+33{rest}" if rest else ""
    if digits.startswith("0") and len(digits) == 10:
        return f"+33{digits[1:]}"
    # Format inattendu : on renvoie les chiffres tels quels, sans inventer.
    return digits


def validate_uai(uai: str) -> bool:
    return bool(UAI_RE.match(uai or ""))


def _text(value) -> str:
    """Conversion en texte sans altération (préserve les zéros initiaux)."""
    if value is None:
        return ""
    return str(value).strip()


def build_address(record: dict) -> str:
    parts = []
    for key in ("adresse_1", "adresse_2", "adresse_3"):
        _, val = first_present(record, AUX_FIELDS[key])
        if val:
            parts.append(str(val).strip())
    return " ".join(parts).strip()


def classify(record: dict, filt: LyceeFilter) -> tuple[bool, str | None, str]:
    """Retourne (garder, motif_rejet, detail). motif_rejet=None si conservé."""
    # 1) Périmètre géographique : étranger / AEFE.
    if filt.exclude_foreign:
        _, aca = first_present(record, FIELD_MAP["Académie"])
        _, dep_code = first_present(record, AUX_FIELDS["code_departement"])
        aca_n = _norm(aca)
        if any(m in aca_n for m in FOREIGN_MARKERS):
            return False, "hors_perimetre_etranger", f"academie={aca}"
        if dep_code and str(dep_code).strip() in {"099", "000", "099 "}:
            return False, "hors_perimetre_etranger", f"code_departement={dep_code}"

    # 2) Établissement fermé.
    if filt.only_open:
        _, etat = first_present(record, AUX_FIELDS["etat"])
        if etat and _norm(etat) not in ("OUVERT", "OUVERTE", "EN ACTIVITE"):
            return False, "etablissement_ferme", f"etat={etat}"

    # 3) Nature/type : est-ce un lycée du périmètre ?
    _, nature = first_present(record, AUX_FIELDS["libelle_nature"])
    _, type_etab = first_present(record, FIELD_MAP["Type"])
    nature_n = _norm(nature)
    type_n = _norm(type_etab)

    # Exclusions explicites (collège, école, EREA...).
    for excl in filt.exclude_types:
        if type_n == _norm(excl) and not any(k in nature_n for k in ("LYCEE",)):
            return False, "type_hors_perimetre", f"type={type_etab}"

    if nature_n:
        if any(nature_n == kn or kn in nature_n for kn in filt.keep_natures):
            return True, None, f"nature={nature}"
        # Nature renseignée mais hors des familles lycée retenues.
        if "LYCEE" not in nature_n:
            return False, "type_hors_perimetre", f"nature={nature}"
        # Contient "LYCEE" mais pas dans la liste blanche : conservé et signalé.
        return True, None, f"nature_inattendue={nature}"

    # Repli sur type_etablissement si la nature est absente.
    if type_n:
        if any(_norm(kt) == type_n or _norm(kt) in type_n for kt in filt.keep_types):
            return True, None, f"type={type_etab}"
        return False, "type_hors_perimetre", f"type={type_etab}"

    return False, "type_hors_perimetre", "nature et type absents"


def build_row(record: dict, source_label: str, extraction_date: str) -> dict:
    """Construit une ligne canonique (colonnes OUTPUT_COLUMNS)."""
    row = {col: "" for col in OUTPUT_COLUMNS}

    for col, candidates in FIELD_MAP.items():
        if col in ("Téléphone", "Latitude", "Longitude"):
            continue
        _, val = first_present(record, candidates)
        row[col] = _text(val)

    row["Adresse"] = build_address(record)

    _, phone_raw = first_present(record, FIELD_MAP["Téléphone"])
    row["Téléphone"] = normalize_phone(phone_raw)

    lat = parse_coordinate(_first(record, FIELD_MAP["Latitude"]))
    lon = parse_coordinate(_first(record, FIELD_MAP["Longitude"]))
    if (lat is None or lon is None):
        # Repli : point géographique combiné (position/geo_point_2d).
        _, pos = first_present(record, AUX_FIELDS["position"])
        lat2, lon2 = _parse_position(pos)
        lat = lat if lat is not None else lat2
        lon = lon if lon is not None else lon2
    row["Latitude"] = "" if lat is None else repr(lat)
    row["Longitude"] = "" if lon is None else repr(lon)

    row["Source"] = source_label
    row["Date extraction"] = extraction_date
    row["Campus rattaché"] = ""
    row["Distance campus km"] = ""
    return row


def _first(record, candidates):
    _, v = first_present(record, candidates)
    return v


def _parse_position(pos) -> tuple[float | None, float | None]:
    if pos is None:
        return None, None
    if isinstance(pos, dict):
        return parse_coordinate(pos.get("lat")), parse_coordinate(pos.get("lon"))
    if isinstance(pos, (list, tuple)) and len(pos) == 2:
        return parse_coordinate(pos[0]), parse_coordinate(pos[1])
    return None, None


def record_dept_code(record: dict) -> str:
    _, dep = first_present(record, AUX_FIELDS["code_departement"])
    d = _text(dep)
    return d.zfill(3) if d.isdigit() else d


def nearest_campus(lat, lon, campuses: list[Campus]) -> tuple[Campus | None, float | None]:
    """Campus actif le plus proche disposant de coordonnées, et sa distance km.
    (None, None) si aucune distance n'est calculable."""
    best, best_d = None, None
    if lat is None or lon is None:
        return None, None
    for c in campuses:
        if c.has_coordinates:
            d = haversine_km(lat, lon, c.latitude, c.longitude)
            if best_d is None or d < best_d:
                best, best_d = c, d
    return best, best_d


def _matches_academie(aca_n: str, campuses: list[Campus]) -> Campus | None:
    for c in campuses:
        if aca_n and any(_norm(a) == aca_n for a in c.academies):
            return c
    return None


def _buffer_campuses(dep_code: str, campuses: list[Campus]) -> list[Campus]:
    out = []
    for c in campuses:
        if dep_code and any(_dept_eq(dep_code, b) for b in c.buffer_departments):
            out.append(c)
    return out


def _dept_eq(a: str, b: str) -> bool:
    ad = re.sub(r"\D", "", a)
    bd = re.sub(r"\D", "", b)
    if ad and bd:
        return ad.zfill(3) == bd.zfill(3)
    return _text(a).upper() == _text(b).upper()


def evaluate_perimeter(row: dict, dep_code: str, campuses: list[Campus],
                       national: bool) -> tuple[bool, str | None, str]:
    """Affecte le campus + la distance, et décide de conserver la ligne.

    - Académie principale d'un campus actif  -> conservé (distance = attribut).
    - Département tampon d'une autre académie -> conservé SEULEMENT si la
      distance réelle au campus est < radius_km ; sinon rejeté avec motif.
    - Campus national (second rideau)         -> conservé.
    Retourne (garder, motif_rejet, detail).
    """
    aca_n = _norm(row.get("Académie"))
    lat = parse_coordinate(row.get("Latitude"))
    lon = parse_coordinate(row.get("Longitude"))

    main_campus = _matches_academie(aca_n, campuses)
    buffers = _buffer_campuses(dep_code, campuses)
    near, dist = nearest_campus(lat, lon, campuses)

    # Renseigne toujours campus + distance quand c'est calculable.
    if near is not None:
        row["Campus rattaché"] = near.name
        row["Distance campus km"] = repr(dist)
    elif main_campus is not None:
        row["Campus rattaché"] = main_campus.name

    # Décision de conservation.
    if main_campus is not None:
        if row["Campus rattaché"] == "":
            row["Campus rattaché"] = main_campus.name
        return True, None, f"academie_principale={main_campus.name}"

    if buffers:
        # On ne conserve que si une distance < radius est VÉRIFIÉE.
        target = None
        target_d = None
        for c in buffers:
            if c.has_coordinates and lat is not None and lon is not None:
                d = haversine_km(lat, lon, c.latitude, c.longitude)
                if target_d is None or d < target_d:
                    target, target_d = c, d
        if target_d is None:
            return False, "distance_non_verifiable", (
                "tampon sans distance calculable "
                f"(coord. campus ou GPS établissement manquante ; dep={dep_code})")
        if target_d > target.radius_km:
            return False, "hors_rayon_km", (
                f"{target_d:.1f} km > {target.radius_km:.0f} km du campus {target.name}")
        row["Campus rattaché"] = target.name
        row["Distance campus km"] = repr(round(target_d, 2))
        return True, None, f"tampon<{target.radius_km:.0f}km={target.name} ({target_d:.1f}km)"

    if national:
        for c in campuses:
            if c.national:
                row["Campus rattaché"] = c.name
                return True, None, "national"

    return False, "hors_perimetre_configuration", (
        f"academie={row.get('Académie')} dep={dep_code} hors académies/tampons configurés")


def assign_campus(row: dict, campuses: list[Campus], dep_code: str = "",
                  national: bool = False) -> None:
    """Compat : renseigne « Campus rattaché » et « Distance campus km » sans
    porter la décision de conservation (utilisé en tests unitaires)."""
    evaluate_perimeter(row, dep_code, campuses, national)


def transform_records(
    records,
    config: AppConfig,
    source_label: str,
    extraction_date: str,
    log,
) -> dict:
    """Applique filtrage + normalisation + dedup + affectation campus.

    Retourne un dict avec kept, rejected, stats, field_presence, drift.
    """
    filt = config.lycee_filter
    campuses = config.active_campuses()
    national = any(c.national for c in campuses)

    kept: list[dict] = []
    rejected: list[dict] = []
    seen_uai: dict[str, str] = {}

    total = 0
    reject_counter: Counter = Counter()
    field_presence: Counter = Counter()   # valeur non vide (complétude)
    key_presence: Counter = Counter()     # clé présente (détection de drift)
    flags = Counter()  # sans_commune, gps_absent
    type_distribution: Counter = Counter()

    for record in records:
        total += 1

        # Complétude (valeur non vide) et présence de clé (drift structurel).
        for col, candidates in FIELD_MAP.items():
            if any(c in record for c in candidates):
                key_presence[col] += 1
            name, _ = first_present(record, candidates)
            if name is not None:
                field_presence[col] += 1

        _, nature = first_present(record, AUX_FIELDS["libelle_nature"])
        _, type_etab = first_present(record, FIELD_MAP["Type"])
        type_distribution[_norm(nature) or _norm(type_etab) or "(inconnu)"] += 1

        keep, reason, detail = classify(record, filt)
        row = build_row(record, source_label, extraction_date)

        if not keep:
            rejected.append(_reject(row, reason, detail))
            reject_counter[reason] += 1
            continue

        uai = row["UAI"]
        if not uai:
            rejected.append(_reject(row, "uai_absent", ""))
            reject_counter["uai_absent"] += 1
            continue
        if not validate_uai(uai):
            rejected.append(_reject(row, "uai_invalide", f"uai={uai}"))
            reject_counter["uai_invalide"] += 1
            continue
        if uai in seen_uai:
            rejected.append(_reject(row, "doublon_uai", f"deja_vu={seen_uai[uai]}"))
            reject_counter["doublon_uai"] += 1
            continue
        seen_uai[uai] = row["Nom"]

        # Décision de périmètre (académie principale / tampon < rayon / national).
        dep_code = record_dept_code(record)
        keep_p, reason_p, detail_p = evaluate_perimeter(row, dep_code, campuses, national)
        if not keep_p:
            rejected.append(_reject(row, reason_p, detail_p))
            reject_counter[reason_p] += 1
            continue

        # Signalements (non bloquants, comptabilisés sur les lignes conservées).
        if not row["Commune"]:
            flags["sans_commune"] += 1
        if not row["Latitude"] or not row["Longitude"]:
            flags["gps_absent"] += 1
        if detail_p.startswith("tampon"):
            flags["tampons_conserves"] += 1

        kept.append(row)

    drift = detect_drift(key_presence, total)
    if drift:
        for col in drift:
            log.warning("Champ jamais résolu (renommage/suppression probable) : « %s »", col)

    stats = {
        "total_extrait": total,
        "conserves": len(kept),
        "rejetes": len(rejected),
        "rejets_par_motif": dict(reject_counter),
        "signalements": dict(flags),
        "distribution_type_nature": dict(type_distribution.most_common()),
    }
    return {
        "kept": kept,
        "rejected": rejected,
        "stats": stats,
        "field_presence": dict(field_presence),
        "drift": drift,
    }


def detect_drift(key_presence: Counter, total: int) -> list[str]:
    """Colonnes canoniques dont AUCUN champ candidat n'existe (clé absente) sur
    l'ensemble du lot : signe fort d'un renommage ou d'une suppression de champ
    côté source. Un champ présent mais toujours vide n'est PAS un drift."""
    if total == 0:
        return []
    return [col for col in FIELD_MAP if key_presence.get(col, 0) == 0]


def _reject(row: dict, reason: str, detail: str) -> dict:
    return {
        "UAI": row.get("UAI", ""),
        "Nom": row.get("Nom", ""),
        "Type": row.get("Type", ""),
        "Académie": row.get("Académie", ""),
        "Département": row.get("Département", ""),
        "reject_reason": reason,
        "reject_detail": detail,
        "Source": row.get("Source", ""),
        "Date extraction": row.get("Date extraction", ""),
    }
