# -*- coding: utf-8 -*-
"""Classeur de restitution - NEXA Etape 1 : zones prioritaires IE campus A distance."""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.comments import Comment

SRC = "../data/bassins_scores.json"
OUT = "../NEXA-Etape1-Zones-Prioritaires.xlsx"
R = json.load(open(SRC))

F = "Arial"
NAVY = "1F3864"; BLUE = "2E5C9A"; LIGHT = "DCE6F1"; GREY = "F2F2F2"
GOLD = "FFF2CC"; GREEN = "E2EFDA"; ROSE = "FCE4EC"
INPUT_FONT = Font(name=F, size=10, color="0000FF", bold=True)
YELLOW = PatternFill("solid", fgColor="FFFF00")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()


def title(ws, text, sub, width=10):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=width)
    c = ws.cell(1, 1, text)
    c.font = Font(name=F, size=15, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[1].height = 30
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width)
    c = ws.cell(2, 2 - 1, sub)
    c.font = Font(name=F, size=9, italic=True, color="595959")
    c.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[2].height = 18


def header(ws, row, labels, widths=None, fill=BLUE):
    for i, lab in enumerate(labels, start=1):
        c = ws.cell(row, i, lab)
        c.font = Font(name=F, size=9, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=fill)
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BOX
    ws.row_dimensions[row].height = 42
    if widths:
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w


