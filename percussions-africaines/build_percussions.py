#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrace vectoriel des trois percussions africaines.

Chaque instrument est reconstruit comme un fut projete : un axe incline, un
profil de rayon releve sur la reference, et des sections elliptiques cisaillees.
Les cerclages, cordages et noeuds sont places par angle sur ces sections, ce
qui garantit des arcs exacts, des croisements coherents et des courbes lisses.
"""
import math

W = 1024
SHIFT = (15.0, 43.5)          # recentrage du sujet dans le viewBox carre

# ---------------------------------------------------------------- palette ---
DARK   = "#2E1C06"   # brun tres fonce : contours, cerclages, bases
BEIGE  = "#D8B076"   # beige clair     : peaux, cerclages clairs, attaches
OCRE   = "#C87D18"   # jaune ocre      : corps du tambour gauche, ame des cordes
OCRE_D = "#B0680F"   # ocre assombri   : veines du bois
TAN    = "#D59A40"   # orange chaud    : peau et cerclage du tambour droit
OCRE2  = "#B96E18"   # ocre orange     : corps du tambour droit
BROWN  = "#90450F"   # brun orange     : corps du djembe

K = 0.5522847498307936   # constante de Bezier pour un quart d'ellipse

# ------------------------------------------------------------- primitives ---
def _f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def pt(p):
    return f"{_f(p[0])},{_f(p[1])}"

class Ring:
    """Ellipse P(phi) = C + A.cos(phi) + B.sin(phi)."""
    __slots__ = ("C", "A", "B")
    def __init__(self, C, A, B):
        self.C, self.A, self.B = C, A, B
    def P(self, phi):
        c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        return (self.C[0] + self.A[0]*c + self.B[0]*s,
                self.C[1] + self.A[1]*c + self.B[1]*s)
    def T(self, phi):
        c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        return (-self.A[0]*s + self.B[0]*c, -self.A[1]*s + self.B[1]*c)
    def phi_right(self):
        return math.degrees(math.atan2(self.B[0], self.A[0]))
    def phi_left(self):
        return self.phi_right() + 180.0
    def phi_at_x(self, x, lo=None, hi=None):
        """Angle de l'arc avant dont l'abscisse vaut x."""
        lo = self.phi_left() if lo is None else lo
        hi = self.phi_right() if hi is None else hi
        for _ in range(60):
            mid = (lo+hi)/2
            if (self.P(lo)[0]-x)*(self.P(mid)[0]-x) <= 0:
                hi = mid
            else:
                lo = mid
        return (lo+hi)/2

def ellipse_ring(cx, cy, rx, ry, ang):
    a = math.radians(ang)
    return Ring((cx, cy), (rx*math.cos(a), rx*math.sin(a)),
                (-ry*math.sin(a), ry*math.cos(a)))

def arc_cmds(ring, p0, p1):
    n = max(1, int(math.ceil(abs(p1 - p0) / 90.0 - 1e-9)))
    step = (p1 - p0) / n
    h = math.radians(step) * (K / (math.pi/2))
    out = []
    for i in range(n):
        a, b = p0 + i*step, p0 + (i+1)*step
        Pa, Pb, Ta, Tb = ring.P(a), ring.P(b), ring.T(a), ring.T(b)
        out.append("C{} {} {}".format(pt((Pa[0]+Ta[0]*h, Pa[1]+Ta[1]*h)),
                                      pt((Pb[0]-Tb[0]*h, Pb[1]-Tb[1]*h)), pt(Pb)))
    return out

def arc_path(ring, p0, p1):
    return "M" + pt(ring.P(p0)) + " " + " ".join(arc_cmds(ring, p0, p1))

def ellipse_path(ring):
    return "M" + pt(ring.P(0.0)) + " " + " ".join(arc_cmds(ring, 0.0, 360.0)) + "Z"

def smooth_cmds(pts):
    n, out = len(pts), []
    for i in range(n-1):
        p0 = pts[i-1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i+1]
        p3 = pts[i+2] if i+2 < n else pts[i+1]
        c1 = (p1[0] + (p2[0]-p0[0])/6.0, p1[1] + (p2[1]-p0[1])/6.0)
        c2 = (p2[0] - (p3[0]-p1[0])/6.0, p2[1] - (p3[1]-p1[1])/6.0)
        out.append(f"C{pt(c1)} {pt(c2)} {pt(p2)}")
    return out

def smooth_path(pts):
    return "M" + pt(pts[0]) + " " + " ".join(smooth_cmds(pts))

def g(gid, body, extra=""):
    return f'<g id="{gid}"{extra}>\n{body}\n</g>'

def path(d, fill="none", stroke=None, w=0.0, extra=""):
    s = f' stroke="{stroke}" stroke-width="{_f(w)}"' if stroke else ""
    return f'<path fill="{fill}"{s}{extra} d="{d}"/>'

def dot(p, r, fill):
    return f'<circle fill="{fill}" cx="{_f(p[0])}" cy="{_f(p[1])}" r="{_f(r)}"/>'

# ------------------------------------------------------------------- fut ----
def lerp_fn(anchors):
    """Interpolation lineaire y -> x sur une liste triee de (y, x)."""
    ys = [a[0] for a in anchors]
    xs = [a[1] for a in anchors]
    def f(y):
        if y <= ys[0]:
            return xs[0] + (xs[1]-xs[0])*(y-ys[0])/(ys[1]-ys[0])
        if y >= ys[-1]:
            return xs[-1] + (xs[-1]-xs[-2])*(y-ys[-1])/(ys[-1]-ys[-2])
        for i in range(len(ys)-1):
            if ys[i] <= y <= ys[i+1]:
                u = (y-ys[i])/(ys[i+1]-ys[i])
                return xs[i] + (xs[i+1]-xs[i])*u
        return xs[-1]
    return f

class Fut:
    """Fut projete : les sections sont deduites des deux bords releves."""
    def __init__(self, left, right, theta_deg, tilt, k):
        self.xL, self.xR = lerp_fn(left), lerp_fn(right)
        a = math.radians(theta_deg)
        self.n = (math.cos(a), math.sin(a))
        d = math.hypot(tilt, 1.0)
        self.d = (tilt/d, 1.0/d)
        self.k = k
        nx, ny = self.n
        dx, dy = self.d
        self.p = math.hypot(nx, k*dx)
        self.q = (nx*ny + k*k*dx*dy) / self.p
    def ring(self, y, scale=1.0):
        p, q = self.p, self.q
        lo, hi = 1.0, 400.0
        for _ in range(70):
            R = (lo+hi)/2
            if self.xR(y + q*R) - self.xL(y - q*R) - 2*p*R > 0:
                lo = R
            else:
                hi = R
        R = (lo+hi)/2
        cx = (self.xR(y + q*R) + self.xL(y - q*R)) / 2
        R *= scale
        return Ring((cx, y), (R*self.n[0], R*self.n[1]),
                    (self.k*R*self.d[0], self.k*R*self.d[1]))
    def ring_through(self, x, y, y0=0.0, y1=900.0):
        """Section dont l'arc avant passe par (x, y)."""
        for _ in range(70):
            mid = (y0+y1)/2
            r = self.ring(mid)
            if r.P(r.phi_at_x(x))[1] > y:
                y1 = mid
            else:
                y0 = mid
        return self.ring((y0+y1)/2)

