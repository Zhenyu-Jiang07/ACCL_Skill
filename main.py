from dotenv import load_dotenv
import os
from pathlib import Path
import json

from zai import ZhipuAiClient
from scripts.extract_signature import extract_metadata
from scripts.match_rules import build_rule_hints
from scripts.format_report import format_markdown_report

load_dotenv()

api_key = os.getenv("ZHIPU_API_KEY")
if not api_key:
    raise ValueError("未读取到 ZHIPU_API_KEY，请检查 .env 文件")

client = ZhipuAiClient(api_key=api_key)

project_root = Path(__file__).parent

# 读取 system prompt
prompt_path = project_root / "prompts" / "mapping_prompt.md"
prompt_text = prompt_path.read_text(encoding="utf-8")

# 读取待分析接口内容
input_path = project_root / "examples" / "input_example.h"
input_text = input_path.read_text(encoding="utf-8")

# 本地预处理提取
metadata = extract_metadata(input_text)

# 本地规则提示
rule_hints = build_rule_hints(input_text, metadata)

# 组织给模型的输入
user_content = f"""下面是待分析的 CCCL 接口或头文件片段。

【原始代码】
{input_text}

【本地预处理提取结果】
{json.dumps(metadata, ensure_ascii=False, indent=2)}

【本地规则提示结果】
{json.dumps(rule_hints, ensure_ascii=False, indent=2)}

请你结合原始代码、本地预处理结果和本地规则提示结果，完成严格的结构化分析，并严格按照 system prompt 中给出的固定格式输出。

注意：
1. 本地规则提示仅作为辅助参考，不能替代你对原始代码的判断。
2. 如果本地规则提示与代码本身不一致，优先以代码本身为准。
3. 你可以参考规则提示提高分析稳定性，但不能机械重复规则内容。
"""

response = client.chat.completions.create(
    model="glm-5",
    messages=[
        {
            "role": "system",
            "content": prompt_text
        },
        {
            "role": "user",
            "content": user_content
        }
    ]
)

result_text = response.choices[0].message.content

# 格式化报告
report_text = format_markdown_report(result_text, source_name=input_path.name)

# 终端打印原始结果
print(result_text)

# 保存到文件
output_dir = project_root / "outputs"
output_dir.mkdir(exist_ok=True)

output_path = output_dir / "result.md"
output_path.write_text(report_text, encoding="utf-8")

print(f"\n结果已保存到: {output_path}")