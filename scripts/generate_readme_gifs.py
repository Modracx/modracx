from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def font(paths, size):
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


SANS = font(
    [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ],
    16,
)
SERIF = font(
    [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
    ],
    22,
)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(value, low, high):
    return max(low, min(high, value))


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    a = hex_to_rgb(c1)
    b = hex_to_rgb(c2)
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))


def vertical_gradient(width, height, top, bottom):
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(height):
        t = y / max(1, height - 1)
        color = mix(top, bottom, t)
        draw.line((0, y, width, y), fill=(*color, 255))
    return img


def blur(base, radius):
    return base.filter(ImageFilter.GaussianBlur(radius))


def add_glow(base, center, radius, color):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow, "RGBA")
    cx, cy = center
    for r in range(radius, 0, -8):
        alpha = int(color[3] * ((r / radius) ** 2))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(color[0], color[1], color[2], alpha))
    return Image.alpha_composite(base, glow)


def add_grain(base, amount=10):
    noise = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(noise, "RGBA")
    width, height = base.size
    for y in range(0, height, 3):
        for x in range((y // 3) % 4, width, 5):
            alpha = amount if (x + y) % 2 == 0 else amount // 2
            draw.point((x, y), fill=(255, 255, 255, alpha))
    return Image.alpha_composite(base, noise)


def add_vignette(base, strength=110):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    w, h = base.size
    max_inset = min(w, h) // 2 - 18
    for inset in range(0, max_inset, 8):
        alpha = int(strength * (1 - inset / 180))
        draw.rounded_rectangle((inset, inset, w - inset, h - inset), radius=28, outline=(0, 0, 0, alpha), width=16)
    return Image.alpha_composite(base, blur(layer, 14))


def eased(t):
    return 0.5 - 0.5 * cos(pi * t)


def draw_starfield(draw, t, stars):
    for idx, (x, y, size) in enumerate(stars):
        twinkle = 150 + int(90 * (0.5 + 0.5 * sin(t * 2 * pi + idx * 0.7)))
        draw.ellipse((x - size, y - size, x + size, y + size), fill=(255, 244, 218, twinkle))


def draw_haze(base, bands):
    haze = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(haze, "RGBA")
    for y, h, color in bands:
        draw.rectangle((0, y, base.size[0], y + h), fill=color)
    return Image.alpha_composite(base, blur(haze, 16))


def draw_person(draw, x, y, scale=1.0, coat=(10, 15, 25, 255), rim=(232, 240, 255, 220), facing="right", arm_lift=0.0):
    head_r = 10 * scale
    draw.ellipse((x - head_r, y - 56 * scale, x + head_r, y - 34 * scale), fill=coat, outline=rim, width=1)
    if facing == "right":
        hair = [(x - 8 * scale, y - 54 * scale), (x + 10 * scale, y - 52 * scale), (x + 13 * scale, y - 36 * scale), (x - 5 * scale, y - 30 * scale)]
    else:
        hair = [(x - 11 * scale, y - 36 * scale), (x - 8 * scale, y - 54 * scale), (x + 9 * scale, y - 52 * scale), (x + 6 * scale, y - 30 * scale)]
    draw.polygon(hair, fill=coat)
    torso = [(x - 9 * scale, y - 30 * scale), (x + 9 * scale, y - 30 * scale), (x + 12 * scale, y + 6 * scale), (x - 13 * scale, y + 8 * scale)]
    skirt = [(x - 13 * scale, y + 4 * scale), (x + 12 * scale, y + 4 * scale), (x + 21 * scale, y + 36 * scale), (x - 18 * scale, y + 36 * scale)]
    draw.polygon(torso, fill=coat, outline=rim)
    draw.polygon(skirt, fill=coat, outline=rim)
    left_arm_y = y - 10 * scale - arm_lift * 12 * scale
    right_arm_y = y - 6 * scale + arm_lift * 8 * scale
    draw.line((x - 8 * scale, y - 12 * scale, x - 24 * scale, left_arm_y), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x + 8 * scale, y - 12 * scale, x + 22 * scale, right_arm_y), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x - 7 * scale, y + 36 * scale, x - 14 * scale, y + 64 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x + 7 * scale, y + 36 * scale, x + 14 * scale, y + 66 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x - 2 * scale, y - 16 * scale, x - 2 * scale, y + 24 * scale), fill=(255, 236, 210, 58), width=max(1, int(scale)))


