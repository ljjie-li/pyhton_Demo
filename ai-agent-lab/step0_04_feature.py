"""Step 0-4: 装饰器 / 生成器 / 上下文管理器 —— 看懂框架源码的钥匙。

═══════════════════════════════════════════════════════════════
为什么这一课是「最后一课」而不是「可以跳过」？
═══════════════════════════════════════════════════════════════
因为你打开任何 AI 框架的文档，第一眼就是这些东西：

    @tool                              ← 装饰器
    def search(query: str) -> str: ...

    @app.post("/chat")                 ← 装饰器
    async def chat(): ...

    for chunk in stream_response():    ← 生成器（流式输出全靠它）
        yield chunk

    with tracer.start_as_current_span("llm_call"):   ← 上下文管理器
        ...

Java 类比：
    装饰器 ≈ 注解（@Transactional / @Cacheable）+ AOP
    生成器 ≈ Iterator / Stream 的惰性求值
    上下文管理器 ≈ try-with-resources

运行：
    cd D:/ai-agent-lab
    ./.venv/Scripts/python.exe step0_04_feature.py
"""

from __future__ import annotations

import functools
import time
from contextlib import contextmanager, suppress
from collections.abc import Generator, Iterator
from typing import Any, Callable

# ═══════════════════════════════════════════════════════════════
# 1. 函数是一等公民（Java 8 才有的能力，Python 一直有）
# ═══════════════════════════════════════════════════════════════

print("1. 函数可以当变量传递（Java 要 Function<T,R> 接口）")


def add(a: int, b: int) -> int:
    return a + b


# 函数可以赋值给变量
op = add                        # 注意：add 后面没有括号！是「函数本身」
print(f"   op = add; op(1,2) = {op(1, 2)}")

# 函数可以当参数传入
def apply_twice(fn: Callable[[int, int], int], a: int, b: int) -> int:
    """把 fn 应用两次。

    Java 类比：
        public int applyTwice(BiFunction<Integer,Integer,Integer> fn, int a, int b) {
            return fn.apply(fn.apply(a,b), fn.apply(a,b));
        }
    """
    return fn(fn(a, b), fn(a, b))


print(f"   函数当参数: apply_twice(add, 1, 2) = {apply_twice(add, 1, 2)}")

# 函数可以当返回值
def make_multiplier(n: int) -> Callable[[int], int]:
    """返回一个「乘以 n」的函数（闭包）。"""
    def multiplier(x: int) -> int:
        return x * n            # n 来自外层作用域 → 闭包
    return multiplier


triple = make_multiplier(3)
print(f"   函数当返回值（闭包）: make_multiplier(3)(5) = {triple(5)}")


# ═══════════════════════════════════════════════════════════════
# 2. ★ 装饰器 = 接收函数、返回函数的高阶函数
#    Java 类比：注解 + AOP（@Transactional 就是在方法前后加逻辑）
# ═══════════════════════════════════════════════════════════════

print("\n2. ★ 装饰器基础")


def timer(func: Callable) -> Callable:
    """计算函数耗时的装饰器。

    ★ 这就是 LangChain 的 @tool、FastAPI 的 @app.get 的本质：
       接收一个函数，包一层，返回新函数。
    """

    @functools.wraps(func)          # ★ 必须加！保留原函数的 __name__ / __doc__
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)       # 调用原函数
        elapsed = time.perf_counter() - start
        print(f"      [timer] {func.__name__} 耗时 {elapsed*1000:.1f} ms")
        return result

    return wrapper


@timer                              # ★ 语法糖：等价于 slow_function = timer(slow_function)
def slow_function(n: int) -> int:
    """一个慢函数。"""
    total = 0
    for i in range(n):
        total += i
    return total


print(f"   调用 @timer 装饰的函数:")
result = slow_function(1_000_000)
print(f"   返回 {result}，函数名仍是 {slow_function.__name__!r}（靠 functools.wraps）")
print(f"   docstring 也保留了: {slow_function.__doc__!r}")


# ---------- 带参数的装饰器（三层嵌套）----------
print("\n   ★ 带参数的装饰器（三层嵌套，这是最容易看晕的地方）")


