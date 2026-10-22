# 元件图形符号 / Component Symbols（GB/T 4728 风格）

元件用 `tools/eeplot.py` 绘制。函数名即符号名；所有元件沿 p1→p2 线段方向绘制。
Draw components with eeplot.py; each function draws the symbol along the p1→p2 segment.

| 元件 | EN | eeplot 函数 | 符号形状 |
|---|---|---|---|
| 电阻 | Resistor | `resistor(sc,p1,p2)` | 矩形（GB）/ 可选锯齿形 `style="zigzag"` |
| 电容 | Capacitor | `capacitor(sc,p1,p2)` | 两平行极板 |
| 电感 | Inductor | `inductor(sc,p1,p2)` | 一串半圆弧 |
| 直流电压源 | DC source | `v_source(sc,p1,p2)` | 圆 + 极性 |
| 交流电源 | AC source | `ac_source(sc,p1,p2)` | 圆 + ~ |
| 电流源 | Current source | `current_source(sc,p1,p2)` | 圆 + 箭头 |
| 开关 | Switch | `switch(sc,p1,p2,closed=False)` | 刀开关（可闭合） |
| 按钮（常开/常闭） | Pushbutton NO/NC | `pushbutton(sc,p1,p2,nc=True/False)` | 圆点 + 触头 |
| 熔断器 | Fuse | `fuse(sc,p1,p2)` | 矩形内穿线 |
| 断路器 | Circuit breaker | `breaker(sc,p1,p2)` | 开关 + × |
| 接触器线圈 | Contactor coil | `contactor_coil(sc,p1,p2)` | 矩形 |
| 接触器触点 | Contactor contact | `contactor_contact(sc,p1,p2,nc=…)` | 圆点 + 触头 |
| 热继电器 | Thermal relay | `thermal_relay(sc,p1,p2)` | 矩形 + 折线 |
| 变压器 | Transformer | `transformer(sc,p1,p2)` | 两线圈 + 铁芯 |
| 互感器 | Instrument transformer | `transformer(sc,p1,p2)` | 同上 + 标注 |
| 电动机 | Motor | `motor(sc,p1,p2)` | 圆 + M（三相标注 M 3~） |
| 灯/指示灯 | Lamp | `lamp(sc,p1,p2)` | 圆 + × |
| 电流/电压表 | Ammeter/Voltmeter | `meter(sc,p1,p2,mark="A"/"V")` | 圆 + A/V |
| 接地 | Ground | `ground(sc,x,y)` | 三条递减横线 |
| 节点 | Node | `node(sc,x,y)` | 实心圆点 |
| 参考方向 | Reference arrow | `current_arrow(sc,p1,p2,label)` | 箭头 + 标签 |
| 电压方向 | Voltage arrow | `voltage_arrow(sc,p1,p2,label)` | 虚线 + 标签 |

## 常用文字符号 / Letter symbols（GB/T 7159）

| 符号 | 名称 | 符号 | 名称 |
|---|---|---|---|
| R / L / C | 电阻/电感/电容 | U / I | 电压/电流 |
| P / Q / S | 有功/无功/视在功率 | cosφ | 功率因数 |
| f / T / ω | 频率/周期/角频率 | φ / ψ | 相位差/初相 |
| X / Z | 电抗/阻抗 | η | 效率 |
| N / k | 匝数/变比 | E | 电动势 |

## 常用标注惯例 / Labeling

- 元件名在上方（R₁、L、C₁），参数值在下方（100 Ω、0.127 H）。
- 三相电机标「M 3~」；接触器线圈标 KM，触点随线圈编号（KM₁、KM₂）；热继电器 FR。
- 电流参考方向画在导线上；电压参考方向用虚线箭头画在元件两端。
