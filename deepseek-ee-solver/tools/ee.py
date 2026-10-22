# -*- coding: utf-8 -*-
"""
ee.py — 电工相量计算与数值校验
EE phasor math & numeric verification helpers
DeepSeek Basic Electrical Problem Solver · deepseek基础电工题目解析

纯标准库，无第三方依赖 / Zero dependencies (stdlib only).

约定 / Conventions（国标·职高《电工基础》教材）
  * 有效值相量 effective-value phasor: İ = I∠ψ, 模为有效值 (RMS), 单位 A/V
  * 幅值 amplitude = √2 × 有效值
  * 角度一律用度 (degrees), 输出统一带 °
  * 瞬时值写法: i = I√2 sin(ωt + ψ) A
"""
import cmath
import math

SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)

# ---------------------------------------------------------------- 基本运算

def ph(mag, deg):
    """由有效值与角度(度)构造相量。Build phasor from RMS magnitude + angle (deg)."""
    return cmath.rect(mag, math.radians(deg))


def pol(z):
    """返回 (有效值模, 角度°)。Return (RMS magnitude, angle in degrees)."""
    return abs(z), math.degrees(cmath.phase(z))


def norm_deg(deg):
    """角度归一化到 [-180, 180)。Normalize angle to [-180, 180)."""
    deg = deg % 360.0
    if deg >= 180.0:
        deg -= 360.0
    return deg


def fmt_deg(deg):
    """角度格式化: −120°。Format angle with degree sign."""
    d = norm_deg(deg)
    sign = "−" if d < 0 else ""
    return f"{sign}{abs(d):g}°"


def fmt(z, unit="A", prec=4):
    """相量格式化: 8∠−120° A。Format phasor: 8∠−120° A."""
    m, d = pol(z)
    if m == 0:
        return f"0{unit}"
    return f"{m:.{prec}g}∠{fmt_deg(d)} {unit}"


def sin_expr(rms, omega, deg, unit="A", var="t"):
    """瞬时值表达式: 8√2 sin(314t − 120°) A。
    Instantaneous expression in textbook form."""
    if rms == 0:
        return f"0 {unit}"
    sign = " − " if deg < 0 else " + "
    return f"{rms:g}√2 sin({omega:g}{var}{sign}{abs(norm_deg(deg)):g}°) {unit}"


# ---------------------------------------------------------------- 串并联/分压分流

def series(*zs):
    """串联等效阻抗。Equivalent series impedance."""
    return sum(zs, complex(0))


def parallel(*zs):
    """并联等效阻抗。Equivalent parallel impedance."""
    zs = [z for z in zs if z != 0]
    if not zs:
        return complex(0)
    y = sum(1.0 / z for z in zs)
    if abs(y) < 1e-15:
        return complex("inf")
    return 1.0 / y


def voltage_divider(utot, z_this, z_other):
    """分压: Ů_this = Ů_tot·Z_this/(Z_this+Z_other)。Voltage division."""
    return utot * z_this / (z_this + z_other)


def current_divider(itot, z_this, z_other):
    """分流: İ_this = İ_tot·Z_other/(Z_this+Z_other)。Current division."""
    return itot * z_other / (z_this + z_other)


# ---------------------------------------------------------------- RLC

def z_series_rlc(r, omega, l=0.0, c=None):
    """RLC 串联阻抗: Z = R + j(ωL − 1/ωC)。Series RLC impedance."""
    xl = omega * l if l else 0.0
    xc = 1.0 / (omega * c) if c else 0.0
    return complex(r, xl - xc)


def z_parallel_rlc(r, omega, l=0.0, c=None):
    """RLC 并联阻抗。Parallel RLC impedance."""
    y = 1.0 / r
    if l:
        y += 1.0 / complex(0, omega * l)
    if c:
        y += complex(0, omega * c)
    if abs(y) < 1e-15:
        return complex("inf")
    return 1.0 / y


def resonance_f(l, c):
    """谐振频率 f₀ = 1/(2π√LC) (Hz)。Resonance frequency."""
    return 1.0 / (2 * math.pi * math.sqrt(l * c))


def power(u, i):
    """复功率与功率三角形。u, i: 相量 (complex)。
    Returns dict: S(复数视在功率), P(有功W), Q(无功var), cosφ, |S|."""
    s = u * i.conjugate()
    p = s.real
    q = s.imag
    mag_s = abs(s)
    cosphi = p / mag_s if mag_s > 1e-15 else 0.0
    return {"S": s, "P": p, "Q": q, "|S|": mag_s, "cosφ": cosphi}


# ---------------------------------------------------------------- 三相

def three_phase(up, kind="Y"):
    """三相关系。kind: 'Y'/'星' 或 'Δ'/'delta'/'角'。
    Y: U线=√3·U相, I线=I相；Δ: U线=U相, I线=√3·I相。
    Returns dict with relation strings + factors."""
    if kind in ("Y", "y", "star", "星"):
        return {
            "kind": "Y 星形",
            "U_line": up * SQRT3, "U_phase": up,
            "I_line_factor": 1.0, "I_phase_factor": 1.0,
            "note": "U线 = √3·U相, I线 = I相",
        }
    if kind in ("Δ", "delta", "角"):
        return {
            "kind": "Δ 三角形",
            "U_line": up, "U_phase": up,
            "I_line_factor": SQRT3, "I_phase_factor": 1.0,
            "note": "U线 = U相, I线 = √3·I相",
        }
    raise ValueError("kind must be Y/星 or Δ/角")


def transformer_ratio(u1, u2):
    """变压器变比 k = U1/U2 = N1/N2。Transformer ratio."""
    return u1 / u2


# ---------------------------------------------------------------- 数值校验

def check_kcl(currents, tol=1e-9):
    """基尔霍夫电流定律校验（流入为正）。KCL check."""
    s = sum(currents)
    return {"sum": s, "ok": abs(s) < tol, "sum_fmt": fmt(s)}


def check_ohms(u, z, i, tol=1e-9):
    """欧姆定律校验 Ů = Z·İ。Ohm's law check."""
    return {"diff": u - z * i, "ok": abs(u - z * i) < tol}


def check_time(f_total, branches, ts=None, tol=1e-9):
    """时域逐点校验: 总瞬时值 == 各支路瞬时值之和。
    f_total, branches: 以 t 为参数的可调用对象（返回瞬时值）。
    Spot-check instantaneous superposition."""
    ts = ts or [0.0, 0.002, 0.005, 0.01, 0.02]
    bad = []
    for t in ts:
        want = f_total(t)
        got = sum(b(t) for b in branches)
        if abs(want - got) > tol:
            bad.append((t, want, got))
    return {"ok": not bad, "bad": bad, "samples": len(ts)}


def report_row(name, z=None, unit="A"):
    """生成一行双语结果文本。"""
    return f"{name} = {fmt(z, unit)}" if z is not None else name


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    # 自检 / self-test: R1=100Ω, R2=200Ω 并联, İ总=12∠−120° A
    itot = ph(12, -120)
    i1 = current_divider(itot, 100, 200)
    i2 = current_divider(itot, 200, 100)
    assert abs(abs(i1) - 8) < 1e-9 and abs(abs(i2) - 4) < 1e-9, "current divider failed"
    assert check_kcl([-itot, i1, i2])["ok"], "KCL failed"
    assert norm_deg(-120) == -120 and fmt_deg(-120) == "−120°"
    print("İ1 =", fmt(i1), " İ2 =", fmt(i2))
    print("i1 =", sin_expr(8, 314, -120), " i2 =", sin_expr(4, 314, -120))
    print("ee.py self-test OK")
