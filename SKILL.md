---
name: cccl-to-accl-mapping-skill
description: 分析单个 CCCL 接口片段，输出 ACCL 映射结论、wrapper 判断与迁移风险说明
---

## 1. Skill 简介
本 Skill 面向华为昇腾代码迁移场景，目标是辅助完成 CCCL 接口到 ACCL 的初步对照与迁移分析。

当前版本聚焦于 **单个 CCCL 接口或头文件片段** 的分析，能够结合：
- 原始代码内容
- 本地预处理提取结果
- 本地规则提示结果

生成一份结构化的接口分析报告，用于支持后续的 ACCL 设计、wrapper 判断和迁移风险识别。

---

## 2. 适用场景
本 Skill 适用于以下场景：

- 分析单个 CCCL 接口的功能与语义
- 判断接口在 ACCL 中的初步映射方式
- 判断该接口是否可能需要 wrapper
- 识别迁移过程中的潜在风险点
- 生成结构化的 Markdown 分析报告

---

## 3. 当前输入范围
当前版本仅支持以下输入形式：

- 单个 CCCL 接口声明
- 单个头文件中的局部代码片段
- 包含必要注释和实现逻辑的单接口代码片段

当前版本**暂不支持**：

- 整个仓库级分析
- 多文件联动分析
- 批量接口分析
- 自动检索整个 CCCL 项目
- 自动生成 ACCL 实现代码

---

## 4. 输出内容
本 Skill 输出一份结构化 Markdown 报告，包含以下内容：

- 接口名称
- 功能说明
- 参数说明
- 返回值说明
- 约束条件
- 所属能力类别
- ACCL 映射结论
- ACCL 映射建议
- 是否需要 wrapper
- wrapper 原因
- 风险与说明

输出文件默认保存为：

`outputs/result.md`

---

## 5. 处理流程
本 Skill 当前采用以下处理流程：

1. 读取待分析的 CCCL 接口片段
2. 使用本地脚本提取基础结构化信息，包括：
   - 函数名
   - 签名行
   - 参数列表
   - 返回值线索
   - 约束条件线索
   - 注释块
3. 使用本地规则脚本生成辅助提示，包括：
   - 能力类别提示
   - 映射倾向提示
   - wrapper 倾向提示
   - 风险提示
4. 将原始代码、本地预处理结果和规则提示结果一并发送给智谱模型
5. 由模型生成结构化分析结果
6. 将结果整理为 Markdown 报告并保存到输出目录

---

## 6. 当前目录结构
当前 Skill 项目目录如下：

```text
cccl_to_accl_mapping_skill/
├── SKILL.md
├── README.md
├── .env
├── main.py
├── prompts/
│   └── mapping_prompt.md
├── scripts/
│   ├── extract_signature.py
│   ├── match_rules.py
│   └── format_report.py
├── examples/
│   ├── input_example.h
│   └── output_example.md
└── outputs/