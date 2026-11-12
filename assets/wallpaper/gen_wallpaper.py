#!/usr/bin/env python3
"""Procedurally renders the default Ultron OS wallpaper ("Still Water").

A monochrome mountain lake at night: layered ridgelines fading into haze,
conifer shorelines, a mist band on the waterline and a rippled reflection.
Everything is generated from seeded noise, so the image is original artwork
with no third-party licensing strings attached.

    python3 gen_wallpaper.py OUT.jpg [WIDTH HEIGHT] [--seed N]

Requires numpy and Pillow.
"""
import sys

import numpy as np
from PIL import Image, ImageFilter


def smooth(t):
    return t * t * (3.0 - 2.0 * t)


def noise1d(x, seed):
    """Value noise on arbitrary float coordinates."""
    xi = np.floor(x).astype(np.int64)
    xf = x - xi
    rng = np.random.default_rng(seed)
    table = rng.random(4096)
    a = table[xi % 4096]
    b = table[(xi + 1) % 4096]
    return a + (b - a) * smooth(xf)


def fbm1d(x, seed, octaves=6, gain=0.5, lac=2.0):
    total = np.zeros_like(x, dtype=np.float64)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        total += amp * noise1d(x * lac**o, seed + o * 101)
        norm += amp
        amp *= gain
    return total / norm


def ridged1d(x, seed, octaves=6, gain=0.52):
    """Sharper, peaky variant: looks like alpine ridgelines."""
    total = np.zeros_like(x, dtype=np.float64)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        n = noise1d(x * 2.0**o, seed + o * 57)
        total += amp * (1.0 - np.abs(2.0 * n - 1.0))
        norm += amp
        amp *= gain
    return total / norm


def noise2d(x, y, seed):
    xi = np.floor(x).astype(np.int64)
    yi = np.floor(y).astype(np.int64)
    xf = smooth(x - xi)
    yf = smooth(y - yi)
    rng = np.random.default_rng(seed)
    table = rng.random((256, 256))
    a = table[yi % 256, xi % 256]
    b = table[yi % 256, (xi + 1) % 256]
    c = table[(yi + 1) % 256, xi % 256]
    d = table[(yi + 1) % 256, (xi + 1) % 256]
    return (a + (b - a) * xf) + ((c + (d - c) * xf) - (a + (b - a) * xf)) * yf


def fbm2d(x, y, seed, octaves=5, gain=0.5):
    total = np.zeros(np.broadcast(x, y).shape, dtype=np.float64)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        total += amp * noise2d(x * 2.0**o, y * 2.0**o, seed + o * 31)
        norm += amp
        amp *= gain
    return total / norm


