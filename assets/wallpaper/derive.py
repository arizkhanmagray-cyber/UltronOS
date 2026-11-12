#!/usr/bin/env python3
"""Cuts the installer banner, installer slide, GRUB background and live boot
splash out of the wallpaper. Run from the repository root."""
import io
import subprocess

from PIL import Image, ImageEnhance, ImageFilter

R = "live-build/config/includes.chroot"
BR = R + "/etc/calamares/branding/ultronos/"
MARK = "assets/logo/ultron-mark.svg"


def mark(px):
    png = subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), MARK],
                         capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


wp = Image.open(R + "/usr/share/wallpapers/Ultron/contents/images/3840x2160.jpg")

# installer: slide background (soft, so text stays readable) and welcome banner
wp.resize((1280, 720)).filter(ImageFilter.GaussianBlur(3)).save(BR + "slide.jpg", quality=86)
banner = ImageEnhance.Brightness(wp.crop((0, 330, 3840, 1770)).resize((1040, 390))).enhance(0.9).convert("RGBA")
banner.alpha_composite(mark(110), ((1040 - 110) // 2, (390 - 110) // 2 - 10))
banner.convert("RGB").save(BR + "welcome.png")

# GRUB menu of the installed system
bg = ImageEnhance.Brightness(wp.resize((1920, 1080)).filter(ImageFilter.GaussianBlur(6))).enhance(0.55).convert("RGBA")
bg.alpha_composite(mark(120), ((1920 - 120) // 2, 250))
bg.convert("RGB").save(R + "/usr/share/grub/themes/ultron/background.png")

# boot menu of the live USB (800x600, GRUB scales it)
sp = wp.resize((1067, 600)).crop((133, 0, 933, 600)).filter(ImageFilter.GaussianBlur(3))
sp = ImageEnhance.Brightness(sp).enhance(0.55).convert("RGBA")
sp.alpha_composite(mark(84), ((800 - 84) // 2, 120))
sp.convert("RGB").save("live-build/config/bootloaders/grub-pc/splash.png")

# sign-in screen: frosted (blurred, slightly dimmed) copy of the wallpaper
login = ImageEnhance.Brightness(wp.resize((2560, 1440)).filter(ImageFilter.GaussianBlur(22))).enhance(0.80)
login.save(R + "/usr/share/sddm/themes/ultron/background.jpg", quality=88)

# translucent selection bar used by both GRUB themes
for dest in (R + "/usr/share/grub/themes/ultron/", "live-build/config/bootloaders/grub-pc/live-theme/"):
    Image.new("RGBA", (8, 8), (134, 179, 156, 70)).save(dest + "select_c.png")
print("derived images written")