def draw_signal_arcs(draw, cx, cy, t, palette):
    for idx, ring in enumerate((34, 62, 96, 136)):
        alpha = 160 - idx * 28
        sweep = 90 + idx * 10
        start = 210 + int(8 * sin(t * 2 * pi + idx))
        end = start + sweep
        draw.arc((cx - ring, cy - ring, cx + ring, cy + ring), start, end, fill=(*palette, alpha), width=2)


def title_overlay(base, line1, line2):
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.text((40, 26), line1, font=SERIF, fill=(247, 244, 238, 210))
    draw.text((42, 58), line2, font=SANS, fill=(228, 233, 242, 150))
    return Image.alpha_composite(base, blur(overlay, 0))


def scene_1_mapping(t):
    img = vertical_gradient(900, 320, "#0c1733", "#e58b6b")
    img = draw_haze(img, [(0, 92, (22, 28, 50, 90)), (118, 58, (255, 211, 188, 28))])
    img = add_glow(img, (708, 86), 160, (255, 209, 156, 120))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_starfield(draw, t, [(84, 40, 2), (164, 72, 1), (244, 42, 2), (388, 68, 1), (530, 52, 2), (680, 74, 1), (790, 44, 2)])

    for offset, alpha in ((0, 215), (38, 190), (84, 160)):
        draw.ellipse((110 + offset, 68, 188 + offset, 110), fill=(255, 217, 182, alpha))
        draw.ellipse((132 + offset, 52, 208 + offset, 96), fill=(255, 217, 182, alpha))

    mountain_back = [(0, 214), (180, 190), (426, 212), (714, 176), (900, 196), (900, 232), (0, 232)]
    mountain_mid = [(0, 246), (196, 214), (442, 244), (684, 198), (900, 230), (900, 320), (0, 320)]
    draw.polygon(mountain_back, fill=(84, 92, 122, 86))
    draw.polygon(mountain_mid, fill="#121d2c")
    draw.polygon([(0, 232), (210, 208), (418, 232), (690, 192), (900, 222), (900, 248), (0, 248)], fill="#1d2a42")
    for px in (132, 324, 608, 794):
        draw.line((px, 142, px, 320), fill=(22, 26, 36, 228), width=4)
    for offset in (0, 26, 52):
        draw.line((0, 184 + offset, 900, 158 + offset), fill=(32, 38, 58, 160), width=2)

    nebula = Image.new("RGBA", img.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula, "RGBA")
    for r in range(170, 26, -10):
        nd.ellipse((560 - r, 96 - r, 560 + r, 96 + r), fill=(250, 194, 144, int(28 * (r / 170))))
    for r in range(122, 20, -8):
        nd.ellipse((654 - r, 58 - r, 654 + r, 58 + r), fill=(238, 160, 182, int(20 * (r / 122))))
    img = Image.alpha_composite(img, blur(nebula, 12))
    draw = ImageDraw.Draw(img, "RGBA")

    constellation = [(182, 92), (238, 74), (304, 102), (356, 84), (420, 118), (522, 170), (620, 186), (690, 196)]
    for point in constellation:
        draw.ellipse((point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2), fill=(255, 245, 218, 224))
    for p1, p2 in zip(constellation, constellation[1:]):
        draw.line((p1[0], p1[1], p2[0], p2[1]), fill=(255, 244, 214, 142), width=1)

    draw_person(draw, 710, 244 + 2 * sin(t * 2 * pi), 1.18, facing="left", arm_lift=0.2)
    draw.arc((516, 92, 584, 146), 208, 342, fill=(255, 235, 204, 188), width=2)
    draw.arc((528, 98, 594, 152), 208, 342, fill=(255, 235, 204, 112), width=1)
    draw.line((688, 188, 546, 120), fill=(255, 236, 208, 112), width=1)
    img = title_overlay(img, "Seren mapped what had not yet been reached.", "The map existed before the journey.")
    return add_vignette(add_grain(img, 7), 92)


