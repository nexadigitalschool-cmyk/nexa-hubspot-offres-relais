#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstruction vectorielle des trois percussions africaines.

Le fichier produit est un SVG 100% vectoriel, sans bitmap, sans filtre,
sans texte et sans fond : uniquement <path>, <ellipse>, <circle>,
<polygon>, <polyline>, <g> et <clipPath>.

Chaque percussion est modelisee comme une surface de revolution :
  - un profil (demi-largeur en fonction de la hauteur locale) ;
  - une projection "ellipse" (ecrasement vertical sq = ry / rx).
Tous les motifs sont places en coordonnees (hauteur, azimut) puis
projetes, ce qui reproduit naturellement la legere perspective de la
reference (bandes qui s'incurvent, motifs comprimes sur les bords).
"""

import math

CANVAS = 1244

# --------------------------------------------------------------------------
# Palette echantillonnee sur la reference
# --------------------------------------------------------------------------
P = {
    "ivoire":       "#F7EFDC",
    "ivoire_ombre": "#E8DABB",
    "or":           "#EFA62B",
    "or_clair":     "#F5C463",
    "or_pale":      "#F7D48A",
    "orange":       "#E4791E",
    "terre":        "#C5531C",
    "rouge":        "#B22A27",
    "rouge_fonce":  "#98221F",
    "brun":         "#AC6A2C",
    "brun_clair":   "#B87B34",
    "brun_fonce":   "#5C3419",
    "contour":      "#3B2015",
    "corde":        "#3F2417",
    "blanc":        "#FFFFFF",
    "creme":        "#FBF3E3",
    "olive":        "#6F8A3A",
}

TRAIT_EXT = 7.0     # contour exterieur
TRAIT_INT = 4.0     # details interieurs


# --------------------------------------------------------------------------
# Utilitaires numeriques / geometriques
# --------------------------------------------------------------------------
def n(v):
    """Nombre compact pour le SVG."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pstr(p):
    return f"{n(p[0])},{n(p[1])}"


def rrect_d(x, y, w, h, r):
    """Rectangle a coins arrondis exprime en <path> (arcs de cercle)."""
    r = min(r, w / 2.0, h / 2.0)
    return (f"M {n(x + r)},{n(y)} L {n(x + w - r)},{n(y)} "
            f"A {n(r)},{n(r)} 0 0 1 {n(x + w)},{n(y + r)} "
            f"L {n(x + w)},{n(y + h - r)} "
            f"A {n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(y + h)} "
            f"L {n(x + r)},{n(y + h)} "
            f"A {n(r)},{n(r)} 0 0 1 {n(x)},{n(y + h - r)} "
            f"L {n(x)},{n(y + r)} "
            f"A {n(r)},{n(r)} 0 0 1 {n(x + r)},{n(y)} Z")


def catmull_rom(pts):
    """Convertit une polyligne en segments de Bezier cubiques (Catmull-Rom)."""
    if len(pts) < 2:
        return []
    ext = [pts[0]] + list(pts) + [pts[-1]]
    segs = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        segs.append((c1, c2, p2))
    return segs


def smooth_path(pts, close=False):
    """Chemin Bezier lisse passant par pts."""
    segs = catmull_rom(pts)
    d = f"M {pstr(pts[0])}"
    for c1, c2, p in segs:
        d += f" C {pstr(c1)} {pstr(c2)} {pstr(p)}"
    if close:
        d += " Z"
    return d


def smooth_segments(pts):
    """Uniquement la partie 'C ...' d'un chemin lisse."""
    return " ".join(f"C {pstr(c1)} {pstr(c2)} {pstr(p)}"
                    for c1, c2, p in catmull_rom(pts))


def sample_spline(pts, per_seg=24):
    """Echantillonne le meme spline Catmull-Rom (pour interpoler hw(y))."""
    segs = catmull_rom(pts)
    out = [pts[0]]
    cur = pts[0]
    for c1, c2, p3 in segs:
        p0 = cur
        for k in range(1, per_seg + 1):
            t = k / per_seg
            u = 1 - t
            x = (u ** 3 * p0[0] + 3 * u * u * t * c1[0]
                 + 3 * u * t * t * c2[0] + t ** 3 * p3[0])
            y = (u ** 3 * p0[1] + 3 * u * u * t * c1[1]
                 + 3 * u * t * t * c2[1] + t ** 3 * p3[1])
            out.append((x, y))
        cur = p3
    return out


# --------------------------------------------------------------------------
# Modele de percussion (surface de revolution)
# --------------------------------------------------------------------------
class Fut:
    def __init__(self, rx, ry, profil):
        self.rx = rx
        self.ry = ry
        self.sq = ry / rx                 # ecrasement de la perspective
        self.profil = profil              # [(y, demi-largeur), ...]
        self.H = profil[-1][0]
        self._dense = sample_spline([(y, w) for y, w in profil], 24)

    # -- profil -----------------------------------------------------------
    def hw(self, y):
        d = self._dense
        if y <= d[0][0]:
            return d[0][1]
        if y >= d[-1][0]:
            return d[-1][1]
        lo, hi = 0, len(d) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if d[mid][0] <= y:
                lo = mid
            else:
                hi = mid
        y0, w0 = d[lo]
        y1, w1 = d[hi]
        t = 0 if y1 == y0 else (y - y0) / (y1 - y0)
        return w0 + (w1 - w0) * t

    # -- projection -------------------------------------------------------
    def pt(self, y, a):
        """Point de la surface a la hauteur y et a l'azimut a (0..pi = face)."""
        w = self.hw(y)
        return (w * math.cos(a), y + self.sq * w * math.sin(a))

    def fore(self, a):
        """Facteur de raccourci horizontal d'un motif place a l'azimut a."""
        return 0.72 + 0.28 * abs(math.sin(a))

    # -- silhouette -------------------------------------------------------
    def contour_d(self):
        gauche = [(-w, y) for y, w in self.profil]
        droite = [(w, y) for y, w in reversed(self.profil)]
        wb = self.profil[-1][1]
        d = f"M {pstr(gauche[0])} " + smooth_segments(gauche)
        d += f" A {n(wb)},{n(self.sq * wb)} 0 0 0 {pstr((wb, self.H))}"
        d += " " + smooth_segments(droite)
        d += f" A {n(self.rx)},{n(self.ry)} 0 0 1 {pstr((-self.rx, 0))} Z"
        return d

    # -- bandes -----------------------------------------------------------
    def bande_d(self, y0, y1):
        r0, r1 = self.hw(y0), self.hw(y1)
        return (f"M {pstr((-r0, y0))} "
                f"A {n(r0)},{n(self.sq * r0)} 0 0 0 {pstr((r0, y0))} "
                f"L {pstr((r1, y1))} "
                f"A {n(r1)},{n(self.sq * r1)} 0 0 1 {pstr((-r1, y1))} Z")

    def bande(self, y0, y1, fill, extra=""):
        return f'<path d="{self.bande_d(y0, y1)}" fill="{fill}"{extra}/>'


# --------------------------------------------------------------------------
# Briques de motifs
# --------------------------------------------------------------------------
def azimuts(count, marge=0.06):
    """Azimuts repartis sur la face visible."""
    a0, a1 = math.pi * marge, math.pi * (1 - marge)
    if count == 1:
        return [math.pi / 2]
    return [a0 + (a1 - a0) * i / (count - 1) for i in range(count)]


def azimuts_cells(count):
    """Centres de `count` cellules contigues sur la face visible."""
    return [math.pi * (i + 0.5) / count for i in range(count)]


def triangle(f, y_base, y_apex, a_c, da, fill):
    p1 = f.pt(y_base, a_c - da)
    p2 = f.pt(y_base, a_c + da)
    p3 = f.pt(y_apex, a_c)
    return (f'<polygon points="{pstr(p1)} {pstr(p3)} {pstr(p2)}" '
            f'fill="{fill}"/>')


def frise_triangles(f, y0, y1, count, c_haut, c_bas, alterne=True):
    """Frise de triangles alternes pointe-en-haut / pointe-en-bas."""
    out = []
    cells = azimuts_cells(count)
    da = math.pi / (2.0 * count)
    for i, a in enumerate(cells):
        if not alterne:
            out.append(triangle(f, y1, y0, a, da, c_haut))
            continue
        if i % 2 == 0:
            out.append(triangle(f, y1, y0, a, da, c_haut))
        else:
            out.append(triangle(f, y0, y1, a, da, c_bas))
    return out


def rang_points(f, y, count, r, fill, marge=0.075):
    out = []
    for a in azimuts(count, marge):
        p = f.pt(y, a)
        rr = r * (0.62 + 0.38 * abs(math.sin(a)))
        out.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="{n(rr)}" '
                   f'fill="{fill}"/>')
    return out


