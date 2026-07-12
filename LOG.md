# Iteration Log — Testosterone Vial Vault

Every iteration is gated by `tools/layout.py` (analytic geometry checks) and, where
geometry changed, by `tools/verify_bbox.py` against the freshly rendered STL. "PASS"
means all HARD checks cleared for A, B, and C.

| # | Change | Problem it fixed / why | Result |
|---|--------|------------------------|--------|
| 1 | Initial row-packed layout + geometry checker | baseline | **FAIL** — 30 mL pedestals 2.0 mm (< 4.0 min); Design C 236 mm long (> 220 bed) |
| 2 | `rim_height` += `INNER_GAP`; rebalanced C (1 mL → 6 cols) | pedestal math dropped the 2 mm bore-bottom gap; C overran bed | **PASS** all three |
| 3 | Rendered STLs, bbox-verified vs computed envelope; C 10 mL → single row of 6 | C lid was 218.4 mm (1.6 mm bed margin — fragile); bbox parser guards silent wrong-part renders | **PASS**, C margin now ~17 mm |
| 4 | Added bore lead-in chamfers (funnel mouth) | vials/syringes catch on a sharp bore lip on the drop-in | **PASS**, manifold NoError |
| 5 | Lid finger-pull scallops + base bottom outer chamfer | lid was hard to lift off flush walls; sharp base edge hurts first-layer adhesion | **PASS**, manifold NoError |
| 6 | Added lid-fit + vial-seating checks to engine | fit was only eyeballed; now proven: 10.0 mm recess, lid clears vial tops | **PASS**, numeric clearances reported |
| 7 | Scallop now points to box centre + breach guard + light-tightness check | uniform +X scallop could pierce the perimeter on an edge pocket; verified each vial fully sleeved | **PASS**, no breach |
| 8 | Cutaway fit-audit render with reference vials | visual proof vials rest on pedestal and sit recessed/shaded | renders/C_section.png |
| 9 | Mesh-volume/mass reporting; rejected side lightening windows | needed print-budget; windows would leak light (kills the "dark" requirement) → opaque walls + 15% infill instead | trays ~275–380 g |
| 10 | Full rebuild + verify all 6 parts (bbox MATCH + manifold + genus) | final gate | **A/B/C tray+lid all PASS**; genus: A_tray 0 (fully light-tight), B/C_tray 2 (only the 2 hand-slots), all lids 0 |

| 11 | Tightened 10 mL & 30 mL clearance 3.0 → 2.0 mm (per-class); 1 mL & syr unchanged | fridge-holder fit was loose (1.5 mm/side); the vault was even looser. Now 1.0 mm/side — snug but one-handed | **PASS**; trays ~4–6 mm smaller, bbox re-MATCH, genus preserved (A 0 / B,C 2) |

| 12 | **Rearchitect: free-standing tubes → monolithic bored block** (denser packing, more openings, mixed-row 2D fill) | user feedback: interior tubes snapped off; too much empty space | **PASS**; A 18→37, C 25→57 openings — but solid block ~700 g (A) / ~980 g (C): too heavy |
| 13 | **Stepped merged-tube honeycomb**: cells fuse (walls overlap 1 mm), each cell only as tall as its vial; scallops dropped | solid block too heavy; still needed fused (not free-standing) walls + light | **PASS**, genus 0 all parts; mass down ~60% (A ~264 g, C ~383 g tray); `tube-fuse margin −1.0 mm` = nothing free-standing |

| 14 | **Reinforce vs cold-snap:** 45° fillet at every cell→base junction + perimeter wall 3→4 mm; recommend PETG (not PLA) + 4 walls | user: use the lightest that won't snap, reinforce if cold-prone | **PASS**, genus 0; +~25 g only (A 264→286, C 383→409 g tray); footprints unchanged |

## Geometry-check summary (final — fused honeycomb)
All HARD checks clear for A, B, C:
- shared web between adjacent bores ≥ 3.0 mm
- **fusion:** every cell overlaps a neighbour or the perimeter wall (`tube-fuse margin −1.0 mm`)
  → no free-standing tubes (the thing that snapped off before)
- every bore ≥ 4.5 mm from the outer face; block **and** lid fit the 220 × 220 mm bed
- 5 mm solid base under every vial; vials recessed 8 mm in their own cell
- light-tightness: all 6 parts **genus 0** — not one through-hole in any wall

## Notes on the iterations
1–10 built and hardened the original per-tube design (real geometry fixes: pedestal
thickness, bed overrun, thin margins, fit/light-tightness). 11 tightened the 10/30 mL fits.
12–13 are the architecture change from user feedback: tubes snapped off and left dead space,
so it was reworked into a denser **fused honeycomb** (12), then made **stepped + light** (13).
Re-run any of it with `python3 tools/layout.py all` then `bash tools/build_all.sh`.
