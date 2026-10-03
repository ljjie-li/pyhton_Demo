"""step0 练习自测运行器（4 课共用）。

⚠️ 这个是给程序用的，学员不用打开、不用改。
   练习题 / 答案文件末尾只有 3 行代码调用它：

       if __name__ == "__main__":
           from _selftest_base import run_suite
           raise SystemExit(run_suite(globals(), "step0_01"))
"""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import io
from typing import Any, Callable


# ═══════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════


def _none(*args: Any, **kwargs: Any) -> str:
    """学员还没写这个函数时的占位。"""
    return "<函数不存在>"


def _safe(fn: Callable, *args: Any) -> Any:
    """调用学员函数，异常转成标记字符串（不让自测崩掉）。"""
    try:
        return fn(*args)
    except Exception as e:
        return f"<异常 {type(e).__name__}: {e}>"


def _run_async(fn: Callable, *args: Any) -> Any:
    """调用异步函数（学员写成同步也能容错）。"""
    try:
        r = fn(*args)
    except Exception as e:
        return f"<异常 {type(e).__name__}: {e}>"
    if inspect.iscoroutine(r):
        try:
            return asyncio.run(r)
        except Exception as e:
            return f"<异常 {type(e).__name__}: {e}>"
    return r


class Checker:
    """记分 + 打印。"""

    def __init__(self) -> None:
        self.passed = 0
        self.total = 0
        self._group = None

    def __call__(self, group: str, label: str, got: Any, expected: Any) -> None:
        if group != self._group:
            print(f"\n[{group}]")
            self._group = group
        self.total += 1
        if got == expected:
            self.passed += 1
            print(f"  [OK]   {label}")
        else:
            print(f"  [FAIL] {label}")
            print(f"         期望: {expected!r}")
            print(f"         实际: {got!r}")


# ═══════════════════════════════════════════════════════════════
# 各课用例
# ═══════════════════════════════════════════════════════════════


def _check_01(ns: dict, c: Checker) -> None:
    """基础语法（11 项）。"""
    def f(name: str) -> Callable:
        return ns.get(name, _none)

    c("1. 容器", "list 长度", _safe(f("exercise_1")), 3)
    c("2. dict", "role 取值", _safe(f("exercise_2")), "user")
    c("3. f-string", "拼字符串", _safe(f("exercise_3"), "李俊杰", 30), "李俊杰 今年 30 岁")
    c("4. 推导式", "偶数×10", _safe(f("exercise_4"), [1, 2, 3, 4, 5, 6]), [20, 40, 60])

    tool_calls = [
        {"function": {"name": "get_weather"}},
        {"function": {"name": "get_weather"}},
        {"function": {"name": "calculate"}},
    ]
    c("5. 循环统计", "工具计数", _safe(f("exercise_5"), tool_calls),
      {"get_weather": 2, "calculate": 1})

    c("6. 默认参数", "默认 level", _safe(f("exercise_6"), "启动"), "[INFO] 启动")
    c("6. 默认参数", "指定 level", _safe(f("exercise_6"), "启动", "DEBUG"), "[DEBUG] 启动")

    c("7. 多返回值", "正常除法", _safe(f("safe_divide"), 10, 2), (5.0, ""))
    c("7. 多返回值", "除零", _safe(f("safe_divide"), 10, 0), (None, "除数不能为 0"))

    c("8. tool 消息", "字符串结果", _safe(f("build_tool_message"), "call_abc", "晴，18度"),
      {"role": "tool", "tool_call_id": "call_abc", "content": "晴，18度"})
    c("8. tool 消息", "数字转字符串", _safe(f("build_tool_message"), "call_xyz", 42),
      {"role": "tool", "tool_call_id": "call_xyz", "content": "42"})


