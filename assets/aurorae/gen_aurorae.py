#!/usr/bin/env python3
"""Generates the "Ultron" KWin window decoration (Aurorae SVG theme).

Translucent glass title bar with a soft drop shadow and macOS-style
traffic-light buttons. The SVGs are written by hand-rolled code rather than
drawn in Inkscape so every measurement lives in one place (the constants
below) and stays in sync with Ultronrc.

    python3 gen_aurorae.py THEMES_DIR      (writes Ultron/ and UltronSolid/)
"""
import os
import sys

# ---- geometry (px) — keep in sync with the [Layout] section written below --
PAD_L = PAD_R = 26      # shadow extent, sides
PAD_T = 18              # shadow extent, top
PAD_B = 34              # shadow extent, bottom (longer = shadow falls downward)
RADIUS = 12             # top corner radius
INNER_B = 12            # part of the bottom slices that sits under the window
EDGE = 8                # length of the stretchable edge slices

# ---- colours ----------------------------------------------------------------
FILL = "#1b1d1c"        # title bar tint
FILL_ALPHA_ACTIVE = 0.68
FILL_ALPHA_INACTIVE = 0.60
RIM_LIGHT = 0.13        # 1px highlight on the inside of the top edge
RIM_DARK = 0.55         # 1px dark hairline hugging the outside
# shadow falloff: (position 0..1 from window toward the outer edge, alpha)
SHADOW = [(0.00, 0.46), (0.30, 0.40), (0.42, 0.27), (0.55, 0.16),
          (0.68, 0.085), (0.82, 0.030), (0.93, 0.008), (1.00, 0.0)]

CW = PAD_L + RADIUS     # corner slice width
CT = PAD_T + RADIUS     # top slice height
CB = PAD_B + INNER_B    # bottom slice height


def stops(strength):
    return "".join(
        f'<stop offset="{o:.2f}" stop-color="#000" stop-opacity="{a * strength:.3f}"/>'
        for o, a in SHADOW)


