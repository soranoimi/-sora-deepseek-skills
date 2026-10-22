---
name: deepseek-ee-solver
description: "deepseek基础电工题目解析（DeepSeek Basic Electrical Problem Solver）——解析电工题目：规范输出电工符号，生成电路图/正弦波形图/相量图（SVG+PNG），可按需生成交互演示卡片；覆盖职高《电工基础》与低压电工考证范围。Solve EE problems with notation-correct symbols and circuit/waveform/phasor diagrams (SVG+PNG), plus interactive demo cards on demand. Covers vocational《电工基础》and low-voltage electrician certificate scope."
---

# deepseek基础电工题目解析 · DeepSeek Basic Electrical Problem Solver

本技能目录即 `<skill_resources>` 根目录，所有相对路径基于它解析。
All relative paths below resolve against this skill's root directory.

## 适用场景 / When to use

电工题：直流/交流电路计算、相量分析、RLC、三相电路、变压器、电动机，低压电工考证理论题；
或用户需要输出电工符号、电路图、正弦波形图、相量图时。

## 铁律 / Hard rules（每次输出前自查）

1. **相量**写大写带点（İ Ů Ė），模取**有效值**；**瞬时值**写小写（i u），幅值 = √2 × 有效值。
2. 相量式**不含 sin**；瞬时式**不含 ∠**；**单位不可省**；角度必须带 °。
3. 用 KCL/KVL 前必须先**声明参考方向**。
4. 计算题按五步规范：解 → 定参考方向 → 写已知相量 → 列式代入 → 校验 → 反变换 + 答。
5. **校验强制**：数值题用 `tools/ee.py`（KCL、欧姆、逐点抽查）验证；生成的图用 `tools/check_examples.py` 检查。
6. 答案给全：相量 + 瞬时值 + 有效值；书写规范红线见 `references/solution-templates.md`。

## 流程 / Workflow

1. **图片题**：按 `references/image-preprocessing.md` 预处理（魔数识别、转正、放大增强）再读题。
2. **转写题面**：按 `references/notation.md` 规范转写并贴出，再开始求解（读数存疑时用比值推导并注明）。
3. **求解**：模板见 `references/solution-templates.md`，公式查 `references/formulas.md`，考证安全题查 `references/safety-regs.md`。
4. **数值校验**：`tools/ee.py`。
5. **出图**：默认静态 SVG+PNG 存工作区 `output/`；用户点名“演示/动画”才做 visualize 卡片（先加载 visualize 技能，模板在 `templates/`）。
6. **回复排版**：转写题面 → 步骤 → 结果表 → 图 → 校验说明（全部带单位）。

## 工具 / Tools（零依赖；PNG 后端需 Pillow，DSH 自带）

- **tools/ee.py** —— 相量运算与校验：`ph()` `pol()` `fmt()` `sin_expr()` `series()` `parallel()` `voltage_divider()` `current_divider()` `z_series_rlc()` `power()` `three_phase()` `check_kcl()` `check_ohms()` `check_time()`。自检：`python tools/ee.py`
- **tools/eeplot.py** —— 图形生成器（场景图 + SVG/PNG 双后端）：
  - 元件：`resistor/capacitor/inductor/v_source/ac_source/current_source/switch/pushbutton/fuse/breaker/contactor_coil/contactor_contact/thermal_relay/transformer/motor/lamp/meter/ground/node/current_arrow/voltage_arrow`
  - 图型：`circuit_parallel()` 并联电路、`circuit_series()` 串联回路、`wave()` 正弦波形、`phasor_diagram()` 相量图
  - CLI：`python tools/eeplot.py demo`（生成示例到 `examples/`）；`python tools/eeplot.py <spec.json>`
- **tools/check_examples.py** —— examples/ 的结构与像素自检。

用法要点 / Usage notes：
- 解释器用 DSH 自带 Python（`load_workspace_dependencies`），先 `sys.path.insert(0, r"<技能目录>\tools")` 再 `import ee, eeplot`；写文件一律 UTF-8。
- 每个问题写一个小的生成脚本（放在工作区），运行后把 SVG/PNG 存 `output/`；SVG 供用户插文档，PNG 供聊天/打印。
- 风格：白底深色线；系列色蓝 `#2563eb`、红 `#dc2626`、绿 `#16a34a`、橙 `#d97706`、紫 `#7c3aed`、青 `#0891b2`；标签中文默认。

## 交互卡片 / Interactive cards（按需）

- 仅当用户要“演示/动画/拖动”时才做卡片；默认静态图。
- 模板：`templates/card-sine-wave.html`（正弦波形动画，f/幅值/相位可调）、`templates/card-phasor-rotation.html`（相量转动 + 头尾相加）、`templates/card-rlc-demo.html`（RLC 串并联计算演示）。
- 做卡片前**必须先加载 visualize 技能**并遵守其契约：theme 变量与 light-dark()、11px 字号下限、无网络请求、whale 卡片风格、内联 SVG 规范。

## 参考库 / References

| 文件 | 内容 |
|---|---|
| `references/notation.md` | 符号书写规范（含 6 条铁律与错误对照表、Unicode 速查） |
| `references/solution-templates.md` | 解题模板（五步规范 + 七类题型 + 书写红线） |
| `references/formulas.md` | 公式速查（直流/正弦/RLC/三相/变压器/电机/换算） |
| `references/symbols.md` | GB 元件符号表与 eeplot 函数映射、文字符号 |
| `references/safety-regs.md` | 低压电工安全规程简表（安全电压/急救/接地接零/灭火/口诀） |
| `references/image-preprocessing.md` | 图片预处理流程（魔数、转正、放大增强） |

## 语言 / Language

默认中文（含专业符号）。用户要求英文时：术语对照见各 references 的 EN 列，答案全英文；图内标注可中英混排（元件符号本身不分语言）。
