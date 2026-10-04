"""Generate a 16-bit pixel art basketball slam dunk animation with theme integration."""

import io
from pathlib import Path

WIDTH = 110
HEIGHT = 55
SCALE = 3
FLOOR_Y = 46
HOOP_X = 90
RIM_Y = 20

DURATIONS = [120, 110, 110, 100, 100, 110, 180, 160, 100, 100, 110, 120, 110, 110]


def hex_to_rgba(hex_color, alpha=255):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def render_gif(theme):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        cached = Path(__file__).resolve().parents[1] / "assets/basketball.gif"
        if cached.is_file():
            return cached.read_bytes()
        raise RuntimeError("Pillow is required to generate the basketball animation GIF.")

    accent = hex_to_rgba(theme.get("accent", "#088DDC"))
    hoodie = (35, 45, 60, 255)
    shorts = (20, 25, 32, 255)
    skin = (225, 175, 130, 255)
    sneaker_white = (240, 240, 245, 255)
    ball_main = (235, 105, 30, 255)
    ball_shade = (195, 75, 20, 255)
    ball_line = (40, 20, 10, 255)
    rim_orange = (245, 90, 30, 255)
    net_white = (220, 225, 230, 230)
    backboard = (180, 190, 205, 220)
    pole = (70, 80, 95, 255)

    def draw_hoop(draw, rim_offset=0, net_swish=0):
        draw.rectangle([HOOP_X + 12, RIM_Y - 14, HOOP_X + 15, FLOOR_Y + 4], fill=pole)
        draw.line([HOOP_X + 12, RIM_Y - 6, HOOP_X + 2, RIM_Y], fill=pole, width=2)
        draw.rectangle([HOOP_X + 6, RIM_Y - 16, HOOP_X + 8, RIM_Y + 8], fill=backboard)
        draw.rectangle([HOOP_X + 6, RIM_Y - 10, HOOP_X + 8, RIM_Y - 2], fill=(240, 80, 60, 255))
        ry = RIM_Y + rim_offset
        draw.rectangle([HOOP_X - 10, ry, HOOP_X + 6, ry + 1], fill=rim_orange)
        net_x1 = HOOP_X - 9
        net_x2 = HOOP_X + 5
        if net_swish == 0:
            draw.line([net_x1, ry + 2, net_x1 + 3, ry + 9], fill=net_white)
            draw.line([net_x2, ry + 2, net_x2 - 3, ry + 9], fill=net_white)
            draw.line([net_x1 + 3, ry + 9, net_x2 - 3, ry + 9], fill=net_white)
            draw.line([net_x1 + 4, ry + 2, net_x1 + 4, ry + 9], fill=net_white)
            draw.line([net_x2 - 4, ry + 2, net_x2 - 4, ry + 9], fill=net_white)
        elif net_swish == 1:
            draw.line([net_x1, ry + 2, net_x1 - 2, ry + 10], fill=net_white)
            draw.line([net_x2, ry + 2, net_x2 + 3, ry + 10], fill=net_white)
            draw.line([net_x1 - 2, ry + 10, net_x2 + 3, ry + 10], fill=net_white)
        elif net_swish == 2:
            draw.line([net_x1, ry + 2, net_x1 + 2, ry + 11], fill=net_white)
            draw.line([net_x2, ry + 2, net_x2 - 1, ry + 11], fill=net_white)
            draw.line([net_x1 + 2, ry + 11, net_x2 - 1, ry + 11], fill=net_white)

    def draw_ball(draw, bx, by):
        draw.ellipse([bx, by, bx + 5, by + 5], fill=ball_main)
        draw.point([bx + 1, by + 4], fill=ball_shade)
        draw.point([bx + 2, by + 4], fill=ball_shade)
        draw.point([bx + 3, by + 4], fill=ball_shade)
        draw.line([bx + 1, by + 2, bx + 4, by + 2], fill=ball_line)
        draw.line([bx + 2, by + 1, bx + 2, by + 4], fill=ball_line)

    def draw_shadow(draw, px, width=10, alpha=90):
        draw.ellipse([px - width // 2, FLOOR_Y, px + width // 2, FLOOR_Y + 3], fill=(10, 15, 20, alpha))

    def draw_player(draw, px, py, pose):
        draw.rectangle([px, py, px + 7, py + 7], fill=hoodie)
        draw.rectangle([px + 3, py + 2, px + 6, py + 5], fill=skin)
        draw.rectangle([px + 4, py + 2, px + 6, py + 3], fill=(30, 30, 35, 255))
        draw.point([px + 3, py + 7], fill=accent)
        draw.point([px + 4, py + 7], fill=accent)
        draw.rectangle([px - 1, py + 8, px + 7, py + 15], fill=hoodie)
        draw.rectangle([px + 1, py + 12, px + 6, py + 14], fill=(25, 32, 45, 255))
        draw.point([px - 1, py + 9], fill=accent)
        draw.point([px + 7, py + 9], fill=accent)

        if pose in ("dribble_high", "reset_step"):
            draw.line([px + 6, py + 9, px + 9, py + 13], fill=hoodie)
            draw.rectangle([px + 9, py + 13, px + 10, py + 14], fill=skin)
            draw.line([px - 1, py + 9, px - 3, py + 12], fill=hoodie)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.rectangle([px + 1, py + 20, px + 2, py + 22], fill=skin)
            draw.rectangle([px + 4, py + 20, px + 5, py + 22], fill=skin)
            draw.rectangle([px, py + 22, px + 3, py + 24], fill=sneaker_white)
            draw.rectangle([px + 4, py + 22, px + 7, py + 24], fill=sneaker_white)
            draw.point([px + 2, py + 23], fill=accent)
            draw.point([px + 6, py + 23], fill=accent)

        elif pose == "dribble_low":
            draw.line([px + 6, py + 10, px + 10, py + 16], fill=hoodie)
            draw.rectangle([px + 9, py + 16, px + 11, py + 17], fill=skin)
            draw.rectangle([px, py + 16, px + 7, py + 19], fill=shorts)
            draw.rectangle([px - 1, py + 20, px + 1, py + 22], fill=skin)
            draw.rectangle([px + 5, py + 20, px + 7, py + 22], fill=skin)
            draw.rectangle([px - 2, py + 22, px + 1, py + 24], fill=sneaker_white)
            draw.rectangle([px + 5, py + 22, px + 8, py + 24], fill=sneaker_white)
            draw.point([px, py + 23], fill=accent)
            draw.point([px + 7, py + 23], fill=accent)

        elif pose == "gather":
            draw.line([px + 6, py + 9, px + 8, py + 11], fill=hoodie)
            draw.rectangle([px + 8, py + 10, px + 10, py + 12], fill=skin)
            draw.rectangle([px, py + 16, px + 7, py + 19], fill=shorts)
            draw.rectangle([px, py + 20, px + 2, py + 22], fill=skin)
            draw.rectangle([px + 5, py + 20, px + 7, py + 22], fill=skin)
            draw.rectangle([px - 1, py + 22, px + 2, py + 24], fill=sneaker_white)
            draw.rectangle([px + 5, py + 22, px + 8, py + 24], fill=sneaker_white)

        elif pose == "jump_takeoff":
            draw.line([px + 6, py + 8, px + 8, py + 4], fill=hoodie)
            draw.rectangle([px + 7, py + 3, px + 9, py + 5], fill=skin)
            draw.line([px - 1, py + 9, px - 4, py + 12], fill=hoodie)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.line([px + 1, py + 20, px - 2, py + 23], fill=skin)
            draw.line([px + 4, py + 20, px + 2, py + 24], fill=skin)
            draw.rectangle([px - 3, py + 23, px - 1, py + 25], fill=sneaker_white)
            draw.rectangle([px + 1, py + 24, px + 3, py + 26], fill=sneaker_white)

        elif pose == "jump_glide":
            draw.line([px + 6, py + 7, px + 9, py + 1], fill=hoodie)
            draw.rectangle([px + 8, py, px + 10, py + 2], fill=skin)
            draw.line([px - 1, py + 9, px - 4, py + 13], fill=hoodie)
            draw.rectangle([px - 1, py + 16, px + 5, py + 19], fill=shorts)
            draw.line([px - 1, py + 20, px - 5, py + 24], fill=skin)
            draw.line([px + 2, py + 20, px - 2, py + 25], fill=skin)
            draw.rectangle([px - 6, py + 24, px - 4, py + 26], fill=sneaker_white)
            draw.rectangle([px - 3, py + 25, px - 1, py + 27], fill=sneaker_white)

        elif pose == "jump_apex":
            draw.line([px + 6, py + 6, px + 9, py - 2], fill=hoodie)
            draw.rectangle([px + 8, py - 3, px + 10, py - 1], fill=skin)
            draw.line([px - 1, py + 8, px - 3, py + 12], fill=hoodie)
            draw.rectangle([px - 1, py + 16, px + 5, py + 19], fill=shorts)
            draw.line([px, py + 20, px - 4, py + 24], fill=skin)
            draw.line([px + 3, py + 20, px - 1, py + 25], fill=skin)
            draw.rectangle([px - 5, py + 24, px - 3, py + 26], fill=sneaker_white)
            draw.rectangle([px - 2, py + 25, px, py + 27], fill=sneaker_white)

        elif pose == "slam_dunk":
            draw.line([px + 6, py + 6, px + 13, py + 6], fill=hoodie)
            draw.rectangle([px + 13, py + 5, px + 15, py + 7], fill=skin)
            draw.line([px - 1, py + 8, px - 4, py + 11], fill=hoodie)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.line([px + 1, py + 20, px + 2, py + 24], fill=skin)
            draw.line([px + 4, py + 20, px + 6, py + 24], fill=skin)
            draw.rectangle([px + 1, py + 24, px + 4, py + 26], fill=sneaker_white)
            draw.rectangle([px + 5, py + 24, px + 8, py + 26], fill=sneaker_white)

        elif pose == "hang_rim":
            draw.line([px + 6, py + 4, px + 11, py + 4], fill=hoodie)
            draw.rectangle([px + 11, py + 3, px + 13, py + 5], fill=skin)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.line([px + 1, py + 20, px + 2, py + 24], fill=skin)
            draw.line([px + 4, py + 20, px + 5, py + 24], fill=skin)
            draw.rectangle([px + 1, py + 24, px + 4, py + 26], fill=sneaker_white)
            draw.rectangle([px + 4, py + 24, px + 7, py + 26], fill=sneaker_white)

        elif pose == "drop_release":
            draw.line([px + 6, py + 8, px + 10, py + 12], fill=hoodie)
            draw.line([px - 1, py + 8, px - 5, py + 12], fill=hoodie)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.line([px + 1, py + 20, px + 1, py + 25], fill=skin)
            draw.line([px + 4, py + 20, px + 4, py + 25], fill=skin)
            draw.rectangle([px, py + 25, px + 3, py + 27], fill=sneaker_white)
            draw.rectangle([px + 3, py + 25, px + 6, py + 27], fill=sneaker_white)

        elif pose == "falling":
            draw.line([px + 6, py + 8, px + 9, py + 12], fill=hoodie)
            draw.line([px - 1, py + 8, px - 4, py + 12], fill=hoodie)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.line([px + 1, py + 20, px + 2, py + 24], fill=skin)
            draw.line([px + 4, py + 20, px + 5, py + 24], fill=skin)
            draw.rectangle([px + 1, py + 24, px + 4, py + 26], fill=sneaker_white)
            draw.rectangle([px + 4, py + 24, px + 7, py + 26], fill=sneaker_white)

        elif pose == "landing":
            draw.line([px + 6, py + 9, px + 8, py + 14], fill=hoodie)
            draw.line([px - 1, py + 9, px - 3, py + 14], fill=hoodie)
            draw.rectangle([px - 1, py + 16, px + 7, py + 19], fill=shorts)
            draw.rectangle([px - 1, py + 20, px + 1, py + 22], fill=skin)
            draw.rectangle([px + 5, py + 20, px + 7, py + 22], fill=skin)
            draw.rectangle([px - 2, py + 22, px + 1, py + 24], fill=sneaker_white)
            draw.rectangle([px + 5, py + 22, px + 8, py + 24], fill=sneaker_white)

        elif pose == "land_catch":
            draw.line([px + 6, py + 8, px + 10, py + 11], fill=hoodie)
            draw.rectangle([px + 9, py + 10, px + 11, py + 12], fill=skin)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.rectangle([px + 1, py + 20, px + 2, py + 22], fill=skin)
            draw.rectangle([px + 4, py + 20, px + 5, py + 22], fill=skin)
            draw.rectangle([px, py + 22, px + 3, py + 24], fill=sneaker_white)
            draw.rectangle([px + 4, py + 22, px + 7, py + 24], fill=sneaker_white)

        elif pose == "dribble_cross":
            draw.line([px + 6, py + 8, px + 4, py + 14], fill=hoodie)
            draw.line([px - 1, py + 8, px - 3, py + 13], fill=hoodie)
            draw.rectangle([px, py + 16, px + 6, py + 19], fill=shorts)
            draw.rectangle([px + 1, py + 20, px + 2, py + 22], fill=skin)
            draw.rectangle([px + 4, py + 20, px + 5, py + 22], fill=skin)
            draw.rectangle([px, py + 22, px + 3, py + 24], fill=sneaker_white)
            draw.rectangle([px + 4, py + 22, px + 7, py + 24], fill=sneaker_white)

    keyframes_data = [
        (18, 25, "dribble_high", 26, 38, 0, 0, 12, 100),
        (24, 26, "dribble_low", 28, 43, 0, 0, 13, 100),
        (30, 27, "gather", 33, 33, 0, 0, 14, 110),
        (38, 21, "jump_takeoff", 39, 21, 0, 0, 12, 80),
        (48, 14, "jump_glide", 51, 10, 0, 0, 10, 60),
        (58, 8,  "jump_apex", 63, 4, 0, 0, 8, 45),
        (68, 8,  "slam_dunk", 82, 18, 2, 1, 8, 40),
        (72, 11, "hang_rim", 83, 23, 1, 2, 9, 50),
        (70, 16, "drop_release", 83, 32, 0, 0, 10, 60),
        (66, 23, "falling", 83, 42, 0, 0, 12, 80),
        (62, 26, "landing", 80, 36, 0, 0, 14, 110),
        (54, 25, "land_catch", 64, 30, 0, 0, 13, 100),
        (42, 25, "dribble_cross", 38, 38, 0, 0, 12, 100),
        (28, 25, "reset_step", 24, 40, 0, 0, 12, 100),
    ]

    frames = []
    for px, py, pose, bx, by, rim_off, swish, sh_w, sh_a in keyframes_data:
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for cx in range(0, WIDTH, 4):
            draw.point([cx, FLOOR_Y + 1], fill=(50, 60, 75, 120))
        draw_hoop(draw, rim_off, swish)
        draw_shadow(draw, px + 3, sh_w, sh_a)
        draw_player(draw, px, py, pose)
        draw_ball(draw, bx, by)
        scaled = img.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.NEAREST)
        frames.append(scaled)

    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=DURATIONS,
        loop=0,
        disposal=2,
        transparency=0,
        optimize=False
    )
    return buffer.getvalue()