def frame(prefix, ox, oy, fill_alpha, strength, mask=False):
    """One nine-slice frame, laid out at (ox, oy). Returns (defs, body)."""
    p = prefix
    gid = p.replace("-", "_")
    x0, x1, x2 = ox, ox + CW, ox + CW + EDGE          # column origins
    y0, y1, y2 = oy, oy + CT, oy + CT + EDGE          # row origins
    d, b = [], []

    def box(x, y, w, h):
        # invisible rect pinning the slice's bounding box
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" fill-opacity="0"/>'

    if mask:
        # Blur region: opaque exactly where the window body is.
        solid = 'fill="#000"'
        b.append(f'<g id="{p}-topleft">{box(x0, y0, CW, CT)}'
                 f'<path {solid} d="M{x1} {y0 + PAD_T}v{RADIUS}h{-RADIUS}a{RADIUS} {RADIUS} 0 0 1 {RADIUS} {-RADIUS}z"/></g>')
        b.append(f'<g id="{p}-top">{box(x1, y0, EDGE, CT)}'
                 f'<rect {solid} x="{x1}" y="{y0 + PAD_T}" width="{EDGE}" height="{RADIUS}"/></g>')
        b.append(f'<g id="{p}-topright">{box(x2, y0, CW, CT)}'
                 f'<path {solid} d="M{x2} {y0 + PAD_T}a{RADIUS} {RADIUS} 0 0 1 {RADIUS} {RADIUS}h{-RADIUS}z"/></g>')
        b.append(f'<g id="{p}-left">{box(x0, y1, CW, EDGE)}'
                 f'<rect {solid} x="{x0 + PAD_L}" y="{y1}" width="{RADIUS}" height="{EDGE}"/></g>')
        b.append(f'<g id="{p}-center"><rect {solid} x="{x1}" y="{y1}" width="{EDGE}" height="{EDGE}"/></g>')
        b.append(f'<g id="{p}-right">{box(x2, y1, CW, EDGE)}'
                 f'<rect {solid} x="{x2}" y="{y1}" width="{RADIUS}" height="{EDGE}"/></g>')
        b.append(f'<g id="{p}-bottomleft">{box(x0, y2, CW, CB)}'
                 f'<rect {solid} x="{x0 + PAD_L}" y="{y2}" width="{RADIUS}" height="{INNER_B}"/></g>')
        b.append(f'<g id="{p}-bottom">{box(x1, y2, EDGE, CB)}'
                 f'<rect {solid} x="{x1}" y="{y2}" width="{EDGE}" height="{INNER_B}"/></g>')
        b.append(f'<g id="{p}-bottomright">{box(x2, y2, CW, CB)}'
                 f'<rect {solid} x="{x2}" y="{y2}" width="{RADIUS}" height="{INNER_B}"/></g>')
        return "", "\n".join(b)

    s = stops(strength)
    U = 'gradientUnits="userSpaceOnUse"'
    # corner gradients: unit circle scaled to the slice, centred on the window-side corner
    d.append(f'<radialGradient id="{gid}_tl" {U} cx="0" cy="0" r="1" gradientTransform="translate({x1} {y1}) scale({CW} {CT})">{s}</radialGradient>')
    d.append(f'<radialGradient id="{gid}_tr" {U} cx="0" cy="0" r="1" gradientTransform="translate({x2} {y1}) scale({CW} {CT})">{s}</radialGradient>')
    d.append(f'<radialGradient id="{gid}_bl" {U} cx="0" cy="0" r="1" gradientTransform="translate({x1} {y2}) scale({CW} {CB})">{s}</radialGradient>')
    d.append(f'<radialGradient id="{gid}_br" {U} cx="0" cy="0" r="1" gradientTransform="translate({x2} {y2}) scale({CW} {CB})">{s}</radialGradient>')
    d.append(f'<linearGradient id="{gid}_t" {U} x1="0" y1="{y1}" x2="0" y2="{y0}">{s}</linearGradient>')
    d.append(f'<linearGradient id="{gid}_b" {U} x1="0" y1="{y2}" x2="0" y2="{y2 + CB}">{s}</linearGradient>')
    d.append(f'<linearGradient id="{gid}_l" {U} x1="{x1}" y1="0" x2="{x0}" y2="0">{s}</linearGradient>')
    d.append(f'<linearGradient id="{gid}_r" {U} x1="{x2}" y1="0" x2="{x2 + CW}" y2="0">{s}</linearGradient>')

    glass = f'fill="{FILL}" fill-opacity="{fill_alpha}"'
    # Hairlines are filled shapes, never strokes: Qt pads the bounding box of a
    # stroked path by half the pen width, which leaves a transparent sliver at
    # the edge of every tiled slice (visible as tick marks along the frame).
    hi = f'fill="#fff" fill-opacity="{RIM_LIGHT}"'
    lo = f'fill="#000" fill-opacity="{RIM_DARK * strength:.3f}"'
    wt = y0 + PAD_T          # y of the window's top edge
    wl = x0 + PAD_L          # x of the window's left edge
    wr = x2 + RADIUS         # x of the window's right edge
    R = RADIUS

    def ring_tl(cx, cy, ro, ri):
        return f'M{cx - ro} {cy}A{ro} {ro} 0 0 1 {cx} {cy - ro}L{cx} {cy - ri}A{ri} {ri} 0 0 0 {cx - ri} {cy}Z'

    def ring_tr(cx, cy, ro, ri):
        return f'M{cx} {cy - ro}A{ro} {ro} 0 0 1 {cx + ro} {cy}L{cx + ri} {cy}A{ri} {ri} 0 0 0 {cx} {cy - ri}Z'

    def bar(x, y, w, h, paint):
        return f'<rect {paint} x="{x}" y="{y}" width="{w}" height="{h}"/>'

    # Shadows are clipped to the outside of the window shape so the translucent
    # glass never sits on top of its own shadow.
    b.append(f'<g id="{p}-topleft">{box(x0, y0, CW, CT)}'
             f'<path fill="url(#{gid}_tl)" d="M{x0} {y0}h{CW}v{PAD_T}a{R} {R} 0 0 0 {-R} {R}h{-PAD_L}z"/>'
             f'<path {glass} d="M{x1} {wt}v{R}h{-R}a{R} {R} 0 0 1 {R} {-R}z"/>'
             f'<path {lo} d="{ring_tl(x1, y1, R + 1, R)}"/>'
             f'<path {hi} d="{ring_tl(x1, y1, R, R - 1)}"/></g>')
    b.append(f'<g id="{p}-top">{box(x1, y0, EDGE, CT)}'
             f'<rect fill="url(#{gid}_t)" x="{x1}" y="{y0}" width="{EDGE}" height="{PAD_T}"/>'
             f'<rect {glass} x="{x1}" y="{wt}" width="{EDGE}" height="{R}"/>'
             + bar(x1, wt - 1, EDGE, 1, lo) + bar(x1, wt, EDGE, 1, hi) + '</g>')
    b.append(f'<g id="{p}-topright">{box(x2, y0, CW, CT)}'
             f'<path fill="url(#{gid}_tr)" d="M{x2} {y0}h{CW}v{CT}h{-PAD_R}a{R} {R} 0 0 0 {-R} {-R}z"/>'
             f'<path {glass} d="M{x2} {wt}a{R} {R} 0 0 1 {R} {R}h{-R}z"/>'
             f'<path {lo} d="{ring_tr(x2, y1, R + 1, R)}"/>'
             f'<path {hi} d="{ring_tr(x2, y1, R, R - 1)}"/></g>')
    b.append(f'<g id="{p}-left">{box(x0, y1, CW, EDGE)}'
             f'<rect fill="url(#{gid}_l)" x="{x0}" y="{y1}" width="{PAD_L}" height="{EDGE}"/>'
             f'<rect {glass} x="{wl}" y="{y1}" width="{R}" height="{EDGE}"/>'
             + bar(wl - 1, y1, 1, EDGE, lo) + '</g>')
    b.append(f'<g id="{p}-center"><rect {glass} x="{x1}" y="{y1}" width="{EDGE}" height="{EDGE}"/></g>')
    b.append(f'<g id="{p}-right">{box(x2, y1, CW, EDGE)}'
             f'<rect fill="url(#{gid}_r)" x="{wr}" y="{y1}" width="{PAD_R}" height="{EDGE}"/>'
             f'<rect {glass} x="{x2}" y="{y1}" width="{R}" height="{EDGE}"/>'
             + bar(wr, y1, 1, EDGE, lo) + '</g>')
    b.append(f'<g id="{p}-bottomleft">{box(x0, y2, CW, CB)}'
             f'<path fill="url(#{gid}_bl)" d="M{x0} {y2}h{PAD_L}v{INNER_B}h{R}v{PAD_B}h{-CW}z"/>'
             f'<rect {glass} x="{wl}" y="{y2}" width="{R}" height="{INNER_B}"/>'
             + bar(wl - 1, y2, 1, INNER_B + 1, lo) + bar(wl, y2 + INNER_B, R, 1, lo) + '</g>')
    b.append(f'<g id="{p}-bottom">{box(x1, y2, EDGE, CB)}'
             f'<rect fill="url(#{gid}_b)" x="{x1}" y="{y2 + INNER_B}" width="{EDGE}" height="{PAD_B}"/>'
             f'<rect {glass} x="{x1}" y="{y2}" width="{EDGE}" height="{INNER_B}"/>'
             + bar(x1, y2 + INNER_B, EDGE, 1, lo) + '</g>')
    b.append(f'<g id="{p}-bottomright">{box(x2, y2, CW, CB)}'
             f'<path fill="url(#{gid}_br)" d="M{x2 + R} {y2}h{PAD_R}v{CB}h{-CW}v{-PAD_B}h{R}z"/>'
             f'<rect {glass} x="{x2}" y="{y2}" width="{R}" height="{INNER_B}"/>'
             + bar(x2, y2 + INNER_B, R, 1, lo) + bar(wr, y2, 1, INNER_B + 1, lo) + '</g>')
    return "\n".join(d), "\n".join(b)


