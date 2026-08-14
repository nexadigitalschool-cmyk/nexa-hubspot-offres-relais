"""Tests du client ODS : pagination >100, erreurs API, retry/backoff, reprise."""
from __future__ import annotations

import pytest

from ie_prospection.config import HttpConfig
from ie_prospection.ods_client import ODSAPIError, ODSClient
from fake_http import FakeResponse, FakeSession

BASE = "https://example.test/api/explore/v2.1"
DSID = "fr-en-annuaire-education"


def _http():
    return HttpConfig(page_size=100, timeout_seconds=5, max_retries=3,
                      backoff_base_seconds=0.01, backoff_max_seconds=0.02,
                      rate_limit_seconds=0)


def _client(tmp_path, session):
    return ODSClient(BASE, DSID, _http(), tmp_path, session=session,
                     sleep=lambda *_: None)


def test_pagination_beyond_100(tmp_path):
    records = [{"identifiant_de_l_etablissement": f"07500{i:03d}A"} for i in range(250)]
    client = _client(tmp_path, FakeSession(records))
    out = list(client.iter_records(where=None, label="Paris", resume=False))
    assert len(out) == 250
    # 3 pages écrites en brut (offsets 0, 100, 200).
    pages = sorted((tmp_path / "paris").glob("page_*.json"))
    assert len(pages) == 3


def test_pagination_exact_multiple_of_page_size(tmp_path):
    records = [{"identifiant_de_l_etablissement": f"075{i:04d}A"} for i in range(200)]
    client = _client(tmp_path, FakeSession(records))
    out = list(client.iter_records(where=None, label="x", resume=False))
    assert len(out) == 200


def test_retry_then_success_on_500(tmp_path):
    records = [{"identifiant_de_l_etablissement": "0750001A"}]
    errors = [FakeResponse(500, text="boom"), FakeResponse(503, text="again")]
    session = FakeSession(records, error_queue=errors)
    client = _client(tmp_path, session)
    # count() consomme les 2 erreurs puis réussit.
    total = client.count()
    assert total == 1
    assert session.calls == 3


def test_retry_exhausted_raises(tmp_path):
    errors = [FakeResponse(500) for _ in range(10)]
    session = FakeSession([], error_queue=errors)
    client = _client(tmp_path, session)
    with pytest.raises(ODSAPIError):
        client.count()


def test_400_raises_immediately(tmp_path):
    session = FakeSession([], error_queue=[FakeResponse(400, text="where invalide")])
    client = _client(tmp_path, session)
    with pytest.raises(ODSAPIError) as exc:
        client.count(where="bad")
    assert "400" in str(exc.value)


def test_429_respects_retry_after(tmp_path):
    records = [{"identifiant_de_l_etablissement": "0750001A"}]
    errors = [FakeResponse(429, headers={"Retry-After": "0"})]
    session = FakeSession(records, error_queue=errors)
    client = _client(tmp_path, session)
    assert client.count() == 1


def test_resume_reads_saved_pages(tmp_path):
    records = [{"identifiant_de_l_etablissement": f"075{i:04d}A"} for i in range(150)]
    session = FakeSession(records)
    client = _client(tmp_path, session)
    list(client.iter_records(where=None, label="Paris", resume=True))
    calls_first = session.calls
    # Deuxième passe : les pages existent, aucune requête de page supplémentaire
    # (seul count() rappelle l'API).
    client2 = _client(tmp_path, session)
    out = list(client2.iter_records(where=None, label="Paris", resume=True))
    assert len(out) == 150
    # count() = 1 appel ; les pages sont relues du disque.
    assert session.calls == calls_first + 1


def test_schema_resolution(tmp_path):
    session = FakeSession([], dataset_fields=["libelle_academie", "identifiant_de_l_etablissement"])
    client = _client(tmp_path, session)
    assert client.resolve_field(["nom_academie", "libelle_academie"]) == "libelle_academie"
    assert client.resolve_field(["inexistant"]) is None
