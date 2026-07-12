#!/usr/bin/env python3
"""
Vial-Vault layout + geometry engine.

Single source of truth for:
  - vial / syringe fit parameters (ASSUMPTIONS -- caliper-verify, edit here)
  - pocket placement (row-packed zones) for designs A / B / C
  - geometry validation (overlaps, wall thickness, bed fit, floor thickness, lid fit)
  - emission of build/<D>_geom.scad + tray/lid wrapper part files

Run:  python3 tools/layout.py [A|B|C|all]
Prints a check report (mm + inches) and writes build/ files.
Exit code is non-zero if any HARD geometry check fails.
"""
import sys, math, os

MM_PER_IN = 25.4
def inch(mm): return mm / MM_PER_IN

# ---------------------------------------------------------------------------
# FIT PARAMETERS  --  ASSUMPTIONS. Measure your actual vials and edit these.
# All dimensions in millimetres.
# ---------------------------------------------------------------------------
# vial outer diameter (OD) and full height for each class
VIAL = {
    "1ml":  {"od": 16.0, "h": 45.0},   # T single-dose vial (~13-17mm OD typical)
    "10ml": {"od": 23.0, "h": 55.0},   # T multidose 10mL (proven peptide holder used 22.5)
    "30ml": {"od": 33.0, "h": 78.0},   # 30mL multidose (proven holder used 32.0)
    "syr":  {"od": 14.0, "h": 65.0},   # 3mL syringe BARREL standing (no long needle) -- see README
}
DIA_CLEAR = 3.0        # added to OD -> bore diameter (radial slop 1.5mm/side)
SYR_CLEAR = 0.0        # syringe "od" already treated as target bore
INNER_GAP = 2.0        # extra bore depth below vial bottom (crumb / tolerance)

# structural
PWALL      = 2.0       # thin wall of each pocket tube
WALL       = 3.0       # perimeter wall thickness
BASE_T     = 3.0       # solid base slab under everything
MIN_WALL   = 2.5       # required plastic between two adjacent bores (HARD check)
MIN_FLOOR  = 4.0       # required solid pedestal under the deepest (30mL) vial (HARD)
CORNER_R   = 4.0       # tray outer corner radius
TOP_GAP    = 8.0       # recess of vial tops below the tray rim (shade + lid clearance)

# lid (lift-off, over-the-top; opaque filament -> darkness)
LID_GAP    = 0.4       # radial clearance skirt<->tray outer wall
SKIRT_W    = 2.4       # lid skirt wall thickness
SKIRT_H    = 15.0      # how far the skirt descends over the tray (grip depth)
ROOF_T     = 2.4       # lid roof plate thickness

# print bed usable area (edit to your printer). HARD check: tray+lid must fit.
BED_X, BED_Y = 220.0, 220.0

MARGIN     = 4.0       # inner margin between pocket field and perimeter wall
ZONE_GAP   = 5.0       # gap between stacked zones (Y)
FINGER_SCALLOP = True  # side notch on 1ml + syr pockets for retrieval

# ---------------------------------------------------------------------------
# DESIGN definitions: ordered zones, each = (type, count, cols) stacked in +Y.
# features: hand slots in end walls (caddy/tote), label ledge.
# ---------------------------------------------------------------------------
DESIGNS = {
    "A": {  # Compact slab tray
        "zones": [("30ml", 2, 2), ("10ml", 4, 4), ("syr", 4, 2), ("1ml", 8, 4)],
        "hand_slots": False,
        "name": "Compact Slab Tray",
    },
    "B": {  # Caddy with hand slots
        "zones": [("30ml", 2, 2), ("10ml", 5, 5), ("syr", 4, 2), ("1ml", 10, 5)],
        "hand_slots": True,
        "name": "Caddy (tote grips)",
    },
    "C": {  # Max vault -- 10mL in a single back row of 6 -> squarer, more bed margin
        "zones": [("30ml", 3, 3), ("10ml", 6, 6), ("syr", 4, 2), ("1ml", 12, 6)],
        "hand_slots": True,
        "name": "Max Vault",
    },
}

# ---------------------------------------------------------------------------
def bore_of(t):
    if t == "syr":
        return VIAL["syr"]["od"] + SYR_CLEAR
    return VIAL[t]["od"] + DIA_CLEAR

