# Parameters & Dimensions

All geometry is generated from `tools/layout.py`. Edit the values there and re-run to
regenerate every design. Dimensions below are given in **mm and inches**.

## ⚠️ Fit assumptions — CALIPER-VERIFY THESE FIRST

These are the numbers most likely to be wrong for *your* vials. They are set generously,
but measure your actual product and edit `VIAL` / `DIA_CLEAR` in `tools/layout.py`.

| Item | Assumed OD | Assumed height | Bore (hole) cut | Notes |
|------|-----------|----------------|-----------------|-------|
| **1 mL vial** | 16.0 mm (0.63 in) | 45 mm (1.77 in) | 19.0 mm (0.75 in) | T single-dose vials run ~13–17 mm; pocket is deliberately roomy |
| **10 mL vial** | 23.0 mm (0.91 in) | 55 mm (2.17 in) | 26.0 mm (1.02 in) | your peptide holder used 22.5; bumped for T multidose |
| **30 mL vial** | 33.0 mm (1.30 in) | 78 mm (3.07 in) | 36.0 mm (1.42 in) | your holder used 32.0; 30 mL multidose ~32–35 mm |
| **Syringe (2×2)** | 14.0 mm bore | 65 mm (2.56 in) | 14.0 mm (0.55 in) | **assumes barrel / short syringe standing, plunger up** |

**Syringe caveat:** a 3 mL syringe *with a long needle + cap* is ~90–115 mm — taller than
the box. The 2×2 pockets are sized for **barrels stored plunger-up (needle off)**. If you
want to store full needled syringes, raise `VIAL["syr"]["h"]` and the box grows to suit.

Radial clearance is `DIA_CLEAR = 3.0 mm` (1.5 mm slop per side) — a vial drops in easily and
the bore mouth is chamfered as a funnel.

## Structural parameters (`tools/layout.py`)

| Param | Value | Meaning |
|-------|-------|---------|
| `PWALL` | 2.0 mm | wall of each individual vial sleeve (this is what keeps light off the vials) |
| `WALL` | 3.0 mm | outer perimeter wall |
| `BASE_T` | 3.0 mm | solid base slab |
| `MIN_WALL` | 2.5 mm | required plastic between two bores (actual min achieved: 4.6 mm) |
| `MIN_FLOOR` | 4.0 mm | solid pedestal under the deepest (30 mL) vial |
| `TOP_GAP` | 8.0 mm | recess of vial tops below the rim (→ 10.0 mm actual, shade + lid clearance) |
| `SKIRT_H` | 15.0 mm | how far the lid skirt grips down over the tray |
| `LID_GAP` | 0.4 mm | lid-to-tray radial clearance |
| `BED_X × BED_Y` | 220 × 220 mm | usable print bed (edit to your printer) |

## Final envelope sizes (mm / inches)

| Design | Contents | Tray W × L × H (mm) | Tray (in) | Lid W × L × H (mm) | Lid (in) | ~PETG (tray+lid) |
|--------|----------|---------------------|-----------|--------------------|----------|------------------|
| **A — Compact Slab** | 4×10 mL, 2×30 mL, 8×1 mL, 2×2 syr | 135.8 × 182.2 × 95.0 | 5.35 × 7.17 × 3.74 | 141.4 × 187.8 × 17.4 | 5.57 × 7.39 × 0.69 | ~314 g |
| **B — Caddy (grips)** | 5×10 mL, 2×30 mL, 10×1 mL, 2×2 syr | 166.4 × 182.2 × 95.0 | 6.55 × 7.17 × 3.74 | 172.0 × 187.8 × 17.4 | 6.77 × 7.39 × 0.69 | ~365 g |
| **C — Max Vault** | 6×10 mL, 3×30 mL, 12×1 mL, 2×2 syr | 197.0 × 182.2 × 95.0 | 7.76 × 7.17 × 3.74 | 202.6 × 187.8 × 17.4 | 7.98 × 7.39 × 0.69 | ~429 g |

All three are **95 mm (3.74 in) tall** — intentionally taller than the fridge holders so the
30 mL vials stand fully enclosed. Every tray + its lid fits a 220 mm bed. Mass is a
conservative estimate at 15 % infill; real prints will likely be lighter.
