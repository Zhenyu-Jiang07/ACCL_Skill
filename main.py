from dotenv import load_dotenv
import os
from pathlib import Path
import json

from zai import ZhipuAiClient
from scripts.extract_signature import extract_metadata

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

# 组织给模型的输入
user_content = f"""下面是待分析的 CCCL 接口或头文件片段。

【原始代码】
{input_text}

【本地预处理提取结果】
{json.dumps(metadata, ensure_ascii=False, indent=2)}

请你结合原始代码与本地预处理结果，完成严格的结构化分析，并严格按照 system prompt 中给出的固定格式输出。
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

print(response.choices[0].message.content)