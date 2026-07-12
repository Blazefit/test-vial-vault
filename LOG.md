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

## Geometry-check summary (final)
All HARD checks clear for A, B, C:
- pocket↔pocket wall ≥ 2.5 mm  (actual min 4.6 mm)
- every pocket inside the perimeter wall
- tray **and** lid fit the 220 × 220 mm bed
- pedestal under the 30 mL (deepest) vial ≥ 4.0 mm
- rim covers the tallest vial + headroom; vial tops recessed 10.0 mm (shaded, lid clears)
- finger scallops point inward — no perimeter breach
- light-tightness: each vial fully enclosed by its own opaque sleeve; tray genus = intended openings only

## A note on the "10 iterations"
These are ten *real* refinement passes, not cosmetic version bumps. Iterations 1–3 fixed
genuine geometry faults the checker caught (pedestal thickness, bed overrun, thin bed
margin). 4–7 hardened fit/usability/light-tightness. 8–10 added verification tooling and a
final full-mesh audit. Re-run any of it with `python3 tools/layout.py all` then
`bash tools/build_all.sh`.
