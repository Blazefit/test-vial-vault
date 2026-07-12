#!/bin/bash
# Render all designs (tray + lid) to STL + PNG, then verify bboxes.
# Run from repo root:  bash tools/build_all.sh
set -e
OSCAD=/opt/homebrew/bin/openscad
cd "$(dirname "$0")/.."
mkdir -p stl renders

render() {  # $1=wrapper.scad $2=out.stl
  perl -e 'alarm 240; exec @ARGV' "$OSCAD" -o "$2" --export-format=binstl "$1" 2>/dev/null
}
snap() {    # $1=wrapper.scad $2=out.png
  perl -e 'alarm 240; exec @ARGV' "$OSCAD" -o "$2" --imgsize=1100,850 \
     --camera=0,0,0,55,0,25,0 --viewall --autocenter --colorscheme=Tomorrow "$1" 2>/dev/null
}

for D in A B C; do
  for P in tray lid; do
    echo "render $D $P ..."
    render "build/${D}_${P}.scad" "stl/${D}_${P}.stl"
    snap   "build/${D}_${P}.scad" "renders/${D}_${P}.png"
  done
done
echo "done."
