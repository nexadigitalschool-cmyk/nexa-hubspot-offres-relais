"""Assemblage des onglets Établissements / Contacts + rapports (étape 4)."""
from __future__ import annotations

from collections import Counter

from .schema4 import ETAB_COLUMNS

NO_CONTACT = "Contact nominatif non trouvé"


def build_nominatif(results: list, date: str) -> dict:
    """results : liste de (etab_row, contacts, attempts). Retourne les onglets
    et les rapports."""
    etablissements: list[dict] = []
    contacts: list[dict] = []
    sans_contact: list[dict] = []
    emails_a_verifier: list[dict] = []
    source_counter: Counter = Counter()

    for etab, etab_contacts, attempts in results:
        uai = etab.get("UAI", "")
        n = len(etab_contacts)

        # Statut de vérification des emails de l'établissement.
        emails = [c for c in etab_contacts if c.get("Email")]
        if not emails:
            verif = "aucun email nominatif" if n else "n/a"
        elif all(c.get("Email vérifié O/N") == "N" for c in emails):
            verif = "emails à vérifier"
        else:
            verif = "vérifiés"

        etab_out = {col: etab.get(col, "") for col in ETAB_COLUMNS}
        etab_out.update({
            "UAI": uai,
            "Nb contacts trouvés": n,
            "Statut recherche nominative": NO_CONTACT if n == 0 else f"{n} contact(s)",
            "Statut vérification emails": verif,
            "Date dernière recherche": date,
        })
        etablissements.append(etab_out)
        contacts.extend(etab_contacts)

        for a in attempts:
            source_counter[(a.step, a.source, a.status)] += 1

        if n == 0:
            reasons = sorted({f"{a.source}:{a.status}" for a in attempts})
            sans_contact.append({
                "UAI": uai, "Nom": etab.get("Nom", ""),
                "Académie": etab.get("Académie", ""),
                "Site web": etab.get("Site web", ""),
                "Statut": NO_CONTACT,
                "Raisons": " | ".join(reasons),
                "Date dernière recherche": date,
            })

        for c in emails:
            if c.get("Email vérifié O/N") == "N":
                emails_a_verifier.append({
                    "UAI établissement": uai,
                    "Prénom": c.get("Prénom", ""), "Nom": c.get("Nom", ""),
                    "Rôle": c.get("Rôle", ""),
                    "Email": c.get("Email", ""),
                    "Type email": c.get("Type email", ""),
                    "Email vérifié O/N": "N",
                    "Source de la donnée": c.get("Source de la donnée", ""),
                    "URL source": c.get("URL source", ""),
                    "Date de collecte": c.get("Date de collecte", ""),
                })

    sources_report = [
        {"étape": step, "source": source, "statut": status, "occurrences": count}
        for (step, source, status), count in sorted(source_counter.items())
    ]

    stats = {
        "etablissements": len(etablissements),
        "contacts": len(contacts),
        "lycees_sans_contact": len(sans_contact),
        "emails_a_verifier": len(emails_a_verifier),
        "contacts_par_lycee_moyen": (len(contacts) / len(etablissements))
        if etablissements else 0.0,
    }
    return {
        "etablissements": etablissements, "contacts": contacts,
        "sans_contact": sans_contact, "emails_a_verifier": emails_a_verifier,
        "sources_report": sources_report, "stats": stats,
    }
