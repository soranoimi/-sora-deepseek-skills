# -*- coding: utf-8 -*-
"""
eeplot.py — 电工图形生成器 / EE diagram generator
DeepSeek Basic Electrical Problem Solver · deepseek基础电工题目解析

生成三类图（Generate three diagram types）:
  1. 电路图 circuit diagrams（GB/教材元件符号: 电阻矩形、电容、电感、电源、开关、
     熔断器、接触器、热继电器、灯、电机、变压器、仪表、接地等）
  2. 正弦波形图 sine waveforms（多曲线、坐标轴、峰值线、图例）
  3. 相量图 phasor diagrams（有效值相量、角度弧、求和叠加）

零依赖（stdlib），PNG 后端使用 Pillow（DSH 自带）+ Windows 中文字体。
Zero deps beyond stdlib; PNG backend needs Pillow (bundled with DSH) + a CJK font.

用法 / Usage:
  # 库方式（推荐，灵活性最高）
  from eeplot import Scene, resistor, ...
  # CLI 方式
  python eeplot.py wave spec.json      # spec: {"type":"wave"|"phasor"|"circuit", ...}
  python eeplot.py demo                # 生成示例图到 ../examples/
"""
import json
import math
import os
import sys

# ---------------------------------------------------------------- 颜色与样式

DARK = "#111827"          # 主线条 / main strokes
GRID = "#d1d5db"          # 网格线 / gridlines
GRAY = "#6b7280"          # 次要文字 / muted text
SERIES = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"]
WHITE = "#ffffff"

FONT_STACK = "'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC', sans-serif"


def _fmt_deg(deg):
    """角度格式化（与 ee.py 的 fmt_deg 保持一致）。Format angle with degree sign."""
    d = deg % 360.0
    if d >= 180.0:
        d -= 360.0
    sign = "−" if d < 0 else ""
    return f"{sign}{abs(d):g}°"


# ---------------------------------------------------------------- 场景模型

class Scene:
    """图元场景（与后端无关）。Scene of primitives (backend-agnostic)."""

    def __init__(self, w, h, bg=WHITE):
        self.w, self.h, self.bg = w, h, bg
        self.items = []

    def line(self, x1, y1, x2, y2, width=2.0, color=DARK, dash=None, arrow=False):
        self.items.append(("line", x1, y1, x2, y2, width, color, dash, arrow))

    def polyline(self, pts, width=2.0, color=DARK, dash=None):
        self.items.append(("polyline", pts, width, color, dash))

    def polygon(self, pts, fill=None, stroke=DARK, width=2.0):
        self.items.append(("polygon", pts, fill, stroke, width))

    def circle(self, cx, cy, r, fill=None, stroke=DARK, width=2.0):
        self.items.append(("circle", cx, cy, r, fill, stroke, width))

    def text(self, x, y, s, size=13, color=DARK, anchor="middle", bold=False, italic=False):
        self.items.append(("text", x, y, s, size, color, anchor, bold, italic))


def _pts_str(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def _dash_segs(x1, y1, x2, y2, dash):
    """把虚线拆成小段（PNG 无原生虚线）。Split a dashed line into segments."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return []
    ux, uy = dx / length, dy / length
    segs, on, t = [], True, 0.0
    while t < length:
        step = dash if on else dash * 0.7
        t2 = min(t + step, length)
        if on:
            segs.append((x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2))
        on = not on
        t = t2
    return segs


def _arrow_head(x2, y2, ang, size=9.0, color=DARK, width=2.0, scene=None):
    """在 (x2,y2) 画箭头（ang=线段方向角）。Draw arrowhead at line end."""
    a1, a2 = ang + math.radians(150), ang - math.radians(150)
    p1 = (x2 + size * math.cos(a1), y2 + size * math.sin(a1))
    p2 = (x2 + size * math.cos(a2), y2 + size * math.sin(a2))
    segs = [p1, (x2, y2), p2]
    if scene is None:
        return segs
    scene.polyline(segs, width=width, color=color)
    return segs


def render_svg(scene):
    """场景 → SVG 文本。Scene → SVG string."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{scene.w}" height="{scene.h}" '
        f'viewBox="0 0 {scene.w} {scene.h}" font-family="{FONT_STACK}">'
    ]
    if scene.bg:
        parts.append(f'<rect width="100%" height="100%" fill="{scene.bg}"/>')
    for it in scene.items:
        kind = it[0]
        if kind == "line":
            _, x1, y1, x2, y2, w, c, dash, arrow = it
            if dash:
                for sx, sy, ex, ey in _dash_segs(x1, y1, x2, y2, dash):
                    parts.append(f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" '
                                 f'stroke="{c}" stroke-width="{w}"/>')
            else:
                parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                             f'stroke="{c}" stroke-width="{w}"/>')
            if arrow:
                ang = math.atan2(y2 - y1, x2 - x1)
                _arrow_head(x2, y2, ang, color=c, width=w, scene=None)
                segs = _arrow_head(x2, y2, ang, color=c, width=w, scene=None)
                parts.append(f'<polyline points="{_pts_str(segs)}" fill="none" stroke="{c}" stroke-width="{w}"/>')
        elif kind == "polyline":
            _, pts, w, c, dash = it
            if dash:
                for i in range(len(pts) - 1):
                    for sx, sy, ex, ey in _dash_segs(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], dash):
                        parts.append(f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" '
                                     f'stroke="{c}" stroke-width="{w}"/>')
            else:
                parts.append(f'<polyline points="{_pts_str(pts)}" fill="none" stroke="{c}" stroke-width="{w}" '
                             f'stroke-linejoin="round" stroke-linecap="round"/>')
        elif kind == "polygon":
            _, pts, fill, stroke, w = it
            f = f' fill="{fill}"' if fill else ' fill="none"'
            parts.append(f'<polygon points="{_pts_str(pts)}"{f} stroke="{stroke}" stroke-width="{w}"/>')
        elif kind == "circle":
            _, cx, cy, r, fill, stroke, w = it
            f = f' fill="{fill}"' if fill else ' fill="none"'
            parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"{f} stroke="{stroke}" stroke-width="{w}"/>')
        elif kind == "text":
            _, x, y, s, size, c, anchor, bold, italic = it
            fw = ' font-weight="bold"' if bold else ''
            fs = ' font-style="italic"' if italic else ''
            parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{c}" text-anchor="{anchor}" '
                         f'dominant-baseline="central"{fw}{fs}>{_svg_escape(s)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _svg_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- PNG 后端