def front_arc(ring, trim=0.0):
    return arc_path(ring, ring.phi_left() - trim, ring.phi_right() + trim)

def band_between(ra, rb):
    d  = "M" + pt(ra.P(ra.phi_left())) + " " + " ".join(arc_cmds(ra, ra.phi_left(), ra.phi_right()))
    d += "L" + pt(rb.P(rb.phi_right())) + " " + " ".join(arc_cmds(rb, rb.phi_right(), rb.phi_left()))
    return d + "Z"

def meridian(fut, phi, ra, rb, steps=8):
    ya, yb = ra.C[1], rb.C[1]
    return smooth_path([fut.ring(ya + (yb-ya)*i/steps).P(phi) for i in range(steps+1)])

def lacing(fut, ra, rb, phi_a, phi_b, steps=10):
    """Helice entre deux sections, limitee a la face visible du fut."""
    ya, yb = ra.C[1], rb.C[1]
    runs, cur = [], []
    for i in range(steps+1):
        u = i/steps
        r = fut.ring(ya + (yb-ya)*u)
        phi = phi_a + (phi_b-phi_a)*u
        if r.phi_right() + 2.0 <= phi <= r.phi_left() - 2.0:
            cur.append(r.P(phi))
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    return [smooth_path(c) for c in runs if len(c) > 2]

