# AuroraViz


[![Python Versions](https://img.shields.io/pypi/pyversions/auroraviz.svg)](https://pypi.org/project/auroraviz/)
[![License](https://img.shields.io/github/license/Gyanankur23/AuroraViz.svg)](https://github.com/Gyanankur23/AuroraViz/blob/main/LICENSE)
[![Build Status](https://github.com/Gyanankur23/AuroraViz/actions/workflows/publish.yml/badge.svg)](https://github.com/Gyanankur23/AuroraViz/actions)
[![Downloads](https://img.shields.io/pypi/dm/auroraviz.svg)](https://pypi.org/project/auroraviz/)
[![GitHub stars](https://img.shields.io/github/stars/Gyanankur23/AuroraViz.svg?style=social&label=Star)](https://github.com/Gyanankur23/AuroraViz)

AuroraViz is a modern Python visualization library with a unique dark/light theme toggle.  
Unlike other libraries, AuroraViz automatically inverts text colors when switching to dark mode, so your charts are always readable.

---

## PyPi Official Publication Badge

[![PyPI version](https://img.shields.io/pypi/v/auroraviz.svg)](https://pypi.org/project/auroraviz/)

## Quick Start in Google Colab

Run the following single block in Colab to clone the repo, import modules, and generate one chart in light mode and one chart in dark mode:

1. Clone the repository

```python

!git clone https://github.com/Gyanankur23/AuroraViz.git
import sys
sys.path.append("/content/AuroraViz/src")
```
2. Import modules
from auroraviz import theme, charts, palettes
import matplotlib.pyplot as plt

3. Run a chart in Light Mode
```python
theme.apply()
theme.set_palette("aurora")
fig, ax = charts.histogram(
    data=[1, 3, 2, 5, 4],
    title="AuroraViz Light Mode",
    xlabel="Index",
    ylabel="Value",
    color=palettes.CATEGORICAL[0]
)
plt.show()
```
4. Run a chart in Dark Mode
```python

theme.apply_dark()
theme.set_palette("vivid")
fig, ax = charts.histogram(
    data=[1, 3, 2, 5, 4],
    title="AuroraViz Dark Mode",
    xlabel="Index",
    ylabel="Value",
    color=palettes.CATEGORICAL[1]
)
plt.show()
`
```
---

## Notes

- The theme.apply() and theme.apply_dark() functions are the only commands you need to toggle between light and dark.  
- Palettes can be set globally with theme.setpalette("aurora") or theme.setpalette("vivid").  
- All chart types (charts.line, charts.bar, charts.scatter, etc.) respect the theme toggle automatically.

---

## Why AuroraViz is Different
- Auto text inversion — titles, labels, ticks, legends adapt instantly.  
- Palette flexibility — choose built‑in palettes or pass your own list of colors.  
- Consistent API — every chart type uses the same syntax:  
  `python
  charts.<chart_type>(data, title="...", xlabel="...", ylabel="...", color=...)
  `

---

## All Charts Display (Live Proof)

![AuroraViz Light Mode](charts/light.jpg)  
![AuroraViz Dark Mode](charts/dark.jpg)

## Showcase PDF

To generate a PDF showcase in Colab:
1. Run the light and dark examples above.
2. Use Colab’s File → Print → Save as PDF to export the notebook.
3. Share the PDF as a visual demo of AuroraViz.


## License

Protected by MIT License

## Created by
Gyanankur Baruah

Github:- [https://www.github.com/Gyanankur23]


---
