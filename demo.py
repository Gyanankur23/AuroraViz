"""
AuroraViz v0.2.0 - Demo Script
===============================
This demonstrates all the features users can experience after pip install auroraviz
Run: python demo.py
"""

import auroraviz as av
import pandas as pd
import numpy as np
import tempfile
import os

print("=" * 60)
print("AuroraViz v0.2.0 - Feature Demo")
print("=" * 60)

# ===========================================================================
# 1. Static Matplotlib charts (v0.1.x surface preserved)
# ===========================================================================
print("\n1. Static Matplotlib Chart (Dark Theme)")
print("-" * 60)

av.apply_dark()
av.charts.line([1, 4, 2, 8, 5, 7], title="Aurora Dark Line")
print("✓ Static line chart created with dark theme")

# ===========================================================================
# 2. Interactive WASM export
# ===========================================================================
print("\n2. Interactive WASM HTML Export")
print("-" * 60)

df = pd.DataFrame({
    "month":   pd.date_range("2024-01", periods=24, freq="MS").astype(str),
    "revenue": np.cumsum(np.random.normal(1000, 200, 24)),
    "segment": np.tile(["Enterprise", "SMB"], 12),
})

with tempfile.TemporaryDirectory() as tmpdir:
    path = av.ignite_interactive(
        df,
        x        = "month",
        y        = "revenue",
        hue      = "segment",
        filename = os.path.join(tmpdir, "revenue_dashboard.html"),
        theme    = "dark",
    )
    print(f"✓ Interactive HTML created: {path}")
    print(f"  File size: {os.path.getsize(path)} bytes")
    print(f"  Open this file in a browser to see interactive chart")

# ===========================================================================
# 3. WebGL point-cloud in Jupyter / Colab
# ===========================================================================
print("\n3. WebGL Point-Cloud Rendering")
print("-" * 60)

N = 50_000  # Smaller for demo (can handle 1M+)
df_webgl = pd.DataFrame({
    "x":        np.random.randn(N),
    "y":        np.random.randn(N),
    "category": np.random.choice(["Alpha", "Beta", "Gamma"], N),
})

print(f"✓ WebGL dataset created with {N:,} points")
print(f"  In Jupyter: av.show_fluid(df_webgl, x_col='x', y_col='y', color_col='category', theme='dark')")
print(f"  This would render instantly with GPU acceleration")

# ===========================================================================
# 4. Theme system
# ===========================================================================
print("\n4. Theme System")
print("-" * 60)

from auroraviz.core.theme import AURORA_DARK, AURORA_LIGHT, get_theme

dark = get_theme("dark")
print(f"✓ Dark theme background: {dark['background']['hex']}")
print(f"✓ Dark theme accent: {dark['css_vars']['--av-accent-1']}")
print(f"✓ Dark theme palette teal: {dark['palette']['teal']['rgb']}")

light = get_theme("light")
print(f"✓ Light theme background: {light['background']['hex']}")

# ===========================================================================
# 5. Palette switching
# ===========================================================================
print("\n5. Palette Switching")
print("-" * 60)

av.set_palette("aurora_dark")
print("✓ Palette set to: aurora_dark")

av.set_palette("vivid")
print("✓ Palette set to: vivid")

av.set_palette(["#FF006E", "#FB5607", "#FFBE0B"])
print("✓ Palette set to: custom colors")

# ===========================================================================
# 6. Scoped theming (context manager)
# ===========================================================================
print("\n6. Scoped Theming")
print("-" * 60)

print("✓ Context manager available:")
print("  with av.use('dark', palette='aurora_dark'):")
print("      av.charts.scatter(x, y, title='Scoped dark chart')")
print("  # Automatically reverts to previous state")

# ===========================================================================
# 7. Package info
# ===========================================================================
print("\n7. Package Information")
print("-" * 60)

print(f"✓ AuroraViz version: {av.__version__}")
print(f"✓ Available functions: {[x for x in dir(av) if not x.startswith('_')]}")

print("\n" + "=" * 60)
print("Demo Complete!")
print("=" * 60)
print("\nKey Features:")
print("• Static matplotlib charts with Aurora themes")
print("• Interactive HTML export (no server required)")
print("• WebGL point-cloud rendering (1M+ points)")
print("• Unified theme system across all renderers")
print("• Palette switching and scoped theming")
print("\nFor full documentation, see README.md")
