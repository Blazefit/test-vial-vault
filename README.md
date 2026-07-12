# Testosterone Vial Vault — dark room-temp storage

3D-printable, **light-blocking** storage for testosterone vials + syringes, kept at **room
temperature** (not fridge/freezer). Three designs at different capacities — **pick one**.
Each is a tray of individual opaque vial sleeves + a lift-off lid; print in an opaque
filament (black/dark) and every vial is shaded from light.

> **These are engineering models, not medical advice.** Verify vial fit with calipers
> before printing a full set (see `PARAMS.md`).

---

## Pick a design

| | **A — Compact Slab** | **B — Caddy (grips)** | **C — Max Vault** |
|---|---|---|---|
| 10 mL vials | 4 | 5 | 6 |
| 30 mL vials | 2 | 2 | 3 |
| 1 mL vials | 8 | 10 | 12 |
| Syringes (2×2) | 4 | 4 | 4 |
| Carry hand-slots | — | ✓ | ✓ |
| Tray (in) | 5.35 × 7.17 × 3.74 | 6.55 × 7.17 × 3.74 | 7.76 × 7.17 × 3.74 |
| Tray (mm) | 135.8 × 182.2 × 95.0 | 166.4 × 182.2 × 95.0 | 197.0 × 182.2 × 95.0 |
| Fits 220 mm bed | ✓ | ✓ | ✓ (17 mm margin) |
| Light-tightness | **fully sealed** (genus 0) | 2 top hand-slots* | 2 top hand-slots* |
| ~PETG (tray+lid) | ~314 g | ~365 g | ~429 g |

\* The hand-slots open into the interior cavity only. Every vial sits inside its **own opaque
sleeve** (2 mm wall, rim above the vial top), so the slots never expose a vial to light.
If you want zero openings, choose **A**.

Renders: `renders/A_tray.png`, `B_tray.png`, `C_tray.png`, lids, and the fit-audit cutaway
`renders/C_section.png`.

## How it keeps things dark
1. **Opaque filament** (print black or another dark color) — walls don't transmit light.
2. **Per-vial sleeves** — each vial drops into its own tube; the tube rim sits ~2 mm above
   the vial top, so vials are shaded even with the lid off.
3. **Lift-off lid** — full opaque cover with a 15 mm skirt; covers the open top completely.
4. Vials rest on stepped pedestals so all tops sit **10 mm below the rim** (shaded + the lid
   clears them).

## Print settings
- **Material:** PETG or PLA in an **opaque dark color** (light-blocking is the whole point).
- **Infill:** 15 % (the pedestals are modeled solid; infill makes them light — mass figures
  above assume 15 %).
- **Supports:** none needed. Print tray base-down, lid **roof-down** (skirt up).
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
LOG.md                 the 10-iteration refinement log + geometry-check summary
```

## Regenerate / retune
```bash
# 1. edit vial sizes in tools/layout.py (VIAL, DIA_CLEAR) if your calipers disagree
python3 tools/layout.py all      # runs all geometry checks, writes build/
bash   tools/build_all.sh        # renders stl/ + renders/
python3 tools/verify_bbox.py stl/C_tray.stl   # bbox + mass sanity
```

## Verification (all designs, final)
- All 6 parts render **manifold / NoError**; rendered bbox **matches** the computed envelope.
- Geometry checks pass: pocket walls ≥ 4.6 mm, all pockets inside the perimeter, tray+lid fit
  the bed, 30 mL pedestal ≥ 4 mm, vial tops recessed 10 mm, scallops don't breach, each vial
  fully sleeved. See `LOG.md`.

## ⚠️ Fit assumptions to check first
1 mL 16.0 mm OD · 10 mL 23.0 mm · 30 mL 33.0 mm · syringe pocket 14 mm bore × 65 mm
(barrel/short syringe, **needle off**). Full details + how to change them: `PARAMS.md`.
