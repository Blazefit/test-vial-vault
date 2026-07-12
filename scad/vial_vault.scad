// vial_vault.scad -- MERGED-TUBE HONEYCOMB dark-storage vial holder (tray + lid).
// Base slab + full-height perimeter wall + one tube per pocket. Tubes are packed so
// their walls overlap and FUSE into a continuous honeycomb (nothing free-standing).
// Each tube is only as tall as its own vial (cell height = BASE_T + depth), so short
// vials don't carry tall dead pedestals -> much lighter than a solid block.
// Geometry + POCKETS from build/<D>_geom.scad. PART set by the wrapper (never re-assign).
$fn = 72;

part_sel = is_undef(PART) ? "tray" : PART;

module rrect(sx, sy, h, r) {
    r = min(r, sx/2, sy/2);
    hull() for (dx = [r - sx/2, sx/2 - r], dy = [r - sy/2, sy/2 - r])
        translate([dx, dy, 0]) cylinder(r = r, h = h);
}

// full-height tube for one pocket (positive). Cell top = BASE_T + depth.
// A conical fillet at the base flares the cell where it meets the slab -- this is the
// stress-relief that stops the wall snapping off its root (worst failure mode when cold).
module tube(p) {
    x = p[0]; y = p[1]; bore = p[2]; depth = p[3];
    od = bore + 2 * PWALL;
    translate([x, y, 0]) {
        cylinder(d = od, h = BASE_T + depth);
        translate([0, 0, BASE_T])                       // fillet root at the slab top
            cylinder(d1 = od + 2 * FILLET, d2 = od, h = FILLET);
    }
}

// negative: vial cavity (rests on the base slab) + mouth funnel + finger scallop
module bore_cut(p) {
    x = p[0]; y = p[1]; bore = p[2]; depth = p[3]; small = p[4];
    scal = len(p) > 5 ? p[5] : 0;
    ctop = BASE_T + depth;                    // this pocket's own rim height
    translate([x, y, 0]) {
        translate([0, 0, BASE_T]) cylinder(d = bore, h = depth + 0.2);          // cavity
        translate([0, 0, ctop - 1.6]) cylinder(d1 = bore, d2 = bore + 2.4, h = 1.8); // funnel
        if (FINGER_SCALLOP && small == 1)
            rotate([0, 0, scal])
                translate([bore/2 - 1.0, 0, ctop - 18]) cylinder(d = bore * 0.5, h = 20);
    }
}

module tray() {
    difference() {
        union() {
            // base slab with a bottom outer chamfer for first-layer adhesion
            hull() {
                translate([0, 0, 0.8]) rrect(OUTER_W, OUTER_L, BASE_T - 0.8, CORNER_R);
                rrect(OUTER_W - 1.6, OUTER_L - 1.6, 0.6, CORNER_R);
            }
            // full-height perimeter wall (darkness + lid seat)
            difference() {
                rrect(OUTER_W, OUTER_L, RIM_H, CORNER_R);
                translate([0, 0, BASE_T])
                    rrect(OUTER_W - 2*WALL, OUTER_L - 2*WALL, RIM_H, max(0.5, CORNER_R - WALL));
            }
            for (p = POCKETS) tube(p);        // fused honeycomb of cells
        }
        for (p = POCKETS) bore_cut(p);
    }
}

module lid() {
    lw = OUTER_W + 2 * (LID_GAP + SKIRT_W);
    ll = OUTER_L + 2 * (LID_GAP + SKIRT_W);
    lr = CORNER_R + LID_GAP + SKIRT_W;
    difference() {
        union() {
            rrect(lw, ll, ROOF_T, lr);
            translate([0, 0, ROOF_T])
                difference() {
                    rrect(lw, ll, SKIRT_H, lr);
                    translate([0, 0, -0.1])
                        rrect(OUTER_W + 2*LID_GAP, OUTER_L + 2*LID_GAP, SKIRT_H + 0.2,
                              CORNER_R + LID_GAP);
                }
        }
        for (sx = [-1, 1])
            translate([sx * lw/2, 0, ROOF_T + SKIRT_H])
                rotate([90, 0, 90]) cylinder(d = 28, h = SKIRT_W * 4, center = true);
    }
}

// fit-audit cutaway: sliced at y=0 with reference vials resting on the base slab
module ghost_vials() {
    for (p = POCKETS) {
        x = p[0]; y = p[1]; bore = p[2]; depth = p[3];
        translate([x, y, BASE_T]) cylinder(d = max(2, bore - 2), h = depth - RECESS);
    }
}
module section() {
    difference() {
        union() { tray(); color([0.85, 0.2, 0.2]) ghost_vials(); }
        translate([-(OUTER_W + 40)/2, 0, -1]) cube([OUTER_W + 40, OUTER_L + 40, RIM_H + 40]);
    }
}

if (part_sel == "tray") tray();
else if (part_sel == "lid") lid();
else if (part_sel == "section") section();
else tray();
