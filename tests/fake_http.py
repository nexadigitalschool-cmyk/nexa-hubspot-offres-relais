"""Faux client HTTP pour tester le client ODS sans réseau."""
from __future__ import annotations

import json


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None, text=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.headers = headers or {}
        self.text = text or json.dumps(self._payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise AssertionError(f"HTTP {self.status_code}")


class FakeSession:
    """Sert une base d'enregistrements en mémoire avec pagination offset/limit.

    Peut aussi injecter une file de réponses d'erreur préfixes (pour tester
    retry/backoff)."""

    def __init__(self, records, error_queue=None, dataset_fields=None):
        self.records = records
        self.error_queue = list(error_queue or [])
        self.dataset_fields = dataset_fields
        self.calls = 0

    def get(self, url, params=None, timeout=None):
        self.calls += 1
        if self.error_queue:
            err = self.error_queue.pop(0)
            return err

        params = params or {}
        # Endpoint métadonnées (schéma).
        if url.endswith(f"/datasets/{self._dsid(url)}") and "records" not in url:
            fields = [{"name": n} for n in (self.dataset_fields or [])]
            return FakeResponse(200, {"dataset": {"fields": fields}})

        limit = int(params.get("limit", 100))
        offset = int(params.get("offset", 0))
        payload = {"total_count": len(self.records)}
        if limit == 0:
            payload["results"] = []
        else:
            payload["results"] = self.records[offset:offset + limit]
        return FakeResponse(200, payload)

    @staticmethod
    def _dsid(url):
        return url.rstrip("/").split("/datasets/")[-1].split("/")[0]