def decoration_svg(alpha_active=FILL_ALPHA_ACTIVE, alpha_inactive=FILL_ALPHA_INACTIVE):
    fw = CW * 2 + EDGE
    fh = CT + EDGE + CB
    gap = 16
    defs, body = [], []
    rows = [
        ("decoration", alpha_active, 1.0, False),
        ("decoration-inactive", alpha_inactive, 0.62, False),
        ("mask", 1.0, 1.0, True),
    ]
    for i, (prefix, alpha, strength, mask) in enumerate(rows):
        d, b = frame(prefix, 0, i * (fh + gap), alpha, strength, mask)
        defs.append(d)
        body.append(b)
    # Maximized windows: flat strip, no rounding, no shadow.
    my = len(rows) * (fh + gap)
    body.append(f'<g id="decoration-maximized-center"><rect x="0" y="{my}" width="{EDGE}" height="{EDGE}" fill="{FILL}" fill-opacity="{alpha_active}"/></g>')
    body.append(f'<g id="decoration-maximized-inactive-center"><rect x="{EDGE * 2}" y="{my}" width="{EDGE}" height="{EDGE}" fill="{FILL}" fill-opacity="{alpha_inactive}"/></g>')
    h = my + EDGE
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fw}" height="{h}" viewBox="0 0 {fw} {h}">\n'
            f'<defs>\n' + "\n".join(defs) + '\n</defs>\n' + "\n".join(body) + '\n</svg>\n')


# ---- traffic lights -----------------------------------------------------------
B = 14  # button diameter

def glyph(kind, ox, colour):
    c = B / 2
    pen = f'fill="none" stroke="{colour}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"'
    lo, hi = 4.3, B - 4.3
    if kind == "close":
        return f'<path {pen} d="M{ox + lo} {lo}L{ox + hi} {hi}M{ox + hi} {lo}L{ox + lo} {hi}"/>'
    if kind == "minimize":
        return f'<path {pen} d="M{ox + 3.8} {c}H{ox + B - 3.8}"/>'
    if kind == "maximize":
        return f'<path {pen} d="M{ox + 3.8} {c}H{ox + B - 3.8}M{ox + c} 3.8V{B - 3.8}"/>'
    return f'<rect {pen} x="{ox + 4.5}" y="4.5" width="{B - 9}" height="{B - 9}" rx="1"/>'


