"""Step 0-2 参考答案

先自己做，卡住 5 分钟以上再看。
看完关掉这个文件，凭记忆重敲一遍。
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field, ValidationError, field_validator


# ---- 1. @dataclass ----
@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str = ""     # 有默认值的字段必须放最后


def exercise_1() -> ToolCall:
    return ToolCall(id="call_1", name="get_weather", arguments='{"city":"北京"}')
    # 注意：不用 new，类名直接当函数调用


# ---- 2. pydantic 基础校验 ----
class SearchArgs(BaseModel):
    query: str = Field(description="检索关键词")             # 无默认值 = 必填
    top_k: int = Field(default=3, ge=1, le=20, description="返回条数")
    #                         └≥1    └≤20


def exercise_2() -> SearchArgs:
    return SearchArgs(query="RAG", top_k=5)


# ---- 3. 自动类型转换 ----
def exercise_3() -> int:
    args = SearchArgs(query="x", top_k="10")   # 传的是字符串 "10"
    return args.top_k                          # 出来是 int 10
    # Java 里必须自己 Integer.parseInt()，pydantic 自动做


# ---- 4. 自定义校验器 ----
class TaskArgs(BaseModel):
    task: str = Field(description="任务描述")
    priority: str = Field(default="medium", description="优先级")

    @field_validator("priority")      # 必须配 @classmethod
    @classmethod
    def priority_must_be_valid(cls, v: str) -> str:
        allowed = {"low", "medium", "high"}
        if v not in allowed:
            raise ValueError(f"priority 必须是 {allowed} 之一，收到 {v!r}")
        return v


def exercise_4() -> str:
    try:
        TaskArgs(task="写代码", priority="urgent")
    except ValidationError as e:
        return e.errors()[0]["msg"]
    return ""


# ---- 5. 生成 LLM 工具 schema ----
class WeatherArgs(BaseModel):
    city: str = Field(description="城市名称")
    days: int = Field(default=1, ge=1, le=7, description="预报天数")


def build_tool_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": WeatherArgs.model_json_schema(),   # ★ 就这一行
        },
    }
    # 对比 step1 里手写的 18 行 JSON：这个永远不会和函数定义不一致


# ---- 6. 解析 LLM 返回的参数 ----
def parse_tool_arguments(raw: str) -> WeatherArgs | None:
    try:
        return WeatherArgs.model_validate_json(raw)
    except ValidationError:
        # 字段缺失 / 类型不对 / 值越界 / 不是合法 JSON，全在这里被接住
        return None
    except Exception:
        return None     # 兜底：任何意外都不让 Agent 崩


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_02", mode="solution"))