# ============================================================= silhouettes ===
def build_silhouette(hoop, left, right, cap):
    pl, pr = hoop.P(hoop.phi_left()), hoop.P(hoop.phi_right())
    pts = [pl] + [(x, y) for y, x in left] + list(cap) \
          + [(x, y) for y, x in reversed(right)] + [pr]
    d = "M" + pt(pts[0]) + " " + " ".join(smooth_cmds(pts))
    d += " " + " ".join(arc_cmds(hoop, hoop.phi_right(), hoop.phi_right()-180.0))
    return d + "Z"

def build_base(ring, cap):
    pts = [ring.P(ring.phi_right())] + list(reversed(cap))
    d = "M" + pt(ring.P(ring.phi_left())) + " " \
        + " ".join(arc_cmds(ring, ring.phi_left(), ring.phi_right())) + " " \
        + " ".join(smooth_cmds(pts))
    return d + "Z"

# ============================================================ TAMBOUR GAUCHE ==
L_LEFT  = [(386,37.7),(411,51.9),(461,67.7),(511,84.8),(561,100.8),(611,118.8),
           (661,136.8),(711,154.8),(761,174.8),(811,193.8),(836,203.8)]
L_RIGHT = [(336,280.5),(411,291.5),(511,304.5),(611,316.5),(711,326.5),
           (786,331.5),(826,331.0)]
L_CAP   = [(204.5,837.8),(208.4,848.9),(213.2,856.3),(222.7,863.5),(249.9,867.4),
           (283.5,862.3),(300.1,855.7),(313.7,848.8),(326.5,837.8)]
L_SKIN  = ellipse_ring(155.4, 322.5, 126.1, 36.7, -19.1)
L_HOOP  = ellipse_ring(157.8, 337.5, 128.6,  37.6, -19.1)
LF = Fut([(373.1, 37.6)] + L_LEFT, [(297.4, 279.0)] + L_RIGHT, -19.1, 0.2253, 0.315)

def lug(fut, ring_top, phi, length=60.0, w=15.5, h=50.0):
    p0 = ring_top.P(phi)
    r1 = fut.ring(ring_top.C[1] + length)
    p1 = r1.P(phi - 4.0)
    ux, uy = p1[0]-p0[0], p1[1]-p0[1]
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux/n, uy/n
    vx, vy = -uy, ux
    cord = "M{} Q{} {}".format(pt(p0), pt(((p0[0]+p1[0])/2 + 5.0, (p0[1]+p1[1])/2)), pt(p1))
    ox, oy = p1[0] - ux*8.0, p1[1] - uy*8.0
    def P(a, b):
        return (ox + vx*a + ux*b, oy + vy*a + uy*b)
    d = ("M" + pt(P(0, 10))
         + f" C{pt(P(-4,2))} {pt(P(-10,-1))} {pt(P(-w+1.5,2))}"
         + f" C{pt(P(-w-1,5))} {pt(P(-w,12))} {pt(P(-w+1,18))}"
         + f" C{pt(P(-14,29))} {pt(P(-7,39))} {pt(P(0,h))}"
         + f" C{pt(P(7,39))} {pt(P(14,29))} {pt(P(w-1,18))}"
         + f" C{pt(P(w,12))} {pt(P(w+1,5))} {pt(P(w-1.5,2))}"
         + f" C{pt(P(10,-1))} {pt(P(4,2))} {pt(P(0,10))} Z")
    return cord, d

def tambour_gauche():
    sil = build_silhouette(L_HOOP, L_LEFT, L_RIGHT, L_CAP)
    out = [f'<clipPath id="galbe-gauche"><path d="{sil}"/></clipPath>',
           path(sil, OCRE, DARK, 9)]
    bois = [path(front_arc(LF.ring_through(200, 500), -7.0), "none", OCRE_D, 3.2)]
    ra, rb = LF.ring(524), LF.ring(806)
    for phi in (40, 62, 88, 112, 136):
        bois.append(path(meridian(LF, phi, ra, rb), "none", OCRE_D, 3.2))
    out.append(g("tambour-gauche-bois", "\n".join(bois), ' clip-path="url(#galbe-gauche)"'))
    out.append(path(build_base(LF.ring_through(260, 846), L_CAP), DARK, DARK, 9))
    out.append(path(ellipse_path(L_HOOP), BEIGE, DARK, 9))
    out.append(path(ellipse_path(L_SKIN), BEIGE, DARK, 9))
    cres = ellipse_ring(L_SKIN.C[0]+7, L_SKIN.C[1]+9, 126.1*0.93, 36.7*0.86, -19.1)
    out.append(path(arc_path(cres, 190, 348), "none", DARK, 4))
    att = []
    for phi in (134, 95, 54):
        cord, head = lug(LF, L_HOOP, phi)
        att.append(path(head, BEIGE, DARK, 6.5))
        att.append(path(cord, "none", DARK, 13.5, ' stroke-linecap="round"'))
        att.append(path(cord, "none", BEIGE, 7.5, ' stroke-linecap="round"'))
    out.append(g("tambour-gauche-attaches", "\n".join(att)))
    return g("tambour-gauche", "\n".join(out),
             ' stroke-linecap="round" stroke-linejoin="round"')

