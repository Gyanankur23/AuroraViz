AuroraViz uses the default `DejaVu Sans` shipped with matplotlib for portability.
You can override fonts via:

```python
from auroraviz import theme
theme.set_font(family="Inter", size=12)