def prose(ws, start, blocks, width=110, col=1):
    """blocks = [(niveau, texte)] ; niveau : 'h' titre, 'p' paragraphe, 'b' puce"""
    r = start
    ws.column_dimensions[get_column_letter(col)].width = width
    for kind, txt in blocks:
        c = ws.cell(r, col, txt)
        if kind == "h":
            c.font = Font(name=F, size=11, bold=True, color=NAVY)
            ws.row_dimensions[r].height = 22
        elif kind == "b":
            c.font = Font(name=F, size=10)
            c.alignment = Alignment(wrap_text=True, vertical="top", indent=1)
            ws.row_dimensions[r].height = max(15, 13 * (len(txt) // (width - 8) + 1))
        else:
            c.font = Font(name=F, size=10)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[r].height = max(15, 13 * (len(txt) // (width - 4) + 1))
        if kind == "h":
            c.alignment = Alignment(vertical="center")
        r += 1
    return r


# =============================================================== 1. PARAMÈTRES
ws = wb.active
ws.title = "Paramètres"
title(ws, "Paramètres du score d'opportunité territoriale", "Les 4 pondérations ci-dessous pilotent la colonne SCORE de l'onglet « 59 bassins ». Modifiez-les pour tester une autre hypothèse de priorisation.", 6)
ws.column_dimensions["A"].width = 46
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 62

header(ws, 4, ["Axe du score", "Pondération", "Nature de la donnée sous-jacente"], [46, 14, 62])
axes = [
    ("Vivier B1 compatible", 0.40, "PROXY — population INSEE × 1,05 % (ratio national Terminale). Pas un effectif observé."),
    ("Affinité avec les filières NEXA", 0.25, "ESTIMATION EXPERTE — déduite du tissu économique. PAS une donnée DEPP."),
    ("Concentration géographique du vivier", 0.20, "OBSERVÉ — calcul sur données INSEE/La Poste."),
    ("Potentiel économique numérique", 0.15, "ESTIMATION EXPERTE — ancrée sur labels French Tech et grands employeurs."),
]
for i, (lab, val, nat) in enumerate(axes):
    r = 5 + i
    ws.cell(r, 1, lab).font = Font(name=F, size=10)
    c = ws.cell(r, 2, val)
    c.font = INPUT_FONT; c.fill = YELLOW; c.number_format = "0%"
    c.alignment = Alignment(horizontal="center")
    ws.cell(r, 3, nat).font = Font(name=F, size=9, italic=True)
    for col in (1, 2, 3):
        ws.cell(r, col).border = BOX
ws.cell(9, 1, "Total (doit valoir 100 %)").font = Font(name=F, size=10, bold=True)
ws.cell(9, 2, "=SUM(B5:B8)").font = Font(name=F, size=10, bold=True)
ws.cell(9, 2).number_format = "0%"
ws.cell(9, 2).alignment = Alignment(horizontal="center")
ws.cell(9, 3, '=IF(ABS(B9-1)<0.0001,"OK","ERREUR : la somme des pondérations doit faire 100 %")').font = Font(name=F, size=10, bold=True, color="C00000")
ws.cell(9, 2).comment = Comment("Pondérations issues du cadre de mission NEXA (40/25/20/15).\nElles constituent un cadre de départ, pas une vérité mathématique.", "Étape 1", width=320, height=90)

prose(ws, 11, [
    ("h", "Ce qui n'entre volontairement PAS dans le score"),
    ("p", "Conformément au cadre de mission, aucune variable de « propension au distanciel » n'est intégrée : éloignement d'une université, absence d'école numérique, ruralité, présence d'un Campus connecté, coût du logement étudiant, densité d'enseignement supérieur, IPS, profil socio-économique. Ces variables sont collectées séparément (onglet « Hypothèses H1-H8 ») pour être confrontées aux résultats commerciaux réels de l'année 1."),
    ("p", "Le coût de déplacement n'entre pas davantage dans le score ni dans la sélection des zones. La distance aux campus est publiée à titre d'information de planification uniquement."),
    ("p", "Conséquence assumée : les 12 zones P1 contiennent toutes un pôle étudiant majeur. Le score, ne récompensant que le vivier, l'affinité, la concentration et l'économie, désigne mécaniquement des territoires bien dotés — l'inverse de l'intuition du « territoire idéal pour le distanciel ». C'est pourquoi le portefeuille de test ne se limite pas aux P1."),
], width=110)
ws.sheet_view.showGridLines = False

# =============================================================== 2. SYNTHÈSE
ws = wb.create_sheet("Synthèse")
title(ws, "NEXA À distance — Où tester les Interventions Extérieures ?", "Étape 1 : livrable territorial. Aucune liste de lycées à ce stade (objet de l'étape 2). Production : 15 août 2026.", 4)
ws.column_dimensions["A"].width = 58
ws.column_dimensions["B"].width = 24
ws.column_dimensions["C"].width = 60

header(ws, 4, ["Indicateur", "Valeur", "Nature"], [58, 24, 60])
kpi = [
    ("Communes analysées", "34 863  (68,3 M hab.)", "observé — INSEE / Etalab"),
    ("Communes exclues (≤ 60 km de Paris, Lyon ou Lille)", "2 982  (19,1 M hab. — 28,0 %)", "calculé — distance orthodromique, commune par commune"),
    ("Départements totalement exclus", "4  (75, 92, 93, 94)", "calculé"),
    ("Départements partiellement touchés, restant exploitables", "11", "calculé — aucun département exclu en bloc"),
    ("Bassins d'opportunité construits", "75", "calculé — algorithme glouton, rayon 30 km"),
    ("Bassins retenus et scorés", "59", "≥ 250 000 hab. + 5 villes moyennes ajoutées pour tester H7"),
    ("Répartition des priorités", "12 P1 · 18 P2 · 29 P3/TEST", "calculé"),
    ("Zones recommandées au test année 1", "9", "6 cœur de cible · 2 adjacentes · 1 expérimentale"),
]
for i, (a, b, c) in enumerate(kpi):
    r = 5 + i
    ws.cell(r, 1, a).font = Font(name=F, size=10)
    cell = ws.cell(r, 2, b); cell.font = Font(name=F, size=10, bold=True, color=NAVY)
    cell.alignment = Alignment(horizontal="center")
    ws.cell(r, 3, c).font = Font(name=F, size=9, italic=True, color="595959")
    for col in (1, 2, 3):
        ws.cell(r, col).border = BOX
        if i % 2 == 0:
            ws.cell(r, col).fill = PatternFill("solid", fgColor=GREY)

nxt = prose(ws, 15, [
    ("h", "Les trois questions auxquelles ce classeur répond"),
    ("p", "1.  OÙ tester ?  →  onglets « Portefeuille test » (les 9 zones) et « 59 bassins » (l'univers complet)."),
    ("p", "2.  POURQUOI ces zones plutôt que d'autres ?  →  colonne « Pourquoi » de l'onglet « 59 bassins », onglet « Fiches P1 », et ANNEXE A (démarche)."),
    ("p", "3.  QU'ALLONS-NOUS APPRENDRE ?  →  onglet « Hypothèses H1-H8 » et onglets « Sans pôle étudiant » / « Anomalies »."),
    ("p", ""),
    ("h", "Deux avertissements à lire avant d'engager un budget"),
    ("p", "① L'axe « affinité filières » n'est PAS une donnée de l'Éducation nationale. L'accès réseau à data.education.gouv.fr était bloqué pendant la production : les effectifs réels par établissement, série et spécialité (NSI, STI2D, CIEL, STMG) n'ont pas pu être téléchargés. Le vivier est un PROXY (population × 1,05 %) et les potentiels par filière des ESTIMATIONS EXPERTES fondées sur le tissu économique. Un script prêt à l'emploi (pipeline/05_enrichissement_depp.py) remplace ces colonnes par les données observées dès qu'il est lancé depuis un poste au réseau ouvert. C'est la première action à mener."),
    ("p", "② Le classement P1/P2/P3 doit être considéré comme provisoire tant que cette collecte n'a pas eu lieu : 40 % du score repose sur un proxy et 40 % sur du jugement expert. Seuls 20 % (la concentration) sont entièrement observés. Les écarts de score inférieurs à ~5 points ne sont pas significatifs."),
    ("p", ""),
    ("h", "Recommandation"),
    ("p", "Tester 9 bassins, pas 59. La contrainte réelle n'est pas le nombre de zones intéressantes — il y en a beaucoup — mais le nombre d'IE nécessaires pour qu'une zone produise un signal lisible. En dessous de 3 à 5 IE dans un bassin, un résultat nul ne se distingue pas du bruit : on ne saura pas si la zone est mauvaise ou si elle a été mal travaillée. Sur une saison (octobre → mars, ~20 semaines utiles) : 9 bassins × 4 à 5 IE ≈ 40 IE."),
    ("p", "Si la capacité de l'équipe est inférieure, réduire le NOMBRE DE ZONES, pas le nombre d'IE par zone. Liste courte à 5 zones : Marseille, Toulouse, Rennes, Niort, Béziers."),
], width=58)
ws.sheet_view.showGridLines = False

# =============================================================== 3. PORTEFEUILLE
ws = wb.create_sheet("Portefeuille test")
title(ws, "Portefeuille de test recommandé — 9 bassins", "Logique 70 / 20 / 10. Sélection fondée sur les fondamentaux et la diversité des profils : le coût de déplacement n'intervient pas.", 7)
header(ws, 4, ["Rôle", "Bassin", "Rang", "Vivier B1 (Tle est.)", "Profil dominant", "Ce que cette zone apporte au panel", "Hypothèse principale testée"],
       [17, 24, 7, 15, 26, 62, 30])
PORT = [
    ("Cœur de cible", "Marseille – Aix", 1, 18520, "Cyber + Dev + Data/IA", "Le plus gros vivier de France hors exclusion (+33 % sur Toulouse). Mesure le plafond de ce qu'une zone peut produire.", "H3 — économie numérique"),
    ("Cœur de cible", "Toulouse", 2, 13900, "Cyber + Dev + Data/IA", "Affinité maximale du panel (94/100) ET forte concentration (81/100). Aéronautique, spatial, embarqué.", "H5 — NSI / STI2D → Cyber-Dev"),
    ("Cœur de cible", "Bordeaux", 3, 12650, "Dev + Marketing", "Le seul gros vivier du cœur orienté marketing (Cdiscount, Ubisoft, vin, tourisme) — famille que Toulouse, Rennes et Grenoble couvrent mal.", "H6 — STMG → Marketing Digital"),
    ("Cœur de cible", "Rennes", 6, 7500, "Cyber pur", "Pôle cyber national (COMCYBER, DGA-MI). Bassin le plus compact du top 10 (87/100). À opposer directement à Vannes.", "H1 (contre-test) — offre locale forte"),
    ("Cœur de cible", "Grenoble", 7, 7210, "Cyber + Dev + Data/IA", "Territoire délibérément spécialisé (marketing 3/5) : permet de tester l'offre technique isolément. Concentration maximale du panel (88/100).", "H5 — vivier scientifique"),
    ("Cœur de cible", "Rouen", 11, 8080, "Cyber industriel", "Seul profil non « French Tech » du cœur (économie 3/5) : chimie, port, logistique, assurance. Gros vivier (6e du panel).", "H4 — alternance vs recrutement"),
    ("Cible adjacente", "Niort", 27, 2390, "Dev + Data/IA", "L'anomalie la plus forte du panel : affinité 88/100 pour un vivier indexé à 1/100 (MAIF, MACIF, MAAF, Groupama). L'affinité compense-t-elle le volume ?", "H7 — villes moyennes"),
    ("Cible adjacente", "Vannes", 19, 3460, "Cyber", "Pôle cyber breton SANS université de plein exercice (pôle étudiant à 47 km). Même filière que Rennes, configuration inverse.", "H1 + H2 — faible offre locale"),
    ("Zone expérimentale", "Béziers – Narbonne", 55, 4410, "Marketing", "Le contre-test le plus pur : vivier réel supérieur à Niort et Vannes, mais économie numérique 1/5 et aucun pôle étudiant à moins de 59 km.", "H1 + H3 — contre-test"),
]
role_fill = {"Cœur de cible": GREEN, "Cible adjacente": GOLD, "Zone expérimentale": ROSE}
for i, row in enumerate(PORT):
    r = 5 + i
    for j, v in enumerate(row, start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9, bold=(j == 2))
        c.alignment = Alignment(wrap_text=(j in (6, 5, 7)), vertical="center",
                                horizontal="center" if j in (3, 4) else "left")
        c.border = BOX
        if j == 1:
            c.fill = PatternFill("solid", fgColor=role_fill[row[0]])
            c.font = Font(name=F, size=9, bold=True)
        if j == 4:
            c.number_format = '#,##0'
    ws.row_dimensions[r].height = 46
ws.cell(15, 1, "TOTAL vivier estimé du portefeuille").font = Font(name=F, size=10, bold=True)
ws.cell(15, 4, "=SUM(D5:D13)").font = Font(name=F, size=10, bold=True, color=NAVY)
ws.cell(15, 4).number_format = '#,##0'
ws.cell(15, 4).alignment = Alignment(horizontal="center")
ws.cell(15, 6, "=\"soit environ \"&TEXT(D15/SUM('59 bassins'!H2:H60),\"0.0%\")&\" du vivier estimé des 59 bassins de l'univers\"").font = Font(name=F, size=9, italic=True)

prose(ws, 17, [
    ("h", "Réserves immédiates"),
    ("p", "Nantes (4e) et Nice (5e) sont volontairement écartés du premier lot — non par manque de potentiel, mais parce que leurs profils recoupent presque exactement ceux de Bordeaux et de Toulouse. Retenir les six premiers du classement reviendrait à tester trois configurations en en payant six. À substituer immédiatement si une zone du cœur se révèle inexploitable."),
    ("p", ""),
    ("h", "Le cas à part : La Réunion"),
    ("p", "La Réunion (17e, ~7 120 Terminales estimées) est le test le plus discriminant de H2 — éloignement maximal de toute alternative métropolitaine. Elle n'est pas dans les 9 pour son potentiel, mais parce qu'elle appelle une modalité de test différente : webinaires, partenariats rectorat et lycées, relais locaux, plutôt que des IE en présentiel. À lancer en parallèle, sur un budget distinct."),
    ("p", ""),
    ("h", "Si la capacité ne permet que 5 bassins"),
    ("p", "Marseille, Toulouse, Rennes, Niort, Béziers. On garde les deux plus gros viviers, un profil cyber très concentré, l'anomalie d'affinité et le contre-test — c'est-à-dire l'essentiel du pouvoir d'apprentissage du panel complet."),
], width=17)
for rr in range(17, 26):
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=7)
ws.sheet_view.showGridLines = False
ws.freeze_panes = "A5"

# =============================================================== 4. 59 BASSINS
ws = wb.create_sheet("59 bassins")
COLS = [
    ("Rang", 6), ("Bassin", 22), ("Priorité", 9), ("Région(s)", 26), ("Départements", 26),
    ("Villes principales", 46), ("Population du bassin", 12), ("Vivier B1\nTerminales estimées\n(PROXY)", 12),
    ("Nb communes", 9), ("Nb villes ≥ 10 000 hab.", 9), ("Étendue du bassin (km)", 9),
    ("Population à ≤ 20 km (%)", 10),
    ("Cyber\n(1-5)", 7), ("Dev\n(1-5)", 7), ("Data/IA\n(1-5)", 7), ("Marketing\n(1-5)", 8),
    ("Filières dominantes", 24), ("Économie numérique\n(1-5)", 9),
    ("Sous-score vivier /100", 9), ("Sous-score affinité /100", 9), ("Sous-score concentration /100", 9), ("Sous-score économie /100", 9),
    ("SCORE", 9),
    ("Pôle étudiant majeur dans le bassin", 11), ("Distance au pôle étudiant (km)", 10),
    ("Distance au campus NEXA (km)", 10), ("Campus le plus proche", 11),
    ("Pourquoi cette zone mérite notre attention", 90),
]
header(ws, 1, [c[0] for c in COLS], [c[1] for c in COLS])
for i, b in enumerate(R):
    r = 2 + i
    vals = [
        f"=RANK(W{r},$W$2:$W$60)", b["bassin"], f'=IF(A{r}<=12,"P1",IF(A{r}<=30,"P2","P3/TEST"))',
        ", ".join(x for x in b["regions"] if x), ", ".join(b["departements"]),
        ", ".join(b["villes_principales"]), b["pop_bassin"], b["tle_estim"],
        b["nb_communes"], b["nb_villes_10k"], b["etendue_km"], b["conc_20km_pct"],
        b["cyber"], b["dev"], b["data"], b["mkt"], b["filieres_dominantes"], b["eco"],
        b["s_vivier"], b["s_affinite"], b["s_conc"], b["s_eco"],
        f"=ROUND(Paramètres!$B$5*S{r}+Paramètres!$B$6*T{r}+Paramètres!$B$7*U{r}+Paramètres!$B$8*V{r},1)",
        "oui" if b["contient_pole_etudiant"] else "non",
        b["d_pole_etudiant_km"], b["d_campus_nexa_km"], b["campus_proche"], b["why"],
    ]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9, bold=(j in (2, 23)))
        c.border = BOX
        if j in (7, 8):
            c.number_format = '#,##0'
        if j in (11, 12, 25, 26):
            c.number_format = '0.0'
        if j in (19, 20, 21, 22, 23):
            c.number_format = '0.0'
        c.alignment = Alignment(
            wrap_text=(j in (4, 5, 6, 17, 28)),
            vertical="center",
            horizontal="center" if j in (1, 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27) else "left")
    ws.row_dimensions[r].height = 30
ws.auto_filter.ref = f"A1:AB{len(R)+1}"
ws.freeze_panes = "C2"
ws.conditional_formatting.add(f"W2:W{len(R)+1}",
    ColorScaleRule(start_type="min", start_color="F8696B", mid_type="percentile", mid_value=50,
                   mid_color="FFEB84", end_type="max", end_color="63BE7B"))
ws.conditional_formatting.add(f"H2:H{len(R)+1}", DataBarRule(start_type="min", end_type="max", color="638EC6"))
for col in ("M", "N", "O", "P", "R"):
    ws.conditional_formatting.add(f"{col}2:{col}{len(R)+1}",
        ColorScaleRule(start_type="num", start_value=1, start_color="FFFFFF",
                       end_type="num", end_value=5, end_color="4472C4"))
ws.cell(1, 8).comment = Comment(
    "PROXY, pas un effectif observé.\nPopulation du bassin × 1,05 % (ratio national Terminale GT+pro / population).\nÀ remplacer par les effectifs DEPP réels — voir ANNEXE C.", "Étape 1", width=340, height=110)
ws.cell(1, 13).comment = Comment(
    "ESTIMATION EXPERTE (1 à 5), déduite du tissu économique et industriel documenté du territoire.\nCE N'EST PAS une donnée DEPP : aucun effectif NSI / STI2D / CIEL / STMG n'a pu être collecté.", "Étape 1", width=340, height=110)
ws.cell(1, 23).comment = Comment(
    "Formule vivante : recalculée à partir des pondérations de l'onglet « Paramètres ».\nModifiez-les pour tester une autre priorisation.", "Étape 1", width=320, height=90)
ws.cell(1, 1).comment = Comment(
    "Rang calculé sur le SCORE arrondi au dixième.\nLes bassins ex æquo partagent donc le même rang (Metz et Caen à 48,3 ; Saint-Brieuc et Mamoudzou à 30,8).\nRappel : les écarts de score inférieurs à ~5 points ne sont pas significatifs — voir ANNEXE C.", "Étape 1", width=360, height=120)
ws.cell(1, 26).comment = Comment(
    "Information de planification des tournées UNIQUEMENT.\nN'entre ni dans le score, ni dans le classement, ni dans le choix des zones de test.", "Étape 1", width=340, height=90)

# =============================================================== 5. FICHES P1
ws = wb.create_sheet("Fiches P1")
title(ws, "Lecture stratégique des 12 zones P1", "Le coût de déplacement n'intervient dans aucune de ces recommandations : les zones sont jugées sur leurs fondamentaux.", 8)
header(ws, 4, ["Rang", "Bassin", "Pourquoi il ressort", "Vivier", "Affinité NEXA", "Concentration", "Économie numérique", "Hypothèses à tester", "Limites / vigilance", "Recommandation"],
       [6, 22, 60, 34, 46, 40, 34, 30, 56, 34])
FICHES = [
 (1, "Marseille – Aix", "Le premier vivier de France hors exclusion, et de très loin : ~18 520 Terminales estimées, soit 33 % de plus que Toulouse. 2e ville de France, 1re université de France par les effectifs.",
  "1 764 141 hab. · 69 communes · 25 villes ≥ 10 000 hab. — le plus grand nombre de points d'appui IE du panel.",
  "Cyber 5 · Dev 5 · Data/IA 5 · Mkt 4. 4e hub internet européen (câbles sous-marins, data centers), CMA CGM, STMicroelectronics Rousset, Airbus Helicopters.",
  "60/100. 80 % de la population à ≤ 20 km mais étendue de 57 km : bassin tricéphale (Marseille / Aix / étang de Berre).",
  "5/5. Potentiel d'alternance considérable sur les quatre familles.",
  "H3, H5. Sert de plafond de référence.",
  "Forte hétérogénéité sociale : Marseille Nord, Marseille Sud et Aix sont trois marchés très différents, que le vivier proxy ne capte pas.",
  "P1 — retenu au portefeuille, avec un plan de tournée en trois sous-ensembles."),
 (2, "Toulouse", "2e vivier de l'univers (~13 900 Tle est.), affinité la plus élevée du panel (94/100) et très bonne concentration.",
  "1 323 768 hab. · 232 communes · 18 villes ≥ 10 000 hab. · étendue 38,5 km.",
  "Cyber 5 · Dev 5 · Data/IA 5 · Mkt 4. Aéronautique et spatial (Airbus, Thales Alenia Space, CNES), 1er bassin d'emploi ingénieur hors IDF.",
  "81/100, excellente. 85 % de la population à ≤ 20 km.",
  "5/5.", "H3, H5.",
  "Zone la plus concurrentielle de France sur les formations numériques privées : une part du vivier est déjà couverte en présentiel. Le score, qui ne mesure pas la propension au distanciel, peut surestimer le potentiel réel.",
  "P1 — retenu au portefeuille."),
 (3, "Bordeaux", "3e vivier de l'univers (~12 650 Tle est.), Capitale French Tech, concentration remarquable pour cette taille (24 villes ≥ 10 000 hab. dans 44 km).",
  "1 204 696 hab. · 176 communes.",
  "Cyber 4 · Dev 5 · Data/IA 4 · Mkt 5. Profil rare : Cdiscount, Ubisoft, aéronautique-défense-spatial (Dassault, Thales, ArianeGroup), économie du vin et du tourisme.",
  "74/100. 82 % de la population à ≤ 20 km.",
  "5/5.", "H6 en priorité (Marketing Digital sur gros vivier).",
  "Offre supérieure locale très dense : comme à Toulouse, une part du vivier est déjà captée en présentiel.",
  "P1 — retenu au portefeuille : seul gros vivier du cœur orienté Marketing."),
 (4, "Nantes", "~10 390 Tle est., bonne concentration (78/100) et l'un des écosystèmes numériques les plus dynamiques de France.",
  "989 985 hab. · 94 communes · 14 villes ≥ 10 000 hab.",
  "Cyber 4 · Dev 5 · Data/IA 4 · Mkt 5. Capitale French Tech, Atlanpole, quartier de la création, Airbus, forte densité d'ESN.",
  "78/100, très bonne.", "5/5.", "H6, H3.",
  "Profil recoupant très largement celui de Bordeaux : les tester tous deux la même année apporterait peu d'information supplémentaire. Saint-Nazaire et Cholet sont limitrophes.",
  "P1 — 1re réserve du portefeuille."),
 (5, "Nice – Antibes – Cannes", "~11 480 Tle est. adossées à Sophia Antipolis, 1er technopôle européen. Volume métropolitain ET spécialisation numérique forte.",
  "1 093 251 hab. · 87 communes · 18 villes ≥ 10 000 hab.",
  "Cyber 5 · Dev 5 · Data/IA 4 · Mkt 4. Sophia Antipolis (Amadeus, Orange Labs), économie touristique et évènementielle haut de gamme.",
  "58/100, la plus faible du top 5. Bassin LINÉAIRE : 47,6 km d'étendue, 51 % de la population à ≤ 20 km.",
  "5/5.", "H3, H5, H6.",
  "La linéarité impose une tournée en axe, pas en étoile. Le profil cyber/dev recoupe Marseille et Toulouse.",
  "P1 — 2e réserve du portefeuille."),
 (6, "Rennes", "Le meilleur rapport affinité / concentration de l'univers. Pôle cyber de rang national, bassin remarquablement compact (22,3 km d'étendue).",
  "714 155 hab. · 144 communes · ~7 500 Tle est. · 8 villes ≥ 10 000 hab.",
  "Cyber 5 · Dev 5 · Data/IA 4 · Mkt 4. COMCYBER, DGA-MI, campus cyber breton, b<>com, télécoms.",
  "87/100, 2e meilleure du panel.", "5/5.",
  "H5 en priorité. Meilleur CONTRE-terrain de H1 du panel.",
  "Écosystème de formation supérieure très fourni (INSA, ENSAI, Rennes 1) : mauvais terrain pour confirmer H1, excellent pour la réfuter.",
  "P1 — retenu au portefeuille : profil cyber le plus pur, à opposer à Vannes."),
 (7, "Grenoble", "Vivier scientifique probablement le plus dense de France rapporté à sa taille, dans un bassin contraint par le relief donc le plus concentré du panel.",
  "686 820 hab. · 181 communes · ~7 210 Tle est. · 11 villes ≥ 10 000 hab.",
  "Cyber 5 · Dev 5 · Data/IA 5 · Mkt 3. CEA-Leti, STMicroelectronics, instrumentation, calcul. Zone SPÉCIALISÉE, pas généraliste.",
  "88/100, la meilleure de tout le panel.", "5/5.",
  "H5, H3. Forme avec Rennes une paire de contrôle.",
  "Ne pas y pousser l'offre Marketing Digital sans test préalable : le vivier local paraît mal aligné. Concurrence forte du supérieur public scientifique.",
  "P1 — retenu au portefeuille : seul territoire délibérément spécialisé du cœur."),
 (8, "Strasbourg", "~8 950 Tle est. avec le profil d'affinité le plus équilibré du panel : 4/5 sur les quatre familles simultanément, cas unique parmi les P1.",
  "852 523 hab. · 204 communes · 12 villes ≥ 10 000 hab.",
  "Cyber 4 · Dev 4 · Data/IA 4 · Mkt 4. Capitale européenne, banque-assurance, industrie, écosystème numérique structuré.",
  "67/100. Haguenau nettement excentré (étendue 48,5 km).", "4/5.",
  "H3, H6. Meilleur candidat pour tester l'offre NEXA complète.",
  "Aucune famille n'y est distinctive, ce qui rend l'interprétation des résultats moins tranchée que sur des zones spécialisées.",
  "P1 — non retenu en année 1 pour cette raison d'interprétabilité."),
 (9, "Montpellier – Nîmes", "~10 080 Tle est. sur l'un des corridors les plus dynamiques démographiquement de France. Bassin interdépartemental par construction (34 + 30).",
  "960 447 hab. · 136 communes · 12 villes ≥ 10 000 hab.",
  "Cyber 4 · Dev 5 · Data/IA 4 · Mkt 4. IBM, Dell, santé numérique. L'un des rares bassins réellement généralistes.",
  "45/100, point faible majeur. Étendue 53 km, 33 % de la population à ≤ 20 km. Bassin BICÉPHALE.",
  "4/5.", "H6, et H7 via Nîmes.",
  "Traiter Montpellier et Nîmes comme deux tournées séparées. La concentration est la plus faible du top 10.",
  "P1 — avec scission opérationnelle explicite en deux sous-bassins."),
 (10, "Angers", "Affinité de niveau métropolitain (81/100) sur un vivier de ville moyenne. Capitale French Tech, Cité de l'objet connecté.",
  "483 174 hab. · 87 communes · ~5 070 Tle est. · 7 villes ≥ 10 000 hab.",
  "Cyber 4 · Dev 5 · Data/IA 4 · Mkt 4. Écosystème électronique / IoT sans équivalent à cette taille de ville.",
  "72/100, bonne. Étendue 33,9 km.", "4/5, remarquable rapportée à la taille du bassin.",
  "H7 en premier lieu (villes moyennes).",
  "À 88 km de Nantes : une partie du vivier peut viser Nantes en présentiel, y compris chez d'autres écoles. Ce risque de substitution n'est pas mesuré.",
  "P1 — meilleur représentant « haut de gamme » de H7."),
 (11, "Rouen", "Gros vivier (~8 080 Tle est., 6e du panel), bonne concentration (16 villes ≥ 10 000 hab. dans un rayon serré) et profil économique distinct de tous les autres P1.",
  "769 914 hab. · 336 communes — le maillage le plus fin du panel.",
  "Cyber 4 · Dev 3 · Data/IA 3 · Mkt 3. Chimie, industrie, logistique portuaire, assurance (Matmut). Orienté cybersécurité industrielle et systèmes.",
  "74/100.", "3/5. Moins visible que Rennes ou Grenoble, mais réelle et industrielle.",
  "H4 — le meilleur terrain du panel.",
  "L'affinité est estimée depuis le tissu industriel, sans donnée DEPP : c'est précisément une zone où le taux réel de STI2D et Bac Pro CIEL doit être vérifié avant d'engager.",
  "P1 — retenu au portefeuille : seul profil industriel non « French Tech » du cœur."),
 (12, "Clermont-Ferrand", "Bassin isolé sans concurrence métropolitaine proche, bien concentré, avec une affinité technique élevée portée par Michelin (data et IA industrielle) et Limagrain.",
  "529 942 hab. · 208 communes · ~5 560 Tle est. · 9 villes ≥ 10 000 hab.",
  "Cyber 4 · Dev 4 · Data/IA 4 · Mkt 3.",
  "72/100. 77 % de la population à ≤ 20 km.", "4/5.",
  "H2 — aucune métropole concurrente à moins de 2 h.",
  "Université Clermont Auvergne et offre supérieure locale substantielle : la zone n'est pas sous-dotée, seulement isolée. Bien distinguer les deux dans l'interprétation.",
  "P1."),
]
for i, row in enumerate(FICHES):
    r = 5 + i
    for j, v in enumerate(row, start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9, bold=(j == 2))
        c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="center" if j == 1 else "left")
        c.border = BOX
        if i % 2 == 0:
            c.fill = PatternFill("solid", fgColor=GREY)
    ws.row_dimensions[r].height = 96
ws.freeze_panes = "C5"
ws.sheet_view.showGridLines = False

# =============================================================== 6. SANS PÔLE ÉTUDIANT
ws = wb.create_sheet("Sans pôle étudiant")
title(ws, "Zones à vivier réel mais sans offre supérieure locale", "Support direct des hypothèses H1 et H2 — celles que NEXA veut pouvoir vérifier, pas confirmer.", 6)
header(ws, 4, ["Bassin", "Priorité", "Vivier B1 (Tle est.)", "Distance au pôle étudiant majeur (km)", "Filières dominantes", "Économie numérique (1-5)"],
       [26, 10, 15, 16, 30, 13])
sub = sorted([b for b in R if not b["contient_pole_etudiant"]], key=lambda x: -x["tle_estim"])
for i, b in enumerate(sub):
    r = 5 + i
    for j, v in enumerate([b["bassin"], b["priorite"], b["tle_estim"], b["d_pole_etudiant_km"], b["filieres_dominantes"], b["eco"]], start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9, bold=(j == 1))
        c.alignment = Alignment(horizontal="left" if j in (1, 5) else "center", vertical="center")
        c.border = BOX
        if j == 3:
            c.number_format = '#,##0'
ws.conditional_formatting.add(f"C5:C{4+len(sub)}", DataBarRule(start_type="min", end_type="max", color="638EC6"))
r = 6 + len(sub)
prose(ws, r, [
    ("h", "Lecture"),
    ("p", "Béziers–Narbonne est le meilleur support de H1/H2 du panel : c'est le plus gros vivier de la liste (~4 410 Terminales estimées, supérieur à Niort et à Vannes), sans aucun pôle étudiant à moins de 59 km, et avec une économie numérique notée 1/5 — il teste donc simultanément H1 et H3."),
    ("p", "Saint-Quentin est le contre-test le plus radical (économie numérique 1/5 également), mais son vivier est le plus faible du panel : un résultat nul y serait ambigu."),
    ("p", "Attention : « offre locale » est ici approximée par la seule présence d'un pôle étudiant majeur. Le décompte réel des formations numériques post-bac (BTS SIO, BTS CIEL, BUT informatique, BUT MMI, BUT R&T, bachelors) n'a pas pu être collecté — voir ANNEXE C."),
], width=26)
for rr in range(r, r + 5):
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=6)
ws.freeze_panes = "A5"
ws.sheet_view.showGridLines = False

