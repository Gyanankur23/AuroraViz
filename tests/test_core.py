"""
AuroraViz v0.2.0 — Test Suite
==============================
Covers:
  - Theme colour matrix structure and value validity
  - WASM exporter: file writing, NaN/Inf sanitisation, missing-column errors
  - WebGL engine: Float32 binary packing, base64 round-trip, colour mapping
  - Integration: end-to-end ignite_interactive on synthetic DataFrames
"""

import base64
import math
import os
import struct
import tempfile
import unittest

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Helper — build a minimal synthetic DataFrame
# ---------------------------------------------------------------------------
def _make_df(n: int = 200, with_hue: bool = False,
             inject_nan: bool = False, inject_inf: bool = False) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    df  = pd.DataFrame({
        "x":     rng.uniform(0, 100, n),
        "y":     rng.standard_normal(n),
        "group": rng.choice(["A", "B", "C"], n),
    })
    if inject_nan:
        df.loc[df.sample(20, random_state=1).index, "y"] = float("nan")
    if inject_inf:
        df.loc[df.sample(10, random_state=2).index, "x"] = math.inf
        df.loc[df.sample(5,  random_state=3).index, "x"] = -math.inf
    if not with_hue:
        df = df.drop(columns=["group"])
    return df


# ===========================================================================
# 1. Theme colour matrices
# ===========================================================================
class TestThemeColorMatrices(unittest.TestCase):

    def setUp(self):
        from auroraviz.core.theme import AURORA_DARK, AURORA_LIGHT
        self.dark  = AURORA_DARK
        self.light = AURORA_LIGHT

    def _validate_theme_dict(self, t: dict, label: str):
        # Required top-level keys
        for key in ("name", "background", "surface", "text", "muted",
                    "palette", "series", "gradient_stops", "css_vars"):
            self.assertIn(key, t, msg=f"[{label}] missing key: {key!r}")

        # background must have hex, rgb, rgba
        bg = t["background"]
        self.assertIn("hex",  bg, msg=f"[{label}] background.hex missing")
        self.assertIn("rgb",  bg, msg=f"[{label}] background.rgb missing")
        self.assertIn("rgba", bg, msg=f"[{label}] background.rgba missing")

        # hex format: '#RRGGBB'
        self.assertRegex(bg["hex"], r"^#[0-9A-Fa-f]{6}$",
                         msg=f"[{label}] background.hex bad format")

        # rgb tuple: 3 floats in [0, 1]
        rgb = bg["rgb"]
        self.assertEqual(len(rgb), 3, msg=f"[{label}] background.rgb len != 3")
        for ch in rgb:
            self.assertGreaterEqual(ch, 0.0)
            self.assertLessEqual(ch, 1.0)

        # rgba tuple: 4 floats in [0, 1]
        rgba = bg["rgba"]
        self.assertEqual(len(rgba), 4, msg=f"[{label}] background.rgba len != 4")

        # series: non-empty list of hex strings
        series = t["series"]
        self.assertIsInstance(series, list)
        self.assertGreater(len(series), 0, msg=f"[{label}] series is empty")
        for hex_c in series:
            self.assertRegex(hex_c, r"^#[0-9A-Fa-f]{6}$",
                             msg=f"[{label}] series colour bad format: {hex_c!r}")

        # css_vars: all keys start with '--av-'
        for var in t["css_vars"]:
            self.assertTrue(var.startswith("--av-"),
                            msg=f"[{label}] css_var key unexpected: {var!r}")

        # palette sub-entries have hex
        for pname, pdata in t["palette"].items():
            self.assertIn("hex", pdata,
                          msg=f"[{label}] palette[{pname!r}] missing hex")
            self.assertIn("rgb", pdata,
                          msg=f"[{label}] palette[{pname!r}] missing rgb")

    def test_dark_theme_structure(self):
        self._validate_theme_dict(self.dark, "AURORA_DARK")

    def test_light_theme_structure(self):
        self._validate_theme_dict(self.light, "AURORA_LIGHT")

    def test_dark_and_light_are_distinct(self):
        self.assertNotEqual(self.dark["background"]["hex"],
                            self.light["background"]["hex"])
        self.assertNotEqual(self.dark["name"], self.light["name"])

    def test_get_theme_returns_correct_dict(self):
        from auroraviz.core.theme import get_theme
        self.assertIs(get_theme("dark"),  self.dark)
        self.assertIs(get_theme("light"), self.light)

    def test_palettes_dict_has_required_entries(self):
        from auroraviz.core.theme import PALETTES
        for name in ("aurora", "aurora_dark", "aurora_light", "vivid", "cool", "warm"):
            self.assertIn(name, PALETTES,
                          msg=f"PALETTES missing expected key: {name!r}")
            self.assertIsInstance(PALETTES[name], list)
            self.assertGreater(len(PALETTES[name]), 0)


