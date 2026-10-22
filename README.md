# deepseek基础电工题目解析 · DeepSeek Basic Electrical Problem Solver

一个面向 [DeepSeek Harness](https://deepseek-harness.github.io/deepseek-harness/)（DSH）的电工学习辅助技能，提供电工题目解析、电工符号规范输出，以及电路图、正弦波形图、相量图的自动绘制。**知识范围限于职高《电工基础》教材与低压电工特种作业操作证理论考试的常见内容。**

A learning-aid skill for [DeepSeek Harness](https://deepseek-harness.github.io/deepseek-harness/) (DSH) that parses electrical problems, applies notation conventions, and renders circuit, sine-waveform, and phasor diagrams. **Its knowledge scope is limited to the vocational high-school textbook *《电工基础》* (Fundamentals of Electrical Engineering) and the common theory topics of the low-voltage electrician certificate examination.**

## 适用范围与局限 / Scope and limitations

**覆盖 / Covered**

- 直流电路：欧姆定律、基尔霍夫定律、电阻串并联与混联、分压分流、电功率
- 单相正弦交流：正弦量三要素、有效值、相量法、RLC 串并联、功率与功率因数、串联谐振
- 三相电路：星形/三角形连接下的线相关系、对称负载功率
- 变压器与三相异步电动机基础
- 低压电工证理论：安全电压、触电急救、保护接地与保护接零、电气防火、低压电器与安全用具（简表）

**不覆盖 / Not covered**

- 大学《电路原理》层次内容（高阶动态电路、拉普拉斯变换、二端口网络等）
- 电子技术、数字电路、高压电工、继电保护
- 特种作业实操培训内容（接线工艺、仪表操作等）
- 元件图形符号仅实现 GB/T 4728 中与上述范围相关的常用低压符号子集，并非完整的标准符号表

**输出性质 / Nature of output**

- 所有解答与图形均由模型生成，供学习参考，**可能存在错误**；计算过程、符号书写与安全规程表述须经人工复核。
- 本技能不替代教材、教师与正式培训。安全规程类内容以现行法规和用户所在教材为准。

## 功能 / Features

- **图片预处理**：按文件魔数识别真实格式，旋转转正、灰度增强、放大裁切，适用于拍摄的题目照片
- **符号规范**：有效值相量（İ = I∠ψ）、瞬时值（i = I√2 sin(ωt+ψ)）、单位与下标遵循教材惯例；内置常见书写错误对照表
- **解题模板**：五步计算流程（定参考方向 → 写已知相量 → 列式代入 → 数值校验 → 反变换作答），含直流、正弦交流、RLC、三相、变压器、电动机六类题型模板
- **数值校验**：基尔霍夫电流定律、欧姆定律、时域抽样三重检查（`tools/ee.py`）
- **图形生成**：电路图、正弦波形图、相量图，SVG 与 PNG 双格式（`tools/eeplot.py`）；20 余种低压元件符号
- **交互演示（可选）**：正弦波形、相量转动、RLC 串并联计算三套卡片模板（`templates/`）
- **生成图自检**：结构与像素级检查（`tools/check_examples.py`）

## 示例 / Examples

| 电路图 Circuit | 相量图 Phasor diagram | 波形图 Waveform |
|---|---|---|
| ![并联电路](examples/circuit-parallel-r1r2.svg) | ![相量图](examples/phasor-r1r2.svg) | ![波形图](examples/wave-r1r2.svg) |

示例题：R₁ = 100 Ω、R₂ = 200 Ω 并联，i总 = 12√2 sin(314t − 120°) A，求 i₁、i₂。结果 İ₁ = 8∠−120° A、İ₂ = 4∠−120° A。RLC 串联示例见 `examples/circuit-series-rlc.svg` 与 `examples/wave-rlc-ui.svg`。

## 安装 / Installation

将本目录复制到 DSH 全局技能目录（目录名须与 `SKILL.md` 中 frontmatter 的 `name` 一致）：

```powershell
Copy-Item -Recurse -Force . "$env:USERPROFILE\.dsh\skills\deepseek-ee-solver"
```

重启 DSH 或新建会话后，技能列表中会出现 `deepseek-ee-solver`；提交电工类问题时自动触发。

## 使用 / Usage

- **对话使用**：直接发送题目文字或照片。默认输出为：规范转写的题面、五步解答（含数值校验）、静态图（SVG 与 PNG，存于工作区 `output/`）。提出“动画演示”等要求时改用交互卡片。
- **命令行使用**：

```powershell
python tools\ee.py                  # 相量运算库自检
python tools\eeplot.py demo         # 生成 examples/
python tools\eeplot.py spec.json    # 按规格出图（type: wave|phasor|parallel|series）
python tools\check_examples.py      # 生成图自检
```

## 目录结构 / Structure

```
deepseek-ee-solver/
├── SKILL.md                     # 技能主文件（触发条件、规范、流程、工具）
├── README.md / ABOUT.md         # 项目说明与简介（中英双语）
├── LICENSE                      # MIT
├── references/                  # 知识库：符号规范、解题模板、公式、元件符号、
│   │                            #   低压安全规程、图片预处理
├── tools/                       # ee.py（相量计算与校验）、eeplot.py（图形生成）、
│                                #   check_examples.py（自检）
├── templates/                   # 交互卡片模板（正弦波形、相量转动、RLC 演示）
└── examples/                    # 示例图（由 demo 生成）
```

## 依赖 / Dependencies

- 图形生成器仅依赖 Python 标准库；PNG 输出需 Pillow（DSH 运行时自带）与系统中文字体（如微软雅黑）。
- 交互卡片由 DSH 的 visualize 组件渲染，不依赖网络资源。

## 免责声明 / Disclaimer

本项目的全部输出（包括解答、公式、图形与安全规程表述）均由人工智能模型生成，仅供学习参考，不保证正确性与完整性；使用者应自行核对，并以现行法规、教材及培训要求为准。本项目不构成特种作业培训或认证服务。

All outputs (solutions, formulas, figures, and safety-regulation statements) are AI-generated and provided for learning reference only, without warranty of correctness or completeness. Users should verify them against current regulations, textbooks, and training requirements. This project does not constitute occupational training or certification services.

## License

[MIT](LICENSE)
