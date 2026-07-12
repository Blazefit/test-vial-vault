# Print Order — Design A (Vial Vault, Compact)

Copy/paste this to the print service. It's a functional storage box that must be **opaque**
(blocks light) and **not brittle** (must not snap, including in the cold).

## Files (2 parts, print 1 of each)
- **Tray ×1** — `stl/A_tray.stl` — https://raw.githubusercontent.com/Blazefit/test-vial-vault/main/stl/A_tray.stl
- **Lid ×1** — `stl/A_lid.stl` — https://raw.githubusercontent.com/Blazefit/test-vial-vault/main/stl/A_lid.stl
- Units: **millimeters**. Tray bounding box 154 × 164 × 91 mm. Lid 160 × 170 × 19 mm.

## Material — pick in this order
1. **BEST: MJF or SLS Nylon (PA12), black/grey.** Strong in every direction (no weak layer to
   snap off), opaque, matte, tough in the cold. Ideal for this part. ~200–350 g of material.
2. **GOOD / cheaper: FDM in PETG, black.** Ask for **≥3 perimeters/walls, 15–20% infill, no
   supports.** Tough and opaque; slightly weaker across layer lines than nylon but fine.
3. **AVOID: SLA / DLP resin, and PLA.** Both are **brittle and snap when cold** — do not use for
   this part, even if offered as "black."

Any opaque dark color is fine — the point is that light can't get through the walls.

## Orientation & notes
- **FDM:** tray printed **flat on its base** (open cells up); lid printed **flat, roof-down**
  (skirt pointing up). No supports needed — everything is self-supporting.
- **MJF/SLS:** orientation doesn't matter (isotropic) — no supports, no notes needed.
- All walls are ≥ 2 mm and the base is 5 mm, so it clears every process's minimum-wall rule.
- Holes are cut with a 1.0 mm/side clearance on the vials, which absorbs normal process
  tolerance — no need to scale the part.

## What it holds (so the shop knows it's a real functional part)
37 pockets: 6× 10 mL vials, 3× 30 mL vials, 24× 1 mL vials, 4× syringes, plus a lift-off lid.
