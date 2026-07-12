#!/usr/bin/env python3
"""
Vial-Vault layout + geometry engine  --  MERGED-TUBE HONEYCOMB rev.

Structure: a solid base slab + full-height perimeter wall, with one tube per pocket.
Tubes are packed so their walls OVERLAP and fuse into a continuous honeycomb -- every
pocket is braced by its neighbours (and edge pockets fuse into the wall), so nothing is
a free-standing tube that can snap off. Each tube is only as TALL as its own vial needs
(stepped), so the dead mass under short vials is gone -> far lighter than a solid block.

Single source of truth for fit params, placement, geometry checks, and SCAD emission.
Run:  python3 tools/layout.py [A|B|C|all]
"""
import sys, math, os

MM_PER_IN = 25.4
def inch(mm): return mm / MM_PER_IN

# ---------------------------------------------------------------------------
# FIT PARAMETERS  --  ASSUMPTIONS. Measure your vials and edit these.  (mm)
# ---------------------------------------------------------------------------
VIAL = {
    "1ml":  {"od": 16.0, "h": 45.0, "clear": 3.0},   # ASSUMED (not yet calipered)
    "10ml": {"od": 21.7, "h": 55.0, "clear": 2.0},   # CALIPER-VERIFIED 2026-07-12 -> bore 23.7 (1.0 mm/side)
    "30ml": {"od": 33.1, "h": 78.0, "clear": 2.0},   # CALIPER-VERIFIED 2026-07-12 -> bore 35.1 (1.0 mm/side)
    "syr":  {"od": 14.0, "h": 65.0, "clear": 0.0},   # ASSUMED 3 mL syringe BARREL, needle off
}

# --- honeycomb structure (reinforced against cold-weather snapping) ---
PWALL     = 2.0        # tube wall; tubes packed so walls OVERLAP (2*PWALL > web) -> fused
WEB_MIN   = 3.0        # solid between two adjacent bores (a fused shared wall)
WALL      = 4.0        # full-height perimeter wall -- thickened 3->4 mm (tallest thin wall)
EDGE_MIN  = 4.5        # bore edge -> outer face (chosen so edge tubes fuse into the wall)
BASE_T    = 5.0        # solid base slab: every vial rests on it; ties all tube bottoms
FILLET    = 2.5        # 45-deg fillet at every cell-to-base junction -- kills the snap-point
RECESS    = 8.0        # vial-top recess below its own cell rim (shade)
CORNER_R  = 5.0
ROW_GAP   = 3.0        # between stacked rows (Y) -- <= 2*PWALL so tubes fuse across it
COL_GAP   = 3.0        # between side-by-side grids (X)

# lid (lift-off, opaque -> darkness)
LID_GAP  = 0.4
SKIRT_W  = 2.6
SKIRT_H  = 16.0
ROOF_T   = 2.6

BED_X, BED_Y = 220.0, 220.0
# Stepped cells only recess a vial ~8 mm below its own rim, so a vial is easy to pinch
# without a finger notch. Scallops off -> fully light-tight (genus 0). Flip on if you
# want the notch back (it opens a pocket into an interior void: harmless but genus 1).
FINGER_SCALLOP = False

# ---------------------------------------------------------------------------
# DESIGNS: list of ROWS (stacked +Y). Each row = list of GRIDS (side-by-side X).
# grid = (type, nrows, ncols).
# ---------------------------------------------------------------------------
DESIGNS = {
    "A": {"name": "Compact Honeycomb", "rows": [
            [("30ml", 1, 3), ("syr", 2, 2)],
            [("10ml", 2, 3), ("1ml", 2, 3)],
            [("1ml", 3, 6)],
        ]},
    "B": {"name": "Standard Honeycomb", "rows": [
            [("30ml", 1, 4), ("syr", 2, 2)],
            [("10ml", 2, 4), ("1ml", 2, 3)],
            [("1ml", 3, 8)],
        ]},
    "C": {"name": "Max Honeycomb", "rows": [
            [("30ml", 1, 5)],
            [("10ml", 2, 5), ("syr", 2, 3)],
            [("1ml", 4, 9)],
        ]},
}

# ---------------------------------------------------------------------------
def bore_of(t):   return VIAL[t]["od"] + VIAL[t]["clear"]
def pitch_of(t):  return bore_of(t) + WEB_MIN
def depth_of(t):  return VIAL[t]["h"] + RECESS          # bore depth = cell height above base
def tube_od(t):   return bore_of(t) + 2 * PWALL

def rim_height():
    return BASE_T + max(v["h"] for v in VIAL.values()) + RECESS

def grid_size(t, nr, nc):
    p = pitch_of(t); b = bore_of(t)
    return ((nc - 1) * p + b, (nr - 1) * p + b)

