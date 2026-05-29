"""
AuroraViz v0.2.0
================
A world-class Python visualization framework.

Quick start::

    import auroraviz as av
    import pandas as pd

    # Static matplotlib chart
    av.theme.apply_dark()
    av.charts.line([1, 4, 2, 8, 5, 7])

    # Interactive WASM single-file HTML export
    av.ignite_interactive(df, x="date", y="revenue", hue="segment",
                          filename="dashboard.html", theme="dark")

    # WebGL point-cloud in Jupyter / Colab
    av.show_fluid(df, x_col="x", y_col="y", color_col="category")
"""

from __future__ import annotations

# ── Sub-module namespaces (kept for backward compat + discoverability) ─
from auroraviz import core
from auroraviz.core import theme          # av.theme.apply_dark() etc.

# ── Static chart helpers (v0.1.x surface, re-exported) ────────────────
try:
    from auroraviz import charts          # noqa: F401  (optional, matplotlib)
except ImportError:
    pass

# ── v0.2.0 flagship functions ──────────────────────────────────────────
from auroraviz.interactive.wasm_exporter import ignite_interactive
from auroraviz.notebook.webgl import show_fluid

# ── Convenience re-exports from core ──────────────────────────────────
from auroraviz.core.theme import (
    AURORA_DARK,
    AURORA_LIGHT,
    PALETTES,
    apply,
    apply_dark,
    toggle,
    use,
    get_theme,
    set_font,
    set_dpi,
    set_size,
    set_palette,
    set_background,
    set_grid,
    auto_style_axes,
)

__version__ = "0.2.0"
__author__  = "Gyanankur Baruah"
__email__   = "gyanankur9@gmail.com"

__all__ = [
    # Sub-modules
    "core",
    "theme",
    "charts",
    # v0.2.0 flagship
    "ignite_interactive",
    "show_fluid",
    # Theme constants
    "AURORA_DARK",
    "AURORA_LIGHT",
    "PALETTES",
    # Theme helpers
    "apply",
    "apply_dark",
    "toggle",
    "use",
    "get_theme",
    "set_font",
    "set_dpi",
    "set_size",
    "set_palette",
    "set_background",
    "set_grid",
    "auto_style_axes",
    # Meta
    "__version__",
    "__author__",
    "__email__",
]
