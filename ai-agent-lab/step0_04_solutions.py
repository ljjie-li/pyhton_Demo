"""Step 0-4 参考答案

先自己做，卡住 5 分钟以上再看。
看完关掉这个文件，凭记忆重敲一遍。
"""

from __future__ import annotations

import functools
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from typing import Any, Callable


# ---- 1. 基础装饰器 ----
def log_calls(func: Callable) -> Callable:
    @functools.wraps(func)          # ★ 不加这个，add.__name__ 会变成 "wrapper"
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        args_str = ", ".join(
            [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        print(f"      调用 {func.__name__}({args_str})")
        result = func(*args, **kwargs)
        print(f"      返回 {result!r}")
        return result

    return wrapper


@log_calls
def add(a: int, b: int) -> int:
    """相加。"""
    return a + b


# ---- 2. 带参数的装饰器（三层嵌套）----
def repeat(n: int = 2):
    """执行 n 次的装饰器。

    三层结构：
        repeat(n)            第 1 层：收装饰器参数，返回 decorator
            decorator(func)  第 2 层：收被装饰函数，返回 wrapper
                wrapper(...) 第 3 层：真正执行

    因为 @repeat(n=3) 等价于：func = repeat(n=3)(func)
    所以第一层先被调用，拿到 decorator，再去装饰函数。
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)     # 执行 n 次
            return result                          # 返回最后一次的结果

        return wrapper

    return decorator


# ---- 3. 分批生成器 ----
def batch(items: list[Any], size: int) -> Iterator[list[Any]]:
    if size <= 0:
        raise ValueError("size 必须大于 0")

    current: list[Any] = []
    for item in items:
        current.append(item)
        if len(current) == size:
            yield current
            current = []     # ★ 必须新建 list，不能 clear()
                             #   否则 yield 出去的那个会被后面改掉

    if current:              # 最后不足一批的剩余
        yield current
    # 为什么要生成器而不是直接返回 list？
    # 一篇 10 万字的文档，所有批次都算出来会占大量内存；
    # 生成器是「产一批、送一批」，内存恒定。


# ---- 4. 模拟流式输出 ----
def stream_words(text: str) -> Generator[str, None, None]:
    for word in text.split():
        yield word
    # 这就是 LLM stream=True 的本质：
    #   非流式 → 等 10 秒拿完整回答，用户干等
    #   流式   → 逐 token 吐出，用户立刻看到在打字


# ---- 5. 上下文管理器 ----
@contextmanager
def trace_span(name: str) -> Generator[dict[str, Any], None, None]:
    print(f"      >>> 开始 {name}")
    span: dict[str, Any] = {"name": name}
    try:
        yield span              # yield 之前 = __enter__，之后 = __exit__
    finally:
        print(f"      <<< 结束 {name}")
    # ★ yield 必须放 try 里、清理放 finally，否则异常时资源泄漏


# ---- 6. retry 装饰器 ----
def retry(max_attempts: int = 3):
    """失败重试。

    为什么 Agent 必用：LLM 调用失败率不低——网络抖动、429 限流、5xx、超时。
    不重试的话，一次抖动整个 Agent 就挂了。

    生产环境还会加指数退避：第 1 次等 1s、第 2 次等 2s、第 3 次等 4s，
    免得瞬间重试把对方 API 打得更死。

    Java 类比：Spring Retry 的 @Retryable(maxAttempts = 3)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)     # 成功立刻返回
                except Exception as e:
                    last_exc = e
                    # 生产写法：time.sleep(2 ** (attempt - 1))
            # ★ 不要吞异常！上层需要知道最终失败了
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_04", mode="solution"))
