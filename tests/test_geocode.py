"""Test du géocodage BAN (avec faux HTTP, sans réseau)."""
from __future__ import annotations

from ie_prospection.geocode import geocode_ban


class _Resp:
    def __init__(self, payload):
        self._p = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._p


class _Sess:
    def __init__(self, payload):
        self._p = payload
        self.last = None

    def get(self, url, params=None, timeout=None):
        self.last = params
        return _Resp(self._p)


def test_geocode_ban_parses_lat_lon():
    payload = {"features": [{
        "geometry": {"coordinates": [2.3652, 48.8710]},  # BAN = [lon, lat]
        "properties": {"score": 0.98},
    }]}
    sess = _Sess(payload)
    coords = geocode_ban("44 bis quai de Jemmapes 75010 Paris", session=sess)
    assert coords == (48.8710, 2.3652)
    assert sess.last["q"].startswith("44 bis")


def test_geocode_ban_no_result_returns_none():
    assert geocode_ban("adresse inexistante", session=_Sess({"features": []})) is None
