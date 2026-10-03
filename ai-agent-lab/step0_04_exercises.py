"""Step 0-4 练习：装饰器 / 生成器 / 上下文管理器

用法
    1. 只在 TODO 处补代码，其他地方不要动
    2. 按 F5 运行，看得分（空模板 0/10，全做完 10/10）
    3. 卡住超过 5 分钟，再看 step0_04_solutions.py

六道题
    1 写个基础装饰器        2 带参数的装饰器（三层嵌套）
    3 分批生成器            4 模拟流式输出
    5 上下文管理器          6 retry 装饰器（Agent 必用）

★ 这三样东西就是看懂 LangGraph 源码的钥匙：
     @tool ≈ AOP   /   yield = 流式输出   /   with ≈ try-with-resources
"""

from __future__ import annotations

import functools
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from typing import Any, Callable


# ---- 1. 基础装饰器 ----
#   要求:  log_calls 装饰器，执行函数前后各打印一行：
#             调用 add(1, 2)
#             返回 3
#   注意:  必须加 @functools.wraps(func)，否则 add.__name__ 会变成 "wrapper"
def log_calls(func: Callable) -> Callable:
    return func     # TODO


@log_calls
def add(a: int, b: int) -> int:
    """相加。"""
    return a + b


# ---- 2. 带参数的装饰器（三层嵌套，最容易看晕的地方）----
#   要求:  repeat(n=2) 把被装饰函数执行 n 次，返回最后一次的结果
#          用法：@repeat(n=3) 然后调用 → 函数体执行 3 次
#   提示:  三层结构
#             def repeat(n):            ← 第 1 层：收装饰器参数
#                 def decorator(func):  ← 第 2 层：收被装饰函数
#                     def wrapper(...): ← 第 3 层：真正执行
#                     return wrapper
#                 return decorator
def repeat(n: int = 2):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return None     # TODO
        return wrapper
    return decorator


# ---- 3. 分批生成器（RAG 实战：一篇长文档要分批送去 embedding）----
#   要求:  batch([1,2,3,4,5], 2) → [[1,2], [3,4], [5]]
#          batch([1,2,3,4], 2)   → [[1,2], [3,4]]
#          batch([], 2)          → []
#   提示:  用 yield，不要 return list（否则大文档会撑爆内存）
#          攒满一批就 yield，然后新建一个空 list（不能 clear，会改到已产出的）
def batch(items: list[Any], size: int) -> Iterator[list[Any]]:
    return iter([])     # TODO


# ---- 4. 模拟流式输出（这就是 LLM stream=True 的机制）----
#   要求:  stream_words("你好 世界 再见") 逐个 yield 出 "你好"、"世界"、"再见"
#   提示:  for word in text.split():  yield word
def stream_words(text: str) -> Generator[str, None, None]:
    return
    yield               # 这行是占位，实现时删掉


# ---- 5. 上下文管理器 ----
#   要求:  trace_span("llm_call") 进入时打印 ">>> 开始 llm_call"
#          退出时打印 "<<< 结束 llm_call"（抛异常时也要打印）
#          yield 出来一个 dict，供 with 块内使用
#   提示:  @contextmanager + yield，清理逻辑放 try/finally 里
@contextmanager
def trace_span(name: str) -> Generator[dict[str, Any], None, None]:
    yield {}            # TODO


# ---- 6. retry 装饰器（Agent 必用：LLM 调用会抖动、限流、超时）----
#   要求:  retry(max_attempts=3) 失败时重试，全部失败则抛出最后一次的异常
#          成功则立刻返回，不重试
#   提示:  for attempt in range(1, max_attempts + 1):
#              try: return func(...)
#              except Exception as e: last_exc = e
#          循环结束后 raise last_exc
def retry(max_attempts: int = 3):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return None     # TODO
        return wrapper
    return decorator


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_04"))