# =============================================================== 7. ANOMALIES
ws = wb.create_sheet("Anomalies")
title(ws, "Anomalies territoriales — forte affinité, vivier modeste", "Les « pépites » qu'un classement mécanique par volume aurait manquées.", 6)
header(ws, 4, ["Bassin", "Rang", "Sous-score affinité /100", "Sous-score vivier /100", "Écart", "Pourquoi"], [24, 7, 13, 13, 9, 84])
ano = sorted(R, key=lambda x: -(x["s_affinite"] - x["s_vivier"]))[:12]
for i, b in enumerate(ano):
    r = 5 + i
    vals = [b["bassin"], b["rang"], b["s_affinite"], b["s_vivier"], f"=C{r}-D{r}", b["why"]]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9, bold=(j in (1, 5)))
        c.alignment = Alignment(wrap_text=(j == 6), vertical="center", horizontal="left" if j in (1, 6) else "center")
        c.border = BOX
        if j in (3, 4, 5):
            c.number_format = '0.0'
    ws.row_dimensions[r].height = 30
ws.conditional_formatting.add(f"E5:E{4+len(ano)}", DataBarRule(start_type="min", end_type="max", color="F4B183"))
ws.freeze_panes = "A5"
ws.sheet_view.showGridLines = False

# =============================================================== 8. HYPOTHÈSES
ws = wb.create_sheet("Hypothèses H1-H8")
title(ws, "Les 8 hypothèses expérimentales et leur terrain de test", "Aucune de ces variables n'entre dans le score. Elles sont collectées pour être confrontées aux résultats commerciaux réels de l'année 1.", 5)
header(ws, 4, ["#", "Hypothèse", "Terrain de test dans le panel", "Zone(s) retenue(s) au portefeuille", "Testable en l'état ?"], [5, 46, 62, 34, 42])
HYP = [
 ("H1", "Les zones faiblement couvertes en formations numériques convertissent mieux.",
  "Paires appariées par vivier ET par région : Lorient/Saint-Brieuc (écart 0,3 %), Amiens/Dunkerque (1,6 %), La Rochelle/Bayonne (1,8 %), Perpignan/Béziers (6,6 %). Contre-terrain : Rennes et Grenoble, offre locale maximale.",
  "Vannes, Béziers–Narbonne (porteuses) · Rennes, Grenoble (contre-test)",
  "Partiellement — « offre locale » approximée par la seule présence d'un pôle étudiant. Le décompte des formations numériques post-bac reste à collecter."),
 ("H2", "L'éloignement des grands pôles étudiants augmente l'intérêt pour le campus À distance.",
  "Gradient complet : 0 km (Rouen, Dijon, Caen, Grenoble) → 38 km (Belfort) → 47 km (Vannes, Évreux) → 59 km (Béziers) → 69 km (Dunkerque) → 92 km (Saint-Brieuc) → 1 415 km (Mayotte) → La Réunion.",
  "Vannes, Béziers · La Réunion sur modalité distincte",
  "Oui — variable observée et publiée (colonne Y de l'onglet « 59 bassins »)."),
 ("H3", "Un environnement économique numérique dynamique augmente l'intérêt pour les formations NEXA.",
  "Gradient 5/5 (Marseille, Toulouse, Bordeaux, Nantes, Rennes, Grenoble, Nice) → 3/5 (Rouen, Valence, Dijon, Dunkerque) → 1/5 (Béziers, Forbach, Saint-Quentin, Mamoudzou).",
  "Béziers–Narbonne (contre-test décisif) · Marseille, Toulouse (haut du gradient)",
  "Oui, mais l'axe économie est une estimation experte, non une mesure d'emploi numérique."),
 ("H4", "L'économie numérique influence davantage l'alternance que le recrutement étudiant.",
  "Zones à besoins IT industriels réels mais écosystème start-up modeste : Rouen, Le Havre, Belfort–Montbéliard, Dunkerque, Saint-Nazaire — opposées à Grenoble, Rennes, Marseille.",
  "Rouen",
  "Oui, à condition de suivre SÉPARÉMENT le taux d'inscription B1 et le taux de signature en alternance."),
 ("H5", "Les territoires concentrant NSI / STI2D / CIEL surperforment en Cyber/Dev.",
  "Rennes, Grenoble, Toulouse, Marseille, Belfort, Vannes, Brest, Toulon.",
  "Rennes, Grenoble, Toulouse, Vannes",
  "NON en l'état. Les notes cyber/dev sont déduites du tissu économique, pas des effectifs de spécialités. Prérequis absolu : lancer pipeline/05_enrichissement_depp.py."),
 ("H6", "Les territoires à forte présence STMG ou généraliste performent en Marketing Digital.",
  "Gros vivier : Bordeaux (5/5), Nantes (5/5). Vivier moyen : Bayonne (5/5), Angoulême (5/5), Perpignan, Béziers, Avignon, Reims, Tours, Orléans.",
  "Bordeaux, Béziers–Narbonne",
  "Partiellement — la présence effective de STMG est inférée depuis l'économie tertiaire locale, pas mesurée."),
 ("H7", "Les villes moyennes constituent un marché particulièrement intéressant.",
  "Cinq bassins ajoutés SOUS le seuil de population pour rendre l'hypothèse testable : Troyes, Angoulême, Niort, Albi, Saint-Malo. Comparés à Angers (ville moyenne « haut de gamme ») et aux métropoles P1.",
  "Niort · Angers en appui",
  "Oui. Indicateur clé : rendement par IE (inscriptions / IE réalisée), pas volume absolu."),
 ("H8", "Les territoires disposant d'un Campus connecté présentent une meilleure réceptivité au modèle À distance.",
  "89 lieux labellisés au niveau national. Deux implantations seulement confirmées par recherche documentaire (Cahors, Nevers — vague expérimentale 2019), aucune dans un bassin retenu.",
  "— (à déterminer après collecte)",
  "NON en l'état. La liste DGESIP n'a pas pu être récupérée (accès bloqué). Collecte de quelques heures à mener avant le lancement."),
]
for i, row in enumerate(HYP):
    r = 5 + i
    for j, v in enumerate(row, start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9, bold=(j == 1))
        c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="center" if j == 1 else "left")
        c.border = BOX
        if j == 5 and v.startswith("NON"):
            c.fill = PatternFill("solid", fgColor="FFC7CE"); c.font = Font(name=F, size=9, color="9C0006")
        elif j == 5 and v.startswith("Oui"):
            c.fill = PatternFill("solid", fgColor="C6EFCE"); c.font = Font(name=F, size=9, color="006100")
        elif j == 5:
            c.fill = PatternFill("solid", fgColor="FFEB9C"); c.font = Font(name=F, size=9, color="9C6500")
        elif i % 2 == 0:
            c.fill = PatternFill("solid", fgColor=GREY)
    ws.row_dimensions[r].height = 80

