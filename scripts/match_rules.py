from typing import Dict, List


def _contains_any(text: str, keywords: List[str]) -> bool:
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


def build_rule_hints(raw_code: str, metadata: Dict[str, object]) -> Dict[str, object]:
    """
    根据原始代码和预处理结果，生成一组轻量规则提示。
    这些提示用于辅助模型分析，不直接替代模型判断。
    """
    hints = {
        "category_hint": [],
        "mapping_hint": [],
        "wrapper_hint": [],
        "risk_hints": [],
    }

    function_name = str(metadata.get("function_name", ""))
    constraints = metadata.get("constraints", [])
    comments = metadata.get("comment_blocks", [])

    merged_text = raw_code + "\n" + "\n".join(constraints) + "\n" + "\n".join(comments)

    # 规则 1：能力类别提示
    if _contains_any(merged_text, ["neg", "abs", "pow", "sqrt", "round", "ceil", "ilog"]):
        hints["category_hint"].append("倾向归类为：数学基础运算")

    if _contains_any(merged_text, ["bit", "unsigned", "to_unsigned_like", "make_unsigned", "~", "<<", ">>"]):
        hints["category_hint"].append("可能涉及：位运算工具 / 类型辅助逻辑")

    if _contains_any(merged_text, ["atomic", "compare_exchange", "fetch_add"]):
        hints["category_hint"].append("可能涉及：原子操作")

    if _contains_any(merged_text, ["memory", "memcpy", "memset", "allocator"]):
        hints["category_hint"].append("可能涉及：内存相关能力")

    # 规则 2：映射结论提示
    if _contains_any(merged_text, ["ptx", "asm(", "__device_builtin__", "__nvvm", "cooperative_groups"]):
        hints["mapping_hint"].append("检测到平台/硬件相关特征：更可能需要 wrapper 或人工复核")
    else:
        hints["mapping_hint"].append("未明显检测到 CUDA 硬件专属指令：更偏向可直接映射")

    # 规则 3：wrapper 提示
    if _contains_any(merged_text, ["ptx", "asm(", "intrinsic", "__shfl", "__syncwarp", "__ballot"]):
        hints["wrapper_hint"].append("存在平台专属能力调用：倾向需要 wrapper")
    else:
        hints["wrapper_hint"].append("未发现明显平台专属调用：倾向暂不需要 wrapper")

    # 规则 4：风险提示
    if _contains_any(merged_text, ["undefined behavior", "doesn't cause undefined behavior", "INT_MIN", "minimum value"]):
        hints["risk_hints"].append("需重点关注未定义行为规避逻辑，迁移时不能简单改写实现")

    if _contains_any(merged_text, ["to_unsigned_like", "make_unsigned", "__cccl_is_integer_v", "is_integer"]):
        hints["risk_hints"].append("依赖类型萃取或类型转换辅助工具，ACCL 侧需确认是否有对应实现")

    if _contains_any(merged_text, ["constexpr"]):
        hints["risk_hints"].append("需关注 constexpr 特性在昇腾编译环境中的保持情况")

    if _contains_any(merged_text, ["noexcept"]):
        hints["risk_hints"].append("需关注异常语义保持，确保迁移后接口仍满足 noexcept 预期")

    # 额外补充：函数名提示
    if function_name:
        hints["mapping_hint"].append(f"当前接口名为 `{function_name}`，建议结合其语义进行人工复核")

    return hints


if __name__ == "__main__":
    from pathlib import Path
    from extract_signature import extract_metadata

    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "examples" / "input_example.h"

    raw_code = input_path.read_text(encoding="utf-8")
    metadata = extract_metadata(raw_code)
    hints = build_rule_hints(raw_code, metadata)

    print("=== 规则提示结果 ===")
    for key, value in hints.items():
        print(f"{key}:")
        for item in value:
            print(f"  - {item}")