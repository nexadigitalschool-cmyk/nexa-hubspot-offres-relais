"""Tests étape 4 : extraction (sans invention), robots, cascade, assemblage."""
from __future__ import annotations

from ie_prospection.enrich_nominatif.build4 import NO_CONTACT, build_nominatif
from ie_prospection.enrich_nominatif.extractors import extract_contacts
from ie_prospection.enrich_nominatif.robots import RobotsPolicy
from ie_prospection.enrich_nominatif.schema4 import (
    classify_email_type,
    is_generic_email,
    profile_for_role,
)
from ie_prospection.enrich_nominatif.sources4 import NominatifConfig, gather_for_etab

DATE = "2026-08-14"

PAGE = """
<html><body>
<h2>Équipe de direction</h2>
<p>Proviseur : M. Jean DUPONT — jean.dupont@ac-paris.fr</p>
<p>Proviseure adjointe : Mme Claire MARTIN</p>
<p>DDFPT : M. Paul BERNARD, tél : 01 23 45 67 89</p>
<p>Référent orientation : Mme Alice PETIT</p>
<p>Professeure documentaliste (CDI) : Mme Sofia NGUYEN</p>
<p>Responsable du bureau des entreprises : M. Karim LEROY</p>
<p>Secrétariat : secretariat@lycee.fr</p>
</body></html>
"""


# --- Extraction --------------------------------------------------------------
def test_extract_names_and_roles_with_proof():
    cs = extract_contacts(PAGE, "https://x.fr", "0750001A", "Site officiel", DATE,
                          generic_email="ce.0750001a@ac-paris.fr")
    by_role = {c["Rôle"]: c for c in cs}
    assert "Proviseur / chef d'établissement" in by_role
    prov = by_role["Proviseur / chef d'établissement"]
    assert prov["Civilité"] == "M." and prov["Prénom"] == "Jean" and prov["Nom"] == "DUPONT"
    assert prov["Profil"] == "Décideur"
    assert prov["Email"] == "jean.dupont@ac-paris.fr"
    assert prov["Email vérifié O/N"] == "N"        # jamais O sans validation
    assert prov["Extrait de preuve"]                # preuve présente
    assert prov["URL source"] == "https://x.fr"


def test_no_name_no_contact_no_invention():
    html = "<p>Proviseur : contactez le secrétariat</p>"
    cs = extract_contacts(html, "u", "0750001A", "s", DATE)
    assert cs == []   # rôle cité sans nom -> aucun contact inventé


def test_generic_email_not_used_as_nominative():
    html = "<p>Proviseur : M. Jean DUPONT — ce.0750001a@ac-paris.fr</p>"
    cs = extract_contacts(html, "u", "0750001A", "s", DATE)
    assert cs[0]["Email"] == ""   # l'email générique n'est pas un email nominatif


def test_reconstructed_email_marked_unverified():
    html = "<p>Proviseure adjointe : Mme Claire MARTIN</p>"
    cs = extract_contacts(html, "u", "0750001A", "s", DATE,
                          generic_email="ce.0750001a@ac-paris.fr",
                          reconstruct_emails=True)
    c = cs[0]
    assert c["Email"] == "claire.martin@ac-paris.fr"
    assert c["Type email"] == "académique reconstruit"
    assert c["Email vérifié O/N"] == "N"
    assert "reconstruit" in c["Extrait de preuve"].lower()


def test_reconstruction_disabled():
    html = "<p>Proviseure adjointe : Mme Claire MARTIN</p>"
    cs = extract_contacts(html, "u", "0750001A", "s", DATE,
                          generic_email="ce.0750001a@ac-paris.fr",
                          reconstruct_emails=False)
    assert cs[0]["Email"] == ""


def test_phone_only_when_present():
    cs = extract_contacts(PAGE, "u", "0750001A", "s", DATE)
    ddfpt = next(c for c in cs if c["Rôle"] == "DDFPT")
    assert ddfpt["Téléphone"].replace(" ", "") == "0123456789"
    prov = next(c for c in cs if c["Rôle"].startswith("Proviseur /"))
    assert prov["Téléphone"] == ""   # pas de téléphone inventé


# --- Classification ----------------------------------------------------------
def test_is_generic_email():
    assert is_generic_email("ce.0750001a@ac-paris.fr")
    assert is_generic_email("secretariat@lycee.fr")
    assert is_generic_email("contact@lycee.fr")
    assert not is_generic_email("jean.dupont@ac-paris.fr")