r = 14
prose(ws, r, [
    ("h", "Ce qu'il faut instrumenter pour que tout ceci serve"),
    ("p", "Sans suivi du funnel PAR ZONE, aucune de ces hypothèses ne sera vérifiable en fin d'année. Le minimum : zone → lycées prospectés → IE obtenues → lycéens exposés → leads → candidatures → admissions → inscriptions B1."),
    ("p", "Trois ratios suffisent à trancher la plupart des hypothèses : (1) taux d'obtention d'IE = IE obtenues / lycées prospectés — mesure l'accessibilité commerciale, pas le potentiel ; (2) taux de captation = leads / lycéens exposés — indicateur central pour H1, H2, H3, H8 ; (3) rendement par IE = inscriptions / IE réalisée — seul indicateur permettant de comparer une ville moyenne à une métropole (H7)."),
    ("p", "RECOMMANDATION : créer un champ « bassin d'opportunité » sur l'objet lycée du CRM et l'alimenter depuis data/handoff_etape2.json AVANT la première IE. Sans lui, l'année 1 produira des inscriptions mais aucun modèle exploitable pour l'année 2."),
], width=5)
for rr in range(r, r + 5):
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5)
    ws.cell(rr, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[rr].height = 46
ws.cell(r, 1).alignment = Alignment(vertical="center")
ws.row_dimensions[r].height = 22
ws.freeze_panes = "A5"
ws.sheet_view.showGridLines = False

# =============================================================== 9. EXCLUSION
ws = wb.create_sheet("Exclusion 60 km")
title(ws, "Périmètre d'exclusion des campus physiques — 60 km autour de Paris, Lyon et Lille", "Calcul commune par commune (distance orthodromique). Aucun département n'est exclu en bloc.", 6)
header(ws, 4, ["Dép.", "Département", "Nb communes", "Communes exclues", "% communes exclues", "% population exclue", "Statut"],
       [7, 26, 11, 11, 12, 12, 40])
import csv as _csv
rows = list(_csv.DictReader(open("../data/exclusion_departements.csv"), delimiter=";"))
for i, d in enumerate(rows):
    r = 5 + i
    vals = [d["dep"], d["departement"], int(d["nb_communes"]), int(d["communes_exclues_A"]),
            float(d["pct_communes_exclues_A"]) / 100, float(d["pct_population_exclue_A"]) / 100, d["statut_perimetre_A"]]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9)
        c.border = BOX
        c.alignment = Alignment(horizontal="center" if j != 2 and j != 7 else "left", vertical="center")
        if j in (5, 6):
            c.number_format = '0.0%'
        if j in (3, 4):
            c.number_format = '#,##0'
    st = d["statut_perimetre_A"]
    fill = "FFC7CE" if "totalement" in st else ("FFEB9C" if "majoritairement" in st else "C6EFCE")
    ws.cell(r, 7).fill = PatternFill("solid", fgColor=fill)
