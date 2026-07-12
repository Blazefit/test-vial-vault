# Testosterone Vial Vault — dark room-temp storage

3D-printable, **light-blocking** storage for testosterone vials + syringes, kept at **room
temperature** (not fridge/freezer). Three sizes at different capacities — **pick one**.

Every pocket is a cell in a **fused honeycomb**: the cell walls overlap and join into one
continuous structure (nothing is a free-standing tube that can snap off), and each cell is
only as **tall as its own vial** so the block stays light. Print in an opaque dark filament
and add the lift-off lid — every vial sits shaded in its own opaque cell.

> **Engineering models, not medical advice.** Verify vial fit with calipers before printing a
> full set (see `PARAMS.md`).

---

## Pick a design

| | **A — Compact** | **B — Standard** | **C — Max** |
|---|---|---|---|
| 10 mL vials | 6 | 8 | 10 |
| 30 mL vials | 3 | 4 | 5 |
| 1 mL vials | 24 | 30 | 36 |
| Syringes (2×N) | 4 | 4 | 6 |
| **Total openings** | **37** | **46** | **57** |
| Block (in) | 6.14 × 6.54 × 3.58 | 7.56 × 6.54 × 3.58 | 8.03 × 7.40 × 3.58 |
| Block (mm) | 156 × 166 × 91 | 192 × 166 × 91 | 204 × 188 × 91 |
| Fits 220 mm bed | ✓ | ✓ | ✓ |
| Light-tightness | genus 0 (sealed) | genus 0 | genus 0 |
| ~PETG tray+lid @15% | ~330 g | ~400 g | ~460 g |

Renders: `renders/{A,C}_top.png` (layout), `{A,C}_tray.png` (3/4), lids, and the fit-audit
cutaway `renders/C_section.png`.

## Why it's strong now (the honeycomb + reinforcement)
The earlier revision used individual tubes with gaps between them — interior tubes were
cantilevered off the base and **snapped off**. This revision packs the cells so their 2 mm
walls **overlap by ~1 mm and fuse** into a continuous honeycomb (verified: every pocket's
nearest neighbour overlaps, `tube-fuse margin = −1.0 mm`). Edge cells fuse into the perimeter
wall; a 5 mm solid base ties every cell bottom together. There are no free-standing walls.

**Reinforced against cold snapping** (the two failure points if it's dropped when cold):
- **Fillet at every cell-to-base junction** (`FILLET = 2.5 mm`, 45°) — spreads the load out of
  the sharp root corner where a wall would otherwise crack off. This is the single biggest
  anti-snap change.
- **Perimeter wall thickened 3 → 4 mm** — it's the tallest thin wall and takes the drops.
- Cost of both: only ~25 g more filament.

**Material matters more than geometry for cold brittleness:** print in **PETG** (tough, stays
that way cold), **not PLA** (PLA is what snaps when cold). If it lives somewhere genuinely cold,
PETG or ASA. Use **4 wall/perimeter lines** in the slicer — the honeycomb's strength is in its walls.

## Why every vial stays dark
1. **Opaque filament** (print black/dark) — walls don't transmit light.
2. **Own opaque cell** — each vial is walled on all sides; the cell rim sits ~8 mm above the
   vial top.
3. **Solid base + perimeter wall + lift-off lid** — the box is closed on all six sides;
   genus 0 means there is not a single through-hole in any wall.

## Stepped cells = lighter
Each cell is only `vial height + 8 mm` tall, so a 45 mm 1 mL vial gets a ~53 mm cell instead
of riding a tall dead pedestal up to the 91 mm rim. That cut the print mass by ~60 % versus a
solid block, while keeping full honeycomb strength.

## Print settings
- **Material:** **PETG** in an **opaque dark color** — light-blocking + cold-tough. Avoid PLA if
  it will ever be cold (that's what snaps).
- **Infill:** 12–15 %. **Walls/perimeters: 4** (the honeycomb strength lives in the walls).
- **Supports:** none. Print tray base-down, lid **roof-down** (skirt up).
- **Bed:** ≤ 220 × 220 mm covers all three. Bore mouths are chamfered for easy drop-in.

## Files
```
scad/vial_vault.scad   parametric model (tray | lid | section) — reads build/<D>_geom.scad
tools/layout.py        layout + geometry engine + all checks (edit fit params HERE)
tools/build_all.sh     render every design to stl/ + renders/
tools/verify_bbox.py   parse STL: bbox match, mesh volume, mass
build/                 auto-generated per-design geometry + part wrappers
stl/  renders/         print files + images
PARAMS.md              every dimension in mm + inches, with the fit assumptions
LOG.md                 iteration log + geometry-check summary
```

## Regenerate / retune
```bash
# edit vial sizes / counts in tools/layout.py, then:
python3 tools/layout.py all      # runs all geometry checks, writes build/
bash   tools/build_all.sh        # renders stl/ + renders/
python3 tools/verify_bbox.py stl/C_tray.stl   # bbox + mass sanity
```

## Verification (final)
All 6 parts render **manifold / NoError**, **genus 0** (no wall openings), and rendered bbox
**matches** the computed envelope. Geometry checks pass: shared webs ≥ 3 mm, every cell fuses
a neighbour or the wall (no free-standing tubes), all pockets inside the faces, tray+lid fit
the bed, 5 mm base under every vial, vials recessed 8 mm. See `LOG.md`.

## ⚠️ Fit assumptions to check first
1 mL 16.0 mm OD · 10 mL 23.0 mm · 30 mL 33.0 mm · syringe cell 14 mm bore × 65 mm
(barrel/short syringe, **needle off**). 10 mL & 30 mL bores tightened to a 1.0 mm radial gap.
Details + how to change them: `PARAMS.md`.
