from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG = "#071021"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#ffd966"
ORANGE = "#ff7b00"
BLUE = "#58a6ff"
GREEN = "#3fb950"
WHITE = "#f6f8fa"
AMBER_FILL = "#c8860a"


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
    18,
)
SANS_SMALL = font(
    [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ],
    14,
)
SANS_TINY = font(
    [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ],
    11,
)
TITLE = font(
    [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ],
    24,
)
MONO = font(
    [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ],
    13,
)


def lerp(a, b, t):
    return a + (b - a) * t


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def mix(c1, c2, t):
    a = hex_to_rgb(c1)
    b = hex_to_rgb(c2)
    return rgb_to_hex(tuple(int(lerp(x, y, t)) for x, y in zip(a, b)))


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def vertical_gradient(width, height, top, bottom):
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / max(1, height - 1)
        draw.line((0, y, width, y), fill=mix(top, bottom, t))
    return img


def add_glow(base, center, radius, inner_rgba):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow, "RGBA")
    cx, cy = center
    for r in range(radius, 8, -8):
        t = r / radius
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=(inner_rgba[0], inner_rgba[1], inner_rgba[2], int(inner_rgba[3] * (t**2))),
        )
    return Image.alpha_composite(base, glow)


def softened(base, blur_radius=2):
    return base.filter(ImageFilter.GaussianBlur(blur_radius))


def draw_stars(draw, points, twinkle):
    for idx, (x, y, size) in enumerate(points):
        alpha = 150 + int(90 * (0.5 + 0.5 * sin(twinkle + idx * 0.8)))
        draw.ellipse((x - size, y - size, x + size, y + size), fill=(255, 246, 221, alpha))


def draw_person(draw, x, y, scale=1.0, coat="#09111b", rim="#dce9ff", look="right"):
    head_r = 10 * scale
    draw.ellipse((x - head_r, y - 56 * scale, x + head_r, y - 34 * scale), fill=coat, outline=rim, width=1)
    if look == "right":
        hair = [(x - 8 * scale, y - 54 * scale), (x + 10 * scale, y - 52 * scale), (x + 12 * scale, y - 36 * scale), (x - 6 * scale, y - 30 * scale)]
    else:
        hair = [(x - 10 * scale, y - 52 * scale), (x + 8 * scale, y - 54 * scale), (x + 6 * scale, y - 30 * scale), (x - 12 * scale, y - 36 * scale)]
    draw.polygon(hair, fill=coat)
    torso = [(x - 8 * scale, y - 30 * scale), (x + 8 * scale, y - 30 * scale), (x + 12 * scale, y + 2 * scale), (x - 12 * scale, y + 2 * scale)]
    skirt = [(x - 12 * scale, y + 2 * scale), (x + 12 * scale, y + 2 * scale), (x + 20 * scale, y + 34 * scale), (x - 18 * scale, y + 34 * scale)]
    draw.polygon(torso, fill=coat, outline=rim)
    draw.polygon(skirt, fill=coat, outline=rim)
    draw.line((x - 6 * scale, y + 34 * scale, x - 13 * scale, y + 62 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x + 6 * scale, y + 34 * scale, x + 14 * scale, y + 64 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x - 8 * scale, y - 14 * scale, x - 22 * scale, y - 2 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x + 8 * scale, y - 14 * scale, x + 18 * scale, y - 3 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x - 3 * scale, y - 16 * scale, x - 3 * scale, y + 22 * scale), fill=(255, 241, 214, 70), width=max(1, int(1 * scale)))


