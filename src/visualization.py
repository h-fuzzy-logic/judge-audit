"""Chart rendering for calibration analysis."""
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display in the Docker container
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_confusion_matrix(matrix: pd.DataFrame, title: str, output_path: Path) -> None:
    plt.figure(figsize=(5, 4))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", square=True)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


# Fixed sizes in inches, independent of how many title lines there are, so
# a longer headline grows the total figure instead of squeezing the heatmaps.
_PLOT_HEIGHT_IN = 4.5
_TITLE_LINE_HEIGHT_IN = 0.3
_SUBTITLE_BLOCK_IN = 0.35
_TOP_PAD_IN = 0.15
_BOTTOM_PAD_IN = 0.55


def plot_confusion_matrix_grid(
    matrices: dict[str, pd.DataFrame], title: str, subtitle: str, output_path: Path
) -> None:
    """Renders multiple confusion matrices side by side in one image.

    matrices maps each subplot's own title to its matrix, e.g.
    {"rubric_v1_strict": matrix_a, "rubric_v2_chain_of_thought": matrix_b}.
    `title` is a left-aligned headline at the top summarizing the result
    (what the reader should notice); `subtitle` (e.g. the model name) sits
    centered just below it, since it's context, not the finding itself.
    """
    n = len(matrices)
    fig_width_inches = 5 * n

    # suptitle doesn't auto-wrap, so long headlines run off the figure edge
    # instead of wrapping - wrap manually to roughly the figure's width.
    # Wrap each line of the title independently so a caller's own manual
    # line breaks (e.g. "more than\n{worst_name} ...") survive instead of
    # being reflowed away like textwrap.fill would do on the whole string.
    wrap_width = int(fig_width_inches * 8)
    wrapped_title = "\n".join(
        textwrap.fill(line, width=wrap_width) for line in title.split("\n")
    )
    n_title_lines = wrapped_title.count("\n") + 1

    title_block_in = n_title_lines * _TITLE_LINE_HEIGHT_IN
    fig_height_inches = (
        _TOP_PAD_IN + title_block_in + _SUBTITLE_BLOCK_IN + _PLOT_HEIGHT_IN + _BOTTOM_PAD_IN
    )

    fig, axes = plt.subplots(1, n, figsize=(fig_width_inches, fig_height_inches))
    if n == 1:
        axes = [axes]

    for ax, (subplot_title, matrix) in zip(axes, matrices.items(), strict=True):
        sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", square=True, ax=ax)
        ax.set_title(subplot_title)

    title_top_y = 1 - _TOP_PAD_IN / fig_height_inches
    subtitle_y = 1 - (_TOP_PAD_IN + title_block_in) / fig_height_inches
    top_margin = 1 - (_TOP_PAD_IN + title_block_in + _SUBTITLE_BLOCK_IN) / fig_height_inches
    bottom_margin = _BOTTOM_PAD_IN / fig_height_inches

    fig.suptitle(wrapped_title, x=0.02, y=title_top_y, ha="left", va="top", fontsize=13, fontweight="bold")
    fig.text(0.5, subtitle_y, subtitle, ha="center", va="top", fontsize=13, color="gray")
    # subplots_adjust sets these margins exactly - unlike tight_layout, it
    # won't pad extra space trying to auto-avoid the manually-positioned
    # suptitle/text artists above, which is what caused a large gap before.
    # Both margins are inches-derived (not flat fractions), so the actual
    # plot area stays _PLOT_HEIGHT_IN regardless of how long the title is.
    fig.subplots_adjust(left=0.08, right=0.98, bottom=bottom_margin, top=top_margin, wspace=0.4)
    fig.savefig(output_path)
    plt.close(fig)
