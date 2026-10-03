"""Step 0-1 参考答案

先自己做，卡住 5 分钟以上再看。
看完关掉这个文件，凭记忆重敲一遍——比看懂重要 10 倍。
"""

from __future__ import annotations


# ---- 1. list 容器 ----
def exercise_1() -> int:
    tools = ["get_weather", "calculate"]   # ① [] 字面量建 list，不用 new
    tools.append("read_file")              # ② .append() 对应 ArrayList.add()
    return len(tools)                      # ③ len() 是函数，不是 .size() 方法


# ---- 2. dict 读写 ----
def exercise_2() -> str:
    message = {"role": "user", "content": "你好"}   # ① 字面量建 dict
    return message["role"]                          # ② [] 取值，对应 map.get()


# ---- 3. f-string ----
def exercise_3(name: str, age: int) -> str:
    return f"{name} 今年 {age} 岁"   # f 前缀 + {} 里直接写变量，不用管类型


# ---- 4. 列表推导式 ----
def exercise_4(nums: list[int]) -> list[int]:
    return [n * 10 for n in nums if n % 2 == 0]
    #      └─要什么─┘ └从哪来┘ └─要哪些─┘
    # 等价写法：
    #   result = []
    #   for n in nums:
    #       if n % 2 == 0:
    #           result.append(n * 10)
    #   return result


# ---- 5. 循环统计 ----
def exercise_5(tool_calls: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for tc in tool_calls:
        name = tc["function"]["name"]
        counts[name] = counts.get(name, 0) + 1   # .get(k, 默认值) = Java 的 getOrDefault
    return counts
    # 更 Pythonic 的写法（先理解上面那个）：
    #   from collections import Counter
    #   return dict(Counter(tc["function"]["name"] for tc in tool_calls))


# ---- 6. 默认参数 ----
def exercise_6(msg: str, level: str = "INFO") -> str:
    return f"[{level}] {msg}"
    # Java 要写三个重载方法，Python 一个默认值搞定


# ---- 7. 多返回值 ----
def safe_divide(a: float, b: float) -> tuple[float | None, str]:
    if b == 0:
        return None, "除数不能为 0"
    return a / b, ""
    # 注意 Python 3 的 / 永远是浮点除法：10 / 2 = 5.0


# ---- 8. 构造 tool 消息 ----
def build_tool_message(tool_call_id: str, result: object) -> dict:
    return {
        "role": "tool",              # ① 角色固定 "tool"
        "tool_call_id": tool_call_id,  # ② 必须和 LLM 返回的 tool_call.id 对应
        "content": str(result),      # ③ 必须转字符串
    }


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_01", mode="solution"))
