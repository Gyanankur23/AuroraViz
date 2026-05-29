import matplotlib.pyplot as plt
import numpy as np
from auroraviz import theme


def _prep_ax(ax):
    if ax is None:
        fig, ax = plt.subplots()
    return ax

def histogram(data, title="", xlabel="", ylabel="", color=None, ax=None):
    ax = _prep_ax(ax)
    ax.hist(data, color=color)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def line(data, title="", xlabel="", ylabel="", color=None, ax=None):
    ax = _prep_ax(ax)
    ax.plot(data, color=color)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def bar(data, title="", xlabel="", ylabel="", color=None, ax=None):
    ax = _prep_ax(ax)
    ax.bar(range(len(data)), data, color=color)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def scatter(x, y, title="", xlabel="", ylabel="", color=None, ax=None):
    ax = _prep_ax(ax)
    ax.scatter(x, y, color=color)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def area(data, title="", xlabel="", ylabel="", color=None, ax=None):
    ax = _prep_ax(ax)
    ax.fill_between(range(len(data)), data, color=color, alpha=0.6)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def stacked_bar(data, labels=None, title="", xlabel="", ylabel="", ax=None):
    ax = _prep_ax(ax)
    data = np.array(data)
    ax.bar(range(len(data[0])), data[0], label=labels[0] if labels else None)
    ax.bar(range(len(data[1])), data[1], bottom=data[0], label=labels[1] if labels else None)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if labels: ax.legend()
    theme.auto_style_axes(ax); return ax

def boxplot(data, title="", xlabel="", ylabel="", ax=None):
    ax = _prep_ax(ax)
    ax.boxplot(data)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def violin(data, title="", xlabel="", ylabel="", ax=None):
    ax = _prep_ax(ax)
    ax.violinplot(data)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def pie(data, labels=None, title="", ax=None):
    ax = _prep_ax(ax)
    ax.pie(data, labels=labels, autopct="%1.1f%%")
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def donut(data, labels=None, title="", ax=None):
    ax = _prep_ax(ax)
    wedges, texts, autotexts = ax.pie(data, labels=labels, autopct="%1.1f%%", wedgeprops=dict(width=0.4))
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def bubble(x, y, sizes, title="", xlabel="", ylabel="", ax=None):
    ax = _prep_ax(ax)
    ax.scatter(x, y, s=sizes)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    theme.auto_style_axes(ax); return ax

def heatmap(matrix, title="", ax=None):
    ax = _prep_ax(ax)
    im = ax.imshow(matrix, cmap="viridis")
    ax.set_title(title)
    plt.colorbar(im, ax=ax)
    theme.auto_style_axes(ax); return ax

def radar(values, labels, title="", ax=None):
    ax = _prep_ax(ax)
    angles = np.linspace(0, 2*np.pi, len(values), endpoint=False).tolist()
    values = values + [values[0]]
    angles += [angles[0]]
    ax.plot(angles, values); ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def parallel(data, title="", ax=None):
    ax = _prep_ax(ax)
    ax.plot(data)
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def stream(data, title="", ax=None):
    ax = _prep_ax(ax)
    ax.plot(data, drawstyle="steps-mid")
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def timeline(data, title="", ax=None):
    ax = _prep_ax(ax)
    ax.plot(range(len(data)), data, marker="o")
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def gantt(tasks, labels=None, title="", ax=None):
    ax = _prep_ax(ax)
    for i, (start, end) in enumerate(tasks):
        ax.barh(i, end-start, left=start)
    if labels: ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels)
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def sunburst(data, title="", ax=None):
    ax = _prep_ax(ax)
    # Simplified: just a pie chart for nested dict
    values = [v for v in data[list(data.keys())[0]].values()]
    labels = [k for k in data[list(data.keys())[0]].keys()]
    ax.pie(values, labels=labels)
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def treemap(data, title="", ax=None):
    ax = _prep_ax(ax)
    sizes = list(data.values()); labels = list(data.keys())
    ax.bar(range(len(sizes)), sizes, tick_label=labels)
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax

def network(edges, title="", ax=None):
    ax = _prep_ax(ax)
    for u,v in edges:
        ax.plot([u,v],[u,v], marker="o")
    ax.set_title(title)
    theme.auto_style_axes(ax); return ax
