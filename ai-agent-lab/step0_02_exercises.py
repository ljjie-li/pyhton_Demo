"""Step 0-2 练习：面向对象 + 类型注解 + pydantic

用法
    1. 只在 TODO 处补代码，其他地方不要动
    2. 按 F5 运行，看得分（空模板 0/15，全做完 15/15）
    3. 卡住超过 5 分钟，再看 step0_02_solutions.py

六道题
    1 @dataclass 定义类       2 pydantic 基础校验     3 自动类型转换
    4 自定义校验器            5 生成 LLM 工具 schema  6 解析 LLM 返回的参数

第 5、6 题是 AI 开发的核心：pydantic 就是工具定义和结构化输出的基础设施。
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field, ValidationError, field_validator


# ---- 1. @dataclass（Java 的 Lombok @Data）----
#   Java:  @Data public class ToolCall {
#              private String id;  private String name;  private String arguments = "";
#          }
#   要求:  用 @dataclass 定义 ToolCall，字段 id / name / arguments（有默认值 ""）
#          删掉下面的 pass，写上三个字段
@dataclass
class ToolCall:
    pass            # TODO


def exercise_1() -> ToolCall:
    """返回 ToolCall(id="call_1", name="get_weather", arguments='{"city":"北京"}')"""
    return None     # TODO


# ---- 2. pydantic 基础校验（Java 的 @Valid + @NotNull）----
#   要求:  SearchArgs 两个字段
#            query: str  —— 必填，描述 "检索关键词"
#            top_k: int  —— 默认 3，最小值 1，最大值 20
#          删掉 pass，写两个字段
class SearchArgs(BaseModel):
    pass            # TODO


def exercise_2() -> SearchArgs:
    """返回 SearchArgs(query="RAG", top_k=5)"""
    return None     # TODO


# ---- 3. 自动类型转换（Java 要自己 Integer.parseInt）----
#   要求:  用 SearchArgs 接收 query="x"、top_k="10"（注意是字符串）
#          返回转换后的 top_k（应该是 int 类型的 10）
def exercise_3() -> int:
    return 0        # TODO


# ---- 4. 自定义校验器（Java 的 @Pattern）----
#   要求:  TaskArgs 两个字段
#            task: str      —— 必填
#            priority: str  —— 默认 "medium"，只允许 low / medium / high
#          用 @field_validator("priority") + @classmethod 校验，
#          非法值要 raise ValueError(...)
class TaskArgs(BaseModel):
    pass            # TODO


def exercise_4() -> str:
    """构造 TaskArgs(task="写代码", priority="urgent")，捕获 ValidationError，
    返回 e.errors()[0]["msg"]（错误信息字符串）"""
    return ""       # TODO


# ---- 5. 生成 LLM 工具 schema（★ 本课重点）----
#   要求:  WeatherArgs 两个字段
#            city: str  —— 必填，描述 "城市名称"
#            days: int  —— 默认 1，范围 1-7，描述 "预报天数"
class WeatherArgs(BaseModel):
    pass            # TODO


def build_tool_schema() -> dict:
    """返回 OpenAI 格式的工具定义：
        {
          "type": "function",
          "function": {
              "name": "get_weather",
              "description": "查询指定城市的天气",
              "parameters": WeatherArgs.model_json_schema(),   ← 就这一行是关键
          },
        }
    """
    return {}       # TODO


# ---- 6. 解析 LLM 返回的参数（★ 本课重点）----
#   背景:  LLM 给的 tool_call 里，arguments 是 JSON 字符串，可能非法：
#          字段缺失 / 类型不对 / 值越界 / 根本不是 JSON。
#   要求:  实现 parse_tool_arguments(raw)
#            成功 → 返回 WeatherArgs 实例
#            失败 → 返回 None（ValidationError 和 JSON 错误都要接住）
def parse_tool_arguments(raw: str):
    return None     # TODO


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_02"))