def rang_chevrons(f, y0, y1, count, couleur, w, sens=1):
    """Rang de chevrons (^ si sens=1, v si sens=-1)."""
    out = []
    cells = azimuts_cells(count)
    da = math.pi / (2.6 * count)
    for a in cells:
        if sens > 0:
            pts = [f.pt(y1, a - da), f.pt(y0, a), f.pt(y1, a + da)]
        else:
            pts = [f.pt(y0, a - da), f.pt(y1, a), f.pt(y0, a + da)]
        out.append(f'<polyline points="{" ".join(pstr(p) for p in pts)}" '
                   f'fill="none" stroke="{couleur}" stroke-width="{n(w)}" '
                   f'stroke-linecap="round" stroke-linejoin="round"/>')
    return out


def rang_croix(f, y0, y1, count, couleur, w):
    """Rang de X (motif 'xxxxx' de la reference)."""
    out = []
    cells = azimuts_cells(count)
    da = math.pi / (2.4 * count)
    for a in cells:
        p1, p2 = f.pt(y0, a - da), f.pt(y1, a + da)
        p3, p4 = f.pt(y0, a + da), f.pt(y1, a - da)
        out.append(f'<path d="M {pstr(p1)} L {pstr(p2)} M {pstr(p3)} '
                   f'L {pstr(p4)}" fill="none" stroke="{couleur}" '
                   f'stroke-width="{n(w)}" stroke-linecap="round"/>')
    return out