last = 4 + len(rows)
ws.cell(last + 2, 2, "TOTAL France").font = Font(name=F, size=10, bold=True)
ws.cell(last + 2, 3, f"=SUM(C5:C{last})").font = Font(name=F, size=10, bold=True)
ws.cell(last + 2, 4, f"=SUM(D5:D{last})").font = Font(name=F, size=10, bold=True)
for cc in (3, 4):
    ws.cell(last + 2, cc).number_format = '#,##0'
    ws.cell(last + 2, cc).alignment = Alignment(horizontal="center")
prose(ws, last + 4, [
    ("h", "Deux conséquences commercialement importantes"),
    ("p", "① Sortent du champ du campus À distance : Saint-Étienne (≈ 51 km de Lyon), Valenciennes, Arras, Douai, Béthune (< 60 km de Lille), Beauvais, Creil, Compiègne et Melun (< 60 km de Paris). Ce sont des « villes moyennes » souvent citées spontanément — la règle des 60 km les neutralise."),
    ("p", "② L'Isère reste exploitable à 59 % : Grenoble est à 94 km de Lyon et demeure pleinement dans le périmètre. De même une large moitié du Pas-de-Calais (Boulogne, Calais, Montreuil) reste ouverte."),
    ("p", "Le total ci-dessus ne porte que sur les 19 départements touchés. À l'échelle nationale : 2 982 communes exclues sur 34 863, soit 19,1 M habitants (28,0 % de la population française)."),
], width=7)
for rr in range(last + 4, last + 8):
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=7)
    ws.cell(rr, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[rr].height = 32
ws.cell(last + 4, 1).alignment = Alignment(vertical="center"); ws.row_dimensions[last + 4].height = 22
ws.freeze_panes = "A5"
ws.sheet_view.showGridLines = False

# =============================================================== 10. ANNEXE A — DÉMARCHE
ws = wb.create_sheet("ANNEXE A — Démarche")
title(ws, "ANNEXE A — La démarche, étape par étape", "Ce qui a été fait, dans quel ordre, et pourquoi.", 2)
prose(ws, 4, [
    ("h", "Le principe directeur"),
    ("p", "La mission ne demandait pas le territoire théoriquement parfait pour le distanciel, mais les territoires disposant d'assez de potentiel étudiant compatible NEXA pour justifier une expérimentation IE, avec une concentration géographique permettant une activation commerciale réaliste. L'année 1 doit produire des inscriptions ET produire de l'apprentissage. La sélection est donc assez rigoureuse pour éviter une prospection nationale indifférenciée, assez ouverte pour ne pas enfermer NEXA dans ses propres hypothèses de départ."),
    ("p", ""),
    ("h", "Étape 1 — Exclure les zones de campus physiques (règle des 60 km)"),
    ("p", "Référentiel : 34 863 communes géolocalisées, couvrant 68,3 M habitants (population légale INSEE via Etalab, coordonnées La Poste). Distance orthodromique (formule de haversine, rayon terrestre 6 371,0088 km) entre le chef-lieu de chaque commune et chacun des trois campus. Une commune est exclue si la distance minimale est ≤ 60 km."),
    ("p", "Point de méthode important : le calcul est fait COMMUNE PAR COMMUNE. Aucun département n'a été exclu en bloc parce qu'il contient un campus. Résultat : 2 982 communes exclues (19,1 M hab., 28,0 % de la population), 4 départements totalement exclus, 11 départements partiellement touchés qui restent exploitables."),
    ("p", "Coordonnées retenues — Paris : 44bis quai de Jemmapes 75010 (48,8709 / 2,3646) · Lille : 250 rue Madeleine Rebérioux 59000 (50,6216 / 3,0790) · Lyon : centre-ville, secteur Bellecour (45,7578 / 4,8320). L'adresse exacte du campus lyonnais n'a pas été trouvée en source primaire ; à 60 km de rayon, une imprécision de 2 km est sans effet matériel."),
    ("p", ""),
    ("h", "Étape 2 — Construire les bassins SANS partir du découpage administratif"),
    ("p", "L'unité commerciale recherchée est le bassin d'activation IE, pas le département. La construction est algorithmique, pas déclarative :"),
    ("b", "① Villes-centres candidates : communes de ≥ 15 000 hab., hors exclusion, qui sont un MAXIMUM LOCAL de population dans un rayon de 12 km. Ce filtre évite qu'un bassin soit centré sur une banlieue — sans lui, l'algorithme centrait le bassin bordelais sur Le Bouscat et le bassin nantais sur Bouguenais. 377 candidates → 231 maxima locaux."),
    ("b", "② Rayon de bassin : 30 km autour de la ville-centre, soit ~45 min de trajet — l'amplitude réaliste d'une tournée IE dans la journée."),
    ("b", "③ Sélection gloutonne : on retient à chaque tour la ville-centre dont le bassin capte la plus grande population ENCORE NON ATTRIBUÉE, puis on retire ces communes du pool. Les bassins sont donc disjoints : pas de double comptage du vivier."),
    ("b", "④ Seuil d'arrêt : 110 000 habitants captés. En dessous, une zone ne justifie pas une tournée."),
    ("b", "⑤ Chaque bassin est nommé d'après sa commune la plus peuplée ; toutes ses distances sont mesurées depuis cette ville principale."),
    ("p", "75 bassins sont produits. Ils traversent librement les frontières administratives quand la géographie le justifie : Montpellier–Nîmes (34+30), Dunkerque–Calais (59+62), Metz–Thionville (57+54), Belfort–Montbéliard (25+90+70), Annecy–Annemasse–Genevois (74+01), Béziers–Narbonne (34+11)."),
    ("p", ""),
    ("h", "Étape 3 — Retenir un univers de 59 bassins"),
    ("p", "Sont retenus les 54 bassins de plus de 250 000 habitants, auxquels s'ajoutent 5 villes moyennes situées sous le seuil : Troyes, Angoulême, Niort, Albi, Saint-Malo. Cet ajout est délibéré — sans elles, l'hypothèse H7 (« les villes moyennes constituent un marché intéressant ») serait invérifiable, l'échantillon ne contenant que des agglomérations."),
    ("p", "Les 16 bassins restants (110 000 à 250 000 hab.) constituent une réserve non scorée : La Roche-sur-Yon, Chalon-sur-Saône, Laval, Chartres, Blois, Brive, Épinal, Maubeuge, Draguignan, Soissons, Agen, Montauban, Alès, La Teste-de-Buch, Montereau, Saint-Paul (Réunion)."),
    ("p", "Le total de 59 dépasse la fourchette indicative de 30 à 50 : conformément au cadre de mission, aucune zone pertinente n'a été supprimée pour atteindre un chiffre rond."),
    ("p", ""),
    ("h", "Étape 4 — Scorer sur quatre axes"),
    ("p", "SCORE = 40 % vivier + 25 % affinité + 20 % concentration + 15 % économie numérique. Les pondérations du cadre de mission ont été conservées et sont modifiables dans l'onglet « Paramètres »."),
    ("b", "Vivier B1 (40 %) — PROXY : population du bassin × 1,05 %. Ratio calé sur les ancrages DEPP publiés pour la rentrée 2024 (~1,597 M élèves en formations générales et technologiques, ~651 000 en voie professionnelle, soit de l'ordre de 720 000 élèves de Terminale pour 68,3 M habitants). Normalisation en RACINE CARRÉE avant mise à l'échelle 0-100 : cela atténue le biais métropolitain sans l'effacer — une agglomération 4 fois plus peuplée n'obtient que 2 fois plus de points."),
    ("b", "Affinité NEXA (25 %) — ESTIMATION EXPERTE. Quatre notes de 1 à 5 (cyber, développement, data/IA, marketing) fondées sur le tissu économique et industriel documenté, avec justification factuelle consignée dans la colonne « Pourquoi ». Raisonnement type : base industrielle / mécatronique / électronique → vivier probable STI2D et Bac Pro CIEL → cyber et dev ; assurance, mutualité, banque, calcul intensif → data/IA ; économie tertiaire, tourisme, commerce, marque → STMG et générales → marketing digital."),
    ("b", "Concentration (20 %) — ENTIÈREMENT OBSERVÉ : 0,40 × part de la population à ≤ 20 km du centre + 0,35 × pénalité d'étendue (100 à ≤ 25 km ; 0 à ≥ 60 km entre villes de ≥ 10 000 hab.) + 0,25 × nombre de villes de ≥ 10 000 hab. (plafonné à 10). Cette troisième composante mesure la capacité à ENCHAÎNER plusieurs IE sur une même tournée : un bassin d'une seule grande ville est concentré mais offre peu de points d'appui."),
    ("b", "Économie numérique (15 %) — ESTIMATION EXPERTE ancrée sur des faits vérifiables : labels French Tech (19 Capitales et 28 Communautés pour 2026-2028), grands employeurs à besoins numériques, technopôles, projets d'implantation. L'analyse ne se limite pas aux start-up : Niort est noté 4/5 pour ses mutuelles, Pau 4/5 pour le supercalculateur de TotalEnergies, Le Havre 3/5 pour la cybersécurité portuaire. Un potentiel économique faible n'élimine jamais une zone — il ne pèse que 15 %."),
    ("p", ""),
    ("h", "Étape 5 — Composer le portefeuille de test"),
    ("p", "Le portefeuille n'est PAS le top 9 du classement. Trois principes le gouvernent :"),
    ("b", "① Diversité de profils. Marseille, Toulouse et Nice partagent un profil Cyber+Dev+Data ; Bordeaux et Nantes un profil Dev+Marketing ; Rennes et Grenoble un profil technique très concentré. Retenir les six premiers du classement reviendrait à tester TROIS configurations en en payant six. Le cœur de cible retenu couvre six profils distincts."),
    ("b", "② Capacité à tester les hypothèses. Les 12 zones P1 contiennent TOUTES un pôle étudiant majeur : elles ne permettent pas, à elles seules, de tester H1 et H2. D'où l'ajout de Vannes, Niort et Béziers."),
    ("b", "③ Répartition 70 / 20 / 10 entre cœur de cible, cibles adjacentes et zone expérimentale — appliquée dans l'esprit, pas mécaniquement."),
    ("p", "Le coût de déplacement n'intervient dans aucun de ces trois principes. Il agit uniquement sur le NOMBRE de zones testées (9 sur 59), pas sur leur identité. L'intégrer à la sélection reviendrait à confondre « où le potentiel est-il réel ? » avec « où est-il commode d'aller ? », et concentrerait mécaniquement l'expérimentation autour de l'Île-de-France, de Rhône-Alpes et des Hauts-de-France."),
], width=125)
ws.sheet_view.showGridLines = False

# =============================================================== 11. ANNEXE B — POURQUOI
ws = wb.create_sheet("ANNEXE B — Choix de méthode")
title(ws, "ANNEXE B — Pourquoi ces choix de méthode", "Les décisions structurantes et ce qu'elles écartent.", 2)
prose(ws, 4, [
    ("h", "Pourquoi ne pas commencer par les lycées ?"),
    ("p", "Produire d'emblée une liste de 1 000 ou 2 000 établissements aurait donné un fichier commercial sans stratégie. La logique appliquée est : où sont les viviers ? → où sont-ils assez intéressants ET assez concentrés pour justifier une expérimentation ? → quels bassins retenir ? Les établissements précis relèvent de l'étape 2, une fois les zones validées. Ce classeur reste donc strictement territorial."),
    ("p", ""),
    ("h", "Pourquoi des bassins et pas des départements ?"),
    ("p", "Un département est une unité administrative, pas un marché. La Haute-Garonne et le Gers n'ont pas le même sens commercial que « Toulouse et sa couronne ». Les bassins construits ici correspondent à ce qu'une équipe commerciale peut réellement travailler dans une journée, et plusieurs d'entre eux sont interdépartementaux parce que la géographie économique l'impose."),
    ("p", ""),
    ("h", "Pourquoi la « propension au distanciel » est-elle exclue du score ?"),
    ("p", "C'est la décision méthodologique la plus importante du livrable, et elle est délibérée. Nous ne savons pas encore si l'éloignement d'une université, la ruralité, l'IPS, l'absence d'école numérique ou la présence d'un Campus connecté prédisent réellement l'intérêt pour NEXA À distance. Les intégrer au scoring maintenant reviendrait à sélectionner uniquement les territoires qui confirment nos hypothèses de départ — et à sortir de l'année 1 avec un modèle qui n'aurait fait que se refléter lui-même."),
    ("p", "Ces variables sont donc COLLECTÉES mais NON SCORÉES : ce sont des variables expérimentales, destinées à être confrontées aux résultats commerciaux réels. Si l'hypothèse se confirme, elle pourra fonder la stratégie commerciale du campus À distance en année 2."),
    ("p", "Conséquence assumée, et c'est l'enseignement méthodologique central de cette étape : les 12 zones P1 contiennent TOUTES un pôle étudiant majeur. Le score, ne récompensant que le volume, l'affinité, la concentration et l'économie, désigne mécaniquement des territoires bien dotés en enseignement supérieur — c'est-à-dire exactement l'inverse de l'intuition du « territoire idéal pour le distanciel ». Cette tension justifie à elle seule que le portefeuille de test ne soit pas constitué des seuls P1."),
    ("p", ""),
    ("h", "Pourquoi la racine carrée sur le vivier ?"),
    ("p", "Un classement mécanique par volume ferait remonter les plus grandes agglomérations françaises et rien d'autre. La normalisation en racine carrée atténue ce biais sans l'effacer — le volume reste un avantage réel, mais décroissant. C'est ce qui permet à Angers (5 070 Tle est.) de se classer devant Metz (7 230) grâce à son affinité et à sa concentration."),
    ("p", "En complément, l'onglet « Anomalies » identifie explicitement les territoires dont l'affinité dépasse le plus largement le poids démographique — les zones qu'un tri par volume aurait manquées. Aucun quota artificiel par région ou par département n'a en revanche été appliqué : une région ne reçoit pas de zone prioritaire pour assurer une représentation nationale."),
    ("p", ""),
    ("h", "Pourquoi le coût de déplacement est-il écarté de la sélection ?"),
    ("p", "Parce qu'il répond à une autre question. « Où le potentiel est-il réel ? » et « où est-il commode d'aller ? » sont deux problèmes distincts, et les confondre produirait une carte de la commodité déguisée en carte du potentiel — concentrée autour de l'Île-de-France, de Rhône-Alpes et des Hauts-de-France, soit précisément le biais que la règle des 60 km cherchait à éviter."),
    ("p", "La contrainte budgétaire est donc prise en compte là où elle a du sens : sur le NOMBRE de zones testées. La distance aux campus reste publiée (colonne Z de l'onglet « 59 bassins ») pour organiser les tournées une fois les zones choisies."),
    ("p", ""),
    ("h", "Pourquoi 9 zones et pas 20 ?"),
    ("p", "Parce que la contrainte réelle n'est pas le nombre de zones intéressantes mais le nombre d'IE nécessaires pour qu'une zone produise un signal lisible. En dessous de 3 à 5 IE dans un bassin, un résultat nul ne se distingue pas du bruit : on ne saura pas si la zone est mauvaise ou si elle a été mal travaillée. Disperser l'effort sur 20 zones produirait 20 résultats non interprétables — c'est le vrai coût, bien plus que le déplacement."),
    ("p", "Corollaire opérationnel : si la capacité de l'équipe est inférieure à ~40 IE, réduire le NOMBRE DE ZONES, jamais le nombre d'IE par zone."),
    ("p", ""),
    ("h", "Pourquoi un contre-test comme Béziers dans le portefeuille ?"),
    ("p", "Parce qu'un plan composé des seules meilleures zones ne peut rien réfuter. Béziers–Narbonne a un vivier réel (~4 410 Tle est., supérieur à Niort et Vannes), une économie numérique notée 1/5, et aucun pôle étudiant à moins de 59 km. Si Béziers convertit, l'axe économie numérique devra être fortement dépondéré en année 2 et l'hypothèse d'un potentiel porté par le seul vivier scolaire prendra le dessus. Si Béziers ne convertit pas, le modèle actuel est conforté. Dans les deux cas, NEXA apprend quelque chose — ce qui n'est pas garanti en ne testant que des zones favorables."),
], width=125)
ws.sheet_view.showGridLines = False

# =============================================================== 12. ANNEXE C — LIMITES
ws = wb.create_sheet("ANNEXE C — Limites")
title(ws, "ANNEXE C — Ce que ce livrable ne permet PAS d'affirmer", "À lire avant d'engager le moindre budget.", 2)
prose(ws, 4, [
    ("h", "La contrainte de collecte, à l'origine de la plupart des limites"),
    ("p", "L'environnement de production disposait d'un accès réseau restreint. data.education.gouv.fr (API DEPP), data.gouv.fr, enseignementsup-recherche.gouv.fr, ONISEP, Parcoursup et les API INSEE étaient TOUS bloqués. Seuls le référentiel Etalab (via npm), la base des codes postaux La Poste (via GitHub) et la recherche web étaient accessibles."),
    ("p", "Il en découle que l'ossature géographique et démographique de l'analyse est observée et recalculable, mais que son ossature SCOLAIRE est un proxy. Aucune valeur n'a été inventée pour combler un trou : les colonnes non collectées sont marquées « À COLLECTER » et jamais remplies par zéro."),
    ("p", ""),
    ("h", "① Le vivier n'est pas mesuré"),
    ("p", "Toutes les valeurs de vivier sont issues de population × 1,05 %. Ce ratio national ignore : la structure par âge locale (La Réunion et Mayotte sont nettement plus jeunes — leur vivier est probablement SOUS-estimé ; Béziers, Perpignan et Saint-Malo, plus âgés, probablement SUR-estimés) ; l'attractivité scolaire d'une ville-centre sur sa périphérie ; le poids de l'enseignement privé, très variable selon les régions ; les taux de scolarisation et de redoublement locaux."),
    ("p", "CONSÉQUENCE PRATIQUE : ces chiffres servent à CLASSER des bassins entre eux, pas à dimensionner une campagne. Ne pas les reprendre dans un budget ou un objectif commercial."),
    ("p", ""),
    ("h", "② L'affinité par filière n'est pas une donnée scolaire"),
    ("p", "Les notes cyber / dev / data / marketing sont dérivées du tissu économique. Elles reposent sur une chaîne de raisonnement plausible mais NON VÉRIFIÉE : économie industrielle locale → lycées techniques → présence de STI2D et Bac Pro CIEL → vivier cyber/dev. Chaque maillon peut être faux."),
    ("p", "Deux faits nationaux invitent à la prudence : un lycée sur trois ne propose toujours pas la spécialité NSI ; et NSI ne représente que 4,0 % des élèves de Terminale générale en 2025 (4,5 % en 2024, en baisse). Autrement dit, le vivier « NSI » d'un bassin de 5 000 Terminales générales se compte en quelques CENTAINES d'élèves, très inégalement répartis. Un territoire industriel peut parfaitement n'offrir NSI que dans deux lycées."),
    ("p", "CONSÉQUENCE PRATIQUE : l'axe affinité (25 % du score) doit être remplacé par des données DEPP AVANT l'allocation du budget de déplacement."),
    ("p", ""),
    ("h", "③ Le score est un outil de tri, pas une mesure"),
    ("p", "40 % du score repose sur un proxy, 40 % supplémentaires (25 % affinité + 15 % économie) sur du jugement expert. Seuls 20 % (concentration) sont entièrement observés. Les écarts de score inférieurs à ~5 points ne sont pas significatifs : Metz et Caen sont à 48,3 tous les deux, et l'ordre entre les rangs 18 et 30 ne doit pas être interprété comme un classement."),
    ("p", ""),
    ("h", "④ Les distances sont orthodromiques, pas routières"),
    ("p", "Toutes les distances sont calculées à vol d'oiseau. L'écart avec le temps de trajet réel est important en zone de relief (Grenoble, Annecy, La Réunion) et sur les littoraux découpés (Bretagne, Var). Cela vaut aussi pour l'exclusion des 60 km : une commune à 58 km à vol d'oiseau de Lyon peut être à plus de 75 min de route. La règle a été appliquée telle qu'énoncée, mais la frontière est poreuse et mérite un arbitrage NEXA sur les cas limites."),
    ("p", ""),
    ("h", "⑤ Les bassins bicéphales"),
    ("p", "Quatre bassins regroupent des marchés que l'algorithme fusionne par contiguïté mais qui doivent être travaillés séparément : Montpellier–Nîmes (53 km d'étendue, 33 % de la population à 20 km), Annecy–Annemasse–Genevois (55 km, 50 %), Dunkerque–Calais (56 km, 50 %) et Marseille–Aix–étang de Berre (57 km, tricéphale)."),
    ("p", ""),
    ("h", "Données manquantes, par ordre de priorité"),
    ("b", "1. Effectifs Terminale réels par établissement — remplace le proxy du vivier (axe à 40 %). Sources : fr-en-lycee_gt-effectifs-niveau-sexe-lv et fr-en-lycee_pro-effectifs-niveau-sexe-lv. Script fourni."),
    ("b", "2. Effectifs par spécialité (NSI, maths) et série (STI2D, STMG, CIEL) — remplace l'affinité experte (axe à 25 %). Source : fr-en-effectifs-specialites-doublettes-terminale-generale. Script fourni."),
    ("b", "3. Nombre de lycées par bassin — dimensionne la cible commerciale de l'étape 2. Source : fr-en-annuaire-education. Script fourni."),
    ("b", "4. Liste des 89 Campus connectés — rend H8 testable, et identifie des partenaires opérationnels potentiels (ce sont des lieux qui accueillent DÉJÀ des étudiants inscrits à distance). Source : services.dgesip.fr/CampusConnectes. Effort : ~2 h."),
    ("b", "5. Offre supérieure numérique locale (BTS SIO/CIEL, BUT informatique/MMI/R&T, bachelors) — rend H1 réellement testable. Sources : Parcoursup, ONISEP. Effort : ~1 j."),
    ("b", "6. IPS des lycées — variable expérimentale socio-économique. Source : fr-en-ips-lycees. Script fourni."),
    ("b", "7. Emploi numérique par bassin — fiabilise l'axe économie (15 %). Sources : France Travail, INSEE Flores, Numeum. Effort : ~1 j."),
    ("b", "8. Temps de trajet routier — planification des tournées en étape 2, sans effet sur la sélection des zones. Effort : ~2 h."),
    ("p", "Les points 1, 2, 3 et 6 sont couverts par le script pipeline/05_enrichissement_depp.py, fourni dans le dépôt et qui n'a pas pu être exécuté faute d'accès réseau."),
], width=125)
ws.sheet_view.showGridLines = False

# =============================================================== 13. ANNEXE D — SOURCES
ws = wb.create_sheet("ANNEXE D — Sources")
title(ws, "ANNEXE D — Sources, millésimes et niveaux de confiance", "Traçabilité des données utilisées.", 4)
header(ws, 4, ["Source", "Millésime", "Usage dans l'analyse", "Accès / date de collecte"], [50, 26, 56, 30])
SRCS = [
    ("INSEE / Etalab — @etalab/decoupage-administratif v6.0.0", "population légale en vigueur 2026", "Population, département, région, EPCI de 34 863 communes", "npm — 15/08/2026"),
    ("La Poste — base officielle des codes postaux (miroir high54/Communes-France-JSON)", "2025", "Coordonnées GPS par code INSEE", "GitHub — 15/08/2026"),
    ("IGN / Etalab — gregoiredavid/france-geojson", "2024", "Contours départementaux (contrôle)", "GitHub — 15/08/2026"),
    ("DEPP — RERS 2025", "rentrée 2024", "~1,597 M élèves en formations générales et technologiques (lycée)", "recherche documentaire — 15/08/2026"),
    ("DEPP", "rentrée 2024", "~651 000 élèves en voie professionnelle (lycée, hors apprentis)", "recherche documentaire — 15/08/2026"),
    ("DEPP", "rentrée 2025", "5,621 M élèves du second degré, tous niveaux", "recherche documentaire — 15/08/2026"),
    ("DEPP — note d'information Enseignements de spécialités", "2025", "Part de NSI en Terminale générale : 4,0 % (4,5 % en 2024)", "recherche documentaire — 15/08/2026"),
    ("DEPP", "2024", "Part des filles en NSI Terminale : 13,7 %", "recherche documentaire — 15/08/2026"),
    ("Société informatique de France", "2024", "~1 lycée sur 3 ne propose pas NSI", "recherche documentaire — 15/08/2026"),
    ("DEPP", "rentrée 2024", "Part de la voie générale en Terminale GT : 72,4 %", "recherche documentaire — 15/08/2026"),
    ("MESR / DGESIP", "2024-2025", "87 à 89 lieux labellisés Campus connecté (liste complète NON récupérée)", "recherche documentaire — 15/08/2026"),
    ("Mission French Tech", "2026-2028", "19 Capitales et 28 Communautés labellisées en France", "recherche documentaire — 15/08/2026"),
    ("NEXA Digital School", "2026", "Campus physiques : Paris, Lyon, Lille — liste confirmée par NEXA", "nexa.fr — 15/08/2026"),
]
for i, row in enumerate(SRCS):
    r = 5 + i
    for j, v in enumerate(row, start=1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BOX
        if i % 2 == 0:
            c.fill = PatternFill("solid", fgColor=GREY)
    ws.row_dimensions[r].height = 28

r = 20
header(ws, r, ["Indicateur", "Niveau de confiance", "Motif", ""], [50, 26, 56, 30])
CONF = [
    ("Exclusion des 60 km", "ÉLEVÉE", "Calcul déterministe sur référentiel officiel", ""),
    ("Population, communes, départements, régions", "ÉLEVÉE", "INSEE / Etalab", ""),
    ("Distances, étendue, concentration", "ÉLEVÉE", "Calcul, sous réserve orthodromique vs routier", ""),
    ("Composition des bassins", "ÉLEVÉE", "Algorithme reproductible et documenté", ""),
    ("Vivier B1 (Terminales estimées)", "MOYENNE", "Proxy national, ignore la structure d'âge locale", ""),
    ("Notes cyber / dev / data / marketing", "FAIBLE", "Estimation experte, non issue de données scolaires", ""),
    ("Note économie numérique", "MOYENNE", "Ancrée sur des faits vérifiables, mais non quantifiée", ""),
    ("Score global", "MOYENNE", "20 % seulement entièrement observés", ""),
    ("Classement P1 / P2 / P3", "MOYENNE", "À réviser après enrichissement DEPP", ""),
    ("Portefeuille de test recommandé", "MOYENNE", "Combine le score et un objectif de diversité de profils et d'hypothèses", ""),
]
for i, row in enumerate(CONF):
    rr = r + 1 + i
    for j, v in enumerate(row[:3], start=1):
        c = ws.cell(rr, j, v)
        c.font = Font(name=F, size=9, bold=(j == 2))
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center" if j == 2 else "left")
        c.border = BOX
        if j == 2:
            fill = {"ÉLEVÉE": "C6EFCE", "MOYENNE": "FFEB9C", "FAIBLE": "FFC7CE"}[v]
            c.fill = PatternFill("solid", fgColor=fill)
    ws.row_dimensions[rr].height = 22
ws.cell(r + 12, 1, "En une phrase : la géographie de ce livrable est solide, sa démographie est raisonnable, sa dimension scolaire reste à établir.").font = Font(name=F, size=10, bold=True, italic=True, color=NAVY)
ws.merge_cells(start_row=r + 12, start_column=1, end_row=r + 12, end_column=4)
ws.sheet_view.showGridLines = False

# =============================================================== 14. LÉGENDE
ws = wb.create_sheet("Légende")
title(ws, "Légende — nature de chaque donnée", "Distinguer ce qui est observé de ce qui est estimé est essentiel pour interpréter ce classeur.", 3)
header(ws, 4, ["Nature", "Ce que cela signifie", "Colonnes concernées"], [24, 62, 62])
LEG = [
    ("DONNÉE OBSERVÉE", "Mesure issue d'une source officielle, recalculable à l'identique.", "Population, nb communes, départements, régions, villes principales, étendue, concentration à 20 km, distances, exclusion 60 km", "C6EFCE"),
    ("PROXY", "Grandeur non disponible, remplacée par une approximation documentée et justifiée.", "Vivier B1 — Terminales estimées (population × 1,05 %)", "FFEB9C"),
    ("ESTIMATION EXPERTE", "Jugement analytique fondé sur des faits documentés, mais qui n'est PAS une mesure.", "Cyber, Dev, Data/IA, Marketing, Économie numérique (notes de 1 à 5)", "FFC7CE"),
    ("HYPOTHÈSE", "Choix de modélisation susceptible d'être révisé par les résultats de l'année 1.", "Pondérations du score (40/25/20/15), table d'affinité série → filière", "DDEBF7"),
    ("INTERPRÉTATION", "Lecture stratégique construite à partir des éléments ci-dessus.", "Colonne « Pourquoi », priorités P1/P2/P3, portefeuille de test recommandé", "E4DFEC"),
]
for i, (a, b, c, col) in enumerate(LEG):
    r = 5 + i
    for j, v in enumerate((a, b, c), start=1):
        cell = ws.cell(r, j, v)
        cell.font = Font(name=F, size=10, bold=(j == 1))
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BOX
        if j == 1:
            cell.fill = PatternFill("solid", fgColor=col)
    ws.row_dimensions[r].height = 42

prose(ws, 12, [
    ("h", "Règle absolue appliquée dans tout le livrable"),
    ("p", "Une absence de donnée n'est JAMAIS transformée en zéro. Les grandeurs non collectées sont marquées « À COLLECTER » avec leur source, et jamais estimées silencieusement."),
    ("p", ""),
    ("h", "Contenu des onglets"),
    ("b", "Paramètres — les 4 pondérations du score, modifiables (cellules jaunes). La colonne SCORE de l'onglet « 59 bassins » se recalcule automatiquement."),
    ("b", "Synthèse — chiffres clés et recommandation en une page."),
    ("b", "Portefeuille test — les 9 zones recommandées pour l'année 1, avec leur rôle et l'hypothèse testée."),
    ("b", "59 bassins — l'univers complet avec tous les indicateurs. Filtres activés, volets figés."),
    ("b", "Fiches P1 — lecture stratégique détaillée des 12 zones prioritaires."),
    ("b", "Sans pôle étudiant — les 18 zones à vivier réel mais sans université de plein exercice (support de H1 et H2)."),
    ("b", "Anomalies — les territoires dont l'affinité dépasse le plus largement le poids démographique."),
    ("b", "Hypothèses H1-H8 — le plan d'apprentissage de l'année 1 et ce qui est testable en l'état."),
    ("b", "Exclusion 60 km — le périmètre neutralisé, département par département."),
    ("b", "ANNEXE A — la démarche, étape par étape."),
    ("b", "ANNEXE B — pourquoi ces choix de méthode, et ce qu'ils écartent."),
    ("b", "ANNEXE C — ce que le livrable ne permet pas d'affirmer, et les données manquantes."),
    ("b", "ANNEXE D — sources, millésimes et niveaux de confiance."),
    ("p", ""),
    ("h", "Prochaine étape"),
    ("p", "L'étape 2 reçoit chaque zone retenue sous forme de périmètre géométrique (point central + rayon de 30 km) via le fichier data/handoff_etape2.json du dépôt, et recherche exhaustivement les établissements de ce périmètre avant de les classer P1/P2/P3. Ce classeur ne descend volontairement pas au niveau lycée."),
], width=24)
for rr in range(12, 33):
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=3)
    ws.cell(rr, 1).alignment = Alignment(wrap_text=True, vertical="top", indent=1)
ws.sheet_view.showGridLines = False

for s in wb.worksheets:
    s.sheet_properties.tabColor = NAVY if s.title.startswith("ANNEXE") else BLUE
wb.save(OUT)
print("écrit :", OUT)