def _check_02(ns: dict, c: Checker) -> None:
    """OOP + 类型注解 + pydantic（15 项）。"""
    def f(name: str) -> Callable:
        return ns.get(name, _none)

    # 1. dataclass
    tc = _safe(f("exercise_1"))
    c("1. dataclass", "类型是 ToolCall", type(tc).__name__, "ToolCall")
    c("1. dataclass", "name 字段", getattr(tc, "name", None), "get_weather")
    c("1. dataclass", "arguments 字段", getattr(tc, "arguments", None), '{"city":"北京"}')

    # 2. pydantic 基础
    sa = _safe(f("exercise_2"))
    c("2. pydantic", "query", getattr(sa, "query", None), "RAG")
    c("2. pydantic", "top_k", getattr(sa, "top_k", None), 5)

    # 3. 自动类型转换
    c("3. 类型转换", "字符串 '10' → int 10", _safe(f("exercise_3")), 10)

    # 4. 自定义校验器
    c("4. 校验器", "返回了错误信息", bool(_safe(f("exercise_4"))), True)

    # 5. 生成工具 schema
    schema = _safe(f("build_tool_schema"))
    if isinstance(schema, dict):
        fn = schema.get("function", {})
        params = fn.get("parameters", {})
    else:
        fn, params = {}, {}
    c("5. 工具 schema", "顶层 type", schema.get("type") if isinstance(schema, dict) else schema, "function")
    c("5. 工具 schema", "function.name", fn.get("name"), "get_weather")
    c("5. 工具 schema", "function.description", fn.get("description"), "查询指定城市的天气")
    c("5. 工具 schema", "parameters.type", params.get("type"), "object")
    c("5. 工具 schema", "parameters 含 city", "city" in params.get("properties", {}), True)

    # 6. 解析 LLM 参数
    parser = f("parse_tool_arguments")
    good = _safe(parser, '{"city": "北京", "days": 3}')
    c("6. 解析参数", "合法 JSON → 拿到对象", getattr(good, "city", None), "北京")
    c("6. 解析参数", "days 解析正确", getattr(good, "days", None), 3)
    # 三种非法输入必须都返回 None；同时合法输入要能通过，
    # 否则「永远返回 None」的空实现也会被算对
    rejects_ok = (
        getattr(good, "city", None) == "北京"
        and _safe(parser, '{"city": "北京", "days": 99}') is None
        and _safe(parser, "不是 JSON") is None
        and _safe(parser, '{"days": 3}') is None
    )
    c("6. 解析参数", "越界 / 非法 / 缺字段 都返回 None", rejects_ok, True)


def _check_03(ns: dict, c: Checker) -> None:
    """异步 IO（10 项）。"""
    def f(name: str) -> Callable:
        return ns.get(name, _none)

    c("1. 异步改造", "async_tool 返回正确", _run_async(f("async_tool"), "X"), "X 完成")

    c("2. 并发", "结果与顺序", _run_async(f("run_three")), ["A 完成", "B 完成", "C 完成"])

    r3 = _run_async(f("run_with_failures"))
    c("3. 异常容错", "长度 3", len(r3) if isinstance(r3, list) else r3, 3)
    c("3. 异常容错", "内容与顺序", r3, ["ok1", "ERROR:网络超时", "ok2"])

    c("4. 超时", "超时返回 TIMEOUT", _run_async(f("call_with_timeout")), "TIMEOUT")

    r5 = _run_async(f("run_limited"))
    expected_fetches = [f"片段{i}" for i in range(8)]
    if isinstance(r5, tuple) and len(r5) == 2:
        c("5. 限流", "8 个结果且内容正确", r5[0], expected_fetches)
        c("5. 限流", "峰值并发 = 3", r5[1], 3)
    else:
        c("5. 限流", "8 个结果且内容正确", r5, expected_fetches)
        c("5. 限流", "峰值并发 = 3", None, 3)

    tool_calls = [
        {"id": "c1", "function": {"name": "get_weather", "arguments": '{"city":"北京"}'}},
        {"id": "c2", "function": {"name": "get_weather", "arguments": '{"city":"上海"}'}},
    ]
    r6 = _run_async(f("execute_tool_calls_async"), tool_calls)
    c("6. 异步工具", "返回 2 条", len(r6) if isinstance(r6, list) else r6, 2)
    c("6. 异步工具", "第一条", r6[0] if isinstance(r6, list) and r6 else None,
      {"role": "tool", "tool_call_id": "c1", "content": "北京：晴，18°C"})
    c("6. 异步工具", "第二条", r6[1] if isinstance(r6, list) and len(r6) > 1 else None,
      {"role": "tool", "tool_call_id": "c2", "content": "上海：晴，18°C"})