# ============================================================ DJEMBE CENTRAL ==
M_LEFT = [(134,306.6),(154,308.6),(194,317.6),(234,325.5),(274,332.7),(314,341.6),
          (354,349.7),(394,361.8),(414,369.9),(434,380.2),(454,394.5),(474,407.8),
          (494,407.5),(514,406.5),(554,400.6),(614,391.6),(674,381.6),(734,371.5),
          (750,371.0)]
M_RIGHT = [(y, 975.0-x) for y, x in M_LEFT]
_MC = [(371.0,750.0),(376.5,761.5),(384.4,769.2),(396.3,776.7),(411.1,784.2),
       (435.5,791.5),(455.6,795.5),(487.5,796.5)]
M_CAP = _MC + [(975.0-x, y) for x, y in reversed(_MC[:-1])]
M_SKIN = ellipse_ring(489.0, 112.0, 171.5, 41.5, 0.0)
M_WRAP = ellipse_ring(489.0, 135.0, 173.5, 42.0, 0.0)
MF = Fut([(112.0, 317.5)] + M_LEFT, [(112.0, 660.5)] + M_RIGHT, 0.0, 0.0, 0.3066)

def djembe():
    sil = build_silhouette(M_SKIN, M_LEFT, M_RIGHT, M_CAP)
    out = [f'<clipPath id="galbe-djembe"><path d="{sil}"/></clipPath>',
           path(sil, BROWN, DARK, 9)]
    bois = []
    ra, rb = MF.ring(322), MF.ring(452)
    for phi in (30, 54, 78, 102, 126, 150):
        bois.append(path(meridian(MF, phi, ra, rb), "none", DARK, 3))
    ra, rb = MF.ring(548), MF.ring(722)
    for phi in (40, 64, 90, 116, 140):
        bois.append(path(meridian(MF, phi, ra, rb), "none", DARK, 3))
    out.append(g("djembe-bois", "\n".join(bois), ' clip-path="url(#galbe-djembe)"'))
    out.append(path(band_between(MF.ring_through(470, 486), MF.ring_through(470, 518)),
                    DARK, DARK, 8))
    out.append(path(build_base(MF.ring_through(470, 768), M_CAP), DARK, DARK, 9))
    out.append(path(ellipse_path(M_WRAP), BEIGE, DARK, 9))
    rings = [MF.ring_through(465, y) for y in (203.0, 250.5, 297.5)]
    cordes = [path(front_arc(r), "none", DARK, 8) for r in rings]
    for phi in (35, 90, 145):
        cordes.append(path(meridian(MF, phi, MF.ring_through(465, 172), rings[2]),
                           "none", DARK, 9))
    noeuds = [dot(rings[2].P(p), 9.5, DARK)
              for p in (rings[2].phi_left(), 145, 90, 35, rings[2].phi_right())]
    noeuds += [dot(rings[1].P(p), 8.5, DARK)
               for p in (rings[1].phi_left(), rings[1].phi_right())]
    noeuds.append(dot(MF.ring_through(465, 178).P(90), 9.0, DARK))
    out.append(g("djembe-cordages", "\n".join(cordes) + "\n" + "\n".join(noeuds),
                 ' clip-path="url(#galbe-djembe)"'))
    out.append(path(ellipse_path(M_SKIN), BEIGE, DARK, 9))
    out.append(path(arc_path(ellipse_ring(489, 128, 152, 12, 0.0), 180, 360), "none", DARK, 4.5))
    return g("djembe-central", "\n".join(out),
             ' stroke-linecap="round" stroke-linejoin="round"')

