"""
auroraviz.notebook.webgl
=========================
Colab-Native WebGL Point-Cloud Engine.

Bypasses JSON serialisation entirely: converts Pandas/Polars series to a
flat base64-encoded Float32Array bitstream, then injects a self-contained
WebGL viewport into the Jupyter/Colab cell via ``IPython.display.HTML``.

Vertex + Fragment shaders read the raw binary buffer off the GPU geometry
pipeline and render a soft-glowing animated particle storm at 1 M+ points.

Public API::

    from auroraviz.notebook import show_fluid

    show_fluid(df, x_col="x", y_col="y", color_col="category", theme="dark")
"""

from __future__ import annotations

import base64
import math
import struct
from typing import Literal

import numpy as np
import pandas as pd

try:
    from IPython.display import HTML, display as _ipy_display
    _IPYTHON_AVAILABLE = True
except ImportError:
    _IPYTHON_AVAILABLE = False

from auroraviz.core.theme import get_theme

# ---------------------------------------------------------------------------
# GLSL shader sources
# ---------------------------------------------------------------------------
_VERTEX_SHADER = """\
#version 300 es
precision highp float;

// Interleaved VBO layout: [x, y, r, g, b, size]
// stride = 6 floats = 24 bytes
layout(location = 0) in float aX;
layout(location = 1) in float aY;
layout(location = 2) in float aR;
layout(location = 3) in float aG;
layout(location = 4) in float aB;
layout(location = 5) in float aSize;

uniform float uTime;
uniform vec2  uResolution;
uniform float uPointScale;

out vec3 vColor;
out float vAlpha;

void main() {
  // Normalised device coords: data already pre-normalised to [-1, 1]
  float x = aX;
  float y = aY;

  // Subtle per-point drift animation — amplitude 0.003 keeps motion organic
  float drift = sin(uTime * 0.8 + aX * 7.3 + aY * 3.7) * 0.003;
  x += drift;
  y += cos(uTime * 0.6 + aY * 5.1 + aX * 2.9) * 0.003;

  gl_Position  = vec4(x, y, 0.0, 1.0);
  gl_PointSize = clamp(aSize * uPointScale, 1.0, 18.0);

  vColor = vec3(aR, aG, aB);
  // Modulate alpha with subtle pulse per point
  vAlpha = 0.65 + 0.25 * sin(uTime * 1.2 + aX * 4.1);
}
"""

_FRAGMENT_SHADER = """\
#version 300 es
precision mediump float;

in vec3  vColor;
in float vAlpha;

out vec4 fragColor;

void main() {
  // Soft circular glow — points outside the radius are discarded
  vec2  coord  = gl_PointCoord - 0.5;
  float dist   = length(coord);
  if (dist > 0.5) discard;

  // Gaussian-ish falloff: bright core, glowing halo
  float core   = 1.0 - smoothstep(0.0, 0.28, dist);   // hard inner
  float glow   = 1.0 - smoothstep(0.20, 0.50, dist);  // soft outer halo
  float alpha  = (core * 0.9 + glow * 0.3) * vAlpha;

  fragColor = vec4(vColor, alpha);
}
"""