def retry(max_attempts: int = 3, delay: float = 0.1):
    """重试装饰器。

    ⚠️ 三层结构（AI 实战超高频，调用 LLM 失败要重试）：
        retry(max_attempts=3)          → 第一层：接收装饰器参数，返回 decorator
        decorator(func)                → 第二层：接收被装饰函数，返回 wrapper
        wrapper(*args, **kwargs)       → 第三层：实际执行逻辑

    Java 类比：自定义注解 @Retry(maxAttempts=3) + Spring AOP 切面
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    print(f"      第 {attempt} 次失败: {e}，{'重试...' if attempt < max_attempts else '放弃'}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorator


_call_count = {"n": 0}


@retry(max_attempts=3, delay=0.01)
def flaky_api_call() -> str:
    """模拟一个前两次失败、第三次成功的 API 调用。"""
    _call_count["n"] += 1
    if _call_count["n"] < 3:
        raise ConnectionError(f"连接失败（第 {_call_count['n']} 次）")
    return "成功！"


print(f"   调用 flaky_api_call() → {flaky_api_call()}")


# ═══════════════════════════════════════════════════════════════
# 3. ★★ 生成器（generator）—— 流式输出的核心
#    Java 类比：Iterator / Stream 的惰性求值
# ═══════════════════════════════════════════════════════════════

print("\n3. ★★ 生成器：yield 关键字")

# ⚠️ 先看问题：如果用 list 存所有数据，内存会爆


def get_all_numbers_list(n: int) -> list[int]:
    """一次性返回所有数字（占内存）。"""
    return [i for i in range(n)]


# 生成器版：用 yield，一次只「产出」一个值
def get_numbers_generator(n: int) -> Iterator[int]:
    """生成器版（惰性求值）。

    ★ yield 的作用：
        1. 产出值给调用方
        2. **函数暂停在这里**，保留所有局部变量
        3. 下次调用 next() 时从暂停处继续

    Java 类比：
        Java 8 的 Stream 是惰性的，但你要实现自定义惰性迭代器非常麻烦
        （得写 Iterator 接口 + hasNext/next）。
        Python 的 yield 让这件事变成「一句话」。
    """
    for i in range(n):
        yield i          # ← 不是 return！是「产出并暂停」


gen = get_numbers_generator(5)
print(f"   生成器对象: {gen!r}")
print(f"   next() 逐个取值: {next(gen)}, {next(gen)}, {next(gen)}")
print(f"   剩下的用 list() 一次取完: {list(gen)}")
print(f"   ⚠️ 已耗尽: list(gen) 再来一次 = {list(gen)}（生成器只能用一次！）")

# for 循环可以直接遍历生成器（最常用姿势）
print(f"   for 遍历生成器: {[x for x in get_numbers_generator(4)]}")

# ---------- 生成器的内存优势（实测）----------
print("\n   内存对比（100 万个数字）:")
import sys

big_list = get_all_numbers_list(1_000_000)
big_gen = get_numbers_generator(1_000_000)
list_size = sys.getsizeof(big_list)
gen_size = sys.getsizeof(big_gen)
print(f"      list  大小: {list_size:>10,} 字节")
print(f"      生成器大小: {gen_size:>10,} 字节")
print(f"      → 生成器省了 {list_size / gen_size:.0f} 倍内存！（惰性求值）")


# ---------- ★ 流式输出：LLM 的 stream=True 就是生成器 ----------
print("\n   ★★ 生成器最核心的应用：LLM 流式输出")


def fake_llm_stream(prompt: str) -> Generator[str, None, None]:
    """模拟 LLM 流式输出（真实场景是 OpenAI SDK 的 stream=True）。

    ⚠️ 真实代码长这样：
        for chunk in client.chat.completions.create(
            model="deepseek-chat", messages=..., stream=True
        ):
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    """
    response = f"好的，我来回答「{prompt}」这个问题。"
    for char in response:
        time.sleep(0.005)     # 模拟逐 token 的网络延迟
        yield char


print(f"   流式输出效果: ", end="", flush=True)
for chunk in fake_llm_stream("什么是 Agent"):
    print(chunk, end="", flush=True)     # flush=True 立刻输出，不等缓冲
print()
print(f"   ⚠️ 为什么必须用生成器？")
print(f"      非流式：等 10 秒拿到完整回答 → 用户干等 10 秒")
print(f"      流式：  每 50ms 吐一个字 → 用户立刻看到在打字（体验天差地别）")


# ---------- 生成器表达式：省内存的推导式 ----------
print("\n   生成器表达式（推导式的惰性版）:")
nums = [1, 2, 3, 4, 5]
list_comp = [x * x for x in nums]        # 列表推导式：立刻算完，占内存
gen_expr = (x * x for x in nums)         # 生成器表达式：括号，惰性
print(f"      列表推导式 [x*x for x in nums] = {list_comp}")
print(f"      生成器表达式 (x*x for x in nums) → {gen_expr}")
print(f"      用 sum() 消费生成器 = {sum(x * x for x in nums)}")
print(f"      ⚠️ 大数量级时，sum(x*x for x in range(10**7)) 不会爆内存")


# ═══════════════════════════════════════════════════════════════
# 4. ★ 上下文管理器（with 语句）
#    Java 类比：try-with-resources
# ═══════════════════════════════════════════════════════════════

print("\n4. ★ 上下文管理器（with）")

# ---------- 方式一：自己写类（__enter__ / __exit__）----------
class Timer:
    """计时上下文管理器。

    Java 类比：
        try (var t = new Timer()) { ... }   // AutoCloseable
    """

    def __init__(self, label: str):
        self.label = label
        self.elapsed = 0.0

    def __enter__(self) -> "Timer":
        """进入 with 块时调用，返回值给 as 后面的变量。"""
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """退出 with 块时调用（无论是否抛异常）。

        ⚠️ 四个参数：异常类型、异常值、traceback（没异常时都是 None）
        返回 True 表示「异常已被处理，不要往外抛」；False/None 表示继续抛。
        """
        self.elapsed = time.perf_counter() - self.start
        print(f"      [Timer] {self.label} 耗时 {self.elapsed*1000:.1f} ms")
        return False        # 不吞异常


with Timer("求和运算") as t:
    total = sum(range(500_000))
print(f"   with 块外仍能访问 t.elapsed = {t.elapsed*1000:.1f} ms")


# ---------- 方式二：@contextmanager 装饰器（更简洁，实战首选）----------
print("\n   ★ @contextmanager 装饰器写法（实战首选）")


@contextmanager
def fake_llm_session(model: str) -> Generator[dict[str, Any], None, None]:
    """模拟「建立 LLM 会话 → 使用 → 关闭」的资源管理。

    ★ 写法和生成器一模一样，只是 yield 把代码分成两半：
        yield 之前 = __enter__（准备工作）
        yield 的值 = as 后面的对象
        yield 之后 = __exit__（清理工作，即使异常也会执行）

    ⚠️ 这就是 LangChain / OpenAI SDK 里 "with client:" 的实现方式。
    """
    print(f"      [session] 建立连接，模型={model}")
    session = {"model": model, "connected": True}
    try:
        yield session                        # ← 把 session 交给 with 块
    finally:
        session["connected"] = False
        print(f"      [session] 连接已关闭（即使异常也会执行）")


with fake_llm_session("deepseek-chat") as s:
    print(f"      with 块内: session={s}")

# 异常也能正确清理
print("   异常场景:")
try:
    with fake_llm_session("deepseek-chat") as s:
        raise RuntimeError("模拟调用失败")
except RuntimeError as e:
    print(f"      异常被正确抛出: {e}")


# ---------- suppress：优雅地忽略异常 ----------
print("\n   contextlib.suppress 忽略指定异常:")
with suppress(FileNotFoundError):
    open("这是一个不存在的文件.txt")     # 不会报错
print("      ✅ 文件不存在，但被 suppress 忽略了（比 try/except/pass 简洁）")


# ═══════════════════════════════════════════════════════════════
# 5. 三个特性合体：一个「工业级工具定义」
# ═══════════════════════════════════════════════════════════════

print("\n5. ★ 三个特性合体：自己实现一个 @tool 装饰器")
print("   （这就是 LangChain 的 @tool 的核心原理）")

REGISTRY: dict[str, dict[str, Any]] = {}


def tool(func: Callable) -> Callable:
    """把一个函数注册成 LLM 可调用的工具。

    ★ 综合用到了本课所有特性：
        1. 装饰器：接收函数、返回函数
        2. 类型注解：生成参数 schema（step0_02 学的）
        3. functools.wraps：保留元信息
        4. 闭包 + 注册表：把工具收集起来给 LLM

    真实框架（LangChain）比这复杂得多（要处理 pydantic 模型、
    嵌套类型、异步函数等），但核心原理完全一致。
    """
    import inspect

    # 从函数签名生成参数 schema（简化版，真实框架用 pydantic）
    sig = inspect.signature(func)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for pname, param in sig.parameters.items():
        ptype = "string"
        if param.annotation is int:
            ptype = "integer"
        elif param.annotation is float:
            ptype = "number"
        elif param.annotation is bool:
            ptype = "boolean"
        properties[pname] = {"type": ptype, "description": f"参数 {pname}"}
        if param.default is inspect.Parameter.empty:
            required.append(pname)

    # 注册到全局表
    REGISTRY[func.__name__] = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip().splitlines()[0],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
        "_fn": func,        # 私有字段：真实执行函数
    }

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper


@tool
def search_docs(query: str, top_k: int = 3) -> str:
    """在知识库中检索文档片段。"""
    return f"[检索] {query} → {top_k} 条结果"


@tool
def get_time(timezone: str) -> str:
    """获取指定时区的时间。"""
    return f"[时间] {timezone}: 12:00"


# 自动生成的 schema（可以直接喂给 LLM）
import json as _json

print(f"   注册了 {len(REGISTRY)} 个工具: {list(REGISTRY.keys())}")
print(f"\n   自动生成的 tool schema（喂给 LLM 的 tools 参数）:")
print(_json.dumps(REGISTRY["search_docs"], ensure_ascii=False, indent=2, default=str))

print(f"""
   ⚠️ 对比一下 step1 里手写的那个 schema（18 行 JSON）——
      框架一行 @tool 就搞定了，而且永远不会和函数定义不一致。

   这就是「理解原理后再用框架」的价值：
      你知道 @tool 背后发生了什么，面试能讲清楚，
      出问题也知道去哪里 debug。
