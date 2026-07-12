// vial_vault.scad -- parametric dark-storage vial holder (tray + lift-off lid)
// Geometry variables + POCKETS list are supplied by build/<D>_geom.scad.
// PART is set by the wrapper (build/<D>_tray.scad / _lid.scad). NEVER re-assign PART here.
$fn = 64;

part_sel = is_undef(PART) ? "tray" : PART;   // read-only selector (see memory gotcha)

// ---- rounded rectangular prism, centred in XY, z=0..h ----
module rrect(sx, sy, h, r) {
    r = min(r, sx/2, sy/2);
    hull() for (dx = [r - sx/2, sx/2 - r], dy = [r - sy/2, sy/2 - r])
        translate([dx, dy, 0]) cylinder(r = r, h = h);
}

// ---- one pocket tube: solid cylinder w/ bored vial cavity from top ----
module pocket(p) {
    x = p[0]; y = p[1]; bore = p[2]; depth = p[3]; small = p[4];
    scal = len(p) > 5 ? p[5] : 0;
    tube_od = bore + 2 * PWALL;
    translate([x, y, BASE_T]) {
        difference() {
            cylinder(d = tube_od, h = TUBE_H);
            // vial cavity: bored from the tube top down by `depth`
            translate([0, 0, TUBE_H - depth])
                cylinder(d = bore, h = depth + 0.1);
            // lead-in chamfer at the bore mouth: funnels the vial in on the drop
            translate([0, 0, TUBE_H - 1.6])
                cylinder(d1 = bore, d2 = bore + 2.4, h = 1.7);
            // finger scallop on small pockets: side notch from rim down ~18mm,
            // pointed toward the box centre (never faces the perimeter wall)
            if (FINGER_SCALLOP && small == 1)
                rotate([0, 0, scal])
                    translate([tube_od/2 - 1.5, 0, TUBE_H - 18])
                        cylinder(d = bore * 0.55, h = 20);
        }
    }
}

module all_pockets() {
    for (p = POCKETS) pocket(p);
}

// ---- hand slots cut through the two short (X-facing) end walls ----
module hand_slots() {
    sw = 60; sh = 16; zc = RIM_H - 14;
    for (sx = [-1, 1])
        translate([sx * (OUTER_W/2), 0, zc]) rotate([90, 0, 90])
            linear_extrude(height = WALL * 4, center = true)
                offset(r = sh/2) square([sw - sh, 0.01], center = true);
}

module tray() {
    difference() {
        union() {
            // base slab (with a bottom outer chamfer for clean first-layer adhesion)
            hull() {
                translate([0, 0, 0.8])
                    rrect(OUTER_W, OUTER_L, BASE_T - 0.8, CORNER_R);
                rrect(OUTER_W - 1.6, OUTER_L - 1.6, 0.6, CORNER_R);
            }
            // perimeter wall (hollow frame)
            difference() {
                rrect(OUTER_W, OUTER_L, RIM_H, CORNER_R);
                translate([0, 0, BASE_T])
                    rrect(OUTER_W - 2*WALL, OUTER_L - 2*WALL, RIM_H, max(0.5, CORNER_R - WALL));
            }
            // pocket tubes
            all_pockets();
        }
        if (HAND_SLOTS) hand_slots();
    }
}

module lid() {
    lw = OUTER_W + 2 * (LID_GAP + SKIRT_W);
    ll = OUTER_L + 2 * (LID_GAP + SKIRT_W);
    lr = CORNER_R + LID_GAP + SKIRT_W;
    // printed roof-down: roof plate at z=0, skirt rising in +z
    difference() {
        union() {
            rrect(lw, ll, ROOF_T, lr);                      // roof
            translate([0, 0, ROOF_T])
                difference() {                              // skirt wall
                    rrect(lw, ll, SKIRT_H, lr);
                    translate([0, 0, -0.1])
                        rrect(OUTER_W + 2*LID_GAP, OUTER_L + 2*LID_GAP, SKIRT_H + 0.2,
                              CORNER_R + LID_GAP);
                }
        }
        // finger-pull scallops on both short (X) ends of the skirt for easy lift-off
        for (sx = [-1, 1])
            translate([sx * lw/2, 0, ROOF_T + SKIRT_H])
                scale([1, 1, 1]) rotate([90, 0, 90])
                    cylinder(d = 26, h = SKIRT_W * 4, center = true);
    }
}

// ---- fit-audit cutaway: tray sliced at y=0 with reference vials at rest height ----
module ghost_vials() {
    for (p = POCKETS) {
        x = p[0]; y = p[1]; bore = p[2]; depth = p[3];
        vial_od = bore - 3;                 // nominal vial OD (bore minus clearance)
        vial_h  = depth - 2;                // nominal vial height (depth minus bore-gap)
        rest_z  = BASE_T + (TUBE_H - depth); // pedestal top the vial sits on
        translate([x, y, rest_z]) cylinder(d = max(2, vial_od), h = vial_h);
    }
}

module section() {
    difference() {
        union() {
            tray();
            // reference vials shown translucent-ish (own color) to check seating
            color([0.85, 0.2, 0.2]) ghost_vials();
        }
        // cut away the +Y half to expose the interior
        translate([-(OUTER_W + 40)/2, 0, -1])
            cube([OUTER_W + 40, OUTER_L + 40, RIM_H + 40]);
    }
}

if (part_sel == "tray") tray();
else if (part_sel == "lid") lid();
else if (part_sel == "section") section();
else { tray(); }
