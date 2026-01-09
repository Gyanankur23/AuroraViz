import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .utils import _apply_titles, _finalize

def _get_ax(ax=None):
    if ax is None:
        fig, ax = plt.subplots()
        return fig, ax
    return ax.figure, ax

def line(data, x=None, y=None, title=None, subtitle=None, xlabel=None, ylabel=None,
         color="#4C78A8", linewidth=2.5, marker=None, ax=None, grid=True, legend=False, label=None):
    fig, ax = _get_ax(ax)
    if isinstance(data, pd.DataFrame):
        xv = data[x] if x else np.arange(len(data))
        yv = data[y] if y else data.iloc[:, 0]
    else:
        xv = np.arange(len(data))
        yv = data
    ax.plot(xv, yv, color=color, linewidth=linewidth, marker=marker, label=label)
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    _finalize(ax, grid=grid, legend=legend)
    return fig, ax

def area(data, x=None, y=None, title=None, subtitle=None, xlabel=None, ylabel=None,
         color="#54A24B", alpha=0.6, ax=None, grid=True):
    fig, ax = _get_ax(ax)
    if isinstance(data, pd.DataFrame):
        xv = data[x] if x else np.arange(len(data))
        yv = data[y] if y else data.iloc[:, 0]
    else:
        xv = np.arange(len(data))
        yv = data
    ax.fill_between(xv, yv, color=color, alpha=alpha)
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    _finalize(ax, grid=grid)
    return fig, ax

def bar(categories, values, title=None, subtitle=None, xlabel=None, ylabel=None,
        color="#F58518", width=0.6, ax=None, grid=True, horizontal=False):
    fig, ax = _get_ax(ax)
    if horizontal:
        ax.barh(categories, values, color=color, alpha=0.9)
    else:
        ax.bar(categories, values, color=color, alpha=0.9, width=width)
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    _finalize(ax, grid=grid)
    return fig, ax

def scatter(x, y, title=None, subtitle=None, xlabel=None, ylabel=None,
            color="#E45756", size=40, alpha=0.8, ax=None, grid=True, label=None):
    fig, ax = _get_ax(ax)
    ax.scatter(x, y, s=size, c=color, alpha=alpha, label=label)
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    _finalize(ax, grid=grid, legend=bool(label))
    return fig, ax

def histogram(data, bins=20, title=None, subtitle=None, xlabel=None, ylabel=None,
              color="#72B7B2", alpha=0.85, ax=None, grid=True):
    fig, ax = _get_ax(ax)
    ax.hist(data, bins=bins, color=color, alpha=alpha, edgecolor="white")
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    _finalize(ax, grid=grid)
    return fig, ax

def boxplot(data, title=None, subtitle=None, xlabel=None, ylabel=None,
            color="#B279A2", ax=None, grid=True):
    fig, ax = _get_ax(ax)
    bp = ax.boxplot(data, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    _finalize(ax, grid=grid)
    return fig, ax

def violinplot(data, title=None, subtitle=None, xlabel=None, ylabel=None,
               color="#9D755D", ax=None, grid=True):
    fig, ax = _get_ax(ax)
    vp = ax.violinplot(data, showmeans=False, showmedians=True)
    for body in vp["bodies"]:
        body.set_facecolor(color)
        body.set_alpha(0.5)
        body.set_edgecolor("black")
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    _finalize(ax, grid=grid)
    return fig, ax

def heatmap(matrix, xlabels=None, ylabels=None, title=None, subtitle=None,
            xlabel=None, ylabel=None, cmap="Blues", ax=None, grid=False, annotate=False):
    fig, ax = _get_ax(ax)
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")
    if annotate:
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", color="#222222", fontsize=8)
    if xlabels:
        ax.set_xticks(np.arange(len(xlabels)))
        ax.set_xticklabels(xlabels, rotation=0)
    if ylabels:
        ax.set_yticks(np.arange(len(ylabels)))
        ax.set_yticklabels(ylabels)
    _apply_titles(ax, title, subtitle, xlabel, ylabel)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    _finalize(ax, grid=grid)
    return fig, ax
