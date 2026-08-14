"""Respect des robots.txt et des limites d'accès.

Politique conservatrice : si le robots.txt interdit l'URL, on ne la récupère
pas. Si le robots.txt est inaccessible, on s'abstient également (on ne force
jamais l'accès). Chaque décision est traçable.
"""
from __future__ import annotations

import urllib.robotparser
from urllib.parse import urlparse

import requests

from ..logging_utils import get_logger

DEFAULT_UA = "NEXA-IE-prospection-bot"


class RobotsPolicy:
    def __init__(self, user_agent: str = DEFAULT_UA, timeout: float = 8.0,
                 session: requests.Session | None = None):
        self.ua = user_agent
        self.timeout = timeout
        self.session = session or requests.Session()
        self._cache: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.log = get_logger()

    def _robots_for(self, url: str):
        """Retourne (état, parser). État ∈ {ok, allow_all, deny, abstain}.

        Conventions robots.txt :
          * 2xx -> on obéit aux règles publiées ;
          * 401/403 -> accès restreint : on s'abstient (deny) ;
          * autres 4xx (404/410…) -> aucun robots.txt = tout autorisé ;
          * 5xx / erreur réseau -> indisponibilité temporaire : abstention.
        """
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base in self._cache:
            return self._cache[base]
        robots_url = base + "/robots.txt"
        result = ("abstain", None)
        try:
            resp = self.session.get(robots_url, timeout=self.timeout,
                                    headers={"User-Agent": self.ua})
            code = resp.status_code
            if code in (401, 403):
                result = ("deny", None)
            elif 400 <= code < 500:
                result = ("allow_all", None)      # pas de robots.txt = autorisé
            elif code >= 500:
                result = ("abstain", None)
            else:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(resp.text.splitlines())
                result = ("ok", rp)
        except Exception as exc:  # noqa: BLE001
            self.log.debug("robots.txt injoignable pour %s : %s", base, exc)
            result = ("abstain", None)
        self._cache[base] = result
        return result

    def can_fetch(self, url: str) -> tuple[bool, str]:
        state, rp = self._robots_for(url)
        if state == "allow_all":
            return True, "aucun robots.txt (autorisé par défaut)"
        if state == "ok":
            if rp.can_fetch(self.ua, url):
                return True, "autorisé par robots.txt"
            return False, "interdit par robots.txt"
        if state == "deny":
            return False, "robots.txt protégé (401/403) — abstention"
        return False, "robots.txt indisponible (5xx/réseau) — abstention"