def rang_tirets(f, y0, y1, count, couleur, w):
    out = []
    for a in azimuts_cells(count):
        p1, p2 = f.pt(y0, a), f.pt(y1, a)
        out.append(f'<path d="M {pstr(p1)} L {pstr(p2)}" fill="none" '
                   f'stroke="{couleur}" stroke-width="{n(w)}" '
                   f'stroke-linecap="round"/>')
    return out


def spirale_d(R, tours=2.4, pas_deg=22):
    """Spirale d'Archimede lissee (Bezier), centree sur l'origine."""
    theta_max = 2 * math.pi * tours
    b = R / theta_max
    pts = []
    th = 0.0
    while th <= theta_max + 1e-6:
        r = b * th
        pts.append((r * math.cos(th - math.pi / 2), r * math.sin(th - math.pi / 2)))
        th += math.radians(pas_deg)
    return smooth_path(pts)


def spirale(f, y, a, R, couleur, w):
    p = f.pt(y, a)
    sx = f.fore(a)
    return (f'<g transform="translate({n(p[0])},{n(p[1])}) scale({n(sx)},1)">'
            f'<path d="{spirale_d(R)}" fill="none" stroke="{couleur}" '
            f'stroke-width="{n(w / sx ** 0.35)}" stroke-linecap="round"/></g>')


def cercle_motif(f, y, a, R):
    """Rosace : disque blanc, couronne de points, coeur orange."""
    p = f.pt(y, a)
    sx = f.fore(a)
    g = [f'<g transform="translate({n(p[0])},{n(p[1])}) scale({n(sx)},1)">']
    g.append(f'<circle cx="0" cy="0" r="{n(R)}" fill="{P["blanc"]}"/>')
    g.append(f'<circle cx="0" cy="0" r="{n(R * 0.60)}" fill="none" '
             f'stroke="{P["orange"]}" stroke-width="{n(R * 0.16)}"/>')
    g.append(f'<circle cx="0" cy="0" r="{n(R * 0.24)}" fill="{P["orange"]}"/>')
    for k in range(12):
        th = 2 * math.pi * k / 12
        g.append(f'<circle cx="{n(R * 0.84 * math.cos(th))}" '
                 f'cy="{n(R * 0.84 * math.sin(th))}" r="{n(R * 0.10)}" '
                 f'fill="{P["orange"]}"/>')
    g.append("</g>")
    return "".join(g)


