"""Draw images/frequencies.png: English letter frequencies next to variant 19's."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from attack import read_ciphertext  # noqa: E402
from cryptanalysis import ENGLISH_FREQUENCY, letter_frequencies  # noqa: E402

SURFACE = "#fcfcfb"
BAR = "#2a78d6"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
LABELLED_BARS = 2


def draw_panel(axis, title, rows):
    letters = [letter for letter, _ in rows]
    values = [value for _, value in rows]
    bars = axis.bar(letters, values, width=0.78, color=BAR)
    for bar, value in list(zip(bars, values))[:LABELLED_BARS]:
        axis.annotate(f"{value:.1f}%", (bar.get_x() + bar.get_width() / 2, value),
                      xytext=(0, 4), textcoords="offset points", ha="center",
                      fontsize=10, color=TEXT_PRIMARY)
    axis.set_title(title, loc="left", fontsize=12, color=TEXT_PRIMARY, pad=12)
    axis.set_facecolor(SURFACE)
    axis.grid(axis="y", color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(axis="x", length=0, labelsize=9, labelcolor=TEXT_SECONDARY)
    axis.tick_params(axis="y", length=0, labelsize=9, labelcolor=TEXT_SECONDARY)
    axis.set_xlim(-0.7, 25.7)
    for side in ("top", "right", "left"):
        axis.spines[side].set_visible(False)
    axis.spines["bottom"].set_color(GRID)


def main():
    english = sorted(ENGLISH_FREQUENCY.items(), key=lambda item: -item[1])
    cipher = [(letter, percent) for letter, _, percent in letter_frequencies(read_ciphertext())]

    figure, axes = plt.subplots(2, 1, figsize=(8.5, 5.4), sharey=True, facecolor=SURFACE)
    draw_panel(axes[0], "English plaintext letters (Table 2.2 of the lab)", english)
    draw_panel(axes[1], "Ciphertext letters in variant 19", cipher)
    axes[0].set_ylim(0, 15)
    axes[0].set_yticks([0, 5, 10, 15])
    for axis in axes:
        axis.set_ylabel("Share of letters, %", fontsize=9, color=TEXT_SECONDARY)
    figure.tight_layout(h_pad=2)

    target = Path(__file__).parent / "images" / "frequencies.png"
    target.parent.mkdir(exist_ok=True)
    figure.savefig(target, dpi=160, facecolor=SURFACE)
    print(f"saved {target}")


if __name__ == "__main__":
    main()