def _find_cjk_font():
    cands = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in cands:
        if os.path.exists(p):
            return p
    return None


def render_png(scene, scale=2.0):
    """场景 → PIL Image（2x 抗锯齿）。Scene → PIL Image at 2x scale."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = int(scene.w * scale), int(scene.h * scale)
    img = Image.new("RGB", (W, H), scene.bg or WHITE)
    dr = ImageDraw.Draw(img)
    font_path = _find_cjk_font()
    cache = {}

    def font(size, bold=False):
        key = (int(size * scale), bold)
        if key not in cache:
            if font_path:
                try:
                    cache[key] = ImageFont.truetype(font_path, key[0])
                except Exception:
                    cache[key] = ImageFont.load_default()
            else:
                cache[key] = ImageFont.load_default()
        return cache[key]

    for it in scene.items:
        kind = it[0]
        if kind == "line":
            _, x1, y1, x2, y2, w, c, dash, arrow = it
            if dash:
                for sx, sy, ex, ey in _dash_segs(x1, y1, x2, y2, dash):
                    dr.line([sx * scale, sy * scale, ex * scale, ey * scale], fill=c, width=max(1, int(w * scale)))
            else:
                dr.line([x1 * scale, y1 * scale, x2 * scale, y2 * scale], fill=c, width=max(1, int(w * scale)))
            if arrow:
                ang = math.atan2(y2 - y1, x2 - x1)
                segs = _arrow_head(x2, y2, ang)
                dr.line([(p[0] * scale, p[1] * scale) for p in segs], fill=c, width=max(1, int(w * scale)))
        elif kind == "polyline":
            _, pts, w, c, dash = it
            if dash:
                for i in range(len(pts) - 1):
                    for sx, sy, ex, ey in _dash_segs(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], dash):
                        dr.line([sx * scale, sy * scale, ex * scale, ey * scale], fill=c, width=max(1, int(w * scale)))
            else:
                dr.line([(p[0] * scale, p[1] * scale) for p in pts], fill=c, width=max(1, int(w * scale)),
                        joint="curve")
        elif kind == "polygon":
            _, pts, fill, stroke, w = it
            dr.polygon([(p[0] * scale, p[1] * scale) for p in pts], fill=fill, outline=stroke,
                       width=max(1, int(w * scale)))
        elif kind == "circle":
            _, cx, cy, r, fill, stroke, w = it
            box = [(cx - r) * scale, (cy - r) * scale, (cx + r) * scale, (cy + r) * scale]
            if fill:
                dr.ellipse(box, fill=fill, outline=stroke, width=max(1, int(w * scale)))
            else:
                dr.ellipse(box, outline=stroke, width=max(1, int(w * scale)))
        elif kind == "text":
            _, x, y, s, size, c, anchor, bold, italic = it
            dr.text((x * scale, y * scale), str(s), font=font(size, bold), fill=c, anchor="mm")
    return img


# ---------------------------------------------------------------- 输出

def save(scene, out, format="both", scale=2.0):
    """保存场景。format: 'svg' | 'png' | 'both'。out 为不带扩展名的路径。
    Returns list of written paths."""
    written = []
    if format in ("svg", "both"):
        p = out + ".svg"
        with open(p, "w", encoding="utf-8") as f:
            f.write(render_svg(scene))
        written.append(p)
    if format in ("png", "both"):
        p = out + ".png"
        render_png(scene, scale=scale).save(p)
        written.append(p)
    return written


# ---------------------------------------------------------------- 基础几何

def _norm(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L, L


def _perp(ux, uy):
    return (-uy, ux)


def _mid(p1, p2):
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def _arc_pts(cx, cy, r, a0, a1, n=24):
    """弧采样为折线（屏幕坐标 y 向下）。Sample an arc into a polyline."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _rect(p1, p2, half_w, n=(0, 0)):
    """沿 p1→p2 的矩形四角（n 为垂直偏移单位向量）。Rectangle corners along axis."""
    ux, uy, L = _norm(p1, p2)
    nx, ny = _perp(ux, uy)
    if n == (0, 0):
        nx, ny = -uy, ux
    else:
        nx, ny = n
    dx, dy = half_w * nx, half_w * ny
    return [(p1[0] + dx, p1[1] + dy), (p1[0] - dx, p1[1] - dy),
            (p2[0] - dx, p2[1] - dy), (p2[0] + dx, p2[1] + dy)]