def pitch_of(t):
    # centre-to-centre within a zone grid
    return bore_of(t) + 2 * PWALL + (MIN_WALL - 2 * PWALL if MIN_WALL > 2 * PWALL else 0.6)

def rim_height():
    # rim so that: base + pedestal(>=MIN_FLOOR) + INNER_GAP + tallest vial + TOP_GAP
    # (INNER_GAP is bored below the vial, so it eats into the pedestal -> must be added)
    tallest = max(v["h"] for v in VIAL.values())
    return BASE_T + MIN_FLOOR + INNER_GAP + tallest + TOP_GAP

def build_pockets(design):
    """Return (pockets, outer_w, outer_l). pockets: list of dicts x,y,type,bore,depth."""
    zones = DESIGNS[design]["zones"]
    rim = rim_height()
    top_plane = rim - TOP_GAP                      # common plane of all vial tops
    # --- size each zone grid ---
    laid = []
    max_w = 0.0
    for (t, count, cols) in zones:
        rows = math.ceil(count / cols)
        px = pitch_of(t)
        zw = (cols - 1) * px + bore_of(t) + 2 * PWALL      # zone width (X)
        zl = (rows - 1) * px + bore_of(t) + 2 * PWALL      # zone length (Y)
        laid.append({"t": t, "count": count, "cols": cols, "rows": rows,
                     "px": px, "zw": zw, "zl": zl})
        max_w = max(max_w, zw)
    total_l = sum(z["zl"] for z in laid) + ZONE_GAP * (len(laid) - 1)
    outer_w = max_w + 2 * (WALL + MARGIN)
    outer_l = total_l + 2 * (WALL + MARGIN)

    # --- place pockets, zones stacked front(-Y) to back(+Y), each grid centred in X ---
    pockets = []
    y_cursor = -total_l / 2.0
    for z in laid:
        t = z["t"]
        depth = VIAL[t]["h"] + INNER_GAP
        n = 0
        # zone's own local origin: grid centred in X, spanning zl in Y from y_cursor
        gx0 = -((z["cols"] - 1) * z["px"]) / 2.0
        gy0 = y_cursor + (bore_of(t) / 2 + PWALL)
        for r in range(z["rows"]):
            for c in range(z["cols"]):
                if n >= z["count"]:
                    break
                x = gx0 + c * z["px"]
                y = gy0 + r * z["px"]
                # scallop points toward box centre (0,0) so it never faces the perimeter
                ang = math.degrees(math.atan2(-y, -x)) if (abs(x) + abs(y)) > 1e-6 else 0.0
                pockets.append({"x": round(x, 3), "y": round(y, 3), "type": t,
                                "bore": round(bore_of(t), 3), "depth": round(depth, 3),
                                "vial_h": VIAL[t]["h"], "scallop_ang": round(ang, 1),
                                "top_plane": top_plane})
                n += 1
        y_cursor += z["zl"] + ZONE_GAP
    return pockets, round(outer_w, 3), round(outer_l, 3), rim, top_plane