def losange_motif(f, y, a, R):
    """Losange central du djembe."""
    p = f.pt(y, a)
    sx = f.fore(a)
    g = [f'<g transform="translate({n(p[0])},{n(p[1])}) scale({n(sx)},1)">']
    ext = f"0,{n(-R)} {n(R * 0.62)},0 0,{n(R)} {n(-R * 0.62)},0"
    mid = f"0,{n(-R * 0.70)} {n(R * 0.44)},0 0,{n(R * 0.70)} {n(-R * 0.44)},0"
    inn = f"0,{n(-R * 0.40)} {n(R * 0.25)},0 0,{n(R * 0.40)} {n(-R * 0.25)},0"
    g.append(f'<polygon points="{ext}" fill="{P["blanc"]}"/>')
    g.append(f'<polygon points="{mid}" fill="{P["rouge"]}"/>')
    g.append(f'<polygon points="{inn}" fill="{P["or"]}"/>')
    g.append("</g>")
    return "".join(g)


# --------------------------------------------------------------------------
# Cordages
# --------------------------------------------------------------------------
def corde(f, y0, y1, a_of_y, couleur, w, pas=14):
    """Corde suivant la surface ; a_of_y(y) donne l'azimut."""
    pts = []
    y = y0
    while y < y1:
        a = a_of_y(y)
        if 0.02 <= a <= math.pi - 0.02:
            pts.append(f.pt(y, a))
        else:
            if len(pts) > 1:
                break
            pts = []
        y += pas
    a = a_of_y(y1)
    if 0.02 <= a <= math.pi - 0.02:
        pts.append(f.pt(y1, a))
    if len(pts) < 2:
        return ""
    return (f'<path d="{smooth_path(pts)}" fill="none" stroke="{couleur}" '
            f'stroke-width="{n(w)}" stroke-linecap="round"/>')


def noeud(f, y, a, rw, rh, couleur):
    p = f.pt(y, a)
    sx = f.fore(a)
    d = rrect_d(-rw, -rh, 2 * rw, 2 * rh, min(rw, rh) * 0.75)
    return (f'<g transform="translate({n(p[0])},{n(p[1])}) scale({n(sx)},1)">'
            f'<path d="{d}" fill="{couleur}"/></g>')


def anneau(f, y, couleur, w, complet=False):
    """Cerclage horizontal.

    complet=True  : anneau de tete, entierement visible autour de la peau.
    complet=False : cerclage plaque sur le fut -> seule la moitie avant
                    est visible, la moitie arriere passe derriere la caisse.
    """
    r = f.hw(y)
    if complet:
        return (f'<ellipse cx="0" cy="{n(y)}" rx="{n(r)}" ry="{n(f.sq * r)}" '
                f'fill="none" stroke="{couleur}" stroke-width="{n(w)}"/>')
    # rayon reduit de la demi-epaisseur : le trait reste dans la silhouette
    r = max(r - w / 2.0, 1.0)
    return (f'<path d="M {pstr((-r, y))} A {n(r)},{n(f.sq * r)} 0 0 0 '
            f'{pstr((r, y))}" fill="none" stroke="{couleur}" '
            f'stroke-width="{n(w)}" stroke-linecap="butt"/>')


def collier(f, y0, y1, ecart, fill, contour=None, trait=5.0):
    """Cerclage massif : bandeau cylindrique ferme, legerement debordant."""
    r = f.hw((y0 + y1) / 2.0) + ecart
    ry = f.sq * r
    d = (f"M {pstr((-r, y0))} A {n(r)},{n(ry)} 0 0 0 {pstr((r, y0))} "
         f"L {pstr((r, y1))} A {n(r)},{n(ry)} 0 0 1 {pstr((-r, y1))} Z")
    out = [f'<path d="{d}" fill="{fill}"/>']
    if contour:
        out.append(f'<path d="{d}" fill="none" stroke="{contour}" '
                   f'stroke-width="{n(trait)}" stroke-linejoin="round"/>')
    return out, r


def collier_noeuds(f, y0, y1, r, count, largeur, couleur):
    """Noeuds repartis sur la face avant d'un collier de rayon r."""
    out = []
    for k in range(count):
        a = math.pi * (k + 0.5) / count
        x = r * math.cos(a)
        yc = f.sq * r * math.sin(a)
        d = rrect_d(x - largeur / 2.0, y0 + yc - 1, largeur,
                    (y1 - y0) + 2, largeur * 0.4)
        out.append(f'<path d="{d}" fill="{couleur}"/>')
    return out


