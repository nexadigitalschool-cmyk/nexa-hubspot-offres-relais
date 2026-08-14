"""Étape 4 — Enrichissement nominatif (contacts professionnels publics).

Recherche de contacts professionnels PUBLICS pour chaque lycée, dans l'ordre :
site officiel de l'établissement, site de l'académie, annuaire institutionnel,
page professionnelle publique, puis LinkedIn/Sales Navigator UNIQUEMENT si un
accès légal déjà configuré est disponible.

Règles impératives appliquées par ce code :
  * aucun nom inventé — on n'extrait que du texte réellement présent ;
  * aucun email déduit sans preuve ; un email académique reconstruit à partir
    d'un nom RÉELLEMENT trouvé est marqué « Non vérifié » ;
  * aucun téléphone créé ou deviné ;
  * les emails génériques du lycée restent dans l'onglet Établissements ;
  * aucune donnée personnelle non professionnelle ;
  * respect des robots.txt et des limites d'accès ;
  * source + date conservées pour chaque information ;
  * si aucun contact n'est trouvé : le lycée est conservé et marqué
    « Contact nominatif non trouvé ».

Aucun envoi à qui que ce soit, aucun import HubSpot.
"""