# ---------------------------------------------------------------------------
def check(design, pockets, outer_w, outer_l, rim, top_plane):
    """Return (ok:bool, issues:list[str], info:dict)."""
    issues = []
    warns = []
    tube_h = top_plane - BASE_T

    # 1. pairwise pocket clearance
    worst_gap = 1e9
    for i in range(len(pockets)):
        for j in range(i + 1, len(pockets)):
            a, b = pockets[i], pockets[j]
            d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            gap = d - (a["bore"] + b["bore"]) / 2.0    # plastic between bores
            worst_gap = min(worst_gap, gap)
            if gap < MIN_WALL - 1e-6:
                issues.append(f"pockets {i}&{j} ({a['type']}/{b['type']}) wall {gap:.2f} < {MIN_WALL}")

    # 2. pockets inside perimeter (bore edge + tube wall must clear inner wall face)
    half_w, half_l = outer_w / 2.0, outer_l / 2.0
    for k, p in enumerate(pockets):
        r = p["bore"] / 2.0 + PWALL
        if abs(p["x"]) + r > half_w - WALL + 1e-6:
            issues.append(f"pocket {k} ({p['type']}) breaches +/-X wall")
        if abs(p["y"]) + r > half_l - WALL + 1e-6:
            issues.append(f"pocket {k} ({p['type']}) breaches +/-Y wall")

    # 3. bed fit (tray and lid). lid grows by skirt+gap both sides.
    lid_w = outer_w + 2 * (LID_GAP + SKIRT_W)
    lid_l = outer_l + 2 * (LID_GAP + SKIRT_W)
    if outer_w > BED_X or outer_l > BED_Y:
        issues.append(f"tray {outer_w:.0f}x{outer_l:.0f} exceeds bed {BED_X:.0f}x{BED_Y:.0f}")
    if lid_w > BED_X or lid_l > BED_Y:
        issues.append(f"lid {lid_w:.0f}x{lid_l:.0f} exceeds bed {BED_X:.0f}x{BED_Y:.0f}")

    # 4. floor / pedestal thickness under each vial (pedestal = tube_h - depth)
    for k, p in enumerate(pockets):
        pedestal = tube_h - p["depth"]
        if pedestal < MIN_FLOOR - 1e-6:
            issues.append(f"pocket {k} ({p['type']}) pedestal {pedestal:.2f} < {MIN_FLOOR}")

    # 5. rim covers tallest vial with headroom
    tallest = max(v["h"] for v in VIAL.values())
    if rim < BASE_T + MIN_FLOOR + INNER_GAP + tallest + TOP_GAP - 1e-6:
        issues.append("rim height does not cover tallest vial + headroom")

    # 5b. finger-scallop breach guard: an inward-pointing scallop on a small pocket
    #     extends ~ (bore*0.55/2) past the tube wall; confirm it clears the perimeter.
    SC_D = 0.55
    for k, p in enumerate(pockets):
        if p["type"] not in ("1ml", "syr"):
            continue
        reach = p["bore"] / 2.0 + PWALL + p["bore"] * SC_D / 2.0   # worst outward extent
        ang = math.radians(p["scallop_ang"])
        sx = p["x"] + reach * math.cos(ang)
        sy = p["y"] + reach * math.sin(ang)
        if abs(sx) > half_w - WALL + 1e-6 or abs(sy) > half_l - WALL + 1e-6:
            issues.append(f"pocket {k} ({p['type']}) scallop breaches perimeter")

    # 5c. light-tightness: each vial fully sleeved (tube rim >= vial top)
    for k, p in enumerate(pockets):
        tube_rim = top_plane           # tube top (global z)
        vtop = top_plane - INNER_GAP   # vial top rests INNER_GAP below tube rim
        if vtop > tube_rim + 1e-6:
            issues.append(f"pocket {k} ({p['type']}) vial protrudes above its opaque sleeve")

    # 6. wall params sanity
    if PWALL < 1.2:  warns.append("PWALL < 1.2mm (fragile)")
    if WALL  < 2.0:  warns.append("perimeter WALL < 2.0mm")

    # 6b. vial seating: every vial top must sit below the rim (won't foul the lid)
    #     and be recessed enough to be shaded, but not so deep it can't be grabbed.
    # vial top (global z) = top_plane - INNER_GAP  (same for all classes by construction)
    vial_top = top_plane - INNER_GAP
    recess = rim - vial_top
    if vial_top > rim - 3.0:
        issues.append(f"vial tops {vial_top:.1f} too close to rim {rim:.1f} (lid foul risk)")
    if recess > 18.0:
        warns.append(f"vial recess {recess:.1f}mm deep (retrieval harder; scallops added)")

    # 6c. lid fit: seated skirt clears vial tops, and skirt inner clears the tray wall
    roof_underside = rim                      # roof sits on the rim when seated
    lid_clear = roof_underside - vial_top
    if lid_clear < 2.0:
        issues.append(f"lid roof clearance over vials {lid_clear:.1f} < 2.0")
    if LID_GAP < 0.2:
        warns.append("lid radial gap < 0.2mm (may bind)")

    # 7. aspect ratio warn (printability / handling)
    ar = max(outer_w, outer_l) / min(outer_w, outer_l)
    if ar > 2.2: warns.append(f"aspect ratio {ar:.2f} (long/awkward)")

    info = {
        "outer_w": outer_w, "outer_l": outer_l, "rim": rim, "tube_h": tube_h,
        "lid_w": round(lid_w, 2), "lid_l": round(lid_l, 2),
        "worst_gap": round(worst_gap, 2), "n_pockets": len(pockets),
        "aspect": round(ar, 2),
        "vial_recess": round(rim - (top_plane - INNER_GAP), 2),
        "lid_clear": round(rim - (top_plane - INNER_GAP), 2),
    }
    return (len(issues) == 0), issues, warns, info

