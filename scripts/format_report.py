from datetime import datetime


def format_markdown_report(raw_result: str, source_name: str = "input_example.h") -> str:
    """将模型原始输出整理成 Markdown 报告。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# CCCL 接口映射分析报告

- 来源文件：{source_name}
- 生成时间：{timestamp}

---

{raw_result}
"""
    return report