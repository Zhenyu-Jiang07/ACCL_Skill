# CCCL → ACCL 接口映射 Skill 原型

## 1. 项目简介
本项目是一个面向华为昇腾代码迁移场景的 Skill 原型，目标是辅助完成 **CCCL → ACCL** 的接口对照与迁移分析。

当前版本聚焦于**单个 CCCL 接口或头文件片段**的分析，能够结合：
- 原始代码内容
- 本地预处理提取结果
- 本地规则提示结果
- 智谱模型分析能力

输出一份结构化的 Markdown 分析报告，用于支持后续的 ACCL 设计、wrapper 判断和迁移风险识别。

---

## 2. 当前能力
当前原型已经实现以下流程：

1. 读取单个 CCCL 接口片段
2. 使用本地脚本提取基础结构信息
3. 使用本地规则生成辅助提示
4. 调用智谱模型完成结构化分析
5. 输出 Markdown 报告到 `outputs/result.md`

---

## 3. 项目目录结构

```text
cccl-to-accl-mapping-skill/
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
    └── result.md
```

---

## 4. 环境准备

### 4.1 创建 conda 环境

```bash
conda create -n accl_skill python=3.10 -y
conda activate accl_skill
```

### 4.2 安装依赖

```bash
pip install -U zai-sdk python-dotenv
```

---

## 5. 配置 API Key

在项目根目录下创建 `.env` 文件，并写入：

```env
ZHIPU_API_KEY=你的完整APIKey
```

说明：

- 需要使用智谱开放平台 API Key
- 当前原型通过 `zai-sdk` 调用智谱模型

---

## 6. 输入说明

当前版本默认从以下文件读取待分析内容：

```text
examples/input_example.h
```

你可以将待分析的 CCCL 接口声明、头文件片段或相关实现代码放入这个文件中。

建议：

- 第一版尽量使用单接口、短片段、语义明确的输入
- 避免一开始直接放入过大的复杂文件

---

## 7. 运行方式

在项目根目录执行：

```bash
python main.py
```

---

## 8. 输出结果

运行后会在终端打印分析结果，并将格式化后的 Markdown 报告保存到：

```text
outputs/result.md
```

报告内容包括：

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

---

## 9. 主要脚本说明

### `main.py`

主程序入口，负责串联整个流程：

- 读取输入
- 调用预处理
- 调用规则层
- 调用智谱模型
- 输出并保存报告

### `scripts/extract_signature.py`

本地预处理脚本，负责提取：

- 函数名
- 签名行
- 参数列表
- 返回值线索
- 约束条件线索
- 注释块

### `scripts/match_rules.py`

本地规则层脚本，负责生成：

- 能力类别提示
- 映射倾向提示
- wrapper 倾向提示
- 风险提示

### `scripts/format_report.py`

负责将模型原始输出整理为 Markdown 报告格式。

### `prompts/mapping_prompt.md`

定义给模型使用的结构化分析 Prompt。

---

## 10. 当前版本限制

当前版本属于原型阶段，主要限制包括：

- 仅支持单个接口片段分析
- 不支持整个仓库或多文件联动分析
- 不支持批量处理
- 不支持自动生成 ACCL 实现代码
- 预处理脚本不是完整 C++ 解析器
- 模型输出仍属于初步分析结果，需结合人工判断

---

## 11. 后续可扩展方向

后续可以继续扩展：

- 增加更多 CCCL 接口测试样例
- 增强规则层覆盖范围
- 支持多文件/模块级分析
- 输出更标准化的结构化结果
- 进一步结合 ACCL 设计和 wrapper 辅助生成流程

---

## 12. 当前版本结论

当前项目已经完成一个最小可运行原型，能够实现：

**输入 CCCL 接口片段 → 本地预处理 → 本地规则辅助 → 智谱模型分析 → Markdown 报告输出**

可作为后续扩展为更完整昇腾代码迁移 Skill 的基础版本。