# ---------------------------------------------------------------------------
# HTML/JS scaffold — the entire WebGL runtime
# ---------------------------------------------------------------------------
_WEBGL_TEMPLATE = """\
<style>
  #av-fluid-wrap-{uid} {{
    width: {width}px;
    height: {height}px;
    background: {bg};
    border-radius: 8px;
    overflow: hidden;
    position: relative;
    border: 1px solid {border};
  }}
  #av-fluid-canvas-{uid} {{ display: block; }}
  #av-fluid-info-{uid} {{
    position: absolute;
    bottom: 8px; left: 12px;
    font: 11px/1.5 'Segoe UI', system-ui, sans-serif;
    color: {muted};
    pointer-events: none;
  }}
  #av-fluid-badge-{uid} {{
    position: absolute;
    top: 8px; right: 12px;
    font: 10px/1 'Segoe UI', system-ui, sans-serif;
    color: {accent};
    letter-spacing: 0.06em;
    text-transform: uppercase;
    pointer-events: none;
  }}
</style>
<div id="av-fluid-wrap-{uid}">
  <canvas id="av-fluid-canvas-{uid}" width="{width}" height="{height}"></canvas>
  <div id="av-fluid-info-{uid}">{n_points} pts &middot; AuroraViz WebGL &middot; {x_col} &times; {y_col}</div>
  <div id="av-fluid-badge-{uid}">&#9632; LIVE</div>
</div>

<script>
(function() {{
  const CANVAS    = document.getElementById("av-fluid-canvas-{uid}");
  const gl        = CANVAS.getContext("webgl2", {{ antialias: true, alpha: false,
                                                    premultipliedAlpha: false }});
  if (!gl) {{
    CANVAS.insertAdjacentHTML("afterend",
      "<p style='color:#FF4D6D;font-size:13px;'>WebGL2 not available in this environment.</p>");
    return;
  }}

  // ── Decode base64 Float32Array binary payload ──────────────────────
  const B64 = "{b64_payload}";
  const raw = atob(B64);
  const buf = new ArrayBuffer(raw.length);
  const u8  = new Uint8Array(buf);
  for (let i = 0; i < raw.length; i++) u8[i] = raw.charCodeAt(i);
  const floats = new Float32Array(buf);
  // floats layout: [ x0, y0, r0, g0, b0, sz0,  x1, y1, r1, g1, b1, sz1, ... ]
  const STRIDE       = 6;
  const N_POINTS     = floats.length / STRIDE;
  const FLOAT_BYTES  = 4;

  // ── Compile shaders ────────────────────────────────────────────────
  function compileShader(type, src) {{
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS))
      throw new Error("Shader compile error: " + gl.getShaderInfoLog(s));
    return s;
  }}

  const VS_SRC = `{vs}`;
  const FS_SRC = `{fs}`;

  const prog = gl.createProgram();
  gl.attachShader(prog, compileShader(gl.VERTEX_SHADER,   VS_SRC));
  gl.attachShader(prog, compileShader(gl.FRAGMENT_SHADER, FS_SRC));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS))
    throw new Error("Program link error: " + gl.getProgramInfoLog(prog));
  gl.useProgram(prog);

  // ── Uniforms ───────────────────────────────────────────────────────
  const uTime        = gl.getUniformLocation(prog, "uTime");
  const uResolution  = gl.getUniformLocation(prog, "uResolution");
  const uPointScale  = gl.getUniformLocation(prog, "uPointScale");
  gl.uniform2f(uResolution, {width}, {height});
  gl.uniform1f(uPointScale, {point_scale});

  // ── Upload VBO ─────────────────────────────────────────────────────
  const vbo = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
  gl.bufferData(gl.ARRAY_BUFFER, floats, gl.STATIC_DRAW);

  const strideBytes = STRIDE * FLOAT_BYTES;
  // location 0 → aX,    location 1 → aY,   location 2 → aR
  // location 3 → aG,    location 4 → aB,   location 5 → aSize
  for (let loc = 0; loc < 6; loc++) {{
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 1, gl.FLOAT, false, strideBytes, loc * FLOAT_BYTES);
  }}

  // ── WebGL state ────────────────────────────────────────────────────
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE);   // additive blending for the glow effect
  gl.clearColor({bg_r}, {bg_g}, {bg_b}, 1.0);

  // ── Animation loop ─────────────────────────────────────────────────
  let startTime = null;
  function frame(ts) {{
    if (!startTime) startTime = ts;
    const t = (ts - startTime) * 0.001;
    gl.uniform1f(uTime, t);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.drawArrays(gl.POINTS, 0, N_POINTS);
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}})();
</script>
"""