""")


# ═══════════════════════════════════════════════════════════════
# 6. Java ↔ Python 对照
# ═══════════════════════════════════════════════════════════════

print("""
6. ═══ Java ↔ Python 特性对照 ═══
┌──────────────────────────────┬────────────────────────────────────┐
│ Java                         │ Python                             │
├──────────────────────────────┼────────────────────────────────────┤
│ 注解 @Override               │ 装饰器 @decorator                   │
│ AOP 切面（@Transactional）    │ 装饰器包一层 wrapper                │
│ 自定义注解 + 反射实现 AOP     │ 装饰器 + functools.wraps            │
│ Function<T,R> / BiFunction   │ 函数直接当参数传（不用包接口）       │
│ Stream 惰性求值              │ 生成器 yield                        │
│ Iterator + hasNext/next      │ 生成器函数（一句话实现）            │
│ → Stream 流式处理            │ → LLM 流式输出（stream=True）       │
│ try-with-resources           │ with 语句 / @contextmanager        │
│ AutoCloseable.close()        │ __exit__ / finally                 │
│ Optional.orElse()            │ d.get(k, default)                  │
│ 静态内部类实现闭包            │ 闭包（天然支持）                    │
└──────────────────────────────┴────────────────────────────────────┘
""")


if __name__ == "__main__":
    print("=" * 62)
    print("Step 0-4 完成 —— 装饰器 / 生成器 / 上下文管理器")
    print("=" * 62)
    print("""
★ 本课最重要的三个对应关系（背下来）：
    @tool 装饰器        ≈ Java 注解 + AOP
    yield 生成器        = LLM 流式输出的实现机制
    with 上下文管理器    ≈ try-with-resources

★ 到这里，step0 全部结束。你现在应该能读懂 LangGraph 的示例代码了。

下一步：
  1. 做 step0_04_exercises.py 的练习
  2. 回头看 step1_agent_loop.py —— 现在你应该能逐行读懂它了
  3. 然后进 step2（LangGraph），你会发现框架代码不再神秘
""")
