"""Client de l'API Opendatasoft Explore v2.1 pour l'Annuaire de l'éducation.

Endpoints utilisés (API officielle, à confirmer au premier appel live) :

* Métadonnées + schéma du dataset :
  ``GET {base}/catalog/datasets/{dataset_id}``
* Enregistrements paginés :
  ``GET {base}/catalog/datasets/{dataset_id}/records?where=...&limit=100&offset=N``

Fonctions couvertes :
  - pagination complète par ``offset`` jusqu'à épuisement,
  - timeout par requête,
  - retry avec backoff exponentiel (+ respect de ``Retry-After``),
  - limitation du rythme des appels (rate limit),
  - sauvegarde des réponses brutes (une par page),
  - reprise sur erreur (les pages déjà écrites sont relues, pas refetchées),
  - réconciliation du schéma réel (les noms de champ sont VÉRIFIÉS auprès
    de la source, jamais devinés en aveugle).

Note sur la fenêtre de pagination : l'API v2.1 plafonne ``offset + limit`` à
10000. On restreint donc systématiquement côté serveur via ``where`` (par
académie) pour que chaque partition reste bien en-deçà de cette fenêtre. Si
la limite est malgré tout atteinte, un avertissement explicite est journalisé
(aucune donnée n'est perdue silencieusement).
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import requests

from .config import HttpConfig
from .logging_utils import get_logger

ODS_MAX_WINDOW = 10000  # offset + limit maximum sur l'API Explore v2.1


class ODSAPIError(RuntimeError):
    """Erreur non récupérable renvoyée par l'API (ex : 400 where invalide)."""