def scene_2_signal(t):
    img = vertical_gradient(900, 320, "#1a2745", "#0a111b")
    img = add_glow(img, (452, 162), 220, (94, 142, 255, 52))
    draw = ImageDraw.Draw(img, "RGBA")
    for x in range(0, 900, 58):
        h = 86 + ((x // 30) % 5) * 24
        draw.rectangle((x, 320 - h, x + 42, 320), fill=(12, 18, 30, 250))
        for wx in range(x + 8, x + 35, 10):
            for wy in range(320 - h + 12, 316, 17):
                if (wx + wy + x) % 3 == 0:
                    draw.rectangle((wx, wy, wx + 3, wy + 6), fill=(255, 210, 132, 164))

    draw.rectangle((84, 28, 820, 282), outline=(212, 226, 255, 168), width=3)
    draw.rectangle((98, 42, 806, 268), outline=(212, 226, 255, 74), width=1)
    draw.line((452, 28, 452, 282), fill=(212, 226, 255, 166), width=3)

    rain = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain, "RGBA")
    for i in range(40):
        x = 110 + i * 18 + int(10 * sin(t * 2 * pi + i * 0.4))
        rd.line((x, 48, x - 24, 260), fill=(190, 214, 255, 74), width=1)
    img = Image.alpha_composite(img, blur(rain, 1))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_signal_arcs(draw, 538, 158, t, (120, 178, 255))
    for idx in range(6):
        y = 150 + idx * 11
        length = 100 + idx * 22 + int(7 * sin(t * 2 * pi + idx))
        draw.line((538 - length, y, 538 + length, y), fill=(102, 162, 255, 54 - idx * 7), width=1)

    draw_person(draw, 270, 238, 1.1, facing="right", arm_lift=0.28)
    draw.line((292, 186, 484, 160), fill=(118, 176, 255, 120), width=1)
    img = title_overlay(img, "Eli listened for pattern inside the static.", "Noise leaned toward music.")
    return add_vignette(add_grain(img, 6), 98)


def scene_3_meeting(t):
    img = vertical_gradient(900, 320, "#101c36", "#f08e72")
    img = draw_haze(img, [(0, 76, (26, 32, 54, 90)), (108, 70, (255, 220, 196, 30))])
    img = add_glow(img, (454, 124), 160, (255, 214, 170, 108))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_starfield(draw, t * 0.7, [(90, 42, 2), (184, 56, 1), (320, 42, 1), (570, 52, 2), (742, 48, 1)])

    draw.polygon([(0, 252), (170, 216), (362, 238), (540, 206), (732, 236), (900, 224), (900, 320), (0, 320)], fill="#121b29")
    draw.polygon([(0, 226), (160, 196), (350, 214), (536, 184), (736, 212), (900, 198), (900, 228), (0, 228)], fill="#2a3b56")
    draw.polygon([(0, 204), (160, 184), (348, 202), (536, 174), (742, 204), (900, 190), (900, 210), (0, 210)], fill=(92, 103, 132, 62))
    draw.line((0, 214, 424, 206), fill=(255, 226, 198, 36), width=1)
    draw.line((472, 206, 900, 214), fill=(130, 180, 242, 34), width=1)

    bridge = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bridge, "RGBA")
    bd.rectangle((208, 216, 690, 226), fill=(28, 34, 46, 255))
    bd.line((208, 216, 690, 226), fill=(86, 96, 120, 120), width=1)
    for px in range(230, 690, 26):
        bd.line((px, 226, px - 10, 320), fill=(20, 24, 34, 220), width=2)
    img = Image.alpha_composite(img, blur(bridge, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    reach = eased(t)
    left_x = int(324 + 34 * reach)
    right_x = int(578 - 34 * reach)
    draw_person(draw, left_x, 240, 1.14, facing="right", arm_lift=0.65)
    draw_person(draw, right_x, 240, 1.14, facing="left", arm_lift=0.65)
    draw.line((left_x + 18, 194, 450, 174), fill=(255, 232, 196, 80), width=1)
    draw.line((right_x - 18, 194, 450, 174), fill=(130, 182, 255, 80), width=1)

    spark = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(spark, "RGBA")
    center = (450, 174)
    for r in range(90, 10, -8):
        alpha = int(42 * (r / 90))
        sd.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), fill=(255, 229, 184, alpha))
    for idx in range(16):
        angle = idx / 16 * 2 * pi + t * 0.5
        sx = center[0] + int(cos(angle) * (18 + idx * 4))
        sy = center[1] + int(sin(angle) * (10 + idx * 3))
        sd.ellipse((sx, sy, sx + 3, sy + 3), fill=(255, 244, 214, 140))
    img = Image.alpha_composite(img, blur(spark, 3))
    img = title_overlay(img, "They met at the edge of a dying nebula.", "Both reaching for the same fading light.")
    return add_vignette(add_grain(img, 7), 94)