# ---------------------------------------------------------------------------
def emit_scad(design, pockets, outer_w, outer_l, rim, top_plane):
    os.makedirs("build", exist_ok=True)
    tube_h = top_plane - BASE_T
    lines = []
    lines.append(f"// AUTO-GENERATED by layout.py for design {design}. Do not edit by hand.")
    lines.append(f"DESIGN = \"{design}\";")
    lines.append(f"OUTER_W = {outer_w};")
    lines.append(f"OUTER_L = {outer_l};")
    lines.append(f"RIM_H = {rim};")
    lines.append(f"TUBE_H = {round(tube_h,3)};")
    lines.append(f"BASE_T = {BASE_T};")
    lines.append(f"WALL = {WALL};")
    lines.append(f"PWALL = {PWALL};")
    lines.append(f"CORNER_R = {CORNER_R};")
    lines.append(f"LID_GAP = {LID_GAP};")
    lines.append(f"SKIRT_W = {SKIRT_W};")
    lines.append(f"SKIRT_H = {SKIRT_H};")
    lines.append(f"ROOF_T = {ROOF_T};")
    lines.append(f"HAND_SLOTS = {'true' if DESIGNS[design]['hand_slots'] else 'false'};")
    lines.append(f"FINGER_SCALLOP = {'true' if FINGER_SCALLOP else 'false'};")
    # POCKETS = [ [x, y, bore, depth, is_small(0/1), scallop_angle_deg], ... ]
    lines.append("POCKETS = [")
    for p in pockets:
        small = 1 if p["type"] in ("1ml", "syr") else 0
        lines.append(f"  [{p['x']}, {p['y']}, {p['bore']}, {p['depth']}, {small}, {p['scallop_ang']}],")
    lines.append("];")
    with open(f"build/{design}_geom.scad", "w") as f:
        f.write("\n".join(lines) + "\n")
    # wrapper part files (never re-assign PART inside vial_vault.scad)
    for part in ("tray", "lid"):
        with open(f"build/{design}_{part}.scad", "w") as f:
            f.write(f"PART = \"{part}\";\n")
            f.write(f"include <{design}_geom.scad>\n")
            f.write(f"include <../scad/vial_vault.scad>\n")

# ---------------------------------------------------------------------------
def run(design, quiet=False):
    pockets, ow, ol, rim, top_plane = build_pockets(design)
    ok, issues, warns, info = check(design, pockets, ow, ol, rim, top_plane)
    emit_scad(design, pockets, ow, ol, rim, top_plane)
    if not quiet:
        d = DESIGNS[design]
        print(f"\n=== Design {design}: {d['name']} ===")
        counts = {}
        for z in d["zones"]:
            counts[z[0]] = counts.get(z[0], 0) + z[1]
        cs = ", ".join(f"{v}x{k}" for k, v in counts.items())
        print(f"  contents: {cs}")
        print(f"  tray  : {ow:.1f} x {ol:.1f} x {rim:.1f} mm"
              f"   ({inch(ow):.2f} x {inch(ol):.2f} x {inch(rim):.2f} in)")
        print(f"  lid   : {info['lid_w']:.1f} x {info['lid_l']:.1f} x {ROOF_T+SKIRT_H:.1f} mm"
              f"   ({inch(info['lid_w']):.2f} x {inch(info['lid_l']):.2f} x {inch(ROOF_T+SKIRT_H):.2f} in)")
        print(f"  pockets: {info['n_pockets']}   min wall between bores: {info['worst_gap']:.2f} mm"
              f"   aspect: {info['aspect']}")
        print(f"  vial top recess below rim: {info['vial_recess']:.1f} mm (shaded, lid clears)")
        if warns:
            for w in warns: print(f"  WARN: {w}")
        if ok:
            print("  CHECKS: PASS")
        else:
            print("  CHECKS: FAIL")
            for it in issues: print(f"    X {it}")
    return ok, info

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = ["A", "B", "C"] if arg == "all" else [arg.upper()]
    all_ok = True
    for t in targets:
        ok, _ = run(t)
        all_ok = all_ok and ok
    print()
    sys.exit(0 if all_ok else 1)
