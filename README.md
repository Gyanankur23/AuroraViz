# AuroraViz v0.2.0

[![PyPI](https://img.shields.io/pypi/v/auroraviz?color=00FFCC&label=PyPI)](https://pypi.org/project/auroraviz/)
[![Python](https://img.shields.io/pypi/pyversions/auroraviz?color=BF5FFF)](https://pypi.org/project/auroraviz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-00D4FF.svg)](LICENSE)

> A world-class Python visualization framework with signature Aurora themes,
> zero-config WASM HTML export, and GPU-accelerated WebGL point-cloud rendering.

---

## What's new in 0.2.0

| Feature | API | Description |
|---|---|---|
| **WASM HTML Exporter** | `av.ignite_interactive()` | One call → fully self-contained, serverless HTML file powered by Apache ECharts. Pan, zoom, PNG/SVG download, chart-type toggle — no build step. |
| **WebGL Point-Cloud** | `av.show_fluid()` | Hard-accelerated binary streaming into Jupyter/Colab. Converts DataFrames to `Float32Array` bitstreams, skipping JSON entirely. Renders 1 M+ points with per-particle glow animation via vanilla WebGL2 shaders. |
| **Unified Theme Core** | `av.AURORA_DARK` / `av.AURORA_LIGHT` | Structured color matrices (Hex, RGB, RGBA) shared across all rendering engines — static Matplotlib, WASM, and WebGL. |

---

## Installation

```bash
pip install auroraviz
```

Core dependencies: `pandas`, `matplotlib`, `jinja2`, `ipython`.  
No compiled extensions. No Rust. No C build step. Pure Python.

---

## Quick Start

### Static Matplotlib charts (v0.1.x surface preserved)

```python
import auroraviz as av

av.apply_dark()
av.charts.line([1, 4, 2, 8, 5, 7], title="Aurora Dark Line")
```

### Interactive WASM export

```python
import auroraviz as av
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "month":   pd.date_range("2024-01", periods=24, freq="MS").astype(str),
    "revenue": np.cumsum(np.random.normal(1000, 200, 24)),
    "segment": np.tile(["Enterprise", "SMB"], 12),
})

path = av.ignite_interactive(
    df,
    x        = "month",
    y        = "revenue",
    hue      = "segment",
    filename = "revenue_dashboard.html",
    theme    = "dark",
)
print(f"Open in browser: {path}")
```

The output file is a **single, portable HTML file** — share by email, embed in
a static site, or open locally. No internet connection required after the first
CDN load of ECharts (~1 MB).

### WebGL point-cloud in Jupyter / Colab

```python
import auroraviz as av
import pandas as pd
import numpy as np

N = 500_000
df = pd.DataFrame({
    "x":        np.random.randn(N),
    "y":        np.random.randn(N),
    "category": np.random.choice(["Alpha", "Beta", "Gamma"], N),
})

av.show_fluid(df, x_col="x", y_col="y", color_col="category", theme="dark")
```

Renders in under a second for 500 K points. At 1 M points, JSON-based
approaches typically crash the notebook — `show_fluid` streams raw binary
to the GPU and stays responsive.

---

## Theme system

```python
from auroraviz.core.theme import AURORA_DARK, AURORA_LIGHT, get_theme

# Access structured colour matrices
dark = get_theme("dark")
print(dark["background"]["hex"])   # '#0B0F19'
print(dark["palette"]["teal"]["rgb"])  # (0.0, 1.0, 0.8)
print(dark["css_vars"]["--av-accent-1"])  # '#00FFCC'

# Inject into Matplotlib
import auroraviz as av
av.apply_dark()   # or av.apply() for light
```

### Palette switching

```python
av.set_palette("aurora_dark")  # default dark series
av.set_palette("vivid")        # classic Tableau-style
av.set_palette(["#FF006E", "#FB5607", "#FFBE0B"])  # custom
```

### Scoped theming (context manager)

```python
with av.use("dark", palette="aurora_dark"):
    av.charts.scatter(x, y, title="Scoped dark chart")
# Reverts to previous state automatically
```

---

## Project structure

```
auroraviz/
├── pyproject.toml
├── README.md
├── tests/
│   ├── __init__.py
│   └── test_core.py          # unittest suite (theme, WASM, WebGL, integration)
└── src/
    └── auroraviz/
        ├── __init__.py        # unified public API
        ├── core/
        │   ├── __init__.py
        │   └── theme.py       # colour matrices + Matplotlib rcParams injection
        ├── interactive/
        │   ├── __init__.py
        │   └── wasm_exporter.py   # ignite_interactive()
        └── notebook/
            ├── __init__.py
            └── webgl.py           # show_fluid()
```

---

## Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
# or
python -m unittest discover -s tests -v
```

---

## License

MIT © 2025 Gyanankur Baruah — MetaMindset Labs