def scene_4_collapse(t):
    img = vertical_gradient(900, 320, "#0c1527", "#1f2740")
    img = add_glow(img, (450, 160), 170, (255, 214, 152, 74))
    img = add_glow(img, (450, 160), 110, (112, 170, 255, 58))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.polygon([(0, 244), (190, 226), (382, 244), (564, 212), (760, 236), (900, 226), (900, 320), (0, 320)], fill="#101827")
    draw.polygon([(0, 208), (168, 194), (352, 212), (540, 182), (744, 206), (900, 194), (900, 214), (0, 214)], fill="#18253d")

    rings = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rings, "RGBA")
    pulse = 0.5 + 0.5 * sin(t * 2 * pi)
    for idx, width in enumerate((168, 132, 96, 64)):
        scale = width + int(12 * pulse)
        rd.arc((450 - scale, 158 - scale, 450 + scale, 158 + scale), 25, 160, fill=(255, 225, 170, 165 - idx * 24), width=3)
        rd.arc((450 - scale + 8, 158 - scale + 8, 450 + scale - 8, 158 + scale - 8), 204, 338, fill=(120, 180, 255, 148 - idx * 22), width=3)
    img = Image.alpha_composite(img, blur(rings, 1))
    draw = ImageDraw.Draw(img, "RGBA")

    left_x = 352 - int(12 * pulse)
    right_x = 548 + int(12 * pulse)
    draw_person(draw, left_x, 248, 1.14, facing="right", arm_lift=0.2)
    draw_person(draw, right_x, 248, 1.14, facing="left", arm_lift=0.2)
    draw.line((left_x + 20, 196, 450, 158), fill=(255, 230, 194, 98), width=1)
    draw.line((right_x - 20, 196, 450, 158), fill=(120, 180, 255, 98), width=1)

    flare = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(flare, "RGBA")
    fd.polygon([(430, 158), (450, 132), (470, 158), (450, 184)], fill=(255, 240, 212, 120))
    for i in range(24):
        angle = i / 24 * 2 * pi + pulse * 0.6
        sx = 450 + int(cos(angle) * (40 + i * 3))
        sy = 158 + int(sin(angle) * (28 + i * 2))
        fd.ellipse((sx, sy, sx + 4, sy + 4), fill=(255, 240, 212, 110))
    img = Image.alpha_composite(img, blur(flare, 2))
    img = title_overlay(img, "Pressure became fire.", "Revision after revision, the noise became a song.")
    return add_vignette(add_grain(img, 6), 106)