def counts(design):
    c = {}
    for row in DESIGNS[design]["rows"]:
        for (t, r, cc) in row:
            c[t] = c.get(t, 0) + r * cc
    return c

def build_pockets(design):
    rows = DESIGNS[design]["rows"]
    rim = rim_height()
    laid = []
    for row in rows:
        grids, rw, rl = [], 0.0, 0.0
        for (t, nr, nc) in row:
            gw, gl = grid_size(t, nr, nc)
            grids.append({"t": t, "nr": nr, "nc": nc, "gw": gw, "gl": gl})
            rw += gw; rl = max(rl, gl)
        rw += COL_GAP * (len(row) - 1)
        laid.append({"grids": grids, "rw": rw, "rl": rl})
    field_w = max(r["rw"] for r in laid)
    total_l = sum(r["rl"] for r in laid) + ROW_GAP * (len(laid) - 1)
    outer_w = field_w + 2 * EDGE_MIN
    outer_l = total_l + 2 * EDGE_MIN

    pockets = []
    y_cursor = -total_l / 2.0
    for r in laid:
        band_cy = y_cursor + r["rl"] / 2.0
        x_cursor = -r["rw"] / 2.0
        for g in r["grids"]:
            t = g["t"]; p = pitch_of(t); b = bore_of(t); dep = depth_of(t)
            gcx = x_cursor + g["gw"] / 2.0
            for ri in range(g["nr"]):
                for ci in range(g["nc"]):
                    x = gcx - (g["nc"] - 1) * p / 2.0 + ci * p
                    y = band_cy - (g["nr"] - 1) * p / 2.0 + ri * p
                    ang = math.degrees(math.atan2(-y, -x)) if (abs(x) + abs(y)) > 1e-6 else 0.0
                    pockets.append({"x": round(x, 3), "y": round(y, 3), "type": t,
                                    "bore": round(b, 3), "depth": round(dep, 3),
                                    "scallop_ang": round(ang, 1)})
            x_cursor += g["gw"] + COL_GAP
        y_cursor += r["rl"] + ROW_GAP
    return pockets, round(outer_w, 3), round(outer_l, 3), rim

# ---------------------------------------------------------------------------
def check(design, pockets, outer_w, outer_l, rim):
    issues, warns = [], []
    half_w, half_l = outer_w / 2.0, outer_l / 2.0

    worst_web = 1e9
    nearest = [1e9] * len(pockets)     # nearest tube-edge gap per pocket (for fusion test)
    for i in range(len(pockets)):
        a = pockets[i]
        for j in range(i + 1, len(pockets)):
            b = pockets[j]
            d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            web = d - (a["bore"] + b["bore"]) / 2.0
            worst_web = min(worst_web, web)
            if web < WEB_MIN - 1e-6:
                issues.append(f"web {web:.2f} < {WEB_MIN} ({a['type']}&{b['type']})")
            tube_gap = d - (a["bore"] + b["bore"]) / 2.0 - 2 * PWALL   # <0 => tubes fuse
            nearest[i] = min(nearest[i], tube_gap)
            nearest[j] = min(nearest[j], tube_gap)

    # fusion: every pocket must fuse with a neighbour OR reach the wall (no free tube)
    for k, p in enumerate(pockets):
        wall_gap = (half_w - WALL) - (abs(p["x"]) + p["bore"] / 2.0 + PWALL)
        wall_gap_y = (half_l - WALL) - (abs(p["y"]) + p["bore"] / 2.0 + PWALL)
        fuses_wall = min(wall_gap, wall_gap_y) < 0
        if nearest[k] > -1e-6 and not fuses_wall:
            issues.append(f"pocket {k} ({p['type']}) is free-standing (fuses nothing)")

    for k, p in enumerate(pockets):
        if abs(p["x"]) + p["bore"] / 2.0 > half_w - EDGE_MIN + 1e-6:
            issues.append(f"pocket {k} ({p['type']}) < {EDGE_MIN}mm from X face")
        if abs(p["y"]) + p["bore"] / 2.0 > half_l - EDGE_MIN + 1e-6:
            issues.append(f"pocket {k} ({p['type']}) < {EDGE_MIN}mm from Y face")

    lid_w = outer_w + 2 * (LID_GAP + SKIRT_W)
    lid_l = outer_l + 2 * (LID_GAP + SKIRT_W)
    if outer_w > BED_X or outer_l > BED_Y:
        issues.append(f"block {outer_w:.0f}x{outer_l:.0f} exceeds bed")
    if lid_w > BED_X or lid_l > BED_Y:
        issues.append(f"lid {lid_w:.0f}x{lid_l:.0f} exceeds bed")

    if BASE_T < 3.0:
        issues.append(f"base slab {BASE_T} < 3mm (vials could push through / light leak)")
    if RECESS < 3.0:
        issues.append("RECESS < 3mm: vials not shaded / lid may foul")

    for k, p in enumerate(pockets):
        if p["type"] not in ("1ml", "syr"):
            continue
        reach = p["bore"] / 2.0 + p["bore"] * 0.5 / 2.0
        ang = math.radians(p["scallop_ang"])
        if abs(p["x"] + reach * math.cos(ang)) > half_w - 2.0 or \
           abs(p["y"] + reach * math.sin(ang)) > half_l - 2.0:
            issues.append(f"pocket {k} scallop breaches face")

    if WEB_MIN < 2.4: warns.append("WEB_MIN < 2.4mm (fragile web)")
    if WEB_MIN > 2 * PWALL: warns.append("web > 2*PWALL: tubes may NOT fuse (free-standing risk)")
    ar = max(outer_w, outer_l) / min(outer_w, outer_l)
    if ar > 2.0: warns.append(f"aspect {ar:.2f} (long)")

    info = {"outer_w": outer_w, "outer_l": outer_l, "rim": rim,
            "lid_w": round(lid_w, 1), "lid_l": round(lid_l, 1),
            "worst_web": round(worst_web, 2), "n": len(pockets),
            "aspect": round(ar, 2), "recess": RECESS,
            "worst_fuse": round(max(nearest), 2) if pockets else 0}
    return (len(issues) == 0), issues, warns, info

