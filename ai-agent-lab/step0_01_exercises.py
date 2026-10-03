"""Step 0-1 练习：基础语法

用法
    1. 只在 TODO 处补代码，其他地方不要动
    2. 按 F5 运行，看得分（空模板 0/11，全做完 11/11）
    3. 卡住超过 5 分钟，再看 step0_01_solutions.py

八道题
    1 list 容器    2 dict 读写    3 f-string    4 列表推导式
    5 循环统计     6 默认参数     7 多返回值     8 构造 tool 消息

每题上方给了 Java 写法，照着翻译成 Python 就行。
"""

from __future__ import annotations


# ---- 1. list 容器（Java 的 ArrayList）----
#   Java:  List<String> t = new ArrayList<>(Arrays.asList("a", "b"));
#          t.add("c");   int n = t.size();
#   要求:  建 list 含 "get_weather" "calculate" → 追加 "read_file" → 返回元素个数
def exercise_1() -> int:
    return 0        # TODO


# ---- 2. dict 读写（Java 的 HashMap）----
#   Java:  Map<String,Object> m = new HashMap<>();
#          m.put("role", "user");   String r = (String) m.get("role");
#   要求:  建 dict（role="user"、content="你好"），返回 m["role"]
def exercise_2() -> str:
    return ""       # TODO


# ---- 3. f-string（Java 没有这个）----
#   Java:  String.format("用户 %s 今年 %d 岁", name, age)
#   要求:  返回 f"{name} 今年 {age} 岁"
def exercise_3(name: str, age: int) -> str:
    return ""       # TODO


# ---- 4. 列表推导式（Java 的 Stream）----
#   Java:  nums.stream().filter(n -> n % 2 == 0).map(n -> n * 10).collect(toList())
#   要求:  传入 [1,2,3,4,5,6] → 返回 [20, 40, 60]
def exercise_4(nums: list[int]) -> list[int]:
    return []       # TODO


# ---- 5. 循环统计（AI 实战：数每个工具被调了几次）----
#   输入:  [{"function":{"name":"get_weather"}}, {"function":{"name":"get_weather"}},
#           {"function":{"name":"calculate"}}]
#   要求:  返回 {"get_weather": 2, "calculate": 1}
#   提示:  for 循环 + d[name] = d.get(name, 0) + 1
def exercise_5(tool_calls: list[dict]) -> dict[str, int]:
    return {}       # TODO


# ---- 6. 默认参数（Java 得写重载，Python 一个默认值搞定）----
#   要求:  exercise_6("启动")            → "[INFO] 启动"
#          exercise_6("启动", "DEBUG")   → "[DEBUG] 启动"
def exercise_6(msg: str, level: str = "INFO") -> str:
    return ""       # TODO


# ---- 7. 多返回值（Java 要么抛异常，要么造个 Result 类）----
#   要求:  safe_divide(10, 2) → (5.0, "")
#          safe_divide(10, 0) → (None, "除数不能为 0")
def safe_divide(a: float, b: float) -> tuple[float | None, str]:
    return None, ""  # TODO


# ---- 8. 构造 tool 消息（Agent 循环每轮都干这件事）----
#   要求:  build_tool_message("call_abc", "晴，18度")
#          → {"role": "tool", "tool_call_id": "call_abc", "content": "晴，18度"}
#   注意:  content 必须是字符串。传进来数字 42，要变成 "42"
def build_tool_message(tool_call_id: str, result: object) -> dict:
    return {}       # TODO


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_01"))
