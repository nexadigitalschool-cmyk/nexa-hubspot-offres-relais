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
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base in self._cache:
            return self._cache[base]
        rp = urllib.robotparser.RobotFileParser()
        robots_url = base + "/robots.txt"
        try:
            resp = self.session.get(robots_url, timeout=self.timeout,
                                    headers={"User-Agent": self.ua})
            if resp.status_code >= 400:
                rp = None  # robots inaccessible -> abstention
            else:
                rp.parse(resp.text.splitlines())
        except Exception as exc:  # noqa: BLE001
            self.log.debug("robots.txt inaccessible pour %s : %s", base, exc)
            rp = None
        self._cache[base] = rp
        return rp

    def can_fetch(self, url: str) -> tuple[bool, str]:
        rp = self._robots_for(url)
        if rp is None:
            return False, "robots.txt inaccessible — abstention"
        if rp.can_fetch(self.ua, url):
            return True, "autorisé par robots.txt"
        return False, "interdit par robots.txt"
