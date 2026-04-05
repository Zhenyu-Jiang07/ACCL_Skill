import re
from pathlib import Path
from typing import Dict, List


def extract_comment_blocks(text: str) -> List[str]:
    """提取连续的 //! 或 /// 风格注释块。"""
    comment_blocks = []
    current_block = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("//!") or stripped.startswith("///"):
            current_block.append(stripped)
        else:
            if current_block:
                comment_blocks.append("\n".join(current_block))
                current_block = []

    if current_block:
        comment_blocks.append("\n".join(current_block))

    return comment_blocks


def is_candidate_signature_line(line: str) -> bool:
    """
    判断某一行是否像函数声明/定义行。
    这里做保守判断，只接受比较像接口签名的行。
    """
    stripped = line.strip()

    if not stripped:
        return False

    # 排除注释、宏定义、include、防卫宏等
    if stripped.startswith("//"):
        return False
    if stripped.startswith("#"):
        return False
    if stripped.startswith("/*") or stripped.startswith("*"):
        return False

    # 必须同时有左右括号
    if "(" not in stripped or ")" not in stripped:
        return False

    # 排除明显不是函数签名的情况
    blacklist_prefixes = (
        "if ", "if(",
        "for ", "for(",
        "while ", "while(",
        "switch ", "switch(",
        "return ",
        "static_cast",
    )
    if stripped.startswith(blacklist_prefixes):
        return False

    # 排除纯宏调用行
    macro_like_prefixes = (
        "_CCCL_TEMPLATE",
        "_CCCL_REQUIRES",
        "_CCCL_BEGIN_NAMESPACE_CUDA",
        "_CCCL_END_NAMESPACE_CUDA",
    )
    if stripped.startswith(macro_like_prefixes):
        return False

    # 要求行里至少有常见函数声明特征之一
    signature_keywords = (
        "constexpr",
        "noexcept",
        "[[nodiscard]]",
        "_CCCL_API",
    )
    if any(keyword in stripped for keyword in signature_keywords):
        return True

    return False


def extract_signature_line(text: str) -> str:
    """提取最像函数声明/定义的那一行。"""
    for line in text.splitlines():
        if is_candidate_signature_line(line):
            return line.strip()
    return "无法从当前输入确定"


def extract_function_name(signature_line: str) -> str:
    """从签名行中提取函数名。"""
    if signature_line == "无法从当前输入确定":
        return "无法从当前输入确定"

    # 匹配函数名(参数...) 里的函数名
    match = re.search(r'\b([A-Za-z_]\w*)\s*\(', signature_line)
    if not match:
        return "无法从当前输入确定"

    name = match.group(1)

    blacklist = {"if", "for", "while", "switch", "return", "static_cast"}
    if name in blacklist:
        return "无法从当前输入确定"

    return name


def extract_parameters(signature_line: str) -> List[str]:
    """从签名行中粗略提取参数列表。"""
    if signature_line == "无法从当前输入确定":
        return []

    match = re.search(r'\((.*)\)', signature_line)
    if not match:
        return []

    param_text = match.group(1).strip()
    if not param_text:
        return []

    return [p.strip() for p in param_text.split(",") if p.strip()]


def extract_constraints(text: str, signature_line: str) -> List[str]:
    """提取约束条件相关线索。"""
    constraints = []

    for line in text.splitlines():
        stripped = line.strip()
        if "_CCCL_REQUIRES" in stripped:
            constraints.append(stripped)

    if signature_line != "无法从当前输入确定":
        if "constexpr" in signature_line or "noexcept" in signature_line:
            constraints.append(signature_line)

    return constraints


def extract_return_hint(signature_line: str, function_name: str) -> str:
    """从签名行中粗略提取返回值类型线索。"""
    if signature_line == "无法从当前输入确定":
        return "无法从当前输入确定"
    if function_name == "无法从当前输入确定":
        return "无法从当前输入确定"

    prefix = signature_line.split(function_name, 1)[0].strip()
    return prefix if prefix else "无法从当前输入确定"


def extract_metadata(text: str) -> Dict[str, object]:
    signature_line = extract_signature_line(text)
    function_name = extract_function_name(signature_line)
    parameters = extract_parameters(signature_line)
    constraints = extract_constraints(text, signature_line)
    return_hint = extract_return_hint(signature_line, function_name)
    comment_blocks = extract_comment_blocks(text)

    return {
        "function_name": function_name,
        "signature_line": signature_line,
        "parameters": parameters,
        "return_hint": return_hint,
        "constraints": constraints,
        "comment_blocks": comment_blocks,
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "examples" / "input_example.h"

    text = input_path.read_text(encoding="utf-8")
    result = extract_metadata(text)

    print("=== 提取结果 ===")
    for key, value in result.items():
        print(f"{key}: {value}")