# ---------------------------------------------------------------- 元件（沿 p1→p2 绘制）

def resistor(sc, p1, p2, label=None, value=None, color=DARK, style="rect"):
    """电阻：GB 矩形（默认）或锯齿形。Resistor: rectangle (GB) or zigzag."""
    if style == "zigzag":
        ux, uy, L = _norm(p1, p2)
        pts = [p1]
        seg = L / 6
        for i in range(6):
            t1 = p1[0] + ux * seg * (i + 0.25), p1[1] + uy * seg * (i + 0.25)
            t2 = p1[0] + ux * seg * (i + 0.75), p1[1] + uy * seg * (i + 0.75)
            m = _mid(t1, t2)
            sign = 1 if i % 2 == 0 else -1
            peak = (m[0] + sign * 8 * (-uy), m[1] + sign * 8 * ux)
            pts.append(peak)
        pts.append(p2)
        sc.polyline(pts, width=2, color=color)
    else:
        ux, uy, L = _norm(p1, p2)
        nx, ny = -uy, ux
        inner = 0.70
        a = (p1[0] + ux * L * 0.15, p1[1] + uy * L * 0.15)
        b = (p1[0] + ux * L * 0.85, p1[1] + uy * L * 0.85)
        hw = 11.0
        pts = [(a[0] + nx * hw, a[1] + ny * hw), (a[0] - nx * hw, a[1] - ny * hw),
               (b[0] - nx * hw, b[1] - ny * hw), (b[0] + nx * hw, b[1] + ny * hw)]
        sc.polygon(pts, fill=WHITE, stroke=color, width=2)
    _elem_label(sc, p1, p2, label, value, color)


