"""Unified matplotlib style helpers for this project template.

This module extracts the common plotting language used in ``D1_temp``:

- serif text with STIX math
- light dashed grid
- inward ticks with minor ticks
- publication-style figure export
- consistent legend and axis styling

The main public helpers are:

- ``apply_plot_style``: apply a global preset
- ``create_figure``: create styled figure/axes and set labels
- ``configure_axes``: apply axis-level conventions
- ``save_figure``: save into ``reports/figures`` by default
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

DEFAULT_FIGURE_DIR = Path("reports/figures")


@dataclass(frozen=True)
class PlotStyle:
    """Project-level plotting preset."""

    figure_size: tuple[float, float]
    figure_dpi: int = 150
    savefig_dpi: int = 300
    font_family: str = "serif"
    font_size: float = 13
    axes_title_size: float = 14
    axes_label_size: float = 13
    tick_label_size: float = 12
    legend_font_size: float = 11
    line_width: float = 1.6
    marker_size: float = 5
    axes_line_width: float = 1.0
    grid_alpha: float = 0.2
    grid_line_width: float = 0.6
    grid_linestyle: str = "--"
    show_grid: bool = True
    show_top_spine: bool = False
    show_right_spine: bool = False
    legend_frame: bool = False

    def rc_params(self) -> dict[str, object]:
        return {
            "figure.figsize": self.figure_size,
            "figure.dpi": self.figure_dpi,
            "savefig.dpi": self.savefig_dpi,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
            "font.family": self.font_family,
            "font.size": self.font_size,
            "axes.titlesize": self.axes_title_size,
            "axes.labelsize": self.axes_label_size,
            "xtick.labelsize": self.tick_label_size,
            "ytick.labelsize": self.tick_label_size,
            "legend.fontsize": self.legend_font_size,
            "mathtext.fontset": "stix",
            "axes.linewidth": self.axes_line_width,
            "axes.grid": self.show_grid,
            "axes.spines.top": self.show_top_spine,
            "axes.spines.right": self.show_right_spine,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 4,
            "ytick.major.size": 4,
            "xtick.minor.size": 2,
            "ytick.minor.size": 2,
            "xtick.minor.visible": True,
            "ytick.minor.visible": True,
            "lines.linewidth": self.line_width,
            "lines.markersize": self.marker_size,
            "grid.alpha": self.grid_alpha,
            "grid.linewidth": self.grid_line_width,
            "grid.linestyle": self.grid_linestyle,
            "legend.frameon": self.legend_frame,
            "legend.handlelength": 2.0,
        }


BASE_STYLE = PlotStyle(figure_size=(6.5, 4.5))

COMPARISON_STYLE = PlotStyle(
    figure_size=(10.0, 13.0),
    font_size=32,
    axes_title_size=36,
    axes_label_size=32,
    tick_label_size=30,
    legend_font_size=28,
    line_width=3.0,
    marker_size=16,
    grid_alpha=0.3,
)

WIDE_STYLE = PlotStyle(
    figure_size=(23.0, 3.0),
    font_size=32,
    axes_title_size=36,
    axes_label_size=32,
    tick_label_size=30,
    legend_font_size=28,
    line_width=3.0,
    marker_size=16,
    grid_alpha=0.3,
)

STYLE_PRESETS = {
    "base": BASE_STYLE,
    "comparison": COMPARISON_STYLE,
    "wide": WIDE_STYLE,
}


def get_style(style: str | PlotStyle = "base") -> PlotStyle:
    """Resolve a named style preset or return a provided style object."""
    if isinstance(style, PlotStyle):
        return style

    try:
        return STYLE_PRESETS[style]
    except KeyError as exc:
        available = ", ".join(sorted(STYLE_PRESETS))
        message = f"unknown style '{style}', available styles: {available}"
        raise ValueError(message) from exc


def apply_plot_style(
    style: str | PlotStyle = "base",
    *,
    figsize: tuple[float, float] | None = None,
) -> PlotStyle:
    """Apply the project's standard matplotlib style."""
    resolved = get_style(style)
    plt.style.use("default")

    rc_params = resolved.rc_params()
    if figsize is not None:
        rc_params["figure.figsize"] = figsize

    mpl.rcParams.update(rc_params)
    return resolved


def configure_axes(
    ax: plt.Axes,
    *,
    xlabel: str | None = None,
    ylabel: str | None = None,
    title: str | None = None,
    grid: bool | None = None,
    legend: bool = False,
    legend_loc: str = "best",
    top_spine: bool | None = None,
    right_spine: bool | None = None,
) -> plt.Axes:
    """Apply project-standard axis formatting to an axes."""
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)

    if grid is not None:
        ax.grid(grid)

    if top_spine is not None:
        ax.spines["top"].set_visible(top_spine)
    if right_spine is not None:
        ax.spines["right"].set_visible(right_spine)

    if legend:
        ax.legend(loc=legend_loc)

    return ax


def create_figure(
    *,
    xlabel: str | None = None,
    ylabel: str | None = None,
    title: str | None = None,
    style: str | PlotStyle = "base",
    figsize: tuple[float, float] | None = None,
    nrows: int = 1,
    ncols: int = 1,
    sharex: bool = False,
    sharey: bool = False,
    constrained_layout: bool = False,
    grid: bool | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Create a styled figure and apply standard labeling to a single axes."""
    apply_plot_style(style, figsize=figsize)

    fig, ax = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=figsize,
        sharex=sharex,
        sharey=sharey,
        constrained_layout=constrained_layout,
    )

    if isinstance(ax, plt.Axes):
        configure_axes(ax, xlabel=xlabel, ylabel=ylabel, title=title, grid=grid)
        return fig, ax

    raise ValueError(
        "create_figure only returns a single Axes. "
        "Use matplotlib directly for multi-axes layouts after apply_plot_style()."
    )


def figure_path(
    filename: str | Path,
    *,
    directory: str | Path = DEFAULT_FIGURE_DIR,
) -> Path:
    """Build and create the default figure output path."""
    path = Path(directory) / Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_figure(
    fig: plt.Figure,
    filename: str | Path,
    *,
    directory: str | Path = DEFAULT_FIGURE_DIR,
    close: bool = False,
) -> Path:
    """Save a figure using the project's default export settings."""
    path = figure_path(filename, directory=directory)
    fig.savefig(path)
    if close:
        plt.close(fig)
    return path
