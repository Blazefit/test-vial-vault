# Parameters & Dimensions

All geometry is generated from `tools/layout.py`. Edit the values there and re-run to
regenerate every design. Dimensions below are given in **mm and inches**.

## ⚠️ Fit assumptions — CALIPER-VERIFY THESE FIRST

These are the numbers most likely to be wrong for *your* vials. They are set generously,
but measure your actual product and edit `VIAL` / `DIA_CLEAR` in `tools/layout.py`.

| Item | OD | Height | Bore (hole) cut | Radial gap | Notes |
|------|-----------|----------------|-----------------|-----------|-------|
| **1 mL vial** | 16.0 mm (0.63 in) *(assumed)* | 45 mm (1.77 in) | 19.0 mm (0.75 in) | 1.5 mm/side | roomy on purpose — doubles as finger-grab room for a tiny vial |
| **10 mL vial** | **21.7 mm** ✓calipered | 55 mm (2.17 in) | **23.7 mm (0.93 in)** | **1.0 mm/side** | measured 2026-07-12 |
| **30 mL vial** | **33.1 mm** ✓calipered | 78 mm (3.07 in) | **35.1 mm (1.38 in)** | **1.0 mm/side** | measured 2026-07-12 |
| **Syringe (2×2)** | 14.0 mm bore *(assumed)* | 65 mm (2.56 in) | 14.0 mm (0.55 in) | — | **assumes barrel / short syringe standing, plunger up** |

**Syringe caveat:** a 3 mL syringe *with a long needle + cap* is ~90–115 mm — taller than
the box. The 2×2 pockets are sized for **barrels stored plunger-up (needle off)**. If you
want to store full needled syringes, raise `VIAL["syr"]["h"]` and the box grows to suit.

Clearance is **per-class** now (`VIAL[...]["clear"]` = mm added to OD → bore). The 10 mL and
30 mL were tightened to a **1.0 mm radial gap** — snug but drops in/out one-handed, and still
forgiving of the unverified OD assumption. Bore mouths are chamfered as a funnel.
**Want it tighter still?** Once you caliper a real vial, you can go to `clear = 1.5`
(0.75 mm/side) for a nicer fit — but tightening + a wrong OD guess = won't fit, so verify OD first.

## Structural parameters — fused honeycomb (`tools/layout.py`)

| Param | Value | Meaning |
|-------|-------|---------|
| `PWALL` | 2.0 mm | cell wall. Tubes are packed so walls **overlap ~1 mm and fuse** (2·PWALL > web) |
| `WEB_MIN` | 3.0 mm | solid between two adjacent bores (the shared, fused honeycomb wall) |
| `WALL` | 4.0 mm | full-height perimeter wall — thickened 3→4 mm (reinforcement) |
| `FILLET` | 2.5 mm | 45° fillet at every cell-to-base junction — the anti-snap stress relief |
| `EDGE_MIN` | 4.5 mm | bore edge → outer face (chosen so edge cells fuse into the wall) |
| `BASE_T` | 5.0 mm | solid base slab — every vial rests on it; ties all cell bottoms together |
| `RECESS` | 8.0 mm | vial-top recess below its own cell rim (shade; cell is only vial+8 mm tall) |
| `ROW_GAP`/`COL_GAP` | 3.0 mm | gaps between grids — ≤ 2·PWALL so cells fuse across them too |
| `SKIRT_H` | 16.0 mm | how far the lid skirt grips down over the block |
| `LID_GAP` | 0.4 mm | lid-to-block radial clearance |
| `BED_X × BED_Y` | 220 × 220 mm | usable print bed (edit to your printer) |

**Structure check:** `tube-fuse margin` reports the worst-case nearest-neighbour tube overlap;
`−1.0 mm` means every cell overlaps a neighbour (or the wall) — no free-standing tubes.

## Final envelope sizes (mm / inches)

| Design | Contents | Block W × L × H (mm) | Block (in) | Lid W × L × H (mm) | Lid (in) | ~PETG (tray+lid) |
|--------|----------|---------------------|-----------|--------------------|----------|------------------|
| **A — Compact** | 6×10 mL, 3×30 mL, 24×1 mL, 4 syr | 154 × 164 × 91 | 6.07 × 6.44 × 3.58 | 160 × 170 × 18.6 | 6.31 × 6.67 × 0.73 | ~320 g |
| **B — Standard** | 8×10 mL, 4×30 mL, 30×1 mL, 4 syr | 192 × 164 × 91 | 7.57 × 6.44 × 3.58 | 198 × 170 × 18.6 | 7.81 × 6.67 × 0.73 | ~395 g |
| **C — Max** | 10×10 mL, 5×30 mL, 36×1 mL, 6 syr | 204 × 186 × 91 | 8.03 × 7.30 × 3.58 | 210 × 192 × 18.6 | 8.27 × 7.54 × 0.73 | ~455 g |

*(10 mL & 30 mL now caliper-verified; sizes updated from the earlier estimate.)*

All three are **91 mm (3.58 in) tall** (set by the 30 mL vial). Shorter vials get shorter cells
inside, so the block is much lighter than a solid one. Every block + its lid fits a 220 mm bed.
Mass is a rough estimate at 15 % infill — slice it for the real number.
