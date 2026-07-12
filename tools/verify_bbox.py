#!/usr/bin/env python3
"""Parse a binary STL and print its bounding box (mm). Compare to expected.
Usage: verify_bbox.py file.stl [exp_x exp_y exp_z tol]
Guards the OpenSCAD wrapper-PART gotcha: a silently-wrong part render will
have a bbox that does not match the design's expected envelope.
"""
import sys, struct

PETG_DENSITY = 1.27e-3   # g per mm^3

def bbox_vol(path):
    """Return (lo, hi, solid_volume_mm3). Volume via signed tetrahedra."""
    with open(path, "rb") as f:
        f.read(80)
        (n,) = struct.unpack("<I", f.read(4))
        lo = [1e18]*3; hi = [-1e18]*3
        vol6 = 0.0
        for _ in range(n):
            data = f.read(50)
            if len(data) < 50: break
            vals = struct.unpack("<12f", data[:48])
            v = [vals[3:6], vals[6:9], vals[9:12]]
            for vv in v:
                for k in range(3):
                    lo[k] = min(lo[k], vv[k]); hi[k] = max(hi[k], vv[k])
            (ax,ay,az),(bx,by,bz),(cx,cy,cz) = v
            vol6 += (ax*(by*cz - bz*cy) - ay*(bx*cz - bz*cx) + az*(bx*cy - by*cx))
    return lo, hi, abs(vol6) / 6.0

if __name__ == "__main__":
    path = sys.argv[1]
    lo, hi, vol = bbox_vol(path)
    dx, dy, dz = (hi[0]-lo[0], hi[1]-lo[1], hi[2]-lo[2])
    cc = vol / 1000.0
    solid_g = vol * PETG_DENSITY
    # printed mass estimate: ~2 perimeters + top/bottom solid + 15% infill core.
    # empirically ~30-40% of the solid-block mass for this wall/pocket geometry.
    est_g = solid_g * 0.35
    print(f"{path}: bbox {dx:.2f} x {dy:.2f} x {dz:.2f} mm"
          f"  ({dx/25.4:.2f} x {dy/25.4:.2f} x {dz/25.4:.2f} in)"
          f"  | solid {cc:.1f} cc  ~{est_g:.0f} g PETG @15% infill")
    if len(sys.argv) >= 5:
        ex, ey, ez = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
        tol = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
        ok = all(abs(a-b) <= tol for a, b in ((dx,ex),(dy,ey),(dz,ez)))
        print(f"  expected {ex:.2f} x {ey:.2f} x {ez:.2f}  -> {'MATCH' if ok else 'MISMATCH'}")
        sys.exit(0 if ok else 2)