def draw_signal_person(draw, x, y, scale=1.0, coat="#08111d", rim="#dce9ff", look="left"):
    head_r = 10 * scale
    draw.ellipse((x - head_r, y - 56 * scale, x + head_r, y - 34 * scale), fill=coat, outline=rim, width=1)
    if look == "left":
        hair = [(x - 12 * scale, y - 38 * scale), (x - 6 * scale, y - 54 * scale), (x + 10 * scale, y - 52 * scale), (x + 4 * scale, y - 32 * scale)]
    else:
        hair = [(x + 12 * scale, y - 38 * scale), (x + 6 * scale, y - 54 * scale), (x - 10 * scale, y - 52 * scale), (x - 4 * scale, y - 32 * scale)]
    draw.polygon(hair, fill=coat)
    torso = [(x - 9 * scale, y - 30 * scale), (x + 9 * scale, y - 30 * scale), (x + 12 * scale, y + 6 * scale), (x - 14 * scale, y + 8 * scale)]
    draw.polygon(torso, fill=coat, outline=rim)
    draw.line((x - 8 * scale, y + 8 * scale, x - 14 * scale, y + 60 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x + 5 * scale, y + 8 * scale, x + 15 * scale, y + 60 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x - 8 * scale, y - 12 * scale, x - 24 * scale, y - 2 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x + 8 * scale, y - 12 * scale, x + 22 * scale, y - 2 * scale), fill=rim, width=max(1, int(2 * scale)))
    draw.line((x + 3 * scale, y - 16 * scale, x + 3 * scale, y + 22 * scale), fill=(182, 216, 255, 65), width=max(1, int(1 * scale)))


def scene_mapping(t):
    img = vertical_gradient(900, 320, "#111a37", "#ec8f70")
    img = add_glow(img, (710, 86), 136, (255, 211, 160, 120))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.polygon([(0, 250), (180, 218), (430, 248), (680, 198), (900, 234), (900, 320), (0, 320)], fill="#111a28")
    draw.polygon([(0, 228), (210, 206), (420, 232), (690, 190), (900, 218), (900, 250), (0, 250)], fill="#1d2a42")

    for px in (132, 322, 606, 794):
        draw.line((px, 142, px, 320), fill=(26, 28, 36, 225), width=4)
    for offset in (0, 26, 52):
        draw.line((0, 184 + offset, 900, 158 + offset), fill=(27, 35, 56, 170), width=2)

    draw_stars(
        draw,
        [(86, 38, 2), (162, 70, 1), (242, 40, 2), (388, 68, 1), (530, 50, 2), (678, 74, 1), (790, 44, 2)],
        t * 2 * pi,
    )

    nebula = Image.new("RGBA", img.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula, "RGBA")
    for r in range(150, 30, -10):
        alpha = int(32 * (r / 150))
        nd.ellipse((560 - r, 92 - r, 560 + r, 92 + r), fill=(255, 199, 146, alpha))
    for r in range(110, 24, -8):
        alpha = int(22 * (r / 110))
        nd.ellipse((650 - r, 56 - r, 650 + r, 56 + r), fill=(245, 164, 182, alpha))
    img = Image.alpha_composite(img, softened(nebula, 10))
    draw = ImageDraw.Draw(img, "RGBA")

    cloud_x = 112 + int(12 * sin(t * 2 * pi))
    for offset, scale, alpha in ((0, 1.0, 215), (38, 0.76, 195), (84, 0.62, 175)):
        draw.ellipse((cloud_x + offset, 70, cloud_x + 70 + offset, 110), fill=(255, 216, 180, alpha))
        draw.ellipse((cloud_x + 22 + offset, 52, cloud_x + 90 + offset, 98), fill=(255, 216, 180, alpha))

    constellation = [(180, 92), (240, 74), (306, 102), (358, 84), (420, 118)]
    for x1, y1 in constellation:
        draw.ellipse((x1 - 2, y1 - 2, x1 + 2, y1 + 2), fill=(255, 244, 210, 230))
    for (x1, y1), (x2, y2) in zip(constellation, constellation[1:]):
        draw.line((x1, y1, x2, y2), fill=(255, 244, 210, 155), width=1)

    draw_person(draw, 710, 242 + 2 * sin(t * 2 * pi), 1.18, "#08111d", "#edf3ff", "left")
    draw.line((682, 188, 546, 120), fill=(255, 238, 210, 130), width=1)
    draw.arc((518, 92, 582, 144), 210, 342, fill=(255, 238, 210, 170), width=2)
    draw.arc((530, 98, 594, 150), 210, 342, fill=(255, 238, 210, 110), width=1)

    return img