def scene_5_orbit(t):
    img = vertical_gradient(900, 320, "#08111f", "#17315a")
    img = add_glow(img, (450, 112), 200, (126, 180, 255, 84))
    img = add_glow(img, (450, 210), 140, (255, 210, 146, 50))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.polygon([(0, 252), (168, 226), (348, 248), (536, 216), (730, 238), (900, 224), (900, 320), (0, 320)], fill="#101827")
    draw.polygon([(0, 214), (204, 194), (422, 214), (620, 186), (900, 216), (900, 246), (0, 246)], fill=(18, 48, 88, 176))
    for i in range(20):
        y = 210 + i * 2
        draw.line((0, y, 900, y - 4), fill=(242, 230, 198, 16 if i < 7 else 9), width=1)
    for i in range(12):
        y = 218 + i * 4
        draw.line((0, y, 900, y - 8), fill=(132, 178, 236, 24), width=1)

    ring = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring, "RGBA")
    pulse = 0.5 + 0.5 * sin(t * 2 * pi)
    orbit_r = 150 + int(10 * pulse)
    rd.arc((450 - orbit_r, 112 - orbit_r, 450 + orbit_r, 112 + orbit_r), 32, 160, fill=(255, 223, 162, 190), width=3)
    rd.arc((450 - orbit_r + 12, 112 - orbit_r + 12, 450 + orbit_r - 12, 112 + orbit_r - 12), 210, 338, fill=(124, 182, 255, 164), width=3)
    rd.arc((450 - 88, 160 - 88, 450 + 88, 160 + 88), 18, 162, fill=(255, 227, 170, 105), width=2)
    img = Image.alpha_composite(img, blur(ring, 1))
    draw = ImageDraw.Draw(img, "RGBA")

    left_x = 334 - int(6 * sin(t * 2 * pi))
    right_x = 566 + int(6 * sin(t * 2 * pi))
    draw_person(draw, left_x, 248, 1.14, facing="right", arm_lift=0.12)
    draw_person(draw, right_x, 248, 1.14, facing="left", arm_lift=0.12)
    draw.line((left_x + 22, 194, 450, 112), fill=(255, 231, 186, 92), width=1)
    draw.line((right_x - 18, 194, 450, 112), fill=(124, 182, 255, 92), width=1)

    for idx in range(18):
        angle = idx / 18 * 2 * pi + t * 0.32
        sx = 450 + int(cos(angle) * (92 + idx * 5))
        sy = 112 + int(sin(angle) * (44 + idx * 3))
        draw.ellipse((sx, sy, sx + 4, sy + 4), fill=(255, 241, 214, 120))

    img = title_overlay(img, "Two minds in orbit understood at last.", "The best work is only continuously discovered.")
    return add_vignette(add_grain(img, 5), 96)


def crossfade_scenes(sequence, holds=18, fades=10):
    frames = []
    for idx, scene in enumerate(sequence):
        for hold in range(holds):
            t = hold / max(1, holds - 1)
            frames.append(scene(t))
        current = scene(1.0)
        nxt = sequence[(idx + 1) % len(sequence)](0.0)
        for fade in range(1, fades + 1):
            frames.append(Image.blend(current, nxt, fade / (fades + 1)))
    return frames


def save_readme_story():
    scenes = [scene_1_mapping, scene_2_signal, scene_3_meeting, scene_4_collapse, scene_5_orbit]
    frames = crossfade_scenes(scenes, holds=16, fades=8)
    frames[0].save(
        ASSETS / "orbit-two-minds.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[120] * len(frames),
        loop=0,
        disposal=2,
        optimize=True,
    )


if __name__ == "__main__":
    save_readme_story()