def azimuts_anneau(count, complet=True):
    if complet:
        return [2 * math.pi * k / count for k in range(count)]
    return [math.pi * (k + 0.5) / count for k in range(count)]


def noeuds_anneau(f, y, count, rw, rh, couleur, complet=True):
    return [noeud(f, y, t, rw, rh, couleur)
            for t in azimuts_anneau(count, complet)]


# ==========================================================================
# 1. TAMBOUR DE GAUCHE  (fut etroit, cordes a tirants suspendus)
# ==========================================================================
GAUCHE = Fut(150, 40, [
    (0, 150), (60, 149.5), (140, 148), (300, 145), (460, 143),
    (620, 141), (720, 140), (795, 140),
])


def tambour_gauche():
    f = GAUCHE
    caisse, motifs, cordages, cerclages, peaux, contours = [], [], [], [], [], []

    # ---- caisse ---------------------------------------------------------
    caisse.append(f'<path d="{f.contour_d()}" fill="{P["or"]}"/>')
    caisse.append(f.bande(86, 158, P["blanc"]))
    caisse.append(f.bande(352, 568, P["or_pale"]))
    caisse.append(f.bande(612, 698, P["blanc"]))
    caisse.append(f.bande(745, 795, P["brun_fonce"]))

    # ---- motifs : frise haute ------------------------------------------
    motifs += rang_points(f, 58, 15, 6.5, P["blanc"])
    motifs.append(f.bande(78, 86, P["terre"]))
    motifs += frise_triangles(f, 88, 156, 9, P["terre"], P["orange"])
    motifs.append(f.bande(158, 166, P["terre"]))
    motifs += rang_points(f, 190, 15, 6.5, P["blanc"])

    # ---- motifs : section claire a spirales -----------------------------
    motifs.append(f.bande(344, 352, P["terre"]))
    motifs += rang_points(f, 374, 13, 5.5, P["blanc"])
    for a in azimuts(4, 0.235):
        motifs.append(spirale(f, 462, a, 43, P["blanc"], 9.5))
    motifs += rang_points(f, 548, 13, 5.5, P["blanc"])
    motifs.append(f.bande(568, 576, P["terre"]))

    # ---- motifs : frise basse en chevrons -------------------------------
    motifs += rang_points(f, 598, 14, 6.5, P["blanc"])
    couleurs = [P["rouge"], P["orange"], P["olive"]]
    cells = azimuts_cells(9)
    da = math.pi / (2.45 * 9)
    for i, a in enumerate(cells):
        motifs.append(triangle(f, 694, 616, a, da, couleurs[i % 3]))
        if i < len(cells) - 1:
            am = (a + cells[i + 1]) / 2
            motifs.append(triangle(f, 616, 694, am, da * 0.62, P["orange"]))
    motifs += rang_points(f, 722, 13, 5.5, P["blanc"])
    motifs.append(f.bande(738, 746, P["terre"]))

    # ---- cordages : tirants en V + fuseaux suspendus --------------------
    lugs = azimuts(5, 0.19)
    dv = 0.105
    for a in lugs:
        for sgn in (-1, 1):
            cordages.append(corde(
                f, 14, 262,
                lambda y, a=a, s=sgn: a + s * dv * (1 - (y - 14) / 248),
                P["corde"], 6.5, pas=40))
    for a in lugs:
        p = f.pt(262, a)
        sx = f.fore(a)
        cordages.append(
            f'<g transform="translate({n(p[0])},{n(p[1])}) scale({n(sx)},1)">'
            f'<path d="M -7,0 A 7,7 0 0 1 7,0" fill="none" '
            f'stroke="{P["corde"]}" stroke-width="5"/>'
            f'<path d="{rrect_d(-11.5, 2, 23, 72, 10)}" '
            f'fill="{P["brun_fonce"]}"/>'
            f'<path d="{rrect_d(-11.5, 2, 23, 72, 10)}" fill="none" '
            f'stroke="{P["contour"]}" stroke-width="3.5"/></g>')

    # ---- cerclage de tete ----------------------------------------------
    cerclages.append(anneau(f, 12, P["corde"], 17, complet=True))
    cerclages += noeuds_anneau(f, 12, 18, 5.5, 11, P["contour"])

    # ---- peau -----------------------------------------------------------
    peaux.append(f'<ellipse cx="0" cy="0" rx="{n(f.rx)}" ry="{n(f.ry)}" '
                 f'fill="{P["ivoire_ombre"]}"/>')
    peaux.append(f'<ellipse cx="0" cy="-2.5" rx="{n(f.rx - 9)}" '
                 f'ry="{n(f.ry - 7)}" fill="{P["ivoire"]}"/>')

    # ---- contours -------------------------------------------------------
    contours.append(f'<path d="{f.contour_d()}" fill="none" '
                    f'stroke="{P["contour"]}" stroke-width="{n(TRAIT_EXT)}" '
                    f'stroke-linejoin="round"/>')
    contours.append(f'<ellipse cx="0" cy="0" rx="{n(f.rx)}" ry="{n(f.ry)}" '
                    f'fill="none" stroke="{P["contour"]}" '
                    f'stroke-width="{n(TRAIT_EXT)}"/>')
    contours.append(f'<path d="{f.bande_d(745, 745)}" fill="none" '
                    f'stroke="{P["contour"]}" stroke-width="{n(TRAIT_INT)}"/>')
    return f, caisse, motifs, cordages, cerclages, peaux, contours