# ============================================================= TAMBOUR DROIT ==
R_LEFT = [(364,680.6),(388,676.6),(412,671.6),(436,664.6),(460,660.5),(508,653.5),
          (556,648.5),(604,644.5),(652,642.5),(700,640.5),(748,638.5),(791,638.3)]
R_RIGHT = [(388,957.4),(412,955.4),(436,949.4),(484,938.4),(532,926.3),(580,913.3),
           (628,898.3),(676,883.2),(724,865.2),(772,847.0),(791,835.7)]
R_CAP = [(640.4,802.8),(644.5,810.5),(653.5,821.9),(666.4,833.2),(684.1,844.1),
         (702.3,850.9),(726.9,857.6),(756.0,863.5),(782.5,859.1),(798.0,852.0),
         (806.7,844.5),(814.6,833.3),(820.5,821.9),(826.5,810.5),(830.6,802.8)]
R_SKIN = ellipse_ring(822.1, 344.8, 139.9, 39.5, 16.0)
R_HOOP = ellipse_ring(824.3, 361.8, 141.6, 40.0, 16.0)
RF = Fut([(329.0, 686.0)] + R_LEFT, [(397.5, 960.6)] + R_RIGHT, 16.0, -0.2075, 0.28)
R_PHI = (22.0, 58.0, 94.0, 130.0, 166.0)

def tambour_droit():
    sil = build_silhouette(R_HOOP, R_LEFT, R_RIGHT, R_CAP)
    out = [f'<clipPath id="galbe-droit"><path d="{sil}"/></clipPath>',
           path(sil, OCRE2, DARK, 9)]
    anneau = path(front_arc(RF.ring_through(830, 424.5)), "none", DARK, 8)
    r_top = RF.ring_through(805, 407)
    r_mid = RF.ring_through(830, 500.5)
    r_low = RF.ring_through(740, 771)
    trace = []
    for phi in R_PHI:
        trace.append(meridian(RF, phi, r_top, r_mid, steps=5))
    for phi in R_PHI + (202.0,):
        trace += lacing(RF, r_top, r_mid, phi, phi - 36.0, steps=6)
    for phi in R_PHI + (202.0,):
        trace += lacing(RF, r_mid, r_low, phi, phi + 18.0)
        trace += lacing(RF, r_mid, r_low, phi, phi - 18.0)
    trace.append(front_arc(r_mid))
    trace.append(front_arc(r_low))
    out.append(g("tambour-droit-cordages",
                 anneau + "\n" +
                 "\n".join(path(d, "none", DARK, 19) for d in trace) + "\n" +
                 "\n".join(path(d, "none", OCRE, 7) for d in trace),
                 ' clip-path="url(#galbe-droit)"'))
    noeuds = []
    for r, phis in ((r_top, R_PHI), (r_mid, R_PHI),
                    (r_low, tuple(p + 18.0 for p in R_PHI) + (4.0,))):
        for phi in phis:
            if r.phi_right() + 1.0 < phi < r.phi_left() - 1.0:
                noeuds.append(dot(r.P(phi), 11.0, DARK))
                noeuds.append(dot(r.P(phi), 5.0, OCRE))
    out.append(g("tambour-droit-noeuds", "\n".join(noeuds), ' clip-path="url(#galbe-droit)"'))
    out.append(path(build_base(RF.ring_through(740, 835), R_CAP), OCRE2, DARK, 9))
    out.append(path(ellipse_path(R_HOOP), TAN, DARK, 9))
    out.append(path(ellipse_path(R_SKIN), TAN, DARK, 9))
    cres = ellipse_ring(R_SKIN.C[0]-4, R_SKIN.C[1]+10, 139.9*0.94, 39.5*0.86, 16.0)
    out.append(path(arc_path(cres, 188, 350), "none", DARK, 4))
    return g("tambour-droit", "\n".join(out),
             ' stroke-linecap="round" stroke-linejoin="round"')

# ==================================================================== SORTIE ==
def build():
    corps = "\n".join([tambour_gauche(), djembe(), tambour_droit()])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" '
            f'width="{W}" height="{W}">\n'
            f'<title>Trois percussions africaines</title>\n'
            f'<g transform="translate({_f(SHIFT[0])},{_f(SHIFT[1])})">\n'
            f'{corps}\n</g>\n</svg>\n')

if __name__ == "__main__":
    import sys, os
    here = os.path.dirname(os.path.abspath(__file__))
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "percussions-africaines.svg")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(build())
    print(dest)
