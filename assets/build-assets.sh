#!/usr/bin/env bash
# Regenerates every derived artwork file under live-build/ from the sources in
# assets/. The outputs are committed, so you only need this after editing the
# logo, the wallpaper generator or the window-decoration generator.
#
# Needs: python3 with numpy + Pillow, rsvg-convert (librsvg2-bin), ImageMagick.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
R=live-build/config/includes.chroot

# logo -> icons, about dialog, splash, installer; dot -> boot splash
install -D -m644 assets/logo/ultron-logo.svg "$R/usr/share/icons/hicolor/scalable/apps/ultron-logo.svg"
install -D -m644 assets/logo/ultron-os.svg   "$R/usr/share/icons/hicolor/scalable/apps/ultron-os.svg"
install -D -m644 assets/logo/ultron-logo.svg "$R/usr/share/icons/Ultron/scalable/apps/ultron-logo.svg"
install -D -m644 assets/logo/ultron-os.svg   "$R/usr/share/icons/Ultron/scalable/apps/ultron-os.svg"
install -D -m644 assets/logo/ultron-mark.svg "$R/usr/share/ultron/ultron-mark.svg"
install -D -m644 assets/logo/ultron-os.svg   "$R/usr/share/ultron/ultron-os.svg"
install -D -m644 assets/logo/ultron-mark.svg "$R/usr/share/plasma/look-and-feel/org.ultronos.desktop/contents/splash/images/ultron-mark.svg"
rsvg-convert -w 256 -h 256 assets/logo/ultron-os.svg   -o "$R/etc/calamares/branding/ultronos/ultron-os.png"
rsvg-convert -w 128 -h 128 assets/logo/ultron-mark.svg -o "$R/etc/calamares/branding/ultronos/ultron-mark.png"
convert -size 512x512 xc:none -fill '#f2f3f2' -draw 'circle 256,256 256,4' -resize 128x128 "$R/usr/share/plymouth/themes/ultron/dot.png"

# wallpaper (4K) and everything cut from it
python3 assets/wallpaper/gen_wallpaper.py "$R/usr/share/wallpapers/Ultron/contents/images/3840x2160.jpg" 3840 2160
python3 assets/wallpaper/derive.py

# window decoration
python3 assets/aurorae/gen_aurorae.py "$R/usr/share/aurorae/themes"

echo "assets regenerated"