# ===========================================================================
# 2. WASM exporter
# ===========================================================================
class TestWasmExporter(unittest.TestCase):

    def setUp(self):
        self.df      = _make_df(n=150, with_hue=True)
        self.df_hue  = _make_df(n=150, with_hue=True)
        self.df_nan  = _make_df(n=200, with_hue=False, inject_nan=True)
        self.df_inf  = _make_df(n=200, with_hue=False, inject_inf=True)

    # ── File-writing ----------------------------------------------------------
    def test_creates_html_file(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(self.df, x="x", y="y",
                                     filename=os.path.join(tmpdir, "out.html"))
            self.assertTrue(out.exists(), "Output file does not exist.")
            self.assertGreater(out.stat().st_size, 1_000,
                               "Output file suspiciously small.")

    def test_output_is_valid_html(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(self.df, x="x", y="y",
                                     filename=os.path.join(tmpdir, "out.html"))
            content = out.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("</html>", content)
            self.assertIn("echarts", content,
                          "ECharts CDN script not embedded.")

    def test_dark_theme_css_vars_injected(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(self.df, x="x", y="y",
                                     filename=os.path.join(tmpdir, "out.html"),
                                     theme="dark")
            content = out.read_text(encoding="utf-8")
            self.assertIn("--av-bg", content)
            self.assertIn("--av-accent-1", content)
            self.assertIn("#0B0F19", content,
                          "Aurora Dark background hex not found in output.")

    def test_light_theme_css_vars_injected(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(self.df, x="x", y="y",
                                     filename=os.path.join(tmpdir, "out.html"),
                                     theme="light")
            content = out.read_text(encoding="utf-8")
            self.assertIn("#F7F9FC", content,
                          "Aurora Light background hex not found in output.")

    def test_hue_series_serialised(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(self.df_hue, x="x", y="y", hue="group",
                                     filename=os.path.join(tmpdir, "out.html"))
            content = out.read_text(encoding="utf-8")
            # Categories A, B, C must appear in the JSON data
            for cat in ["A", "B", "C"]:
                self.assertIn(f'"{cat}"', content,
                              f"Hue category {cat!r} missing from output.")

    def test_returns_path_object(self):
        import pathlib
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(self.df, x="x", y="y",
                                     filename=os.path.join(tmpdir, "out.html"))
            self.assertIsInstance(out, pathlib.Path)

    # ── NaN / Inf sanitisation -----------------------------------------------
    def test_nan_rows_excluded_from_output(self):
        """The output chart data must not contain JSON 'null' from NaN values."""
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise
            out = ignite_interactive(self.df_nan, x="x", y="y",
                                     filename=os.path.join(tmpdir, "out.html"))
            content = out.read_text(encoding="utf-8")
            # NaN becomes null in naive JSON — verify it is absent from data
            self.assertNotIn('"y": null', content)

    def test_inf_rows_excluded_without_crash(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(self.df_inf, x="x", y="y",
                                     filename=os.path.join(tmpdir, "out.html"))
            self.assertTrue(out.exists())

    # ── Error handling --------------------------------------------------------
    def test_raises_on_missing_x_column(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                ignite_interactive(self.df, x="nonexistent", y="y",
                                   filename=os.path.join(tmpdir, "out.html"))

    def test_raises_on_missing_y_column(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                ignite_interactive(self.df, x="x", y="nonexistent",
                                   filename=os.path.join(tmpdir, "out.html"))

    def test_raises_on_missing_hue_column(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                ignite_interactive(self.df, x="x", y="y", hue="no_such_col",
                                   filename=os.path.join(tmpdir, "out.html"))

    def test_raises_on_non_dataframe_input(self):
        from auroraviz.interactive import ignite_interactive
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(TypeError):
                ignite_interactive({"x": [1], "y": [2]}, x="x", y="y",
                                   filename=os.path.join(tmpdir, "out.html"))

    def test_all_nan_raises_value_error(self):
        from auroraviz.interactive import ignite_interactive
        bad_df = pd.DataFrame({"x": [float("nan")] * 10,
                               "y": [float("nan")] * 10})
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                ignite_interactive(bad_df, x="x", y="y",
                                   filename=os.path.join(tmpdir, "out.html"))


# ===========================================================================
# 3. WebGL engine — binary memory conversion
# ===========================================================================
class TestWebGLBinaryConversion(unittest.TestCase):

    def test_normalise_range_bounds(self):
        from auroraviz.notebook.webgl import _normalise_range
        arr = np.array([0.0, 25.0, 50.0, 75.0, 100.0])
        out = _normalise_range(arr)
        self.assertGreaterEqual(float(out.min()), -0.93)
        self.assertLessEqual(float(out.max()),     0.93)
        self.assertEqual(out.dtype, np.float32)

    def test_normalise_constant_array_returns_zeros(self):
        from auroraviz.notebook.webgl import _normalise_range
        arr = np.full(50, 7.0)
        out = _normalise_range(arr)
        np.testing.assert_array_equal(out, np.zeros(50, dtype=np.float32))

    def test_vbo_bytes_length(self):
        from auroraviz.notebook.webgl import _build_vbo_bytes
        n = 100
        ones = np.ones(n, dtype=np.float32)
        raw  = _build_vbo_bytes(ones, ones, ones, ones, ones, ones)
        # 6 float32 channels × 4 bytes each × n points
        self.assertEqual(len(raw), n * 6 * 4)

    def test_vbo_bytes_round_trip(self):
        """Values packed into bytes must survive an unpack round-trip."""
        from auroraviz.notebook.webgl import _build_vbo_bytes
        rng  = np.random.default_rng(42)
        n    = 50
        x_a  = rng.standard_normal(n).astype(np.float32)
        y_a  = rng.standard_normal(n).astype(np.float32)
        r_a  = rng.uniform(0, 1, n).astype(np.float32)
        g_a  = rng.uniform(0, 1, n).astype(np.float32)
        b_a  = rng.uniform(0, 1, n).astype(np.float32)
        sz_a = np.full(n, 4.0, dtype=np.float32)

        raw     = _build_vbo_bytes(x_a, y_a, r_a, g_a, b_a, sz_a)
        floats  = np.frombuffer(raw, dtype=np.float32).reshape(n, 6)

        np.testing.assert_array_almost_equal(floats[:, 0], x_a,  decimal=5)
        np.testing.assert_array_almost_equal(floats[:, 1], y_a,  decimal=5)
        np.testing.assert_array_almost_equal(floats[:, 2], r_a,  decimal=5)
        np.testing.assert_array_almost_equal(floats[:, 3], g_a,  decimal=5)
        np.testing.assert_array_almost_equal(floats[:, 4], b_a,  decimal=5)
        np.testing.assert_array_almost_equal(floats[:, 5], sz_a, decimal=5)

    def test_base64_round_trip(self):
        """base64 encode → decode must reproduce the exact bytes."""
        from auroraviz.notebook.webgl import _build_vbo_bytes
        n    = 30
        data = np.arange(n * 6, dtype=np.float32)
        x, y, r, g, b, s = (data[i::6] for i in range(6))
        raw    = _build_vbo_bytes(x, y, r, g, b, s)
        b64    = base64.b64encode(raw).decode("ascii")
        decoded = base64.b64decode(b64)
        self.assertEqual(raw, decoded)

    def test_hex_to_rgb_float_known_values(self):
        from auroraviz.notebook.webgl import _hex_to_rgb_float
        # Pure red
        r, g, b = _hex_to_rgb_float("#FF0000")
        self.assertAlmostEqual(r, 1.0, places=5)
        self.assertAlmostEqual(g, 0.0, places=5)
        self.assertAlmostEqual(b, 0.0, places=5)
        # Pure green
        r, g, b = _hex_to_rgb_float("#00FF00")
        self.assertAlmostEqual(r, 0.0, places=5)
        self.assertAlmostEqual(g, 1.0, places=5)
        self.assertAlmostEqual(b, 0.0, places=5)
        # Aurora teal #00FFCC
        r, g, b = _hex_to_rgb_float("#00FFCC")
        self.assertAlmostEqual(r, 0.0,   places=3)
        self.assertAlmostEqual(g, 1.0,   places=3)
        self.assertAlmostEqual(b, 0.800, places=3)

    def test_color_mapping_no_hue(self):
        from auroraviz.notebook.webgl import _map_colors_to_series
        palette = ["#00FFCC", "#BF5FFF"]
        r, g, b = _map_colors_to_series(None, 50, palette)
        self.assertEqual(len(r), 50)
        # All points should share the first palette colour
        self.assertTrue(np.all(r == r[0]))
        self.assertTrue(np.all(g == g[0]))
        self.assertTrue(np.all(b == b[0]))

    def test_color_mapping_with_categories(self):
        from auroraviz.notebook.webgl import _map_colors_to_series
        palette  = ["#FF0000", "#00FF00", "#0000FF"]
        series   = pd.Series(["A"] * 30 + ["B"] * 20 + ["C"] * 10)
        r, g, b  = _map_colors_to_series(series, 60, palette)
        self.assertEqual(len(r), 60)
        # Category A → red (#FF0000) → r=1, g=0, b=0
        np.testing.assert_array_almost_equal(r[:30], np.ones(30),  decimal=4)
        np.testing.assert_array_almost_equal(g[:30], np.zeros(30), decimal=4)


# ===========================================================================
# 4. Integration — end-to-end
# ===========================================================================
class TestIntegrationEndToEnd(unittest.TestCase):

    def test_full_dark_pipeline_no_hue(self):
        """Complete ignite_interactive run with dark theme, no hue."""
        from auroraviz.interactive import ignite_interactive
        df = _make_df(n=500, with_hue=False)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(df, x="x", y="y",
                                     theme="dark",
                                     filename=os.path.join(tmpdir, "test.html"))
            content = out.read_text(encoding="utf-8")
            self.assertIn("AuroraViz", content)
            self.assertIn("ECharts",   content)

    def test_full_light_pipeline_with_hue(self):
        """Complete ignite_interactive run with light theme and hue grouping."""
        from auroraviz.interactive import ignite_interactive
        df = _make_df(n=300, with_hue=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(df, x="x", y="y", hue="group",
                                     theme="light",
                                     filename=os.path.join(tmpdir, "test_light.html"))
            self.assertGreater(out.stat().st_size, 5_000)

    def test_mixed_nan_inf_pipeline(self):
        """NaN + Inf rows must be silently dropped; file must still be produced."""
        from auroraviz.interactive import ignite_interactive
        df = _make_df(n=400, with_hue=False, inject_nan=True, inject_inf=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = ignite_interactive(df, x="x", y="y",
                                     filename=os.path.join(tmpdir, "mixed.html"))
            self.assertTrue(out.exists())

    def test_package_version(self):
        import auroraviz
        self.assertEqual(auroraviz.__version__, "0.2.0")

    def test_top_level_imports(self):
        """All public API symbols must be importable from the top-level package."""
        import auroraviz as av
        for symbol in ("ignite_interactive", "show_fluid", "AURORA_DARK",
                       "AURORA_LIGHT", "apply_dark", "apply", "get_theme"):
            self.assertTrue(hasattr(av, symbol),
                            msg=f"av.{symbol} not found in top-level package.")

    def test_webgl_vbo_pipeline_smoke(self):
        """
        Smoke-test the full WebGL data pipeline (everything up to display()).
        Skips the IPython display call to remain CI-compatible.
        """
        from auroraviz.notebook.webgl import (
            _normalise_range, _build_vbo_bytes, _map_colors_to_series,
            _hex_to_rgb_float,
        )
        from auroraviz.core.theme import get_theme

        df      = _make_df(n=1000, with_hue=True, inject_nan=True, inject_inf=True)
        work    = df[["x", "y", "group"]].copy()
        for col in ["x", "y"]:
            work[col] = pd.to_numeric(work[col], errors="coerce")
        work.replace([math.inf, -math.inf], float("nan"), inplace=True)
        work.dropna(subset=["x", "y"], inplace=True)

        n       = len(work)
        t       = get_theme("dark")
        palette = t["series"]

        x_norm  = _normalise_range(work["x"].to_numpy())
        y_norm  = _normalise_range(work["y"].to_numpy())
        r, g, b = _map_colors_to_series(work["group"], n, palette)
        sz      = np.full(n, 4.0, dtype=np.float32)
        raw     = _build_vbo_bytes(x_norm, y_norm, r, g, b, sz)
        b64     = base64.b64encode(raw).decode("ascii")

        self.assertGreater(len(b64), 0)
        decoded = base64.b64decode(b64)
        self.assertEqual(len(decoded), n * 6 * 4)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main(verbosity=2)
