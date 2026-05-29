"""
auroraviz.interactive.wasm_exporter
=====================================
Auto-WASM Single-File HTML Exporter.

Serializes a Pandas DataFrame into a fully self-contained, serverless
HTML file powered by Apache ECharts (CDN-backed), styled with AuroraViz
theme CSS variables, with pan/zoom, download toolbar, and responsive
window resizing — zero server dependencies, works offline after first CDN load.

Public API::

    from auroraviz.interactive import ignite_interactive

    ignite_interactive(df, x="date", y="revenue", hue="segment",
                       filename="dashboard.html", theme="dark")
"""

from __future__ import annotations

import json
import math
import pathlib
from typing import Literal

import pandas as pd
from jinja2 import Template

from auroraviz.core.theme import AURORA_DARK, AURORA_LIGHT, get_theme

# ---------------------------------------------------------------------------
# Internal: sanitise DataFrame for JSON serialisation
# ---------------------------------------------------------------------------
def _sanitise(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Drop rows with NaN or ±Inf in the selected columns.
    Returns a clean copy — never modifies the caller's DataFrame.
    """
    sub = df[cols].copy()
    # Replace ±inf with NaN then drop
    sub.replace([math.inf, -math.inf], float("nan"), inplace=True)
    sub.dropna(inplace=True)
    return sub


def _df_to_json_records(df: pd.DataFrame) -> str:
    """
    Convert a sanitised DataFrame to a JSON-safe list-of-dicts string.
    Datetime columns are converted to ISO-8601 strings.
    Numeric columns are rounded to 8 significant figures to avoid float noise.
    """
    out = df.copy()
    for col in out.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
        out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%S")
    for col in out.select_dtypes(include="float").columns:
        out[col] = out[col].map(lambda v: round(v, 8) if pd.notna(v) else None)
    return json.dumps(out.to_dict(orient="records"), ensure_ascii=False)


# ---------------------------------------------------------------------------
# Jinja2 HTML template
# ---------------------------------------------------------------------------
_HTML_TEMPLATE = Template(r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{ title }}</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>
    /* ── AuroraViz CSS variable injection ───────────────────────────── */
    :root {
      {% for var, val in css_vars.items() %}
      {{ var }}: {{ val }};
      {% endfor %}
      --av-radius: 8px;
      --av-font: 'Segoe UI', system-ui, -apple-system, sans-serif;
      --av-transition: 0.2s ease;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html, body {
      height: 100%;
      background: var(--av-bg);
      color: var(--av-text);
      font-family: var(--av-font);
      overflow: hidden;
    }

    /* ── Shell layout ────────────────────────────────────────────────── */
    #av-shell {
      display: flex;
      flex-direction: column;
      height: 100vh;
      padding: 16px;
      gap: 12px;
    }

    /* ── Header bar ──────────────────────────────────────────────────── */
    #av-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 16px;
      background: var(--av-surface);
      border: 1px solid var(--av-border);
      border-radius: var(--av-radius);
      flex-shrink: 0;
    }

    #av-header h1 {
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--av-accent-1);
    }

    #av-header span.badge {
      font-size: 11px;
      color: var(--av-muted);
      margin-left: 10px;
      font-weight: 400;
    }

    /* ── Toolbar ─────────────────────────────────────────────────────── */
    #av-toolbar {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .av-btn {
      cursor: pointer;
      padding: 5px 12px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid var(--av-border);
      border-radius: 4px;
      background: transparent;
      color: var(--av-text);
      transition: background var(--av-transition), color var(--av-transition);
      letter-spacing: 0.03em;
    }

    .av-btn:hover {
      background: var(--av-accent-1);
      color: var(--av-bg);
      border-color: var(--av-accent-1);
    }

    .av-btn.active {
      background: var(--av-accent-2);
      color: #fff;
      border-color: var(--av-accent-2);
    }

    /* ── Chart container ─────────────────────────────────────────────── */
    #av-chart {
      flex: 1;
      background: var(--av-surface);
      border: 1px solid var(--av-border);
      border-radius: var(--av-radius);
      min-height: 0;
    }

    /* ── Footer ──────────────────────────────────────────────────────── */
    #av-footer {
      text-align: center;
      font-size: 11px;
      color: var(--av-muted);
      flex-shrink: 0;
    }

    #av-footer a {
      color: var(--av-accent-1);
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div id="av-shell">

    <!-- Header -->
    <div id="av-header">
      <div>
        <h1>AuroraViz Workspace</h1>
        <span class="badge">{{ n_rows }} rows · {{ n_cols }} columns · {{ theme_name }}</span>
      </div>
      <div id="av-toolbar">
        <button class="av-btn" id="btn-zoom-reset" title="Reset zoom">⟳ Reset</button>
        <button class="av-btn" id="btn-download-png" title="Download as PNG">⬇ PNG</button>
        <button class="av-btn" id="btn-download-svg" title="Download as SVG">⬇ SVG</button>
        <button class="av-btn" id="btn-toggle-type" title="Toggle chart type">⇌ Type</button>
      </div>
    </div>

    <!-- Chart -->
    <div id="av-chart"></div>

    <!-- Footer -->
    <div id="av-footer">
      Generated by <a href="https://github.com/gyanankur/auroraviz" target="_blank">AuroraViz v0.2.0</a>
      &nbsp;·&nbsp; MetaMindset Labs
    </div>

  </div>

  <script>
    // ── Data payload (sanitised, NaN/Inf-free) ────────────────────────
    const AV_RECORDS = {{ records_json }};
    const AV_X      = {{ x_json }};
    const AV_Y      = {{ y_json }};
    const AV_HUE    = {{ hue_json }};
    const AV_SERIES = {{ series_json }};
    const AV_COLORS = {{ colors_json }};

    // ── Chart init ────────────────────────────────────────────────────
    const chartEl = document.getElementById("av-chart");
    const chart   = echarts.init(chartEl, null, { renderer: "canvas" });

    let currentType = "line";   // toggles between line / bar / scatter

    // ── Build ECharts series from data ────────────────────────────────
    function buildSeries(type) {
      if (AV_HUE) {
        // Group by hue column
        return AV_SERIES.map((name, i) => {
          const rows = AV_RECORDS.filter(r => String(r[AV_HUE]) === String(name));
          return {
            name: String(name),
            type: type,
            smooth: type === "line",
            symbol: type === "scatter" ? "circle" : "none",
            symbolSize: 5,
            data: rows.map(r => [r[AV_X], r[AV_Y]]),
            itemStyle: { color: AV_COLORS[i % AV_COLORS.length] },
            lineStyle: { width: 2 },
            areaStyle: type === "line" ? {
              color: {
                type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: AV_COLORS[i % AV_COLORS.length] + "55" },
                  { offset: 1, color: AV_COLORS[i % AV_COLORS.length] + "00" },
                ]
              }
            } : undefined,
          };
        });
      }
      // No hue — single series
      return [{
        name: AV_Y,
        type: type,
        smooth: type === "line",
        symbol: type === "scatter" ? "circle" : "none",
        symbolSize: 5,
        data: AV_RECORDS.map(r => [r[AV_X], r[AV_Y]]),
        itemStyle: { color: AV_COLORS[0] },
        lineStyle: { width: 2 },
        areaStyle: type === "line" ? {
          color: {
            type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: AV_COLORS[0] + "55" },
              { offset: 1, color: AV_COLORS[0] + "00" },
            ]
          }
        } : undefined,
      }];
    }

    // ── Base ECharts option ───────────────────────────────────────────
    function buildOption(type) {
      return {
        backgroundColor: "transparent",
        textStyle: { color: "{{ text_color }}", fontFamily: "Segoe UI, system-ui, sans-serif" },
        animation: true,
        animationDuration: 800,
        animationEasing: "cubicOut",
        tooltip: {
          trigger: "axis",
          backgroundColor: "{{ surface_color }}",
          borderColor: "{{ border_color }}",
          textStyle: { color: "{{ text_color }}", fontSize: 12 },
          axisPointer: { type: "cross", lineStyle: { color: "{{ muted_color }}", opacity: 0.5 } },
        },
        legend: {
          show: Boolean(AV_HUE),
          top: "4px",
          right: "8px",
          textStyle: { color: "{{ text_color }}", fontSize: 12 },
          icon: "roundRect",
        },
        grid: {
          left: "3%", right: "4%", bottom: "60px", top: AV_HUE ? "40px" : "20px",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: type === "bar",
          axisLine:  { lineStyle: { color: "{{ border_color }}" } },
          axisLabel: { color: "{{ muted_color }}", fontSize: 11 },
          splitLine: { show: false },
          name: AV_X,
          nameTextStyle: { color: "{{ muted_color }}", fontSize: 11 },
          nameLocation: "end",
        },
        yAxis: {
          type: "value",
          axisLine:  { lineStyle: { color: "{{ border_color }}" } },
          axisLabel: { color: "{{ muted_color }}", fontSize: 11 },
          splitLine: { lineStyle: { color: "{{ border_color }}", opacity: 0.4 } },
          name: AV_Y,
          nameTextStyle: { color: "{{ muted_color }}", fontSize: 11 },
        },
        dataZoom: [
          { type: "inside", xAxisIndex: 0, filterMode: "filter" },
          {
            type: "slider",
            xAxisIndex: 0,
            height: 22,
            bottom: 8,
            borderColor: "{{ border_color }}",
            fillerColor: "{{ accent1_color }}22",
            handleStyle: { color: "{{ accent1_color }}" },
            textStyle: { color: "{{ muted_color }}", fontSize: 10 },
            dataBackground: {
              lineStyle: { color: "{{ accent1_color }}88" },
              areaStyle: { color: "{{ accent1_color }}22" },
            },
          },
        ],
        toolbox: { show: false },   // We use our own custom toolbar
        series: buildSeries(type),
      };
    }

    chart.setOption(buildOption(currentType));

    // ── Responsive resize ─────────────────────────────────────────────
    const resizeObserver = new ResizeObserver(() => chart.resize());
    resizeObserver.observe(chartEl);
    window.addEventListener("resize", () => chart.resize());

    // ── Toolbar handlers ──────────────────────────────────────────────
    document.getElementById("btn-zoom-reset").addEventListener("click", () => {
      chart.dispatchAction({ type: "dataZoom", start: 0, end: 100 });
    });

    document.getElementById("btn-download-png").addEventListener("click", () => {
      const url = chart.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: "{{ bg_color }}" });
      const link = document.createElement("a");
      link.href = url;
      link.download = "auroraviz_chart.png";
      link.click();
    });

    document.getElementById("btn-download-svg").addEventListener("click", () => {
      // Re-render to SVG renderer for export quality
      const svgChart = echarts.init(document.createElement("div"), null,
                                    { renderer: "svg", width: 1200, height: 700 });
      svgChart.setOption(buildOption(currentType));
      const svgStr = svgChart.renderToSVGString();
      const blob = new Blob([svgStr], { type: "image/svg+xml" });
      const url  = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "auroraviz_chart.svg";
      link.click();
      URL.revokeObjectURL(url);
      svgChart.dispose();
    });

    const typeSequence = ["line", "bar", "scatter"];
    document.getElementById("btn-toggle-type").addEventListener("click", () => {
      const idx = typeSequence.indexOf(currentType);
      currentType = typeSequence[(idx + 1) % typeSequence.length];
      chart.setOption(buildOption(currentType), { replaceMerge: ["series"] });
      document.getElementById("btn-toggle-type").textContent = "⇌ " + currentType[0].toUpperCase() + currentType.slice(1);
    });
  </script>
</body>
</html>
""")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def ignite_interactive(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: "str | None" = None,
    filename: str = "auroraviz_workspace.html",
    theme: Literal["dark", "light"] = "dark",
) -> pathlib.Path:
    """
    Export a DataFrame to a fully self-contained, serverless HTML workspace.

    The output file contains an Apache ECharts chart with AuroraViz theming,
    responsive pan/zoom, PNG/SVG download buttons, and chart-type toggle.
    No build step, no server — open directly in any modern browser.

    Parameters
    ----------
    df : pd.DataFrame
        Source data. Must contain columns ``x`` and ``y`` (and ``hue`` if given).
    x : str
        Column name for the horizontal axis.
    y : str
        Column name for the vertical (metric) axis. Must be numeric.
    hue : str, optional
        Column name to split into multiple series.
    filename : str
        Output path. Relative paths are resolved from the current working directory.
    theme : "dark" | "light"
        Which AuroraViz theme to embed.

    Returns
    -------
    pathlib.Path
        Absolute path to the generated HTML file.

    Raises
    ------
    ValueError
        If ``x``, ``y``, or ``hue`` are not present in *df*.
    TypeError
        If *df* is not a ``pd.DataFrame``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df).__name__!r}.")

    required_cols = [x, y] + ([hue] if hue else [])
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Column(s) not found in DataFrame: {missing}")

    t = get_theme(theme)
    css_vars = t["css_vars"]
    series_colors = t["series"]

    # ── Sanitise: drop NaN / ±Inf rows in relevant columns ────────────
    clean = _sanitise(df, required_cols)
    if clean.empty:
        raise ValueError(
            "DataFrame has no finite rows after removing NaN/Inf values in "
            f"columns: {required_cols}"
        )

    # ── Compute hue series labels ─────────────────────────────────────
    hue_series_labels: list = sorted(clean[hue].unique().tolist()) if hue else []

    # ── Serialise ─────────────────────────────────────────────────────
    records_json   = _df_to_json_records(clean[required_cols])
    x_json         = json.dumps(x)
    y_json         = json.dumps(y)
    hue_json       = json.dumps(hue)
    series_json    = json.dumps(hue_series_labels)
    colors_json    = json.dumps(series_colors)

    # ── Render template ───────────────────────────────────────────────
    html = _HTML_TEMPLATE.render(
        title          = f"AuroraViz — {y} by {x}",
        theme_name     = t["name"],
        n_rows         = len(clean),
        n_cols         = len(df.columns),
        css_vars       = css_vars,
        records_json   = records_json,
        x_json         = x_json,
        y_json         = y_json,
        hue_json       = hue_json,
        series_json    = series_json,
        colors_json    = colors_json,
        # Individual colour references for the inline JS template strings
        bg_color       = t["background"]["hex"],
        surface_color  = t["surface"]["hex"],
        text_color     = t["text"]["hex"],
        muted_color    = t["muted"]["hex"],
        border_color   = css_vars["--av-border"],
        accent1_color  = css_vars["--av-accent-1"],
        accent2_color  = css_vars["--av-accent-2"],
    )

    # ── Write file ────────────────────────────────────────────────────
    out_path = pathlib.Path(filename).expanduser().resolve()
    out_path.write_text(html, encoding="utf-8")
    return out_path
