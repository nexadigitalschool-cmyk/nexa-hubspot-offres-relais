"""Schéma de l'étape 4 : colonnes, rôles ciblés, profils, classification email."""
from __future__ import annotations

import re

# --- Onglet Contacts (ordre exact demandé) -----------------------------------
CONTACT_COLUMNS = [
    "UAI établissement", "Civilité", "Prénom", "Nom", "Rôle", "Profil",
    "Email", "Type email", "Email vérifié O/N", "Téléphone", "LinkedIn",
    "Source de la donnée", "URL source", "Extrait de preuve",
    "Date de collecte", "Canal préféré",
]

# --- Onglet Établissements ---------------------------------------------------
ETAB_COLUMNS = [
    "UAI", "Nom", "Type", "Statut public/privé", "Adresse", "CP", "Commune",
    "Académie", "Département", "Région", "Téléphone", "Mail ce.", "Site web",
    "Campus rattaché", "Distance campus km",
    "Nb contacts trouvés", "Statut recherche nominative",
    "Statut vérification emails", "Date dernière recherche",
]

# --- Rôles ciblés (priorité) + profil associé --------------------------------
# (clé de détection -> (libellé de rôle, profil, ordre de priorité))
ROLE_SPECS = [
    ("proviseur adjoint", "Proviseur adjoint", "Décideur", 2),
    ("proviseure adjointe", "Proviseur adjoint", "Décideur", 2),
    ("chef d'établissement adjoint", "Proviseur adjoint", "Décideur", 2),
    ("proviseur", "Proviseur / chef d'établissement", "Décideur", 1),
    ("proviseure", "Proviseur / chef d'établissement", "Décideur", 1),
    ("chef d'établissement", "Proviseur / chef d'établissement", "Décideur", 1),
    ("cheffe d'établissement", "Proviseur / chef d'établissement", "Décideur", 1),
    ("ddfpt", "DDFPT", "Facilitateur", 3),
    ("directeur délégué aux formations", "DDFPT", "Facilitateur", 3),
    ("chef de travaux", "DDFPT", "Facilitateur", 3),
    ("bureau des entreprises", "Responsable bureau des entreprises", "Facilitateur", 4),
    ("référent orientation", "Référent orientation", "Prescripteur", 5),
    ("referent orientation", "Référent orientation", "Prescripteur", 5),
    ("professeur documentaliste", "Professeur documentaliste / CDI", "Prescripteur", 6),
    ("professeure documentaliste", "Professeur documentaliste / CDI", "Prescripteur", 6),
    ("documentaliste", "Professeur documentaliste / CDI", "Prescripteur", 6),
]

MAX_CONTACTS_PER_ETAB = 5

# --- Classification des emails ----------------------------------------------
# Emails génériques (à laisser dans l'onglet Établissements, jamais nominatifs).
GENERIC_LOCALPARTS = (
    "ce", "contact", "secretariat", "secrétariat", "intendance", "gestion",
    "direction", "accueil", "scolarite", "scolarité", "info", "communication",
    "cdi", "vie-scolaire", "viescolaire", "0",
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
UAI_LOCAL_RE = re.compile(r"^ce\.[0-9]{7}[a-z]", re.IGNORECASE)


def is_generic_email(email: str) -> bool:
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        return True
    local = email.split("@", 1)[0]
    if UAI_LOCAL_RE.match(email):
        return True
    if "." not in local:
        # sans point : rarement un prénom.nom -> traité comme générique.
        return local in GENERIC_LOCALPARTS or True
    return local.split(".")[0] in GENERIC_LOCALPARTS


def classify_email_type(email: str, reconstructed: bool) -> str:
    if reconstructed:
        return "académique reconstruit"
    dom = (email or "").split("@")[-1].lower()
    if dom.startswith("ac-") or ".ac-" in dom or dom.endswith("education.gouv.fr"):
        return "académique publié"
    return "professionnel publié"


def profile_for_role(role_label: str) -> str:
    for _, label, profile, _ in ROLE_SPECS:
        if label == role_label:
            return profile
    return ""
