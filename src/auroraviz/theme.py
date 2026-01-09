import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
from contextlib import contextmanager

# ---------------------------------------------------------------------
# Paths to style files
# ---------------------------------------------------------------------
STYLE_PATH = Path(__file__).resolve().parent / "styles" / "aurora.mplstyle"
DARK_STYLE_PATH = Path(__file__).resolve().parent / "styles" / "aurora-dark.mplstyle"

# ---------------------------------------------------------------------
# Mode & palette state
# ---------------------------------------------------------------------
_current_mode = "light"
_current_palette = [
    "#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2",
    "#EECA3B", "#B279A2", "#FF9DA6", "#9C755F", "#BAB0AC"
]

# Named palettes for quick switching
PALETTES = {
    "aurora": _current_palette,
    "vivid": [
        "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
        "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"
    ],
    "mono": ["#FFFFFF"],  # useful for single‑color emphasis
    "cool": ["#4C78A8", "#72B7B2", "#9CBCD9", "#A0CBE8", "#BBD7EA"],
    "warm": ["#F58518", "#EECA3B", "#E45756", "#B279A2", "#9C755F"],
}

# ---------------------------------------------------------------------
# Core apply functions
# ---------------------------------------------------------------------
def apply():
    """Apply light theme."""
    global _current_mode
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use(str(STYLE_PATH))
    _set_text_colors(light=True)
    _current_mode = "light"

def apply_dark():
    """Apply dark theme with automatic text inversion."""
    global _current_mode
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use(str(DARK_STYLE_PATH))
    _set_text_colors(light=False)
    _current_mode = "dark"

def toggle():
    """Toggle between light and dark themes."""
    apply_dark() if _current_mode == "light" else apply()

# ---------------------------------------------------------------------
# Public configuration helpers
# ---------------------------------------------------------------------
def set_font(family="DejaVu Sans", size=12, titleweight="bold"):
    mpl.rcParams["font.family"] = family
    mpl.rcParams["font.size"] = size
    mpl.rcParams["axes.titleweight"] = titleweight

def set_dpi(dpi=120):
    mpl.rcParams["figure.dpi"] = dpi
    mpl.rcParams["savefig.dpi"] = dpi

def set_size(width=8, height=5):
    mpl.rcParams["figure.figsize"] = (width, height)

def set_palette(palette="aurora"):
    """Set global color cycle. Accepts name or list of colors."""
    global _current_palette
    if isinstance(palette, str):
        if palette not in PALETTES:
            raise ValueError(f"Unknown palette '{palette}'. Available: {list(PALETTES.keys())}")
        _current_palette = PALETTES[palette]
    elif isinstance(palette, (list, tuple)):
        _current_palette = list(palette)
    else:
        raise TypeError("palette must be a name (str) or a list/tuple of colors")

    mpl.rcParams["axes.prop_cycle"] = plt.cycler(color=_current_palette)

def set_background(color=None):
    """Override background colors (figure & axes)."""
    if color is None:
        # Reset to style defaults
        return
    mpl.rcParams["figure.facecolor"] = color
    mpl.rcParams["axes.facecolor"] = color

def set_grid(visible=True, axis="y", color="gray", alpha=0.2, linewidth=0.8):
    mpl.rcParams["axes.grid"] = bool(visible)
    mpl.rcParams["axes.grid.axis"] = axis
    mpl.rcParams["grid.color"] = color
    mpl.rcParams["grid.alpha"] = alpha
    mpl.rcParams["grid.linewidth"] = linewidth

# ---------------------------------------------------------------------
# Axes auto‑styling (works for any chart type)
# ---------------------------------------------------------------------
def auto_style_axes(ax, text_color=None, spine_color=None, tick_color=None):
    """
    Apply text & spine colors to any Axes.
    Use this inside chart functions or after plotting.
    """
    # Resolve defaults based on current mode
    if text_color is None:
        text_color = "white" if _current_mode == "dark" else "black"
    if spine_color is None:
        spine_color = "lightgray" if _current_mode == "dark" else "#444444"
    if tick_color is None:
        tick_color = text_color

    # Titles & labels
    ax.title.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)

    # Ticks
    ax.tick_params(axis="x", colors=tick_color)
    ax.tick_params(axis="y", colors=tick_color)

    # Spines
    for side in ("top", "right", "left", "bottom"):
        if side in ax.spines:
            ax.spines[side].set_color(spine_color)

    # Legend text
    leg = ax.get_legend()
    if leg:
        for txt in leg.get_texts():
            txt.set_color(text_color)

# ---------------------------------------------------------------------
# Context manager for scoped usage
# ---------------------------------------------------------------------
@contextmanager
def use(mode="light", palette=None):
    """
    Context manager to apply a theme temporarily.
    Example:
        with theme.use("dark", palette="vivid"):
            charts.line(...)
    """
    prev_mode = _current_mode
    prev_cycle = mpl.rcParams.get("axes.prop_cycle", None)

    if mode == "dark":
        apply_dark()
    else:
        apply()

    if palette is not None:
        set_palette(palette)

    try:
        yield
    finally:
        # Restore previous mode & cycle
        if prev_mode == "dark":
            apply_dark()
        else:
            apply()
        if prev_cycle is not None:
            mpl.rcParams["axes.prop_cycle"] = prev_cycle

# ---------------------------------------------------------------------
# Internal: text color inversion
# ---------------------------------------------------------------------
def _set_text_colors(light=True):
    """
    Invert text colors globally via rcParams.
    Ensures titles, labels, ticks, and general text are readable.
    """
    if light:
        mpl.rcParams["axes.labelcolor"] = "black"
        mpl.rcParams["axes.titlecolor"] = "black"
        mpl.rcParams["xtick.color"] = "black"
        mpl.rcParams["ytick.color"] = "black"
        mpl.rcParams["text.color"] = "black"
        mpl.rcParams["axes.edgecolor"] = "#444444"
    else:
        mpl.rcParams["axes.labelcolor"] = "white"
        mpl.rcParams["axes.titlecolor"] = "white"
        mpl.rcParams["xtick.color"] = "white"
        mpl.rcParams["ytick.color"] = "white"
        mpl.rcParams["text.color"] = "white"
        mpl.rcParams["axes.edgecolor"] = "lightgray"
