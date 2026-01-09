AuroraViz uses the default `DejaVu Sans` shipped with matplotlib for portability.
You can override fonts via:

```python
from auroraviz import theme
theme.set_font(family="Inter", size=12)
```

Ensure the font is installed on your system.


---

## Examples

### examples/quickstart.py
```python
from auroraviz import theme, charts, palettes

theme.apply()
theme.set_size(8, 5)

# Line
charts.line(
    data=[1, 3, 2, 5, 4],
    title="Line chart",
    subtitle="AuroraViz defaults",
    xlabel="Index",
    ylabel="Value",
    color=palettes.CATEGORICAL[0]
)

# Bar
charts.bar(
    categories=["A", "B", "C", "D"],
    values=[10, 7, 12, 5],
    title="Bar chart",
    subtitle="Minimal ink",
    xlabel="Category",
    ylabel="Value",
    color=palettes.CATEGORICAL[1]
)

# Scatter
charts.scatter(
    x=[1, 2, 3, 4, 5],
    y=[2.2, 2.8, 3.1, 4.0, 4.5],
    title="Scatter chart",
    subtitle="Readable markers",
    xlabel="X",

```
    ylabel="Y",
    color=palettes.CATEGORICAL[3]
)