# ==========================================================================
# 2. DJEMBE CENTRAL
# ==========================================================================
DJEMBE = Fut(228, 48, [
    (0, 228), (70, 227), (140, 223), (222, 216), (290, 203), (345, 183),
    (392, 153), (415, 131), (437, 104), (455, 88), (472, 78), (496, 76),
    (520, 79), (546, 87), (580, 98), (628, 112), (700, 124), (772, 135),
    (880, 148), (977, 160),
])


def djembe_central():
    f = DJEMBE
    caisse, motifs, cordages, cerclages, peaux, contours = [], [], [], [], [], []

    # ---- caisse ---------------------------------------------------------
    caisse.append(f'<path d="{f.contour_d()}" fill="{P["brun"]}"/>')
    caisse.append(f.bande(505, 977, P["brun_clair"]))
    caisse.append(f.bande(150, 204, P["blanc"]))
    caisse.append(f.bande(905, 962, P["or"]))
    caisse.append(f.bande(962, 977, P["brun_fonce"]))

    # ---- motifs de la cuve ---------------------------------------------
    motifs.append(f.bande(142, 150, P["blanc"]))
    motifs += frise_triangles(f, 152, 202, 11, P["orange"], P["terre"])
    for a in azimuts_cells(11)[::2]:
        p = f.pt(166, a)
        motifs.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="5" '
                      f'fill="{P["blanc"]}"/>')
    motifs.append(f.bande(204, 212, P["terre"]))
    motifs += rang_points(f, 243, 15, 8, P["blanc"])

    # ---- motifs du pied -------------------------------------------------
    motifs += rang_croix(f, 566, 600, 10, P["blanc"], 6)
    motifs.append(f.bande(612, 620, P["blanc"]))
    cells = azimuts_cells(11)
    da = math.pi / (2.3 * 11)
    for i, a in enumerate(cells):
        motifs.append(triangle(f, 674, 622, a, da,
                               P["terre"] if i % 2 else P["orange"]))
        p = f.pt(662, a)
        motifs.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="4.5" '
                      f'fill="{P["blanc"]}"/>')
    motifs.append(f.bande(676, 684, P["blanc"]))

    trio = azimuts(3, 0.26)
    motifs.append(spirale(f, 762, trio[0], 50, P["blanc"], 10.5))
    motifs.append(spirale(f, 762, trio[2], 50, P["blanc"], 10.5))
    motifs.append(losange_motif(f, 762, trio[1], 68))
    for a, c in ((trio[1] - 0.27, P["olive"]), (trio[1] + 0.27, P["olive"])):
        motifs.append(triangle(f, 706, 682, a, 0.055, c))
        motifs.append(triangle(f, 818, 842, a, 0.055, c))

    motifs += rang_tirets(f, 872, 894, 18, P["blanc"], 5.5)
    motifs.append(f.bande(898, 905, P["blanc"]))
    cells = azimuts_cells(12)
    da = math.pi / (2.35 * 12)
    for i, a in enumerate(cells):
        motifs.append(triangle(f, 958, 908, a, da,
                               P["orange"] if i % 2 else P["terre"]))
        p = f.pt(946, a)
        motifs.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="4" '
                      f'fill="{P["olive"] if i % 2 else P["rouge"]}"/>')

    # ---- cordages verticaux de la cuve ----------------------------------
    for a in azimuts(15, 0.035):
        cordages.append(corde(f, 26, 462, lambda y, a=a: a, P["corde"], 7,
                              pas=40))

    # ---- cerclages (anneaux rouges + noeuds) ----------------------------
    cerclages.append(anneau(f, 20, P["rouge"], 26, complet=True))
    cerclages += noeuds_anneau(f, 20, 22, 4.5, 14, P["contour"])
    cerclages.append(anneau(f, 8, P["corde"], 12, complet=True))
    col, rcol = collier(f, 458, 492, 7, P["rouge"], P["contour"], 5)
    cerclages += col
    cerclages += collier_noeuds(f, 458, 492, rcol, 11, 8, P["contour"])
    cerclages.append(anneau(f, 450, P["corde"], 10))

    # ---- peau -----------------------------------------------------------
    peaux.append(f'<ellipse cx="0" cy="0" rx="{n(f.rx)}" ry="{n(f.ry)}" '
                 f'fill="{P["ivoire_ombre"]}"/>')
    peaux.append(f'<ellipse cx="0" cy="-3" rx="{n(f.rx - 11)}" '
                 f'ry="{n(f.ry - 8)}" fill="{P["ivoire"]}"/>')

    # ---- contours -------------------------------------------------------
    contours.append(f'<path d="{f.contour_d()}" fill="none" '
                    f'stroke="{P["contour"]}" stroke-width="{n(TRAIT_EXT)}" '
                    f'stroke-linejoin="round"/>')
    contours.append(f'<ellipse cx="0" cy="0" rx="{n(f.rx)}" ry="{n(f.ry)}" '
                    f'fill="none" stroke="{P["contour"]}" '
                    f'stroke-width="{n(TRAIT_EXT)}"/>')
    return f, caisse, motifs, cordages, cerclages, peaux, contours


