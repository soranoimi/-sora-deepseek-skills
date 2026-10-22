# deepseek基础电工题目解析 · DeepSeek Basic Electrical Problem Solver

## 一句话简介 / One-liner

**中文**：面向 DeepSeek Harness 的电工学习辅助技能，可解析电工题目并绘制电路图、正弦波形图与相量图；知识范围限于职高《电工基础》教材与低压电工特种作业操作证理论考试常见内容，输出供学习参考，须经人工复核。

**English**: A learning-aid skill for DeepSeek Harness that parses electrical problems and renders circuit, sine-waveform, and phasor diagrams. Its knowledge scope is limited to the vocational high-school textbook *《电工基础》* and common theory topics of the low-voltage electrician certificate examination; outputs are for reference and require human review.

## 简介 / Introduction

### 中文

本项目是运行于 DeepSeek Harness 的电工学习辅助技能。围绕职高《电工基础》教学与低压电工证理论学习中的常见需求，提供以下能力：

- **图片预处理**：按文件魔数识别真实格式，对拍摄的题目照片进行旋转转正、灰度增强与放大裁切；
- **符号规范输出**：按教材惯例书写有效值相量（İ = I∠ψ）与瞬时值（i = I√2 sin(ωt+ψ)），保留单位与下标，内置常见书写错误对照；
- **五步解题**：定参考方向 → 写已知相量 → 列式代入 → 数值校验（基尔霍夫定律、欧姆定律、时域抽样）→ 反变换作答；
- **图形生成**：依据 GB/T 4728 常用低压符号子集绘制电路图、正弦波形图与相量图，输出 SVG 与 PNG 双格式；
- **交互演示（可选）**：正弦波形、相量转动、RLC 串并联计算三套卡片模板；
- **低压安全规程简表**：安全电压、触电急救、接地与接零、电气防火及判断题要点。

**边界说明**：本技能不覆盖大学《电路原理》层次内容、电子技术、高压电工与实操培训；元件符号为常用子集而非全表；全部输出由模型生成，可能出错，须经人工复核，不替代教材、教师与正式培训。

### English

This project is a learning-aid skill running on DeepSeek Harness. It addresses common needs in the vocational textbook *《电工基础》* and low-voltage certificate theory study:

- **Image preprocessing**: identifies true file formats by magic bytes; rotates, enhances, and crops photos of problems;
- **Notation-correct output**: writes RMS phasors (İ = I∠ψ) and instantaneous values (i = I√2 sin(ωt+ψ)) per textbook conventions, with units and subscripts, plus a table of common notation errors;
- **Five-step solving**: reference directions → known phasors → formulas with substitution → numeric verification (KCL, Ohm's law, time-domain sampling) → inverse transform and final answer;
- **Diagram generation**: circuit, sine-waveform, and phasor diagrams from a common low-voltage subset of GB/T 4728 symbols, in SVG and PNG;
- **Optional interactive demos**: sine-wave animation, phasor rotation, and an RLC series/parallel calculator;
- **Low-voltage safety quick reference**: safety voltages, first aid, earthing/zeroing, electrical fire, and judgment-question notes.

**Scope**: university-level circuit theory, electronics, high-voltage work, and hands-on training are outside its scope; the symbol set is a subset, not the full standard; all outputs are model-generated and require human review. It does not replace textbooks, teachers, or formal training.

## 技术说明 / Technical notes

- 图形引擎零第三方依赖：Python 标准库实现场景图与 SVG 后端，PNG 后端使用 Pillow（DSH 运行时自带）；
- 校验强制：数值题执行三重校验，生成图执行结构与像素自检（`tools/check_examples.py`）；
- 文档与技能指令中英双语；答案语言默认中文，可按需切换英文。

Zero third-party dependencies for the graphics engine (stdlib scene graph + SVG backend; PNG uses Pillow, bundled with DSH); numeric problems are triple-verified and generated figures pass structural and pixel self-checks; skill instructions and documentation are bilingual (Chinese default, English on request).
