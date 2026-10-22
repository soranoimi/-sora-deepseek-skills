# -*- coding: utf-8 -*-
"""像素/结构级自检：验证 examples 下的图没有画空、关键元素存在。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(os.path.dirname(HERE), "examples")

CHECKS = {
    "circuit-parallel-r1r2": {
        "png_colors": [(0x25, 0x63, 0xEB)],          # 蓝色电流箭头
        "svg_has": ["R₁", "R₂", "100 Ω", "200 Ω", "i总", "Ů"],
        "nonwhite_min": 0.01,
    },
    "circuit-series-rlc": {
        "svg_has": ["R", "L", "C", "220 V", "İ", "0.127 H"],
        "nonwhite_min": 0.01,
    },
    "phasor-r1r2": {
        "png_colors": [(0x25, 0x63, 0xEB), (0xDC, 0x26, 0x26), (0x16, 0xA3, 0x4A)],
        "svg_has": ["İ", "İ₁", "İ₂", "12", "8", "−120°"],
        "nonwhite_min": 0.005,
    },
    "wave-r1r2": {
        "png_colors": [(0x25, 0x63, 0xEB), (0xDC, 0x26, 0x26), (0x16, 0xA3, 0x4A)],
        "svg_has": ["i总", "i₁", "i₂"],
        "nonwhite_min": 0.01,
    },
    "wave-rlc-ui": {
        "png_colors": [(0x25, 0x63, 0xEB), (0xDC, 0x26, 0x26)],
        "svg_has": ["u", "i"],
        "nonwhite_min": 0.01,
    },
}


def close(c1, c2, tol=60):
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))


def main():
    ok = True
    for name, spec in CHECKS.items():
        png = os.path.join(EX, name + ".png")
        svg = os.path.join(EX, name + ".svg")
        img = Image.open(png).convert("RGB")
        w, h = img.size
        px = img.load()
        # 非白占比
        nonwhite = sum(1 for y in range(0, h, 3) for x in range(0, w, 3)
                       if sum(px[x, y]) < 720) / ((w // 3 + 1) * (h // 3 + 1))
        # 期望颜色出现
        found = {c: False for c in spec.get("png_colors", [])}
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                p = px[x, y]
                for c in found:
                    if close(p, c):
                        found[c] = True
        svg_text = open(svg, encoding="utf-8").read()
        svg_ok = all(s in svg_text for s in spec.get("svg_has", []))
        nw_ok = nonwhite >= spec.get("nonwhite_min", 0.005)
        color_ok = all(found.values())
        status = "OK" if (nw_ok and svg_ok and color_ok) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"{name:24s} {status}  nonwhite={nonwhite:.4f} svg_ok={svg_ok} "
              f"colors={found} size={img.size}")
    print("ALL OK" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
