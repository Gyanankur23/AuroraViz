"""auroraviz.core — theme engine and color matrices."""
from .theme import (
    AURORA_DARK, AURORA_LIGHT, PALETTES,
    apply, apply_dark, toggle, use, get_theme,
    set_font, set_dpi, set_size, set_palette, set_background, set_grid,
    auto_style_axes,
)

__all__ = [
    "AURORA_DARK", "AURORA_LIGHT", "PALETTES",
    "apply", "apply_dark", "toggle", "use", "get_theme",
    "set_font", "set_dpi", "set_size", "set_palette",
    "set_background", "set_grid", "auto_style_axes",
]