def test_profile_mapping():
    assert profile_for_role("Proviseur / chef d'établissement") == "Décideur"
    assert profile_for_role("DDFPT") == "Facilitateur"
    assert profile_for_role("Référent orientation") == "Prescripteur"


def test_classify_email_type():
    assert classify_email_type("jean.dupont@ac-paris.fr", False) == "académique publié"
    assert classify_email_type("j.dupont@lycee.fr", False) == "professionnel publié"
    assert classify_email_type("x@y.fr", True) == "académique reconstruit"


# --- robots.txt --------------------------------------------------------------
class _R:
    def __init__(self, code, text):
        self.status_code = code
        self.text = text


class _S:
    def __init__(self, robots_text, code=200):
        self._t = robots_text
        self._c = code

    def get(self, url, timeout=None, headers=None):
        return _R(self._c, self._t)


def test_robots_disallow_blocks():
    pol = RobotsPolicy(session=_S("User-agent: *\nDisallow: /"))
    ok, _ = pol.can_fetch("https://site.fr/direction")
    assert ok is False


def test_robots_allow_permits():
    pol = RobotsPolicy(session=_S("User-agent: *\nDisallow: /private"))
    ok, _ = pol.can_fetch("https://site.fr/direction")
    assert ok is True


def test_robots_unreachable_abstains():
    pol = RobotsPolicy(session=_S("", code=500))
    ok, reason = pol.can_fetch("https://site.fr/x")
    assert ok is False and "abstention" in reason


def test_robots_404_means_allow_all():
    # Absence de robots.txt (404) = pas de restriction => autorisé.
    pol = RobotsPolicy(session=_S("Not Found", code=404))
    ok, reason = pol.can_fetch("https://site.fr/direction")
    assert ok is True and "aucun robots.txt" in reason


def test_robots_403_denies():
    pol = RobotsPolicy(session=_S("Forbidden", code=403))
    ok, _ = pol.can_fetch("https://site.fr/x")
    assert ok is False


# --- Cascade + plafond 5 -----------------------------------------------------
class _PageSession:
    """robots.txt permissif + une page riche sur la home, vide ailleurs."""
    def get(self, url, timeout=None, headers=None):
        if url.endswith("/robots.txt"):
            return _R(200, "User-agent: *\nAllow: /")
        if url.rstrip("/").endswith(".fr"):   # home
            return _R(200, PAGE)
        return _R(200, "<html></html>")


def test_cascade_caps_at_five_and_orders_by_priority():
    etab = {"UAI": "0750001A", "Nom": "Lycée X", "Académie": "Paris",
            "Site web": "https://lycee.fr", "Mail ce.": "ce.0750001a@ac-paris.fr"}
    cfg = NominatifConfig(max_pages_per_site=2)
    contacts, attempts = gather_for_etab(etab, cfg, RobotsPolicy(session=_PageSession()),
                                         _PageSession(), DATE)
    assert len(contacts) == 5                     # 6 rôles présents -> plafonné à 5
    assert contacts[0]["Rôle"].startswith("Proviseur /")   # priorité 1 d'abord
    # LinkedIn désactivé par défaut.
    assert any(a.step == 5 and a.status == "skipped" for a in attempts)


# --- Assemblage --------------------------------------------------------------
def test_build_keeps_all_and_flags_no_contact():
    etabs = [
        ({"UAI": "0750001A", "Nom": "A", "Mail ce.": "ce.0750001a@ac-paris.fr"}, [], []),
        ({"UAI": "0750002B", "Nom": "B"}, [{
            "UAI établissement": "0750002B", "Prénom": "Jean", "Nom": "DUPONT",
            "Rôle": "Proviseur / chef d'établissement", "Profil": "Décideur",
            "Email": "jean.dupont@ac-paris.fr", "Type email": "académique publié",
            "Email vérifié O/N": "N", "Source de la donnée": "Site officiel",
            "URL source": "u", "Date de collecte": DATE}], []),
    ]
    built = build_nominatif(etabs, DATE)
    assert built["stats"]["etablissements"] == 2
    assert built["stats"]["contacts"] == 1
    et = {e["UAI"]: e for e in built["etablissements"]}
    assert et["0750001A"]["Statut recherche nominative"] == NO_CONTACT
    assert et["0750002B"]["Nb contacts trouvés"] == 1
    assert len(built["sans_contact"]) == 1
    assert len(built["emails_a_verifier"]) == 1   # email non vérifié listé
