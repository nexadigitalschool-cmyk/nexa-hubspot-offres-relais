"""Extraction de contacts professionnels depuis une page HTML publique.

Principe : on n'extrait QUE ce qui est littéralement présent. Un nom n'est
retenu que s'il apparaît explicitement à côté d'un rôle ciblé (civilité +
Prénom + NOM). Aucun nom, email ou téléphone n'est inventé. Chaque contact
porte un extrait de preuve et l'URL source.
"""
from __future__ import annotations

import html as _html
import re

from .schema4 import (
    EMAIL_RE,
    ROLE_SPECS,
    classify_email_type,
    is_generic_email,
    profile_for_role,
)

# Civilité + Prénom (Capitalisé) + NOM (MAJUSCULES) — conservateur.
_NAME_RE = re.compile(
    r"(M\.|Mme|Mr|Monsieur|Madame)\s+"
    r"([A-ZÀ-Ÿ][a-zà-ÿ'’\-]+)\s+"
    r"([A-ZÀ-Ÿ][A-ZÀ-Ÿ'’\-]{1,})"
)
_PHONE_RE = re.compile(r"(?:t[ée]l[\s.:]*)((?:0|\+33)[\s.\-]?\d(?:[\s.\-]?\d){8})",
                       re.IGNORECASE)
_TAG_RE = re.compile(r"(?is)<(script|style).*?>.*?</\1>")
_ANYTAG_RE = re.compile(r"(?s)<[^>]+>")


def html_to_text(html: str) -> str:
    txt = _TAG_RE.sub(" ", html or "")
    txt = _ANYTAG_RE.sub(" ", txt)
    txt = _html.unescape(txt)
    return re.sub(r"\s+", " ", txt).strip()


def _civility(raw: str) -> str:
    r = raw.lower().rstrip(".")
    if r in ("m", "mr", "monsieur"):
        return "M."
    if r in ("mme", "madame"):
        return "Mme"
    return raw


def _reconstruct_email(prenom: str, nom: str, generic_email: str) -> str | None:
    """Reconstruit un email académique à partir d'un NOM réellement trouvé.
    Retourne None si aucun domaine académique n'est disponible."""
    dom = (generic_email or "").split("@")[-1].strip().lower()
    if not dom or not (dom.startswith("ac-") or ".ac-" in dom
                       or dom.endswith("education.gouv.fr")):
        return None
    p = _slug(prenom)
    n = _slug(nom)
    if not p or not n:
        return None
    return f"{p}.{n}@{dom}"


def _slug(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower())


def extract_contacts(html: str, url: str, uai: str, source_label: str,
                     date: str, generic_email: str = "",
                     reconstruct_emails: bool = True) -> list[dict]:
    """Extrait les contacts ciblés présents dans la page."""
    text = html_to_text(html)
    low = text.lower()
    found: dict[tuple, dict] = {}
    consumed: list[tuple[int, int]] = []   # spans de rôles déjà attribués

    # Rôles traités du plus spécifique au plus générique (évite « proviseur »
    # de capter « proviseure adjointe »).
    specs = sorted(ROLE_SPECS, key=lambda s: -len(s[0]))
    for key, role_label, profile, _prio in specs:
        start = 0
        while True:
            i = low.find(key, start)
            if i == -1:
                break
            start = i + len(key)
            span = (i, i + len(key))
            if any(not (span[1] <= c[0] or span[0] >= c[1]) for c in consumed):
                continue  # chevauche un rôle plus spécifique déjà attribué

            m, name_abs = _bind_name(text, i, len(key))
            if not m:
                continue  # rôle cité sans nom explicite -> on n'invente pas
            consumed.append(span)
            civ, prenom, nom = _civility(m.group(1)), m.group(2), m.group(3)
            dedup_key = (uai, prenom.lower(), nom.lower(), role_label)
            if dedup_key in found:
                continue

            # Email / téléphone : fenêtre ÉTROITE, bornée AVANT le nom suivant
            # (n'attribue jamais les coordonnées de l'entrée voisine).
            end = name_abs + 90
            nxt = _NAME_RE.search(text, name_abs + len(m.group(0)))
            if nxt:
                end = min(end, nxt.start())
            near = text[name_abs: end]

            email, email_type, verified, reconstructed = "", "", "N", False
            for em in EMAIL_RE.findall(near):
                if not is_generic_email(em):
                    email = em
                    break
            if not email and reconstruct_emails:
                rec = _reconstruct_email(prenom, nom, generic_email)
                if rec:
                    email, reconstructed = rec, True
            if email:
                email_type = classify_email_type(email, reconstructed)

            # Téléphone : seulement si littéralement présent juste après le nom.
            phone = ""
            pm = _PHONE_RE.search(near)
            if pm:
                phone = re.sub(r"[\s.\-]", " ", pm.group(1)).strip()

            proof = text[max(0, name_abs - 60): name_abs + 140].strip()
            if len(proof) > 240:
                proof = proof[:237] + "…"
            if reconstructed:
                proof = "Email reconstruit (NON vérifié) à partir du nom publié : " + proof

            found[dedup_key] = {
                "UAI établissement": uai,
                "Civilité": civ, "Prénom": prenom, "Nom": nom,
                "Rôle": role_label, "Profil": profile,
                "Email": email,
                "Type email": email_type,
                "Email vérifié O/N": verified,   # jamais "O" sans validation externe
                "Téléphone": phone,
                "LinkedIn": "",
                "Source de la donnée": source_label,
                "URL source": url,
                "Extrait de preuve": proof,
                "Date de collecte": date,
                "Canal préféré": _preferred_channel(email, phone),
                "_priority": _prio,
            }
    return list(found.values())


def _bind_name(text: str, i: int, klen: int):
    """Associe à un rôle situé à l'index ``i`` le nom qui lui est ADJACENT :
    d'abord juste après le rôle (« Rôle : M. Prénom NOM »), sinon juste avant
    (« M. Prénom NOM, rôle »). Retourne (match, position_absolue) ou (None, -1).
    """
    fwd = text[i + klen: i + klen + 55]
    m = _NAME_RE.search(fwd)
    if m and m.start() <= 25:
        return m, i + klen + m.start()
    bwd_start = max(0, i - 55)
    bwd = text[bwd_start: i]
    last = None
    for mm in _NAME_RE.finditer(bwd):
        last = mm
    if last and (len(bwd) - last.end()) <= 20:
        return last, bwd_start + last.start()
    return None, -1


def _preferred_channel(email: str, phone: str) -> str:
    if email:
        return "Email (à vérifier)"
    if phone:
        return "Téléphone"
    return "Standard établissement"
