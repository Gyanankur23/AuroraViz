# Fonts in AuroraViz

AuroraViz uses the default `DejaVu Sans` font shipped with matplotlib to ensure portability across systems.  
This choice guarantees that charts render consistently without requiring external font installations.

## Customizing Fonts

You can override the default font family and size using the `theme.set_font()` function:

```python
from auroraviz import theme
```

# Change font family and size
theme.set_font(family="Inter", size=12)