# ==========================================================================
# 3. TAMBOUR DE DROITE (cordage croise en losanges)
# ==========================================================================
DROITE = Fut(165, 42, [
    (0, 165), (80, 153), (150, 146), (250, 140), (360, 136),
    (500, 136), (650, 137), (790, 138),
])


def tambour_droit():
    f = DROITE
    caisse, motifs, cordages, cerclages, peaux, contours = [], [], [], [], [], []

    # ---- caisse ---------------------------------------------------------
    caisse.append(f'<path d="{f.contour_d()}" fill="{P["rouge"]}"/>')
    caisse.append(f.bande(96, 158, P["creme"]))
    caisse.append(f.bande(608, 745, P["or"]))
    caisse.append(f.bande(640, 700, P["blanc"]))
    caisse.append(f.bande(745, 790, P["brun_fonce"]))

    # ---- motifs ---------------------------------------------------------
    motifs += rang_points(f, 62, 15, 6.5, P["blanc"])
    motifs.append(f.bande(86, 96, P["orange"]))
    motifs += rang_chevrons(f, 108, 148, 10, P["orange"], 9, sens=1)
    motifs.append(f.bande(158, 168, P["orange"]))
    motifs += rang_points(f, 192, 15, 6.5, P["blanc"])

    for a in azimuts(4, 0.235):
        motifs.append(cercle_motif(f, 432, a, 40))

    motifs += rang_points(f, 545, 15, 6.5, P["blanc"])
    motifs.append(f.bande(576, 586, P["blanc"]))
    motifs += rang_points(f, 620, 15, 6, P["blanc"])
    motifs.append(f.bande(632, 640, P["terre"]))
    motifs += frise_triangles(f, 642, 698, 10, P["terre"], P["orange"])
    motifs.append(f.bande(700, 708, P["terre"]))
    motifs += rang_points(f, 726, 14, 6, P["blanc"])
    motifs.append(f.bande(738, 746, P["terre"]))

    # ---- cordages croises ------------------------------------------------
    s = math.pi / 5.0
    y0, y1 = 44, 596
    k = s / 220.0
    for i in range(-4, 10):
        cordages.append(corde(f, y0, y1,
                              lambda y, i=i: i * s + k * (y - y0),
                              P["corde"], 6.5, pas=22))
        cordages.append(corde(f, y0, y1,
                              lambda y, i=i: i * s - k * (y - y0),
                              P["corde"], 6.5, pas=22))
    for m in range(0, 6):
        ym = y0 + 110.4 * m
        for i in range(-3, 9):
            a = i * s + m * s / 2.0
            if 0.03 <= a <= math.pi - 0.03:
                cordages.append(noeud(f, ym, a, 9, 8, P["contour"]))

    # ---- cerclages -------------------------------------------------------
    cerclages.append(anneau(f, 12, P["corde"], 16, complet=True))
    cerclages += noeuds_anneau(f, 12, 18, 5, 11, P["contour"])
    cerclages.append(anneau(f, 40, P["corde"], 9))
    cerclages.append(anneau(f, 600, P["corde"], 13))
    cerclages += noeuds_anneau(f, 600, 8, 4.5, 9, P["contour"], complet=False)

    # ---- peau -----------------------------------------------------------
    peaux.append(f'<ellipse cx="0" cy="0" rx="{n(f.rx)}" ry="{n(f.ry)}" '
                 f'fill="{P["ivoire_ombre"]}"/>')
    peaux.append(f'<ellipse cx="0" cy="-2.5" rx="{n(f.rx - 9)}" '
                 f'ry="{n(f.ry - 7)}" fill="{P["ivoire"]}"/>')

    # ---- contours --------------------------------------------------------
    contours.append(f'<path d="{f.contour_d()}" fill="none" '
                    f'stroke="{P["contour"]}" stroke-width="{n(TRAIT_EXT)}" '
                    f'stroke-linejoin="round"/>')
    contours.append(f'<ellipse cx="0" cy="0" rx="{n(f.rx)}" ry="{n(f.ry)}" '
                    f'fill="none" stroke="{P["contour"]}" '
                    f'stroke-width="{n(TRAIT_EXT)}"/>')
    contours.append(f'<path d="{f.bande_d(745, 745)}" fill="none" '
                    f'stroke="{P["contour"]}" stroke-width="{n(TRAIT_INT)}"/>')
    return f, caisse, motifs, cordages, cerclages, peaux, contours