def render(width, height, seed=7):
    W, H = width, height
    horizon = int(H * 0.615)          # waterline
    xs = np.arange(W, dtype=np.float64)
    u = xs / W                          # 0..1 across
    yy, xx = np.mgrid[0:horizon, 0:W].astype(np.float64)
    v = yy / horizon                    # 0 at top, 1 at waterline

    # ---- sky -----------------------------------------------------------
    sky = 0.050 + 0.24 * v**1.9
    clouds = fbm2d(xx / W * 3.2, yy / horizon * 5.5, seed + 1, octaves=5)
    clouds = np.clip((clouds - 0.42) * 2.4, 0.0, 1.0)
    sky += clouds * (0.045 + 0.11 * v**1.4)
    # soft glow low in the sky, slightly right of centre
    glow = np.exp(-(((xx / W - 0.60) / 0.42) ** 2 + ((v - 0.95) / 0.40) ** 2))
    sky += 0.085 * glow
    img = sky

    haze_tone = 0.30                    # what distant things fade toward

    # ---- mountain ranges, far to near -----------------------------------
    def gauss1d(arr, sigma):
        r = max(1, int(sigma * 3))
        k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
        return np.convolve(np.pad(arr, r, mode="edge"), k / k.sum(), mode="valid")

    def massif(r, n, hmin, hmax, wmin, wmax, gap):
        """A handful of big peaks; the middle of the frame is kept lower."""
        prof = np.zeros(W)
        for _ in range(n):
            c = r.random() * 1.2 - 0.1
            h = hmin + (hmax - hmin) * r.random()
            h *= 0.40 + 0.60 * min(1.0, abs(c - 0.52) / gap)
            w = wmin + (wmax - wmin) * r.random()
            cone = h * np.clip(1.0 - np.abs(u - c) / w, 0.0, None) ** 1.18
            prof = np.maximum(prof, cone)
        return prof

    # (foot, peaks, min h, max h, min w, max w, gap, tone, haze, snow, seed)
    layers = [
        (0.70, 7, 0.20, 0.34, 0.16, 0.30, 0.20, 0.215, 0.74, 0.16, 11),
        (0.78, 6, 0.26, 0.47, 0.14, 0.26, 0.26, 0.150, 0.50, 0.40, 23),
        (0.86, 5, 0.30, 0.56, 0.13, 0.24, 0.34, 0.095, 0.27, 0.52, 37),
        (0.94, 6, 0.14, 0.30, 0.10, 0.20, 0.36, 0.055, 0.12, 0.20, 53),
    ]
    px = H / 1080.0
    for foot, n, hmin, hmax, wmin, wmax, gap, tone, haze, snow, off in layers:
        r = np.random.default_rng(seed + off)
        prof = massif(r, n, hmin, hmax, wmin, wmax, gap)
        crag = ridged1d(u * 9.0 + off, seed + off, octaves=6) - 0.5
        fine = fbm1d(u * 60.0 + off, seed + off + 3, octaves=4) - 0.5
        prof = prof + crag * (0.030 + 0.11 * prof) + fine * 0.010
        ridge_y = (foot - prof) * horizon
        depth = yy - ridge_y[None, :]                 # px below the ridgeline
        mask = np.clip(depth / (1.5 * px), 0.0, 1.0)
        dn = np.clip(depth, 0.0, None) / horizon      # normalised depth

        # which way a face looks: ridge slope near the crest, noise further down
        slope = np.gradient(gauss1d(ridge_y, W * 0.0030))
        crest = np.clip(0.5 - slope * 0.55, 0.0, 1.0)[None, :]
        lean = fbm2d(xx / W * 5.0, dn * 7.0, seed + off + 7, octaves=3) - 0.5
        spurs = fbm2d(xx / W * 15.0 + lean * 3.0, dn * 11.0 + lean * 2.0,
                      seed + off + 8, octaves=5)
        blend = np.clip(dn / 0.10, 0.0, 1.0)
        facing = crest * (1.0 - blend) + np.clip((spurs - 0.30) * 2.4, 0, 1) * blend

        # snow fields and gullies, thinning out with altitude loss
        gully = fbm2d(xx / W * 42.0 + lean * 9.0, dn * 26.0 + lean * 5.0,
                      seed + off + 9, octaves=5)
        cover = np.clip((gully - 0.40) * 3.4, 0.0, 1.0) * np.exp(-dn * 5.5)
        body = tone * (0.62 + 0.80 * facing) + snow * cover * (0.22 + 0.78 * facing)
        # each range sinks into mist toward its foot
        base_fog = np.clip((yy - horizon * 0.56) / (horizon * 0.44), 0.0, 1.0)
        local_haze = np.clip(haze + 0.62 * base_fog**1.5, 0.0, 0.95)
        body = body * (1.0 - local_haze) + haze_tone * local_haze
        img = img * (1.0 - mask) + body * mask

    # ---- conifer shorelines ----------------------------------------------
    rng = np.random.default_rng(seed + 99)

    def forest(profile, tone, haze, tree_h, density, sd, taper=None):
        r = np.random.default_rng(sd)
        top = profile.copy()
        n = int(W * density)
        px = r.integers(0, W, n)
        ph = tree_h * (0.45 + 0.75 * r.random(n))
        if taper is not None:
            ph = ph * np.clip(taper[px] * 5.0, 0.0, 1.0)
        for cx, h in zip(px, ph):
            half = max(2, int(h * 0.20))
            lo, hi = max(0, cx - half), min(W, cx + half + 1)
            seg = np.arange(lo, hi)
            tri = h * (1.0 - np.abs(seg - cx) / half)
            top[lo:hi] = np.minimum(top[lo:hi], profile[lo:hi] - tri)
        d = yy - top[None, :]
        m = np.clip(d / max(1.0, H / 1440.0), 0.0, 1.0)
        return m, tone * (1.0 - haze) + haze_tone * haze

    s = H / 2160.0
    # far shore: a thin dark band of trees right on the waterline
    prof = horizon - (22 + 34 * fbm1d(u * 7.0, seed + 201)) * s
    m, t = forest(prof, 0.050, 0.34, 46 * s, 0.30, seed + 301)
    img = img * (1 - m) + t * m
    # left headland
    left = np.clip(1.0 - u / 0.40, 0.0, 1.0) ** 0.85
    prof = horizon - (left * (150 + 110 * fbm1d(u * 5.0, seed + 202)) + 6) * s
    m, t = forest(prof, 0.030, 0.12, 96 * s, 0.14, seed + 302, left)
    m = m * (left > 0.004)[None, :]
    img = img * (1 - m) + t * m
    # right headland, a little taller
    right = np.clip((u - 0.66) / 0.34, 0.0, 1.0) ** 0.80
    prof = horizon - (right * (200 + 130 * fbm1d(u * 4.4, seed + 203)) + 6) * s
    m, t = forest(prof, 0.024, 0.06, 118 * s, 0.13, seed + 303, right)
    m = m * (right > 0.004)[None, :]
    img = img * (1 - m) + t * m

    # ---- mist lying on the water ------------------------------------------
    band = np.exp(-((yy - horizon) / (horizon * 0.075)) ** 2)
    drift = fbm2d(xx / W * 4.0, yy / horizon * 14.0, seed + 401, octaves=4)
    mist = np.clip(band * (0.25 + 0.95 * drift), 0.0, 1.0) * 0.62
    img = img * (1 - mist) + 0.36 * mist

    # ---- lake: darkened, rippled mirror ------------------------------------
    lake_h = H - horizon
    ly, lx = np.mgrid[0:lake_h, 0:W].astype(np.float64)
    t = ly / lake_h                                    # 0 at waterline
    src_y = horizon - 1 - ly * 0.92
    ripple = (fbm2d(lx / W * 9.0, ly / lake_h * 70.0, seed + 501, octaves=3) - 0.5)
    src_x = lx + ripple * (10.0 + 95.0 * t) * s
    src_y = src_y + ripple * (2.0 + 20.0 * t) * s
    sy = np.clip(src_y, 0, horizon - 1).astype(np.int64)
    sx = np.clip(src_x, 0, W - 1).astype(np.int64)
    lake = img[sy, sx]
    lake = lake * (0.74 - 0.54 * t**0.75) + 0.008
    # long horizontal glints
    glint = fbm2d(lx / W * 2.2, ly / lake_h * 120.0, seed + 601, octaves=3)
    lake += np.clip(glint - 0.63, 0.0, 1.0) * 0.20 * (1.0 - t) ** 2
    # mist continues a little way over the water
    band2 = np.exp(-(ly / (horizon * 0.055)) ** 2)
    drift2 = fbm2d(lx / W * 4.0, ly / lake_h * 9.0, seed + 402, octaves=4)
    mist2 = np.clip(band2 * (0.25 + 0.95 * drift2), 0.0, 1.0) * 0.55
    lake = lake * (1 - mist2) + 0.33 * mist2

    full = np.vstack([img, lake])

    # soften the reflection horizontally (water is never a perfect mirror)
    pil = Image.fromarray(np.uint8(np.clip(full, 0, 1) * 255), "L")
    low = pil.crop((0, horizon, W, H)).resize((max(1, W // 3), lake_h), Image.BILINEAR)
    low = low.resize((W, lake_h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2 * s))
    pil.paste(low, (0, horizon))
    full = np.asarray(pil, dtype=np.float64) / 255.0

    # ---- grade: vignette, darker top for the panel, fine grain ------------
    gy, gx = np.mgrid[0:H, 0:W].astype(np.float64)
    r2 = ((gx / W - 0.5) / 0.78) ** 2 + ((gy / H - 0.52) / 0.80) ** 2
    full *= np.clip(1.05 - 0.55 * r2, 0.30, 1.0)
    full *= 0.82 + 0.18 * np.clip(gy / (H * 0.16), 0.0, 1.0)
    full = np.clip(full, 0, 1) ** 0.94
    grain = np.random.default_rng(seed + 900).normal(0.0, 0.010, (H, W))
    full = np.clip(full + grain, 0.0, 1.0)

    # barely-there cool tint so it sits well with the sage accent colour
    rgb = np.stack([full * 0.965, full * 1.0, full * 0.985], axis=-1)
    return Image.fromarray(np.uint8(np.clip(rgb, 0, 1) * 255), "RGB")


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    seed = 7
    if "--seed" in argv:
        seed = int(argv[argv.index("--seed") + 1])
        args = [a for a in args if a != str(seed)]
    out = args[0] if args else "ultron-still-water.jpg"
    w = int(args[1]) if len(args) > 2 else 3840
    h = int(args[2]) if len(args) > 2 else 2160
    render(w, h, seed).save(out, quality=92, optimize=True)
    print(f"wrote {out} ({w}x{h}, seed {seed})")


if __name__ == "__main__":
    main(sys.argv)