# ---------------------------------------------------------------------------
# Internal: colour mapping helpers
# ---------------------------------------------------------------------------
def _hex_to_rgb_float(hex_color: str) -> tuple[float, float, float]:
    """'#RRGGBB' → (r_norm, g_norm, b_norm) in [0.0, 1.0]."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def _build_vbo_bytes(
    x_arr: np.ndarray,
    y_arr: np.ndarray,
    r_arr: np.ndarray,
    g_arr: np.ndarray,
    b_arr: np.ndarray,
    size_arr: np.ndarray,
) -> bytes:
    """
    Interleave six float32 channels into a packed binary buffer.
    Layout: [x, y, r, g, b, size] × N  (no padding).
    Returned as raw bytes for base64 encoding.
    """
    n = len(x_arr)
    interleaved = np.empty((n, 6), dtype=np.float32)
    interleaved[:, 0] = x_arr.astype(np.float32)
    interleaved[:, 1] = y_arr.astype(np.float32)
    interleaved[:, 2] = r_arr.astype(np.float32)
    interleaved[:, 3] = g_arr.astype(np.float32)
    interleaved[:, 4] = b_arr.astype(np.float32)
    interleaved[:, 5] = size_arr.astype(np.float32)
    return interleaved.tobytes()


def _normalise_range(arr: np.ndarray, lo: float = -0.92, hi: float = 0.92) -> np.ndarray:
    """Min-max normalise to [lo, hi] for NDC space. Returns float32."""
    mn, mx = arr.min(), arr.max()
    if math.isclose(mn, mx, abs_tol=1e-9):
        return np.zeros_like(arr, dtype=np.float32)
    return (((arr - mn) / (mx - mn)) * (hi - lo) + lo).astype(np.float32)


def _map_colors_to_series(
    series_arr: "pd.Series | None",
    n_points: int,
    palette: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Map a categorical series to per-point (r, g, b) float32 arrays.
    Falls back to the first palette colour when color_col is None.
    """
    if series_arr is None:
        r0, g0, b0 = _hex_to_rgb_float(palette[0])
        return (
            np.full(n_points, r0, dtype=np.float32),
            np.full(n_points, g0, dtype=np.float32),
            np.full(n_points, b0, dtype=np.float32),
        )

    categories = pd.Categorical(series_arr)
    color_idx  = categories.codes  # integer code per row
    r = np.empty(n_points, dtype=np.float32)
    g = np.empty(n_points, dtype=np.float32)
    b = np.empty(n_points, dtype=np.float32)
    for i, cat in enumerate(categories.categories):
        hex_c = palette[i % len(palette)]
        rc, gc, bc = _hex_to_rgb_float(hex_c)
        mask = color_idx == i
        r[mask] = rc
        g[mask] = gc
        b[mask] = bc
    return r, g, b


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def show_fluid(
    df: "pd.DataFrame | object",
    x_col: str,
    y_col: str,
    color_col: "str | None" = None,
    theme: Literal["dark", "light"] = "dark",
    width: int = 760,
    height: int = 480,
    point_size: float = 4.0,
    max_points: int = 1_000_000,
    uid: "str | None" = None,
) -> None:
    """
    Render a hard-accelerated WebGL point-cloud directly into a Jupyter or
    Colab cell output area.

    Converts the DataFrame to a flat base64-encoded ``Float32Array`` bitstream
    and injects a vanilla WebGL2 viewport with per-particle glow animation.
    JSON serialisation is never used — the binary path keeps notebooks
    responsive for datasets with 1 M+ points.

    Parameters
    ----------
    df : pd.DataFrame (or any object with a ``to_pandas()`` method, e.g. Polars)
        Source data.
    x_col : str
        Column name for the horizontal axis (numeric).
    y_col : str
        Column name for the vertical axis (numeric).
    color_col : str, optional
        Categorical column to map points to distinct series colours.
    theme : "dark" | "light"
        Which AuroraViz palette to use.
    width : int
        Canvas width in pixels.
    height : int
        Canvas height in pixels.
    point_size : float
        Base point radius in pixels (GPU-scaled by device resolution).
    max_points : int
        Cap on displayed points. If the DataFrame exceeds this, a uniform
        random sample is taken (reproducible via seed 42).
    uid : str, optional
        Unique suffix for DOM element IDs. Auto-generated when not given.

    Raises
    ------
    ImportError
        If ``IPython`` is not available (non-notebook environment).
    ValueError
        If required columns are missing or no finite data remains.
    TypeError
        If *df* is not a supported DataFrame type.
    """
    if not _IPYTHON_AVAILABLE:
        raise ImportError(
            "IPython is required for show_fluid. "
            "Install it with: pip install ipython"
        )

    # ── Coerce Polars / other DataFrame-like objects to pandas ────────
    if hasattr(df, "to_pandas") and not isinstance(df, pd.DataFrame):
        df = df.to_pandas()
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame (or Polars), got {type(df).__name__!r}.")

    required = [x_col, y_col] + ([color_col] if color_col else [])
    missing  = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Column(s) not found in DataFrame: {missing}")

    # ── Sanitise: drop NaN / ±Inf in numeric columns ──────────────────
    work = df[required].copy()
    for col in [x_col, y_col]:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    work.replace([math.inf, -math.inf], float("nan"), inplace=True)
    work.dropna(subset=[x_col, y_col], inplace=True)

    if work.empty:
        raise ValueError(
            "No finite data remains after removing NaN/Inf in "
            f"{x_col!r} and {y_col!r}."
        )

    # ── Cap points ────────────────────────────────────────────────────
    if len(work) > max_points:
        work = work.sample(n=max_points, random_state=42)

    n_points = len(work)
    t        = get_theme(theme)
    palette  = t["series"]

    # ── Build per-point arrays ────────────────────────────────────────
    x_norm = _normalise_range(work[x_col].to_numpy())
    y_norm = _normalise_range(work[y_col].to_numpy())

    color_series = work[color_col] if color_col else None
    r_arr, g_arr, b_arr = _map_colors_to_series(color_series, n_points, palette)

    # Size: uniform for now — future releases can map a numeric column
    size_arr = np.full(n_points, point_size, dtype=np.float32)

    # ── Pack to Float32 binary blob → base64 ─────────────────────────
    raw_bytes  = _build_vbo_bytes(x_norm, y_norm, r_arr, g_arr, b_arr, size_arr)
    b64_payload = base64.b64encode(raw_bytes).decode("ascii")

    # ── Background RGB for WebGL clearColor ───────────────────────────
    bg_r, bg_g, bg_b = t["background"]["rgb"]

    # ── Unique element ID (prevents collision across multiple cells) ───
    import uuid as _uuid
    cell_uid = uid or _uuid.uuid4().hex[:8]

    # ── Compute point scale relative to canvas DPI ────────────────────
    point_scale = max(1.0, height / 480.0)

    html_src = _WEBGL_TEMPLATE.format(
        uid           = cell_uid,
        width         = width,
        height        = height,
        b64_payload   = b64_payload,
        vs            = _VERTEX_SHADER.replace("`", "\\`"),
        fs            = _FRAGMENT_SHADER.replace("`", "\\`"),
        n_points      = f"{n_points:,}",
        x_col         = x_col,
        y_col         = y_col,
        bg            = t["background"]["hex"],
        border        = t["css_vars"]["--av-border"],
        muted         = t["muted"]["hex"],
        accent        = t["css_vars"]["--av-accent-1"],
        bg_r          = bg_r,
        bg_g          = bg_g,
        bg_b          = bg_b,
        point_scale   = point_scale,
    )

    _ipy_display(HTML(html_src))