def _check_04(ns: dict, c: Checker) -> None:
    """装饰器 / 生成器 / 上下文管理器（10 项）。"""
    def f(name: str) -> Callable:
        return ns.get(name, _none)

    # 1. 装饰器：必须真包了一层（原样返回未装饰的函数不算）
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        added = _safe(f("add"), 1, 2)
    logged = buf.getvalue()
    c("1. 装饰器", "add 返回 3、名称保留、调用时有日志",
      (added == 3
       and getattr(f("add"), "__name__", None) == "add"
       and "调用" in logged and "返回" in logged), True)

    # 2. 带参装饰器 repeat —— 现场造一个被装饰的函数
    calls: list[str] = []
    try:
        decorated = f("repeat")(n=3)(lambda msg: calls.append(msg) or msg)
        decorated("hi")
        c("2. repeat", "执行 3 次", len(calls), 3)
    except Exception as e:
        c("2. repeat", "执行 3 次", f"<异常 {type(e).__name__}: {e}>", 3)

    # 3. 分批生成器
    def as_list(fn: Callable, *args: Any) -> Any:
        try:
            return list(fn(*args))
        except Exception as e:
            return f"<异常 {type(e).__name__}: {e}>"

    c("3. batch", "分批", as_list(f("batch"), [1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])
    c("3. batch", "整除", as_list(f("batch"), [1, 2, 3, 4], 2), [[1, 2], [3, 4]])
    # 空输入 + 单元素一起判，避免「返回空迭代器」的空实现蒙混过关
    c("3. batch", "空输入 / 单元素",
      (as_list(f("batch"), [], 2) == [] and as_list(f("batch"), [1], 2) == [[1]]), True)

    # 4. 流式生成器
    c("4. 流式", "按空格切词", as_list(f("stream_words"), "你好 世界 再见"),
      ["你好", "世界", "再见"])

    # 5. 上下文管理器：既要 yield 出 dict，也要有进入/退出日志
    tb = io.StringIO()
    span_is_dict: Any = None
    try:
        with contextlib.redirect_stdout(tb):
            with f("trace_span")("llm_call") as span:
                span_is_dict = isinstance(span, dict)
        tlog = tb.getvalue()
        c("5. trace_span", "yield 出 dict 且打了开始/结束日志",
          (span_is_dict is True and "开始" in tlog and "结束" in tlog), True)
    except Exception as e:
        c("5. trace_span", "yield 出 dict 且打了开始/结束日志",
          f"<异常 {type(e).__name__}: {e}>", True)

    # 6. retry —— 现场造两个测试函数
    attempts = {"n": 0}

    try:
        @f("retry")(max_attempts=3)
        def flaky() -> str:
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise ValueError("暂时失败")
            return "成功了"

        c("6. retry", "重试后成功", _safe(flaky), "成功了")
        c("6. retry", "尝试了 3 次", attempts["n"], 3)
    except Exception as e:
        c("6. retry", "重试后成功", f"<异常 {type(e).__name__}: {e}>", "成功了")
        c("6. retry", "尝试了 3 次", attempts["n"], 3)

    try:
        @f("retry")(max_attempts=2)
        def always_fail() -> str:
            raise ValueError("一直失败")

        try:
            always_fail()
            c("6. retry", "全失败抛最后异常", "<没抛异常>", "一直失败")
        except ValueError as e:
            c("6. retry", "全失败抛最后异常", str(e), "一直失败")
    except Exception as e:
        c("6. retry", "全失败抛最后异常", f"<异常 {type(e).__name__}: {e}>", "一直失败")


SUITES: dict[str, Callable[[dict, Checker], None]] = {
    "step0_01": _check_01,
    "step0_02": _check_02,
    "step0_03": _check_03,
    "step0_04": _check_04,
}

COURSE_NAMES = {
    "step0_01": "基础语法",
    "step0_02": "面向对象 + pydantic",
    "step0_03": "异步 IO",
    "step0_04": "装饰器 / 生成器 / 上下文管理器",
}


# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════


def run_suite(ns: dict, course: str, mode: str = "exercise") -> int:
    """跑一课的用例并打印得分。

    Args:
        ns: 调用方传 globals()
        course: "step0_01" ... "step0_04"
        mode: "exercise"（作业）/ "solution"（参考答案）
    """
    if course not in SUITES:
        print(f"[自测器] 未知课程: {course}")
        return 1

    line = "=" * 62
    title = COURSE_NAMES.get(course, course)
    print(line)
    if mode == "exercise":
        print(f"{course}  练习题 · {title}")
        print("这是你的作业文件。空模板得分低是正常的，全做对就满分。")
    else:
        print(f"{course}  参考答案 · {title}")
        print("这是小助理的答案，全绿是应该的。你的作业在同课 exercises.py。")
    print(line)

    c = Checker()
    SUITES[course](ns, c)

    print("\n" + line)
    print(f"得分: {c.passed}/{c.total}")
    if c.passed == c.total:
        print("全绿，这一课过关。")
    else:
        print(f"还差 {c.total - c.passed} 项。看同课 solutions 文件对照，然后关掉重敲一遍。")
    print(line)
    return 0 if c.passed == c.total else 1