class ODSClient:
    def __init__(
        self,
        base_url: str,
        dataset_id: str,
        http: HttpConfig,
        raw_dir: str | Path,
        session: requests.Session | None = None,
        sleep=time.sleep,
    ):
        self.base_url = base_url.rstrip("/")
        self.dataset_id = dataset_id
        self.http = http
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.session = session or requests.Session()
        self._sleep = sleep
        self._last_call = 0.0
        self._schema_fields: set[str] | None = None
        self.log = get_logger()

    # -- URLs -----------------------------------------------------------------
    @property
    def _dataset_url(self) -> str:
        return f"{self.base_url}/catalog/datasets/{self.dataset_id}"

    @property
    def _records_url(self) -> str:
        return f"{self._dataset_url}/records"

    # -- Rate limiting --------------------------------------------------------
    def _respect_rate_limit(self) -> None:
        wait = self.http.rate_limit_seconds - (time.monotonic() - self._last_call)
        if wait > 0:
            self._sleep(wait)
        self._last_call = time.monotonic()

    # -- HTTP avec retry/backoff ---------------------------------------------
    def _get(self, url: str, params: dict) -> dict:
        attempt = 0
        while True:
            attempt += 1
            self._respect_rate_limit()
            try:
                resp = self.session.get(url, params=params, timeout=self.http.timeout_seconds)
            except (requests.Timeout, requests.ConnectionError) as exc:
                if attempt > self.http.max_retries:
                    raise ODSAPIError(f"Échec réseau après {attempt-1} tentatives : {exc}") from exc
                self._backoff(attempt, reason=str(exc))
                continue

            # 4xx non récupérables (sauf 429) : on lève avec le message serveur.
            if resp.status_code == 400:
                raise ODSAPIError(f"400 Bad Request : {resp.text[:500]}")
            if resp.status_code in (401, 403, 404):
                raise ODSAPIError(f"{resp.status_code} sur {url} : {resp.text[:300]}")

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt > self.http.max_retries:
                    raise ODSAPIError(
                        f"HTTP {resp.status_code} après {attempt-1} tentatives sur {url}"
                    )
                retry_after = resp.headers.get("Retry-After")
                self._backoff(attempt, reason=f"HTTP {resp.status_code}", retry_after=retry_after)
                continue

            resp.raise_for_status()
            return resp.json()

    def _backoff(self, attempt: int, reason: str, retry_after: str | None = None) -> None:
        if retry_after:
            try:
                delay = float(retry_after)
            except ValueError:
                delay = self.http.backoff_base_seconds * (2 ** (attempt - 1))
        else:
            delay = self.http.backoff_base_seconds * (2 ** (attempt - 1))
        delay = min(delay, self.http.backoff_max_seconds)
        self.log.warning("Tentative %d échouée (%s) — nouvelle tentative dans %.1fs",
                         attempt, reason, delay)
        self._sleep(delay)

    # -- Schéma ---------------------------------------------------------------
    def get_schema_fields(self) -> set[str]:
        """Récupère la liste réelle des champs du dataset (mise en cache)."""
        if self._schema_fields is not None:
            return self._schema_fields
        try:
            data = self._get(self._dataset_url, params={})
        except ODSAPIError as exc:
            self.log.warning("Schéma du dataset indisponible (%s) — "
                             "réconciliation des champs différée au vol.", exc)
            self._schema_fields = set()
            return self._schema_fields
        fields = data.get("dataset", {}).get("fields", []) or data.get("fields", [])
        names = {f.get("name") for f in fields if isinstance(f, dict) and f.get("name")}
        self._schema_fields = names
        self.log.info("Schéma dataset récupéré : %d champs", len(names))
        return names

    def resolve_field(self, candidates: list[str]) -> str | None:
        """Retourne le premier champ candidat réellement présent dans le
        schéma du dataset. Journalise si aucun ne l'est."""
        fields = self.get_schema_fields()
        if not fields:
            # Schéma indisponible : on retient le 1er candidat (best effort),
            # la présence réelle sera revérifiée sur les enregistrements.
            return candidates[0] if candidates else None
        for c in candidates:
            if c in fields:
                return c
        self.log.warning("Aucun champ candidat présent dans le schéma parmi %s", candidates)
        return None

    # -- Comptage -------------------------------------------------------------
    def count(self, where: str | None = None) -> int:
        params = {"limit": 0}
        if where:
            params["where"] = where
        data = self._get(self._records_url, params=params)
        return int(data.get("total_count", 0))

    # -- Pagination -----------------------------------------------------------
    def iter_records(self, where: str | None, label: str, resume: bool = True):
        """Génère tous les enregistrements correspondant à ``where``.

        Sauvegarde chaque page brute sous ``raw_dir/<label>/page_<offset>.json``.
        Avec ``resume=True``, une page déjà présente sur disque est relue au
        lieu d'être refetchée (reprise sur erreur / rejouabilité).
        """
        page_dir = self.raw_dir / _safe(label)
        page_dir.mkdir(parents=True, exist_ok=True)
        limit = self.http.page_size

        total = self.count(where)
        self.log.info("[%s] total_count annoncé par l'API : %d", label, total)
        if total > ODS_MAX_WINDOW:
            self.log.warning(
                "[%s] %d > fenêtre max %d de l'API v2.1 : les résultats au-delà "
                "de l'offset %d ne seront pas paginables. Restreindre davantage le "
                "périmètre (par département).",
                label, total, ODS_MAX_WINDOW, ODS_MAX_WINDOW,
            )

        offset = 0
        yielded = 0
        while True:
            if offset + limit > ODS_MAX_WINDOW and offset < total:
                self.log.warning(
                    "[%s] fenêtre de pagination (%d) atteinte à l'offset %d : "
                    "arrêt. %d / %d enregistrements récupérés.",
                    ODS_MAX_WINDOW, offset, yielded, total)
                break

            page_file = page_dir / f"page_{offset:06d}.json"
            if resume and page_file.exists():
                data = json.loads(page_file.read_text(encoding="utf-8"))
                self.log.info("[%s] page offset=%d relue depuis le disque", label, offset)
            else:
                params = {"limit": limit, "offset": offset}
                if where:
                    params["where"] = where
                data = self._get(self._records_url, params=params)
                page_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

            results = data.get("results", [])
            if not results:
                break
            for rec in results:
                yield rec
                yielded += 1

            if len(results) < limit:
                break
            offset += limit

        self.log.info("[%s] pagination terminée : %d enregistrements", label, yielded)


def where_hash(where: str | None) -> str:
    return hashlib.sha1((where or "").encode("utf-8")).hexdigest()[:8]


def _safe(name: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", name)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return "".join(ch if ch.isalnum() else "_" for ch in s).strip("_").lower()