# ==========================================================================
# Assemblage du document
# ==========================================================================
def groupe(nom, contenu, attrs=""):
    if not contenu:
        return ""
    corps = "\n      ".join(x for x in contenu if x)
    return f'    <g id="{nom}"{attrs}>\n      {corps}\n    </g>\n'


def instrument(nom, builder, cx, cy, angle):
    f, caisse, motifs, cordages, cerclages, peaux, contours = builder()
    clip = f"clip-{nom}"
    # clipPath en userSpaceOnUse : il herite deja de la transformation
    # du groupe qui le reference -> pas de transform ici.
    defs = (f'  <clipPath id="{clip}" clipPathUnits="userSpaceOnUse">\n'
            f'    <path d="{f.contour_d()}"/>\n'
            f'  </clipPath>\n')
    tr = f' transform="translate({n(cx)},{n(cy)}) rotate({n(angle)})"'
    g = f'  <g id="{nom}"{tr}>\n'
    g += groupe(f"{nom}-caisse", caisse)
    g += groupe(f"{nom}-motifs", motifs, f' clip-path="url(#{clip})"')
    g += groupe(f"{nom}-cordages", cordages, f' clip-path="url(#{clip})"')
    g += groupe(f"{nom}-cerclages", cerclages)
    g += groupe(f"{nom}-peaux", peaux)
    g += groupe(f"{nom}-contours", contours)
    g += "  </g>\n"
    return defs, g


def build():
    pieces = [
        instrument("tambour-gauche", tambour_gauche, 196, 330, -5.3),
        instrument("djembe-central", djembe_central, 620, 128, 0),
        instrument("tambour-droit", tambour_droit, 1055, 345, 5.4),
    ]
    defs = "".join(p[0] for p in pieces)
    corps = "".join(p[1] for p in pieces)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{CANVAS}" height="{CANVAS}" '
        f'viewBox="0 0 {CANVAS} {CANVAS}" '
        f'fill-rule="evenodd" shape-rendering="geometricPrecision">\n'
        f'<defs>\n{defs}</defs>\n'
        f'{corps}'
        f'</svg>\n'
    )


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "trois_percussions_vectorielles.svg"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(build())
    print(f"ecrit : {out}")