def capacitor(sc, p1, p2, label=None, value=None, color=DARK):
    """电容：两平行极板。Capacitor: two parallel plates."""
    ux, uy, L = _norm(p1, p2)
    nx, ny = -uy, ux
    c = _mid(p1, p2)
    for off in (-5.0, 5.0):
        a = (c[0] + ux * off + nx * 9, c[1] + uy * off + ny * 9)
        b = (c[0] + ux * off - nx * 9, c[1] + uy * off - ny * 9)
        sc.line(*a, *b, width=2.2, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def inductor(sc, p1, p2, label=None, value=None, color=DARK, arcs=4):
    """电感：一串半圆弧。Inductor: chain of semicircle arcs."""
    ux, uy, L = _norm(p1, p2)
    nx, ny = -uy, ux
    d = L / arcs
    r = d / 2
    pts = [p1]
    c0 = (p1[0] + ux * r, p1[1] + uy * r)
    for i in range(arcs):
        cx, cy = c0[0] + ux * d * i, c0[1] + uy * d * i
        sign = 1 if i % 2 == 0 else -1
        a0 = 180 if sign > 0 else 0
        a1 = 360 if sign > 0 else 180
        arc = _arc_pts(cx, cy, r, a0, a1, n=16)
        if i == 0:
            pts += arc[1:]
        else:
            pts += arc[1:]
    pts.append(p2)
    sc.polyline(pts, width=2, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def _source_body(sc, p1, p2, inner, label=None, value=None, color=DARK):
    ux, uy, L = _norm(p1, p2)
    c = _mid(p1, p2)
    r = 11.0
    sc.circle(c[0], c[1], r, fill=WHITE, stroke=color, width=2)
    inner(sc, c, r, ux, uy, color)
    _elem_label(sc, p1, p2, label, value, color)


def v_source(sc, p1, p2, label=None, value=None, color=DARK):
    """直流电压源（圆 + 极性）。DC voltage source (circle with +/-)."""
    def inner(sc, c, r, ux, uy, color):
        nx, ny = -uy, ux
        sc.line(c[0], c[1] - ny * 5, c[0], c[1] + ny * 5, width=2, color=color)
        sc.line(c[0] - ux * 5, c[1], c[0] + ux * 5, c[1], width=2, color=color)
    _source_body(sc, p1, p2, inner, label, value, color)


def ac_source(sc, p1, p2, label=None, value=None, color=DARK):
    """交流电源（圆 + ~）。AC source (circle with ~)."""
    def inner(sc, c, r, ux, uy, color):
        nx, ny = -uy, ux
        pts = _arc_pts(c[0], c[1] - ny * 5, 5, 180, 360, 14) + \
               _arc_pts(c[0], c[1] + ny * 5, 5, 0, 180, 14)
        sc.polyline(pts, width=2, color=color)
    _source_body(sc, p1, p2, inner, label, value, color)


def current_source(sc, p1, p2, label=None, value=None, color=DARK):
    """电流源（圆 + 箭头）。Current source (circle with arrow)."""
    def inner(sc, c, r, ux, uy, color):
        sc.line(c[0] - ux * 6, c[1] - uy * 6, c[0] + ux * 5, c[1] + uy * 5, width=2, color=color,
                arrow=True)
    _source_body(sc, p1, p2, inner, label, value, color)


def switch(sc, p1, p2, label=None, value=None, color=DARK, closed=False):
    """开关（断开时刀斜置）。Switch."""
    ux, uy, _ = _norm(p1, p2)
    nx, ny = -uy, ux
    a = (p1[0] + ux * 6, p1[1] + uy * 6)
    b = (p2[0] - ux * 6, p2[1] - uy * 6)
    if closed:
        sc.line(*a, *b, width=2, color=color)
    else:
        tip = (b[0] - ux * 14 - nx * 7, b[1] - uy * 14 - ny * 7)
        sc.line(*a, *tip, width=2, color=color)
    sc.circle(a[0], a[1], 1.8, fill=color)
    sc.circle(b[0], b[1], 1.8, fill=color)
    _elem_label(sc, p1, p2, label, value, color)


def pushbutton(sc, p1, p2, label=None, value=None, color=DARK, nc=False):
    """按钮（常开 NO / 常闭 NC）。Pushbutton NO/NC."""
    ux, uy, _ = _norm(p1, p2)
    nx, ny = -uy, ux
    a = (p1[0] + ux * 6, p1[1] + uy * 6)
    b = (p2[0] - ux * 6, p2[1] - uy * 6)
    if not nc:
        tip = (b[0] - ux * 12 - nx * 6, b[1] - uy * 12 - ny * 6)
        sc.line(*a, *tip, width=2, color=color)
    else:
        sc.line(*a, *b, width=2, color=color)
    sc.circle(a[0], a[1], 1.8, fill=color)
    sc.circle(b[0], b[1], 1.8, fill=color)
    _elem_label(sc, p1, p2, label, value, color)


def fuse(sc, p1, p2, label=None, value=None, color=DARK):
    """熔断器（矩形内穿线）。Fuse (rect with line through)."""
    ux, uy, L = _norm(p1, p2)
    nx, ny = -uy, ux
    a = (p1[0] + ux * L * 0.15, p1[1] + uy * L * 0.15)
    b = (p2[0] - ux * L * 0.15, p2[1] - uy * L * 0.15)
    pts = _rect(a, b, 7)
    sc.polygon(pts, fill=WHITE, stroke=color, width=2)
    sc.line(*a, *b, width=2, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def breaker(sc, p1, p2, label=None, value=None, color=DARK):
    """断路器（开关 + ×）。Circuit breaker (switch with ×)."""
    ux, uy, L = _norm(p1, p2)
    nx, ny = -uy, ux
    a = (p1[0] + ux * 6, p1[1] + uy * 6)
    b = (p2[0] - ux * 6, p2[1] - uy * 6)
    tip = (b[0] - ux * 13 - nx * 6, b[1] - uy * 13 - ny * 6)
    sc.line(*a, *tip, width=2, color=color)
    sc.circle(a[0], a[1], 1.8, fill=color)
    sc.circle(b[0], b[1], 1.8, fill=color)
    c = _mid(p1, p2)
    for s in (1, -1):
        sc.line(c[0] + ux * 4 - nx * 4, c[1] + uy * 4 - ny * 4 - s * 4 * ux,
                c[0] + ux * 4 + nx * 4, c[1] + uy * 4 + ny * 4 - s * 4 * ux, width=1.6, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def thermal_relay(sc, p1, p2, label=None, value=None, color=DARK):
    """热继电器（矩形 + 内部热元件折线）。Thermal relay (rect with heater zigzag)."""
    ux, uy, L = _norm(p1, p2)
    nx, ny = -uy, ux
    a = (p1[0] + ux * L * 0.12, p1[1] + uy * L * 0.12)
    b = (p2[0] - ux * L * 0.12, p2[1] - uy * L * 0.12)
    sc.polygon(_rect(a, b, 9), fill=WHITE, stroke=color, width=2)
    seg = L * 0.76 / 5
    pts = [a]
    for i in range(1, 5):
        t = (a[0] + ux * seg * i, a[1] + uy * seg * i)
        sign = 1 if i % 2 == 1 else -1
        pts.append((t[0] + sign * 4 * nx, t[1] + sign * 4 * ny))
    pts.append(b)
    sc.polyline(pts, width=1.6, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def contactor_coil(sc, p1, p2, label=None, value=None, color=DARK):
    """接触器线圈。Contactor coil."""
    ux, uy, L = _norm(p1, p2)
    a = (p1[0] + ux * L * 0.12, p1[1] + uy * L * 0.12)
    b = (p2[0] - ux * L * 0.12, p2[1] - uy * L * 0.12)
    pts = _rect(a, b, 8)
    sc.polygon(pts, fill=WHITE, stroke=color, width=2)
    _elem_label(sc, p1, p2, label, value, color)


def contactor_contact(sc, p1, p2, label=None, value=None, color=DARK, nc=False):
    """接触器触点（常开/常闭）。Contactor contact NO/NC."""
    pushbutton(sc, p1, p2, label=None, value=None, color=color, nc=nc)
    _elem_label(sc, p1, p2, label, value, color)


def lamp(sc, p1, p2, label=None, value=None, color=DARK):
    """指示灯/灯（圆 + ×）。Lamp (circle with ×)."""
    ux, uy, _ = _norm(p1, p2)
    c = _mid(p1, p2)
    r = 10.0
    sc.circle(c[0], c[1], r, fill=WHITE, stroke=color, width=2)
    for s in (1, -1):
        sc.line(c[0] - 6, c[1] - s * 6, c[0] + 6, c[1] + s * 6, width=2, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def motor(sc, p1, p2, label=None, value=None, color=DARK):
    """电动机（圆 + M）。Motor (circle with M)."""
    c = _mid(p1, p2)
    sc.circle(c[0], c[1], 13, fill=WHITE, stroke=color, width=2)
    sc.text(c[0], c[1], "M", size=13, color=color, bold=True)
    _elem_label(sc, p1, p2, label, value, color)


def transformer(sc, p1, p2, label=None, value=None, color=DARK, core=True):
    """变压器（两线圈）。Transformer (two coils)."""
    ux, uy, L = _norm(p1, p2)
    nx, ny = -uy, ux
    c = _mid(p1, p2)
    for side in (-1, 1):
        c0 = (c[0] + nx * 11 * side, c[1] + ny * 11 * side)
        a = (c0[0] - ux * L * 0.35, c0[1] - uy * L * 0.35)
        b = (c0[0] + ux * L * 0.35, c0[1] + uy * L * 0.35)
        inductor(sc, a, b, label=None, value=None, color=color, arcs=3)
    if core:
        sc.line(c[0] - ux * L * 0.45, c[1] - uy * L * 0.45, c[0] + ux * L * 0.45, c[1] + uy * L * 0.45,
                width=2, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def meter(sc, p1, p2, mark="A", label=None, value=None, color=DARK):
    """仪表（圆 + A/V）。Meter (circle with A/V)."""
    c = _mid(p1, p2)
    sc.circle(c[0], c[1], 11, fill=WHITE, stroke=color, width=2)
    sc.text(c[0], c[1], mark, size=12, color=color)
    _elem_label(sc, p1, p2, label, value, color)


def ground(sc, x, y, color=DARK):
    """接地符号。Ground symbol."""
    for i, w in enumerate((12, 8, 4)):
        sc.line(x - w, y + i * 3.5, x + w, y + i * 3.5, width=2, color=color)


def node(sc, x, y, color=DARK):
    """节点圆点。Node dot."""
    sc.circle(x, y, 2.6, fill=color)


def _elem_label(sc, p1, p2, label, value, color):
    """元件标签：label 在上方，value 在下方。Label above, value below."""
    if not label and not value:
        return
    ux, uy, _ = _norm(p1, p2)
    nx, ny = -uy, ux
    c = _mid(p1, p2)
    if label:
        sc.text(c[0] - nx * 16, c[1] - ny * 16, label, size=13, color=color)
    if value:
        sc.text(c[0] + nx * 16, c[1] + ny * 16, value, size=12, color=GRAY)


def current_arrow(sc, p1, p2, label=None, color=SERIES[0], offset=(0, 14)):
    """电流参考方向箭头 + 标签。Current direction arrow with label."""
    sc.line(*p1, *p2, width=2, color=color, arrow=True)
    if label:
        c = _mid(p1, p2)
        sc.text(c[0] + offset[0], c[1] + offset[1], label, size=13, color=color)


def voltage_arrow(sc, p1, p2, label=None, color=GRAY, offset=(14, 0)):
    """电压参考方向（虚线双箭头）。Voltage reference (dashed)."""
    sc.line(*p1, *p2, width=1.8, color=color, dash=6, arrow=True)
    if label:
        c = _mid(p1, p2)
        sc.text(c[0] + offset[0], c[1] + offset[1], label, size=13, color=color)


# ---------------------------------------------------------------- 电路：并联框架

def circuit_parallel(sc, lx, ly, rx, ry, branches, gap=52, total_label="i总",
                     voltage_label=None, bottom_ext=26):
    """并联电路图：左/右母线 + 水平支路 + 底部总电流箭头。
    branches: list of dicts {el, label, value, color?}；el ∈
      resistor/capacitor/inductor/lamp/fuse/switch/...（元件函数名）。
    Returns branch rects [(x1,y1,x2,y2), ...]."""
    n = len(branches)
    ys = [ly - gap * (n - 1) / 2.0 + gap * i for i in range(n)]
    top, bot = ys[0], ys[-1]
    # 母线
    sc.line(lx, top, lx, bot + bottom_ext, width=2)
    sc.line(rx, top, rx, bot + bottom_ext, width=2)
    # 支路
    rects = []
    for i, br in enumerate(branches):
        y = ys[i]
        sc.line(lx, y, lx + 22, y, width=2)
        sc.line(rx - 22, y, rx, y, width=2)
        fn = globals().get(br.get("el", "resistor"), resistor)
        fn(sc, (lx + 22, y), (rx - 22, y), label=br.get("label"), value=br.get("value"),
           color=br.get("color", DARK))
        rects.append((lx + 22, y, rx - 22, y))
    # 总电流箭头（从左母线底部流入）
    if total_label:
        current_arrow(sc, (lx, bot + bottom_ext), (lx, bot), label=total_label,
                      color=br_color(branches), offset=(-26, 0))
    # 电压箭头
    if voltage_label:
        voltage_arrow(sc, (rx - 10, top), (rx - 10, bot), label=voltage_label)
    return rects


def br_color(branches):
    return branches[0].get("color", SERIES[0]) if branches else SERIES[0]


def circuit_series(sc, x, y, w, h, elements, source=None, current_label="İ",
                   source_value=None):
    """串联回路电路图：矩形回路，元件沿顶边，电源在左边。
    elements: list of dicts {el, label, value}（沿顶边从左到右）。
    source: None 或 'ac'/'dc'。"""
    x2 = x + w
    y2 = y + h
    # 回路导线（先画，元件后画覆盖）
    sc.polyline([(x, y), (x2, y), (x2, y2), (x, y2), (x, y)], width=2)
    if source:
        fn = ac_source if source == "ac" else v_source
        fn(sc, (x, y + h * 0.62), (x, y + h * 0.38), label=None, value=source_value)
    if elements:
        seg = w / len(elements)
        for i, el in enumerate(elements):
            a = (x + seg * i + 26, y)
            b = (x + seg * (i + 1) - 26, y)
            sc.line(x + seg * i, y, a[0], y, width=2)
            sc.line(b[0], y, x + seg * (i + 1), y, width=2)
            fn = globals().get(el.get("el", "resistor"), resistor)
            fn(sc, a, b, label=el.get("label"), value=el.get("value"), color=el.get("color", DARK))
    if current_label:
        current_arrow(sc, (x2 - 70, y2), (x2 - 10, y2), label=current_label, offset=(0, 18))
    return (x, y, x2, y2)


# ---------------------------------------------------------------- 正弦波形

def wave(sc, ax, ay, w, h, series, t_max=0.02, y_min=None, y_max=None,
         x_ms=True, y_label="i/A", x_label="t/ms", peak_lines=False, grid=True):
    """正弦波形图。series: list of dicts {amp, omega, phase_deg, label, color, dash?}
    amp 为幅值（瞬时值峰）。phase_deg 为初相（度）。"""
    x2, y2 = ax + w, ay + h
    N = 600
    ts = [t_max * i / (N - 1) for i in range(N)]
    amps = [s["amp"] for s in series]
    m = max(amps) * 1.25 if amps else 1.0
    if y_min is None:
        y_min = -m
    if y_max is None:
        y_max = m

    def px(t):
        return ax + w * t / t_max

    def py(v):
        return ay + h * (y_max - v) / (y_max - y_min)

    # 坐标轴与网格
    sc.line(ax, py(0), x2, py(0), width=1.6, color=GRAY, arrow=True)          # x 轴
    sc.line(ax, y2, ax, ay, width=1.6, color=GRAY, arrow=True)                # y 轴（向上为正）
    if grid:
        n_grid = 8
        for i in range(n_grid + 1):
            t = t_max * i / n_grid
            sc.line(px(t), ay, px(t), y2, width=1, color=GRID)
            v = y_min + (y_max - y_min) * i / n_grid
            sc.line(ax, py(v), x2, py(v), width=1, color=GRID)
    # 轴刻度标签
    for i in range(6):
        t = t_max * i / 5
        lab = f"{t * 1000:g}" if x_ms else f"{t:g}"
        sc.text(px(t), py(0) + 14, lab, size=11, color=GRAY)
    for i in range(5):
        v = y_min + (y_max - y_min) * i / 4
        sc.text(ax - 8, py(v), f"{v:g}", size=11, color=GRAY, anchor="end")
    # 轴标题
    sc.text(x2 + 4, py(0), x_label, size=12, color=GRAY)
    sc.text(ax - 6, ay - 12, y_label, size=12, color=GRAY)
    # 曲线
    for si, s in enumerate(series):
        color = s.get("color", SERIES[si % len(SERIES)])
        pts = [(px(t), py(s["amp"] * math.sin(s["omega"] * t + math.radians(s.get("phase_deg", 0)))))
               for t in ts]
        sc.polyline(pts, width=2, color=color, dash=s.get("dash"))
        if peak_lines:
            pv = py(s["amp"])
            sc.line(ax, pv, x2, pv, width=1, color=color, dash=4)
    # 图例
    _legend(sc, x2 - 10, ay + 8, series)
    return sc


def _legend(sc, x, y, series):
    n = len(series)
    for i, s in enumerate(series):
        color = s.get("color", SERIES[i % len(SERIES)])
        yy = y + i * 18
        sc.line(x - 60, yy, x - 38, yy, width=2.4, color=color)
        sc.text(x - 32, yy, s.get("label", f"曲线{i + 1}"), size=12, color=DARK, anchor="start")


# ---------------------------------------------------------------- 相量图

def phasor_diagram(sc, ox, oy, scale, vectors, show_angles=True, arc_r=None,
                   axis_label="+1", y_label="+j"):
    """相量图。vectors: list of dicts {mag, deg, label, color?}。
    mag 为有效值；deg 为相角（度）。"""
    big = max((v["mag"] for v in vectors), default=1.0)
    arc_r = arc_r or scale * big * 0.28
    # 参考轴
    sc.line(ox - scale * big * 1.25, oy, ox + scale * big * 1.25, oy, width=1.6, color=GRAY, arrow=True)
    sc.line(ox, oy + scale * big * 1.25, ox, oy - scale * big * 1.25, width=1.6, color=GRAY, arrow=True)
    sc.text(ox + scale * big * 1.25 + 6, oy, axis_label, size=12, color=GRAY, anchor="start")
    sc.text(ox + 6, oy - scale * big * 1.25 - 6, y_label, size=12, color=GRAY, anchor="start")
    for i, v in enumerate(vectors):
        mag, deg = v["mag"], v.get("deg", 0)
        color = v.get("color", SERIES[i % len(SERIES)])
        a = math.radians(deg)
        ex, ey = ox + scale * mag * math.cos(a), oy - scale * mag * math.sin(a)
        sc.line(ox, oy, ex, ey, width=2.4, color=color, arrow=True)
        # 幅值标签（中点）
        mx, my = (ox + ex) / 2, (oy + ey) / 2
        sc.text(mx + 8 * math.sin(a), my + 8 * math.cos(a), f"{mag:g}", size=12, color=color)
        # 相量名（端点）
        anchor = "end" if math.cos(a) < 0 else "start"
        tx = ex - 8 if anchor == "end" else ex + 8
        sc.text(tx, ey - 10 * math.sin(a) - 4, v.get("label", f"V{i + 1}"),
                size=13, color=color, bold=True, anchor=anchor)
        # 角度弧
        if show_angles and deg != 0:
            a0, a1 = 0.0, -deg  # 屏幕坐标（y 向下）
            pts = _arc_pts(ox, oy, arc_r, min(a0, a1), max(a0, a1), n=40)
            sc.polyline(pts, width=1.4, color=GRAY)
            am = math.radians(-deg / 2.0)
            sc.text(ox + arc_r * 1.35 * math.cos(am), oy + arc_r * 1.35 * math.sin(am),
                    _fmt_deg(deg), size=11, color=GRAY)
    return sc


# ---------------------------------------------------------------- CLI / demo

def _load_spec(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_from_spec(spec):
    """按 spec 构建并保存。spec keys: type(wave|phasor|parallel|series),
    size:[w,h], out: 输出路径（不含扩展名）, format: svg|png|both。"""
    w, h = spec.get("size", [640, 400])
    out = spec["out"]
    fmt = spec.get("format", "both")
    sc = Scene(w, h)
    t = spec.get("type", "wave")
    if t == "wave":
        wave(sc, spec.get("ax", 70), spec.get("ay", 60), spec.get("w", w - 140),
             spec.get("h", h - 110), spec.get("series", []), t_max=spec.get("t_max", 0.02),
             x_ms=spec.get("x_ms", True), y_label=spec.get("y_label", "i/A"),
             peak_lines=spec.get("peak_lines", True))
    elif t == "phasor":
        phasor_diagram(sc, spec.get("ox", w / 2), spec.get("oy", h / 2), spec.get("scale", 15),
                       spec.get("vectors", []))
    elif t == "parallel":
        circuit_parallel(sc, spec.get("lx", 140), spec.get("ly", h / 2), spec.get("rx", w - 120),
                         spec.get("ry", h / 2), spec.get("branches", []),
                         total_label=spec.get("total_label", "i总"),
                         voltage_label=spec.get("voltage_label"))
    elif t == "series":
        circuit_series(sc, spec.get("x", 120), spec.get("y", 70), spec.get("w", w - 240),
                       spec.get("h", h - 140), spec.get("elements", []),
                       source=spec.get("source", "ac"), current_label=spec.get("current_label", "İ"))
    else:
        raise ValueError(f"unknown type: {t}")
    return save(sc, out, format=fmt)


def demo():
    """生成示例图到本技能 examples/ 目录。Generate example images."""
    here = os.path.dirname(os.path.abspath(__file__))
    exdir = os.path.join(os.path.dirname(here), "examples")
    os.makedirs(exdir, exist_ok=True)

    # 1) 作业题电路：R1=100Ω, R2=200Ω 并联, i总 流入
    sc = Scene(520, 400)
    circuit_parallel(sc, 130, 200, 400, 200, [
        {"el": "resistor", "label": "R₁", "value": "100 Ω"},
        {"el": "resistor", "label": "R₂", "value": "200 Ω"},
    ], gap=80, total_label="i总", voltage_label="Ů")
    save(sc, os.path.join(exdir, "circuit-parallel-r1r2"), format="both")

    # 2) 相量图：İ=12∠−120°, İ₁=8∠−120°, İ₂=4∠−120°
    sc = Scene(560, 420)
    phasor_diagram(sc, 90, 250, 15, [
        {"mag": 12, "deg": -120, "label": "İ", "color": SERIES[0]},
        {"mag": 8, "deg": -120, "label": "İ₁", "color": SERIES[1]},
        {"mag": 4, "deg": -120, "label": "İ₂", "color": SERIES[2]},
    ])
    save(sc, os.path.join(exdir, "phasor-r1r2"), format="both")

    # 3) 波形图：i总/i₁/i₂ 同相
    sc = Scene(680, 420)
    wave(sc, 70, 60, 540, 300, [
        {"amp": 12 * math.sqrt(2), "omega": 314, "phase_deg": -120, "label": "i总", "color": SERIES[0]},
        {"amp": 8 * math.sqrt(2), "omega": 314, "phase_deg": -120, "label": "i₁", "color": SERIES[1]},
        {"amp": 4 * math.sqrt(2), "omega": 314, "phase_deg": -120, "label": "i₂", "color": SERIES[2]},
    ], t_max=0.02, peak_lines=True)
    save(sc, os.path.join(exdir, "wave-r1r2"), format="both")

    # 4) RLC 串联电路
    sc = Scene(560, 400)
    circuit_series(sc, 100, 60, 360, 260, [
        {"el": "resistor", "label": "R", "value": "30 Ω"},
        {"el": "inductor", "label": "L", "value": "0.127 H"},
        {"el": "capacitor", "label": "C", "value": "40 μF"},
    ], source="ac", source_value="220 V", current_label="İ")
    save(sc, os.path.join(exdir, "circuit-series-rlc"), format="both")

    # 5) RLC 串联电压/电流波形（相位差示例）
    sc = Scene(680, 420)
    wave(sc, 70, 60, 540, 300, [
        {"amp": 220 * math.sqrt(2), "omega": 314, "phase_deg": 0, "label": "u", "color": SERIES[0]},
        {"amp": 4.4 * math.sqrt(2), "omega": 314, "phase_deg": 53.1, "label": "i", "color": SERIES[1]},
    ], t_max=0.02, peak_lines=False)
    save(sc, os.path.join(exdir, "wave-rlc-ui"), format="both")
    return exdir


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        d = demo()
        print("examples written to", d)
    elif len(sys.argv) > 1:
        spec = _load_spec(sys.argv[1])
        print("\n".join(build_from_spec(spec)))
    else:
        print(__doc__)
