from .theme import apply, set_font, set_dpi, set_size
from .palettes import CATEGORICAL, SEQUENTIAL, DIVERGING
from .charts import (
    line, area, bar, scatter, histogram, boxplot, violinplot, heatmap
)

__all__ = [
    "apply", "set_font", "set_dpi", "set_size",
    "CATEGORICAL", "SEQUENTIAL", "DIVERGING",
    "line", "area", "bar", "scatter", "histogram", "boxplot", "violinplot", "heatmap"
]