# ---------------------------------------------------------------------------
def emit_scad(design, pockets, outer_w, outer_l, rim):
    os.makedirs("build", exist_ok=True)
    L = [f"// AUTO-GENERATED by layout.py for design {design}. Merged-tube honeycomb rev.",
         f"DESIGN = \"{design}\";",
         f"OUTER_W = {outer_w};", f"OUTER_L = {outer_l};", f"RIM_H = {rim};",
         f"BASE_T = {BASE_T};", f"WALL = {WALL};", f"PWALL = {PWALL};",
         f"FILLET = {FILLET};",
         f"CORNER_R = {CORNER_R};", f"RECESS = {RECESS};",
         f"LID_GAP = {LID_GAP};", f"SKIRT_W = {SKIRT_W};", f"SKIRT_H = {SKIRT_H};",
         f"ROOF_T = {ROOF_T};",
         f"FINGER_SCALLOP = {'true' if FINGER_SCALLOP else 'false'};",
         "// POCKETS = [x, y, bore, depth, is_small, scallop_deg]  (cell height = BASE_T+depth)",
         "POCKETS = ["]
    for p in pockets:
        small = 1 if p["type"] in ("1ml", "syr") else 0
        L.append(f"  [{p['x']}, {p['y']}, {p['bore']}, {p['depth']}, {small}, {p['scallop_ang']}],")
    L.append("];")
    open(f"build/{design}_geom.scad", "w").write("\n".join(L) + "\n")
    for part in ("tray", "lid"):
        open(f"build/{design}_{part}.scad", "w").write(
            f"PART = \"{part}\";\ninclude <{design}_geom.scad>\ninclude <../scad/vial_vault.scad>\n")

# ---------------------------------------------------------------------------
def run(design, quiet=False):
    pockets, ow, ol, rim = build_pockets(design)
    ok, issues, warns, info = check(design, pockets, ow, ol, rim)
    emit_scad(design, pockets, ow, ol, rim)
    if not quiet:
        d = DESIGNS[design]; c = counts(design)
        cs = ", ".join(f"{c.get(k,0)}x{k}" for k in ("30ml", "10ml", "1ml", "syr"))
        print(f"\n=== Design {design}: {d['name']} ===")
        print(f"  contents: {cs}   ({info['n']} openings)")
        print(f"  block : {ow:.1f} x {ol:.1f} x {rim:.1f} mm"
              f"   ({inch(ow):.2f} x {inch(ol):.2f} x {inch(rim):.2f} in)")
        print(f"  lid   : {info['lid_w']:.1f} x {info['lid_l']:.1f} x {ROOF_T+SKIRT_H:.1f} mm"
              f"   ({inch(info['lid_w']):.2f} x {inch(info['lid_l']):.2f} x {inch(ROOF_T+SKIRT_H):.2f} in)")
        print(f"  min web: {info['worst_web']:.2f} mm   tube-fuse margin: {info['worst_fuse']:.2f} mm (<0 = fused)"
              f"   aspect: {info['aspect']}")
        for w in warns: print(f"  WARN: {w}")
        print("  CHECKS: PASS" if ok else "  CHECKS: FAIL")
        for it in issues: print(f"    X {it}")
    return ok, info

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = ["A", "B", "C"] if arg == "all" else [arg.upper()]
    all_ok = all(run(t)[0] for t in targets)
    print()
    sys.exit(0 if all_ok else 1)
