import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

STYLE_PATH = Path(__file__).parent / "styles" / "aurora.mplstyle"

def apply():
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use(str(STYLE_PATH))

def set_font(family="DejaVu Sans", size=12):
    mpl.rcParams["font.family"] = family
    mpl.rcParams["font.size"] = size
    mpl.rcParams["axes.titleweight"] = "bold"

def set_dpi(dpi=120):
    mpl.rcParams["figure.dpi"] = dpi
    mpl.rcParams["savefig.dpi"] = dpi

def set_size(width=8, height=5):
    mpl.rcParams["figure.figsize"] = (width, height)

def apply_dark():
    from pathlib import Path
    DARK_STYLE_PATH = Path(__file__).parent / "styles" / "aurora-dark.mplstyle"
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use(str(DARK_STYLE_PATH))


    mpl.rcParams['xtick.color'] = 'lightgray'
    mpl.rcParams['ytick.color'] = 'lightgray'
    mpl.rcParams['axes.labelcolor'] = 'lightgray'
    mpl.rcParams['axes.titlecolor'] = 'white'
    mpl.rcParams['legend.labelcolor'] = 'lightgray'
    mpl.rcParams['text.color'] = 'lightgray'
    mpl.rcParams['axes.edgecolor'] = 'dimgray'
