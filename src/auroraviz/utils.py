import matplotlib.pyplot as plt

def _apply_titles(ax, title=None, subtitle=None, xlabel=None, ylabel=None, caption=None):
    if title:
        ax.set_title(title, loc="left", pad=10)
    if subtitle:
        ax.text(0, 1.08, subtitle, transform=ax.transAxes, ha="left", va="bottom",
                fontsize=10, color="#555555")
    if xlabel:
        ax.set_xlabel(xlabel, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, labelpad=8)
    if caption:
        ax.text(0, -0.18, caption, transform=ax.transAxes, ha="left", va="top",
                fontsize=9, color="#666666")

def _finalize(ax, grid=True, legend=False, tight=True):
    if grid:
        ax.grid(True, axis="y", alpha=0.15)
    if legend:
        ax.legend(frameon=False, loc="best")
    if tight:
        plt.tight_layout()

def save(fig, path, transparent=False):
    fig.savefig(path, bbox_inches="tight", transparent=transparent)
