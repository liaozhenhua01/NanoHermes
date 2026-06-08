"""工具集定义和解析。

工具集是命名的工具分组，用于动态选择要暴露给 LLM 的工具子集。
支持 enabled_toolsets（白名单）和 disabled_toolsets（黑名单）两种过滤模式。
"""

from typing import Callable, Optional

# TOOLSETS 映射：toolset 名称 → 工具名称列表
TOOLSETS: dict[str, list[str]] = {
    "terminal": ["terminal", "process"],
    "file": ["read_file", "write_file", "search_files", "patch"],
    "memory": ["memory"],
    "skills": ["skill_manage", "skill_view", "skills_list"],
    "delegation": ["delegate_task"],
    "todo": ["todo"],
    "session_search": ["session_search"],
    "clarify": ["clarify"],
    "code_execution": ["execute_code"],
    "cronjob": ["cronjob"],
    "web": ["web_search"],
}

# 旧版工具集名称映射 → 现代名称
LEGACY_TOOLSET_MAP: dict[str, str] = {
    "terminal_tools": "terminal",
    "file_tools": "file",
    "memory_tools": "memory",
    "skills_tools": "skills",
    "delegation_tools": "delegation",
    "todo_tools": "todo",
}

# 工具集可用性检查函数（可选）
TOOLSET_CHECK_FNS: dict[str, Callable[[], bool]] = {}


def resolve_toolset(name: str) -> set[str]:
    """将工具集名称展开为工具名称集合。

    支持旧版名称自动映射到现代名称。
    如果工具集不存在，返回空集合。

    Args:
        name: 工具集名称（如 "terminal", "terminal_tools"）。

    Returns:
        该工具集包含的工具名称集合。
    """
    # 尝试旧版名称映射
    modern_name = LEGACY_TOOLSET_MAP.get(name, name)

    if modern_name not in TOOLSETS:
        return set()

    return set(TOOLSETS[modern_name])


def resolve_enabled_toolsets(
    enabled_toolsets: Optional[list[str]] = None,
    disabled_toolsets: Optional[list[str]] = None,
) -> set[str]:
    """解析当前启用的工具集，返回所有应启用的工具名称。

    优先级：
    1. 如果 enabled_toolsets 非空：只包含列出的工具集（白名单模式）
    2. 如果 disabled_toolsets 非空：排除列出的工具集（黑名单模式）
    3. 两者都为空：包含所有工具集

    Args:
        enabled_toolsets: 要启用的工具集名称列表。
        disabled_toolsets: 要禁用的工具集名称列表。

    Returns:
        所有应启用的工具名称集合。
    """
    result = set()

    if enabled_toolsets:
        # 白名单模式：只包含列出的工具集
        for ts_name in enabled_toolsets:
            modern_name = LEGACY_TOOLSET_MAP.get(ts_name, ts_name)
            if modern_name in TOOLSETS:
                # 检查可用性
                check_fn = TOOLSET_CHECK_FNS.get(modern_name)
                if check_fn and not check_fn():
                    continue
                result.update(TOOLSETS[modern_name])
    elif disabled_toolsets:
        # 黑名单模式：排除列出的工具集
        disabled_set = set()
        for ts_name in disabled_toolsets:
            modern_name = LEGACY_TOOLSET_MAP.get(ts_name, ts_name)
            disabled_set.add(modern_name)

        for ts_name, tools in TOOLSETS.items():
            if ts_name in disabled_set:
                continue
            check_fn = TOOLSET_CHECK_FNS.get(ts_name)
            if check_fn and not check_fn():
                continue
            result.update(tools)
    else:
        # 包含所有工具集
        for ts_name, tools in TOOLSETS.items():
            check_fn = TOOLSET_CHECK_FNS.get(ts_name)
            if check_fn and not check_fn():
                continue
            result.update(tools)

    return result


def register_toolset_check(name: str, check_fn: Callable[[], bool]) -> None:
    """注册工具集可用性检查函数。

    Args:
        name: 工具集名称。
        check_fn: 返回布尔值的无参函数，True 表示可用。
    """
    TOOLSET_CHECK_FNS[name] = check_fn
