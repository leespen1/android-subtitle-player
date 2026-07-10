#!/usr/bin/env bash
# Rebuild the vector launcher icon from the design.
#
# The adaptive launcher icon is a VectorDrawable (crisp at any size), NOT the
# raster mipmaps @capacitor/assets produces. Do not run `@capacitor/assets
# generate` for the icon: it would overwrite mipmap-anydpi-v26/ic_launcher*.xml
# back to raster PNGs with an inset. (Splash images are still fine to generate
# with gen-native-icons.py + @capacitor/assets.)
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/gen-icon-svg.py
npx svg2vectordrawable \
  -i assets/icon-foreground.svg \
  -o android/app/src/main/res/drawable/ic_launcher_foreground.xml

# Remove the Capacitor template's default android-robot foreground. Its -v24
# qualifier would otherwise shadow our drawable/ vector on API 24+.
rm -f android/app/src/main/res/drawable-v24/ic_launcher_foreground.xml
rmdir android/app/src/main/res/drawable-v24 2>/dev/null || true

echo "Updated res/drawable/ic_launcher_foreground.xml"
echo "The adaptive-icon XMLs reference @color/appBg + @drawable/ic_launcher_foreground."
