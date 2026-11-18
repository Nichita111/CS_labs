"""Renders the images for the report from real runs of main.py (Windows; needs Pillow).

    python scripts/render_screenshots.py              # every scenario
    python scripts/render_screenshots.py 01_manual    # only some of them

For every file in scripts/scenarios/ the program is run with those lines as
keyboard input, each one typed at the next prompt. The output, colours
included, is captured exactly as the program prints it, and drawn as a
terminal window into images/<scenario>.png. Option 2 uses random data, so
the random generator is seeded to make the images reproducible.
"""

import builtins
import io
import random
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from PIL import Image, ImageDraw, ImageFont

LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR))
import main  # noqa: E402  (needs the path above)

SEED = 19
FONT_SIZE = 17
FONTS = "C:/Windows/Fonts/"
FONT = ImageFont.truetype(FONTS + "consola.ttf", FONT_SIZE)
BOLD = ImageFont.truetype(FONTS + "consolab.ttf", FONT_SIZE)
SYMBOLS = ImageFont.truetype(FONTS + "seguisym.ttf", FONT_SIZE + 1)
NOT_IN_FONT = set("✗✓⊕")  # drawn with Segoe UI Symbol instead of Consolas

# Windows Terminal's "Campbell" colour scheme.
BACKGROUND = (12, 12, 12)
TITLE_BAR = (32, 32, 32)
FOREGROUND = (204, 204, 204)
DIM = (118, 118, 118)
COLOURS = {"31": (231, 72, 86), "32": (22, 198, 12), "36": (58, 150, 221)}

CELL_W = round(FONT.getlength("M"))
CELL_H = FONT_SIZE + 6
PAD = 16
TITLE_H = 34
ANSI = re.compile(r"\x1b\[([0-9;]*)m")


def record(inputs):
    """Run the program on the inputs; return what the terminal shows, ANSI codes included."""
    output = io.StringIO()
    lines = iter(inputs)

    def typed(prompt=""):
        line = next(lines)
        print(prompt + line)  # a terminal echoes what is typed after the prompt
        return line

    random.seed(SEED)
    with mock.patch.object(main, "USE_COLOR", True), \
            mock.patch.object(builtins, "input", typed), redirect_stdout(output):
        main.main()
    return output.getvalue()


def spans(line):
    """Split a line into (text, colour, bold) pieces following its ANSI codes."""
    colour, bold, position = FOREGROUND, False, 0
    for match in ANSI.finditer(line):
        if match.start() > position:
            yield line[position:match.start()], colour, bold
        for code in (match.group(1) or "0").split(";"):
            if code == "0":
                colour, bold = FOREGROUND, False
            elif code == "1":
                bold = True
            elif code == "2":
                colour = DIM
            elif code in COLOURS:
                colour = COLOURS[code]
        position = match.end()
    if position < len(line):
        yield line[position:], colour, bold


def render(text, title, target):
    lines = text.rstrip("\n").split("\n")
    lines = lines[:-1]  # "bye": the image shows the session up to the last prompt
    columns = max(len(ANSI.sub("", line)) for line in lines) + 2
    width = PAD * 2 + columns * CELL_W
    height = TITLE_H + PAD * 2 + len(lines) * CELL_H
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, TITLE_H), fill=TITLE_BAR)
    for i, dot in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        draw.ellipse((14 + i * 20, 12, 26 + i * 20, 24), fill=dot)
    draw.text((width // 2, TITLE_H // 2), title, font=FONT, fill=DIM, anchor="mm")
    for row, line in enumerate(lines):
        y = TITLE_H + PAD + row * CELL_H
        column = 0
        for piece, colour, bold in spans(line):
            for char in piece:
                x = PAD + column * CELL_W
                if char in NOT_IN_FONT:
                    draw.text((x + CELL_W / 2, y + CELL_H / 2 - 3), char, font=SYMBOLS, fill=colour, anchor="mm")
                else:
                    draw.text((x, y), char, font=BOLD if bold else FONT, fill=colour)
                column += 1
    image.save(target)


def main_script():
    names = sys.argv[1:] or sorted(p.stem for p in (LAB_DIR / "scripts" / "scenarios").glob("*.txt"))
    (LAB_DIR / "images").mkdir(exist_ok=True)
    for name in names:
        scenario = LAB_DIR / "scripts" / "scenarios" / f"{name}.txt"
        inputs = scenario.read_text(encoding="utf-8").rstrip("\n").split("\n")
        target = LAB_DIR / "images" / f"{name}.png"
        render(record(inputs), "lab4 · python main.py", target)
        print(f"images/{name}.png")


if __name__ == "__main__":
    main_script()
