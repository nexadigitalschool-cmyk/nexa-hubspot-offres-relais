"""Chargement et validation de la configuration des campus."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Campus:
    name: str
    academies: list[str]
    priority_departments: list[str] = field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None
    active: bool = False
    national: bool = False

    @property
    def has_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None


@dataclass
class HttpConfig:
    page_size: int = 100
    timeout_seconds: float = 30.0
    max_retries: int = 5
    backoff_base_seconds: float = 2.0
    backoff_max_seconds: float = 60.0
    rate_limit_seconds: float = 0.4


@dataclass
class LyceeFilter:
    keep_natures: list[str] = field(default_factory=list)
    keep_types: list[str] = field(default_factory=list)
    exclude_types: list[str] = field(default_factory=list)
    exclude_foreign: bool = True
    only_open: bool = True


@dataclass
class SourceConfig:
    dataset_id: str
    base_url: str
    mirrors: list[str] = field(default_factory=list)


@dataclass
class AppConfig:
    source: SourceConfig
    http: HttpConfig
    lycee_filter: LyceeFilter
    campuses: list[Campus]

    def active_campuses(self) -> list[Campus]:
        return [c for c in self.campuses if c.active]

    def campus_by_name(self, name: str) -> Campus | None:
        for c in self.campuses:
            if c.name == name:
                return c
        return None


def load_config(path: str | Path) -> AppConfig:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration introuvable : {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    src = raw.get("source", {})
    if not src.get("dataset_id") or not src.get("base_url"):
        raise ValueError("config.source doit définir dataset_id et base_url")
    source = SourceConfig(
        dataset_id=str(src["dataset_id"]),
        base_url=str(src["base_url"]).rstrip("/"),
        mirrors=[str(m).rstrip("/") for m in src.get("mirrors", [])],
    )

    http = HttpConfig(**{k: v for k, v in raw.get("http", {}).items()
                         if k in HttpConfig.__dataclass_fields__})
    # Garde-fou : l'API Explore v2.1 plafonne la taille de page à 100.
    if http.page_size > 100:
        http.page_size = 100

    lf_raw = raw.get("lycee_filter", {})
    lycee_filter = LyceeFilter(
        keep_natures=[_norm(x) for x in lf_raw.get("keep_natures", [])],
        keep_types=[str(x) for x in lf_raw.get("keep_types", [])],
        exclude_types=[str(x) for x in lf_raw.get("exclude_types", [])],
        exclude_foreign=bool(lf_raw.get("exclude_foreign", True)),
        only_open=bool(lf_raw.get("only_open", True)),
    )

    campuses: list[Campus] = []
    for c in raw.get("campuses", []):
        campuses.append(
            Campus(
                name=str(c["name"]),
                academies=[str(a) for a in c.get("academies", [])],
                priority_departments=[str(d) for d in c.get("priority_departments", [])],
                latitude=_as_float_or_none(c.get("latitude")),
                longitude=_as_float_or_none(c.get("longitude")),
                active=bool(c.get("active", False)),
                national=bool(c.get("national", False)),
            )
        )
    if not campuses:
        raise ValueError("config.campuses est vide")

    return AppConfig(source=source, http=http, lycee_filter=lycee_filter, campuses=campuses)


def _as_float_or_none(value) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _norm(value: str) -> str:
    """Normalisation légère pour comparer des libellés de nature (accents,
    ponctuation, casse). Utilisée UNIQUEMENT pour la comparaison, jamais
    pour altérer la valeur stockée."""
    import unicodedata

    s = unicodedata.normalize("NFKD", str(value))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.upper()
    for ch in "-'’.,/()":
        s = s.replace(ch, " ")
    return " ".join(s.split())
