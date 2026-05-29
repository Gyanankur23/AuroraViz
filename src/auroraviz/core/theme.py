"""
auroraviz.core.theme
====================
Unified visual language for AuroraViz v0.2.0.

Exports structured color matrices (Hex, RGB-normalized, RGBA) for
'Aurora Dark' and 'Aurora Light' themes, injects them into Matplotlib
rcParams for static rendering, and exposes them as clean dict parameters
for the WASM and WebGL rendering engines.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Style file paths (preserved from v0.1.x for backward compat)
# ---------------------------------------------------------------------------
_STYLE_DIR = Path(__file__).resolve().parent.parent / "styles"
_LIGHT_STYLE = _STYLE_DIR / "aurora.mplstyle"
_DARK_STYLE = _STYLE_DIR / "aurora-dark.mplstyle"

# ---------------------------------------------------------------------------
# Aurora Dark — Canonical color definitions
# ---------------------------------------------------------------------------
DARK_BG_HEX = "#0B0F19"
DARK_BG_RGB = (0.043, 0.059, 0.098)
DARK_BG_RGBA = (0.043, 0.059, 0.098, 1.0)

DARK_SURFACE_HEX = "#131929"
DARK_SURFACE_RGB = (0.075, 0.098, 0.161)

DARK_TEAL_HEX = "#00FFCC"
DARK_TEAL_RGB = (0.0, 1.0, 0.8)
DARK_TEAL_RGBA = (0.0, 1.0, 0.8, 1.0)

DARK_PURPLE_HEX = "#BF5FFF"
DARK_PURPLE_RGB = (0.749, 0.373, 1.0)
DARK_PURPLE_RGBA = (0.749, 0.373, 1.0, 1.0)

DARK_CYAN_HEX = "#00D4FF"
DARK_CYAN_RGB = (0.0, 0.831, 1.0)
DARK_CYAN_RGBA = (0.0, 0.831, 1.0, 1.0)

DARK_AMBER_HEX = "#FFB830"
DARK_AMBER_RGB = (1.0, 0.722, 0.188)

DARK_CORAL_HEX = "#FF4D6D"
DARK_CORAL_RGB = (1.0, 0.302, 0.427)

DARK_LIME_HEX = "#39FF14"
DARK_LIME_RGB = (0.224, 1.0, 0.078)

DARK_TEXT_HEX = "#E8EBF4"
DARK_TEXT_RGB = (0.910, 0.922, 0.957)

DARK_MUTED_HEX = "#5A6480"
DARK_MUTED_RGB = (0.353, 0.392, 0.502)

# ---------------------------------------------------------------------------
# Aurora Light — Canonical color definitions
# ---------------------------------------------------------------------------
LIGHT_BG_HEX = "#F7F9FC"
LIGHT_BG_RGB = (0.969, 0.976, 0.988)
LIGHT_BG_RGBA = (0.969, 0.976, 0.988, 1.0)

LIGHT_SURFACE_HEX = "#FFFFFF"
LIGHT_SURFACE_RGB = (1.0, 1.0, 1.0)

LIGHT_TEAL_HEX = "#007A8C"
LIGHT_TEAL_RGB = (0.0, 0.478, 0.549)

LIGHT_PURPLE_HEX = "#6B21A8"
LIGHT_PURPLE_RGB = (0.420, 0.129, 0.659)

LIGHT_CYAN_HEX = "#0369A1"
LIGHT_CYAN_RGB = (0.012, 0.412, 0.631)

LIGHT_AMBER_HEX = "#B45309"
LIGHT_AMBER_RGB = (0.706, 0.325, 0.035)

LIGHT_CORAL_HEX = "#C0392B"
LIGHT_CORAL_RGB = (0.753, 0.224, 0.169)

LIGHT_LIME_HEX = "#15803D"
LIGHT_LIME_RGB = (0.082, 0.502, 0.239)

LIGHT_TEXT_HEX = "#111827"
LIGHT_TEXT_RGB = (0.067, 0.094, 0.153)

LIGHT_MUTED_HEX = "#6B7280"
LIGHT_MUTED_RGB = (0.420, 0.447, 0.502)

# ---------------------------------------------------------------------------
# Structured color matrices — consumed by WASM + WebGL engines
# ---------------------------------------------------------------------------
AURORA_DARK: dict = {
    "name": "Aurora Dark",
    "background": {"hex": DARK_BG_HEX, "rgb": DARK_BG_RGB, "rgba": DARK_BG_RGBA},
    "surface": {"hex": DARK_SURFACE_HEX, "rgb": DARK_SURFACE_RGB},
    "text": {"hex": DARK_TEXT_HEX, "rgb": DARK_TEXT_RGB},
    "muted": {"hex": DARK_MUTED_HEX, "rgb": DARK_MUTED_RGB},
    "palette": {
        "teal":   {"hex": DARK_TEAL_HEX,   "rgb": DARK_TEAL_RGB,   "rgba": DARK_TEAL_RGBA},
        "purple": {"hex": DARK_PURPLE_HEX, "rgb": DARK_PURPLE_RGB, "rgba": DARK_PURPLE_RGBA},
        "cyan":   {"hex": DARK_CYAN_HEX,   "rgb": DARK_CYAN_RGB,   "rgba": DARK_CYAN_RGBA},
        "amber":  {"hex": DARK_AMBER_HEX,  "rgb": DARK_AMBER_RGB},
        "coral":  {"hex": DARK_CORAL_HEX,  "rgb": DARK_CORAL_RGB},
        "lime":   {"hex": DARK_LIME_HEX,   "rgb": DARK_LIME_RGB},
    },
    "series": [
        DARK_TEAL_HEX, DARK_PURPLE_HEX, DARK_CYAN_HEX,
        DARK_AMBER_HEX, DARK_CORAL_HEX, DARK_LIME_HEX,
    ],
    "gradient_stops": [DARK_TEAL_HEX, DARK_CYAN_HEX, DARK_PURPLE_HEX],
    "css_vars": {
        "--av-bg":       DARK_BG_HEX,
        "--av-surface":  DARK_SURFACE_HEX,
        "--av-text":     DARK_TEXT_HEX,
        "--av-muted":    DARK_MUTED_HEX,
        "--av-accent-1": DARK_TEAL_HEX,
        "--av-accent-2": DARK_PURPLE_HEX,
        "--av-accent-3": DARK_CYAN_HEX,
        "--av-border":   "#1E2740",
    },
}

AURORA_LIGHT: dict = {
    "name": "Aurora Light",
    "background": {"hex": LIGHT_BG_HEX, "rgb": LIGHT_BG_RGB, "rgba": LIGHT_BG_RGBA},
    "surface": {"hex": LIGHT_SURFACE_HEX, "rgb": LIGHT_SURFACE_RGB},
    "text": {"hex": LIGHT_TEXT_HEX, "rgb": LIGHT_TEXT_RGB},
    "muted": {"hex": LIGHT_MUTED_HEX, "rgb": LIGHT_MUTED_RGB},
    "palette": {
        "teal":   {"hex": LIGHT_TEAL_HEX,   "rgb": LIGHT_TEAL_RGB},
        "purple": {"hex": LIGHT_PURPLE_HEX, "rgb": LIGHT_PURPLE_RGB},
        "cyan":   {"hex": LIGHT_CYAN_HEX,   "rgb": LIGHT_CYAN_RGB},
        "amber":  {"hex": LIGHT_AMBER_HEX,  "rgb": LIGHT_AMBER_RGB},
        "coral":  {"hex": LIGHT_CORAL_HEX,  "rgb": LIGHT_CORAL_RGB},
        "lime":   {"hex": LIGHT_LIME_HEX,   "rgb": LIGHT_LIME_RGB},
    },
    "series": [
        LIGHT_TEAL_HEX, LIGHT_PURPLE_HEX, LIGHT_CYAN_HEX,
        LIGHT_AMBER_HEX, LIGHT_CORAL_HEX, LIGHT_LIME_HEX,
    ],
    "gradient_stops": [LIGHT_TEAL_HEX, LIGHT_CYAN_HEX, LIGHT_PURPLE_HEX],
    "css_vars": {
        "--av-bg":       LIGHT_BG_HEX,
        "--av-surface":  LIGHT_SURFACE_HEX,
        "--av-text":     LIGHT_TEXT_HEX,
        "--av-muted":    LIGHT_MUTED_HEX,
        "--av-accent-1": LIGHT_TEAL_HEX,
        "--av-accent-2": LIGHT_PURPLE_HEX,
        "--av-accent-3": LIGHT_CYAN_HEX,
        "--av-border":   "#DDE3EE",
    },
}

# ---------------------------------------------------------------------------
# Named palettes (backward compat from v0.1.x + new aurora palettes)
# ---------------------------------------------------------------------------
PALETTES: dict = {
    "aurora_dark": AURORA_DARK["series"],
    "aurora_light": AURORA_LIGHT["series"],
    "aurora": AURORA_DARK["series"],       # alias
    "vivid": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
              "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],
    "cool":  ["#4C78A8", "#72B7B2", "#9CBCD9", "#A0CBE8", "#BBD7EA"],
    "warm":  ["#F58518", "#EECA3B", "#E45756", "#B279A2", "#9C755F"],
    "mono":  ["#FFFFFF"],
}

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
_current_mode: Literal["light", "dark"] = "light"
_current_palette: list[str] = AURORA_DARK["series"]


def get_theme(theme: Literal["dark", "light"] = "dark") -> dict:
    """Return the canonical structured theme dict for the given mode."""
    return AURORA_DARK if theme == "dark" else AURORA_LIGHT


# ---------------------------------------------------------------------------
# Core apply helpers
# ---------------------------------------------------------------------------
def apply() -> None:
    """Apply Aurora Light theme to Matplotlib rcParams."""
    global _current_mode
    mpl.rcParams.update(mpl.rcParamsDefault)
    if _LIGHT_STYLE.exists():
        plt.style.use(str(_LIGHT_STYLE))
    _inject_rcparams(AURORA_LIGHT)
    _current_mode = "light"


def apply_dark() -> None:
    """Apply Aurora Dark theme to Matplotlib rcParams."""
    global _current_mode
    mpl.rcParams.update(mpl.rcParamsDefault)
    if _DARK_STYLE.exists():
        plt.style.use(str(_DARK_STYLE))
    _inject_rcparams(AURORA_DARK)
    _current_mode = "dark"


def toggle() -> None:
    """Toggle between light and dark themes."""
    apply_dark() if _current_mode == "light" else apply()


# ---------------------------------------------------------------------------
# Public configuration helpers
# ---------------------------------------------------------------------------
def set_font(family: str = "DejaVu Sans", size: int = 12,
             titleweight: str = "bold") -> None:
    mpl.rcParams["font.family"] = family
    mpl.rcParams["font.size"] = size
    mpl.rcParams["axes.titleweight"] = titleweight


def set_dpi(dpi: int = 120) -> None:
    mpl.rcParams["figure.dpi"] = dpi
    mpl.rcParams["savefig.dpi"] = dpi


def set_size(width: float = 8, height: float = 5) -> None:
    mpl.rcParams["figure.figsize"] = (width, height)


def set_palette(palette: "str | list[str]" = "aurora") -> None:
    """Set global Matplotlib color cycle. Accepts palette name or hex list."""
    global _current_palette
    if isinstance(palette, str):
        if palette not in PALETTES:
            raise ValueError(
                f"Unknown palette '{palette}'. Available: {list(PALETTES.keys())}"
            )
        _current_palette = PALETTES[palette]
    elif isinstance(palette, (list, tuple)):
        _current_palette = list(palette)
    else:
        raise TypeError("palette must be a name (str) or list/tuple of hex colors.")
    mpl.rcParams["axes.prop_cycle"] = plt.cycler(color=_current_palette)


def set_background(color: "str | None" = None) -> None:
    """Override figure and axes background color."""
    if color is None:
        return
    mpl.rcParams["figure.facecolor"] = color
    mpl.rcParams["axes.facecolor"] = color


def set_grid(visible: bool = True, axis: str = "y",
             color: str = "gray", alpha: float = 0.2,
             linewidth: float = 0.8) -> None:
    mpl.rcParams["axes.grid"] = bool(visible)
    mpl.rcParams["axes.grid.axis"] = axis
    mpl.rcParams["grid.color"] = color
    mpl.rcParams["grid.alpha"] = alpha
    mpl.rcParams["grid.linewidth"] = linewidth


def auto_style_axes(ax, text_color: "str | None" = None,
                    spine_color: "str | None" = None,
                    tick_color: "str | None" = None) -> None:
    """Apply AuroraViz text, spine, and tick colours to a Matplotlib Axes."""
    t = AURORA_DARK if _current_mode == "dark" else AURORA_LIGHT
    text_color = text_color or t["text"]["hex"]
    spine_color = spine_color or t["css_vars"]["--av-border"]
    tick_color = tick_color or text_color

    ax.title.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.tick_params(axis="x", colors=tick_color)
    ax.tick_params(axis="y", colors=tick_color)
    for side in ("top", "right", "left", "bottom"):
        if side in ax.spines:
            ax.spines[side].set_color(spine_color)
    leg = ax.get_legend()
    if leg:
        for txt in leg.get_texts():
            txt.set_color(text_color)


# ---------------------------------------------------------------------------
# Context manager for scoped usage
# ---------------------------------------------------------------------------
@contextmanager
def use(mode: Literal["light", "dark"] = "light", palette: "str | None" = None):
    """
    Temporarily apply a theme within a `with` block.

    Example::

        with theme.use("dark", palette="aurora_dark"):
            charts.line(...)
    """
    prev_mode = _current_mode
    prev_cycle = mpl.rcParams.get("axes.prop_cycle", None)
    apply_dark() if mode == "dark" else apply()
    if palette is not None:
        set_palette(palette)
    try:
        yield
    finally:
        apply_dark() if prev_mode == "dark" else apply()
        if prev_cycle is not None:
            mpl.rcParams["axes.prop_cycle"] = prev_cycle


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _inject_rcparams(t: dict) -> None:
    """Push AuroraViz theme values into Matplotlib rcParams."""
    bg = t["background"]["hex"]
    fg = t["text"]["hex"]
    border = t["css_vars"]["--av-border"]
    series = t["series"]

    mpl.rcParams.update({
        "figure.facecolor":    bg,
        "axes.facecolor":      t["surface"]["hex"],
        "axes.edgecolor":      border,
        "axes.labelcolor":     fg,
        "axes.titlecolor":     fg,
        "xtick.color":         fg,
        "ytick.color":         fg,
        "text.color":          fg,
        "axes.prop_cycle":     plt.cycler(color=series),
        "grid.color":          t["muted"]["hex"],
        "grid.alpha":          0.2,
        "legend.facecolor":    t["surface"]["hex"],
        "legend.edgecolor":    border,
        "legend.labelcolor":   fg,
    })