COLOURS = {  # fill, rim, glyph
    "close": ("#ff5f57", "#e0443e", "#4d0000"),
    "minimize": ("#febc2e", "#d89e24", "#5a3a00"),
    "maximize": ("#28c840", "#1aab29", "#0a4d00"),
    "restore": ("#28c840", "#1aab29", "#0a4d00"),
}
IDLE = ("#4b4e4d", "#3b3e3d")       # unfocused windows: quiet grey dots


def button_svg(kind):
    fill, rim, glyph_colour = COLOURS[kind]
    states = [
        # (prefix, fill, rim, show glyph, darken)
        ("active", fill, rim, False, 0.0),
        ("hover", fill, rim, True, 0.0),
        ("pressed", fill, rim, True, 0.22),
        ("deactivated", IDLE[0], IDLE[1], False, 0.0),
        ("inactive", IDLE[0], IDLE[1], False, 0.0),
        ("hover-inactive", fill, rim, True, 0.0),
        ("pressed-inactive", fill, rim, True, 0.22),
        ("deactivated-inactive", IDLE[0], IDLE[1], False, 0.0),
    ]
    out = []
    for i, (prefix, f, r, show, dark) in enumerate(states):
        ox = i * (B + 6)
        c = B / 2
        g = [f'<rect x="{ox}" y="0" width="{B}" height="{B}" fill="#000" fill-opacity="0"/>',
             f'<circle cx="{ox + c}" cy="{c}" r="{c - .5}" fill="{f}" stroke="{r}" stroke-width="1"/>']
        if dark:
            g.append(f'<circle cx="{ox + c}" cy="{c}" r="{c}" fill="#000" fill-opacity="{dark}"/>')
        if show:
            g.append(glyph(kind, ox, glyph_colour))
        out.append(f'<g id="{prefix}-center">' + "".join(g) + '</g>')
    w = len(states) * (B + 6)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{B}" viewBox="0 0 {w} {B}">\n'
            + "\n".join(out) + '\n</svg>\n')


RC = f"""[General]
ActiveTextColor=236,238,237,255
InactiveTextColor=138,144,141,255
UseTextShadow=false
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=120

[Layout]
BorderLeft=0
BorderRight=0
BorderBottom=0
TitleEdgeTop=10
TitleEdgeBottom=10
TitleEdgeLeft=14
TitleEdgeRight=14
TitleEdgeTopMaximized=10
TitleEdgeBottomMaximized=10
TitleEdgeLeftMaximized=14
TitleEdgeRightMaximized=14
TitleBorderLeft=12
TitleBorderRight=12
TitleHeight={B}
ButtonWidth={B}
ButtonHeight={B}
ButtonSpacing=8
ButtonMarginTop=0
ExplicitButtonSpacer=8
PaddingTop={PAD_T}
PaddingBottom={PAD_B}
PaddingLeft={PAD_L}
PaddingRight={PAD_R}
"""

def metadata(name, comment):
    return f"""[Desktop Entry]
Name={name}
Comment={comment}
X-KDE-PluginInfo-Author=Ultron OS Project
X-KDE-PluginInfo-Name={name}
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-License=GPL-3.0-or-later
X-KDE-PluginInfo-EnabledByDefault=true
"""


def write_theme(parent, name, comment, alpha_active, alpha_inactive):
    out = os.path.join(parent, name)
    os.makedirs(out, exist_ok=True)
    files = {
        "decoration.svg": decoration_svg(alpha_active, alpha_inactive),
        f"{name}rc": RC,
        "metadata.desktop": metadata(name, comment),
    }
    for kind in ("close", "minimize", "maximize", "restore"):
        files[f"{kind}.svg"] = button_svg(kind)
    for fname, data in files.items():
        with open(os.path.join(out, fname), "w") as fh:
            fh.write(data)
    print(f"wrote {len(files)} files to {out}")


def main(parent):
    # Glass: translucent, blurred by KWin. Solid: same frame, opaque; used when
    # there is no 3D driver (see /usr/bin/ultron-glass).
    write_theme(parent, "Ultron", "Glass title bar with traffic-light buttons",
                FILL_ALPHA_ACTIVE, FILL_ALPHA_INACTIVE)
    write_theme(parent, "UltronSolid", "Solid title bar with traffic-light buttons", 1.0, 1.0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "themes")
