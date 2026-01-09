import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

# Paths to style files
STYLE_PATH = Path(__file__).resolve().parent / "styles" / "aurora.mplstyle"
DARK_STYLE_PATH = Path(__file__).resolve().parent / "styles" / "aurora-dark.mplstyle"

# Track current mode
_current_mode = "light"

def apply():
    """Apply light theme."""
    global _current_mode
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use(str(STYLE_PATH))
    _current_mode = "light"

def apply_dark():
    """Apply dark theme with automatic text inversion."""
    global _current_mode
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use(str(DARK_STYLE_PATH))

    # Invert text colors for dark background
    mpl.rcParams['axes.labelcolor'] = 'white'
    mpl.rcParams['axes.titlecolor'] = 'white'
    mpl.rcParams['xtick.color'] = 'white'
    mpl.rcParams['ytick.color'] = 'white'
    mpl.rcParams['text.color'] = 'white'
    mpl.rcParams['axes.edgecolor'] = 'lightgray'
    _current_mode = "dark"

def toggle():
    """Toggle between light and dark themes."""
    if _current_mode == "light":
        apply_dark()
    else:
        apply()

def set_font(family="DejaVu Sans", size=12):
    mpl.rcParams["font.family"] = family
    mpl.rcParams["font.size"] = size
    mpl.rcParams["axes.titleweight"] = "bold"

def set_dpi(dpi=120):
    mpl.rcParams["figure.dpi"] = dpi
    mpl.rcParams["savefig.dpi"] = dpi

def set_size(width=8, height=5):
    mpl.rcParams["figure.figsize"] = (width, height)
