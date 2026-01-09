import numpy as np
from auroraviz import theme, charts, palettes

theme.apply()
theme.set_size(8, 5)

# Area
charts.area(
    data=[0, 1, 3, 2, 4, 3],
    title="Area chart",
    subtitle="Soft fill",
    xlabel="Index",
    ylabel="Value",
    color=palettes.CATEGORICAL[2]
)

# Histogram
rng = np.random.default_rng(42)
data = rng.normal(loc=0, scale=1, size=500)
charts.histogram(
    data=data,
    bins=25,
    title="Histogram",
    subtitle="Edge-highlighted bins",
    xlabel="Value",
    ylabel="Frequency",
    color=palettes.CATEGORICAL[4]
)

# Boxplot
charts.boxplot(
    data=[rng.normal(0, 1, 200), rng.normal(1, 0.5, 200)],
    title="Boxplot",
    subtitle="Two distributions",
    xlabel="Group",
    ylabel="Value",
    color=palettes.CATEGORICAL[6]
)

# Violinplot
charts.violinplot(
    data=[rng.normal(0, 1, 200), rng.normal(1, 0.5, 200)],
    title="Violin plot",
    subtitle="Median shown",
    xlabel="Group",
    ylabel="Value",
    color=palettes.CATEGORICAL[7]
)

# Heatmap
matrix = np.round(np.random.rand(6, 8) * 10, 2)
charts.heatmap(
    matrix=matrix,
    xlabels=[f"C{i}" for i in range(1, 9)],
    ylabels=[f"R{i}" for i in range(1, 7)],
    title="Heatmap",
    subtitle="Annotated off by default",
    xlabel="Columns",
    ylabel="Rows",
    cmap="Blues",
    annotate=False
)