def scene_signal(t):
    img = vertical_gradient(900, 320, "#182542", "#0a111b")
    img = add_glow(img, (458, 170), 210, (92, 140, 255, 48))
    draw = ImageDraw.Draw(img, "RGBA")

    for x in range(0, 900, 56):
        height = 78 + ((x // 28) % 5) * 24
        draw.rectangle((x, 320 - height, x + 42, 320), fill=(12, 18, 30, 250))
        for wx in range(x + 7, x + 34, 10):
            for wy in range(320 - height + 12, 314, 16):
                if (wx + wy + x) % 3 == 0:
                    draw.rectangle((wx, wy, wx + 3, wy + 6), fill=(255, 210, 132, 165))

    draw.rectangle((82, 26, 820, 282), outline=(210, 226, 255, 170), width=3)
    draw.rectangle((96, 40, 806, 268), outline=(210, 226, 255, 78), width=1)
    draw.line((452, 26, 452, 282), fill=(210, 226, 255, 170), width=3)

    rain = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain, "RGBA")
    for i in range(34):
        x = 120 + i * 20 + int(8 * sin(t * 2 * pi + i))
        rd.line((x, 48, x - 24, 260), fill=(190, 215, 255, 72), width=1)
    img = Image.alpha_composite(img, softened(rain, 1))
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = 528, 156
    for ring, alpha in ((44, 130), (78, 95), (118, 55)):
        draw.arc((cx - ring, cy - ring, cx + ring, cy + ring), 230, 20, fill=(126, 176, 255, alpha), width=2)

    for j in range(5):
        y = 154 + j * 10
        length = 110 + j * 18 + int(8 * sin(t * 2 * pi + j))
        draw.line((cx - length, y, cx + length, y), fill=(95, 152, 255, 55 - j * 8), width=1)

    draw_signal_person(draw, 270, 236, 1.12, "#09111d", "#edf4ff", "right")
    draw.line((294, 184, 480, 158), fill=(116, 176, 255, 120), width=1)

    return img


def scene_orbit(t):
    img = vertical_gradient(900, 320, "#091221", "#16325b")
    img = add_glow(img, (452, 112), 180, (132, 184, 255, 78))
    img = add_glow(img, (452, 210), 120, (255, 209, 142, 48))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.polygon([(0, 248), (160, 220), (340, 244), (520, 214), (744, 238), (900, 224), (900, 320), (0, 320)], fill="#111827")
    draw.polygon([(0, 268), (184, 244), (376, 268), (548, 236), (744, 260), (900, 248), (900, 320), (0, 320)], fill="#0b1422")

    lake = [(0, 212), (204, 192), (422, 214), (620, 184), (900, 214), (900, 246), (0, 246)]
    draw.polygon(lake, fill=(22, 54, 98, 170))
    for i in range(10):
        y = 214 + i * 4
        draw.line((0, y, 900, y - 8), fill=(130, 178, 238, 26), width=1)

    left_x = 332 - int(6 * sin(t * 2 * pi))
    right_x = 572 + int(6 * sin(t * 2 * pi))
    draw_person(draw, left_x, 246, 1.12, "#09111d", "#edf4ff", "right")
    draw_signal_person(draw, right_x, 246, 1.12, "#09111d", "#edf4ff", "left")

    phase = 0.5 + 0.5 * sin(t * 2 * pi)
    ring_r = 146 + int(10 * phase)
    orbit = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(orbit, "RGBA")
    od.arc((452 - ring_r, 110 - ring_r, 452 + ring_r, 110 + ring_r), 28, 160, fill=(255, 223, 162, 175), width=3)
    od.arc((452 - ring_r + 10, 110 - ring_r + 10, 452 + ring_r - 10, 110 + ring_r - 10), 208, 340, fill=(126, 182, 255, 150), width=3)
    img = Image.alpha_composite(img, softened(orbit, 1))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.line((left_x + 22, 188, 452, 110), fill=(255, 231, 186, 95), width=1)
    draw.line((right_x - 18, 188, 452, 110), fill=(126, 182, 255, 95), width=1)

    for idx in range(12):
        angle = idx / 12 * 2 * pi + t * 0.6
        sx = 452 + int(cos(angle) * (90 + idx * 7))
        sy = 110 + int(sin(angle) * (42 + idx * 3))
        draw.ellipse((sx, sy, sx + 4, sy + 4), fill=(255, 242, 214, 120))

    return img


def crossfade_scenes(sequence, holds=10, fades=6):
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


def save_comic():
    frames = crossfade_scenes([scene_mapping, scene_signal, scene_orbit], holds=10, fades=6)
    frames[0].save(
        ASSETS / "orbit-two-minds.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[150] * len(frames),
        loop=0,
        disposal=2,
        optimize=True,
    )


def chart_background(draw, title):
    draw.text((20, 16), title, font=TITLE, fill=ACCENT)
    left, top, width, height = 36, 48, 352, 100
    for gy in [0, 25, 50, 75, 100]:
        y = top + height - gy
        draw.line((left, y, left + width, y), fill=BORDER, width=1)
    draw.line((left, top, left, top + height), fill=MUTED, width=2)
    draw.line((left, top + height, left + width, top + height), fill=MUTED, width=2)
    return left, top, width, height


def bars_frame(tick):
    img = Image.new("RGBA", (420, 190), BG)
    draw = ImageDraw.Draw(img)
    rounded(draw, (0, 0, 419, 189), 18, BG)
    left, top, _, height = chart_background(draw, "Monthly signups")
    values = [28, 46, 64, 40, 56]
    labels = ["Jan", "Feb", "Mar", "Apr", "May"]
    colors = [ORANGE, ACCENT, "#b7c0cc", "#9aa4b2", BLUE]
    for i, (value, label, color) in enumerate(zip(values, labels, colors)):
        x = left + 24 + i * 64
        phase = (tick / 14 + i * 0.12) % 1.0
        animated = value * (0.76 + 0.24 * sin(phase * 2 * pi))
        bar_h = int(animated)
        rounded(draw, (x, top + height - bar_h, x + 36, top + height), 6, color)
        draw.text((x + 5, top + height + 11), label, font=SANS_SMALL, fill=TEXT)
        draw.text((x + 6, top + height - bar_h - 18), str(value), font=SANS_SMALL, fill=ACCENT)
    draw.text((20, 166), "Steady acquisition across the first five months.", font=SANS_TINY, fill=MUTED)
    return img


def save_bars():
    frames = [bars_frame(i) for i in range(15)]
    frames[0].save(
        ASSETS / "graph1.gif",
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
        disposal=2,
        optimize=True,
    )


def line_frame(tick):
    img = Image.new("RGBA", (420, 190), BG)
    draw = ImageDraw.Draw(img)
    rounded(draw, (0, 0, 419, 189), 18, BG)
    left, top, _, height = chart_background(draw, "Daily active users")
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    base = [32, 56, 48, 62, 54, 76]
    points = []
    for i, value in enumerate(base):
        mod = 6 * sin((tick / 18) * 2 * pi + i * 0.55) + 2 * cos((tick / 18) * 2 * pi + i * 0.8)
        current = max(18, min(90, value + mod))
        x = left + i * 58
        y = top + height - current
        points.append((x, y))
    area = [(points[0][0], top + height)] + points + [(points[-1][0], top + height)]
    draw.polygon(area, fill=AMBER_FILL)
    draw.line(points, fill=BLUE, width=4)
    for i, (x, y) in enumerate(points):
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=ACCENT, outline=WHITE)
        draw.text((x - 12, top + height + 11), labels[i], font=SANS_SMALL, fill=TEXT)
    draw.text((20, 166), "Usage climbs into the weekend with a smooth loop.", font=SANS_TINY, fill=MUTED)
    return img


def save_line():
    frames = [line_frame(i) for i in range(18)]
    frames[0].save(
        ASSETS / "graph2.gif",
        save_all=True,
        append_images=frames[1:],
        duration=95,
        loop=0,
        disposal=2,
        optimize=True,
    )


if __name__ == "__main__":
    save_comic()
    save_bars()
    save_line()
