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


def assign_campus(row: dict, campuses: list[Campus]) -> None:
    """Affecte un campus (par académie, priorité au département prioritaire)
    et calcule la distance à vol d'oiseau si les coordonnées du campus ET de
    l'établissement sont disponibles."""
    aca_n = _norm(row.get("Académie"))
    dep = _text(row.get("Département"))

    chosen: Campus | None = None
    # Priorité 1 : campus dont le département prioritaire correspond.
    for c in campuses:
        if c.priority_departments and _dept_matches(dep, c.priority_departments):
            if aca_n and any(_norm(a) == aca_n for a in c.academies):
                chosen = c
                break
    # Priorité 2 : correspondance par académie.
    if chosen is None:
        for c in campuses:
            if aca_n and any(_norm(a) == aca_n for a in c.academies):
                chosen = c
                break
    # Priorité 3 : campus national (second rideau).
    if chosen is None:
        for c in campuses:
            if c.national:
                chosen = c
                break

    if chosen is None:
        return
    row["Campus rattaché"] = chosen.name

    if not chosen.has_coordinates:
        return
    lat = parse_coordinate(row.get("Latitude"))
    lon = parse_coordinate(row.get("Longitude"))
    if lat is None or lon is None:
        return
    row["Distance campus km"] = repr(haversine_km(lat, lon, chosen.latitude, chosen.longitude))


def _dept_matches(dep_label_or_code: str, priority: list[str]) -> bool:
    d = _text(dep_label_or_code)
    d_digits = re.sub(r"\D", "", d)
    for p in priority:
        p_digits = re.sub(r"\D", "", p)
        if p_digits and (d_digits == p_digits or d_digits.zfill(3) == p_digits.zfill(3)):
            return True
    return False


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

        # Signalements (non bloquants, comptabilisés).
        if not row["Commune"]:
            flags["sans_commune"] += 1
        if not row["Latitude"] or not row["Longitude"]:
            flags["gps_absent"] += 1

        assign_campus(row, campuses)
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
