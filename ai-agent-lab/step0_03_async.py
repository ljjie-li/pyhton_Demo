"""Step 0-3: 异步 IO（async/await）—— AI Agent 开发的命脉。

═══════════════════════════════════════════════════════════════
为什么这一课对你（Java 开发者）尤其重要？
═══════════════════════════════════════════════════════════════
AI 应用的本质：**90% 的时间在等网络 IO**（等 LLM 返回、等向量库、等工具 API）。

Java 的做法：线程池 + CompletableFuture + @Async（每个请求一个线程，线程很贵）
Python 的做法：**单线程事件循环 + 协程**（一个线程扛几千并发，因为不等 IO 时不占线程）

⚠️ 这是两套完全不同的心智模型。很多 Java 转 Python 的人栽在这里：
   以为 async 就是多线程 → 写出错误的代码 → 性能还不如同步。

而且：**LangGraph / LangChain 的核心方法几乎全是 async 的**。
不熟 async，你连它们的文档示例都读不懂。

运行：
    cd D:/ai-agent-lab
    ./.venv/Scripts/python.exe step0_03_async.py

⚠️ 本文件依赖 httpx，已安装。
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

# ═══════════════════════════════════════════════════════════════
# 1. 先看问题：同步代码在 IO 上浪费了多少时间
# ═══════════════════════════════════════════════════════════════


def fake_llm_call_sync(name: str, seconds: float) -> str:
    """模拟一次 LLM 调用（同步版）。现实里是 requests.post(...)，耗时 1-3 秒。"""
    time.sleep(seconds)        # 模拟网络等待 —— 注意：这会「卡住整个线程」
    return f"{name} 返回了"


def run_sync_demo() -> float:
    """同步串行：3 个任务依次执行。"""
    start = time.perf_counter()
    results = [
        fake_llm_call_sync("任务A", 0.5),
        fake_llm_call_sync("任务B", 0.5),
        fake_llm_call_sync("任务C", 0.5),
    ]
    elapsed = time.perf_counter() - start
    print(f"1. 同步串行: {results}")
    print(f"   耗时 {elapsed:.2f} 秒  ← 0.5+0.5+0.5，白白串起来等")
    return elapsed


sync_time = run_sync_demo()


# ═══════════════════════════════════════════════════════════════
# 2. async def / await：把「等待」让出去，而不是占着线程
# ═══════════════════════════════════════════════════════════════


async def fake_llm_call_async(name: str, seconds: float) -> str:
    """异步版。

    ⚠️ 两个变化：
      1. def → async def（这样函数变成「协程函数」，调用它不会执行，只返回协程对象）
      2. time.sleep() → await asyncio.sleep()（把「等待」让给事件循环）
    """
    await asyncio.sleep(seconds)     # ← 关键：await 表示「我在这里等，别的地方可以干活」
    return f"{name} 返回了"


async def run_async_demo() -> float:
    """异步并发：3 个任务同时跑。"""
    start = time.perf_counter()
    # ★ asyncio.gather 同时启动多个协程，一起等（≈ Java 的 CompletableFuture.allOf）
    results = await asyncio.gather(
        fake_llm_call_async("任务A", 0.5),
        fake_llm_call_async("任务B", 0.5),
        fake_llm_call_async("任务C", 0.5),
    )
    elapsed = time.perf_counter() - start
    print(f"2. 异步并发: {list(results)}")
    print(f"   耗时 {elapsed:.2f} 秒  ← 只花了最慢的那个的时间！")
    return elapsed


async_time = asyncio.run(run_async_demo())


# ═══════════════════════════════════════════════════════════════
# 3. ⚠️ 最常见的错误：以为调用了 async 函数就自动异步了
# ═══════════════════════════════════════════════════════════════

print(f"\n3. ⚠️ 陷阱：直接调用 async 函数不会执行！  （注意这行警告是故意的）")


async def who_am_i() -> str:
    print("        （who_am_i 真的执行了）")
    return "我是协程"


_coro = who_am_i()          # 故意创建协程但不 await，用来演示陷阱
print(f"   调用 who_am_i() 拿到的是: {type(_coro).__name__} 对象")
print(f"   ↑ 这是一个「协程对象」，函数体一行都没执行！")
print(f"   （补上面那条 RuntimeWarning：Python 在提醒你「创建了协程却忘了 await」）")
print(f"   Java 类比：这就像拿到了一个 CompletableFuture，但还没 subscribe")
_coro.close()               # 显式关闭，避免资源泄漏

# 必须 await 或交给事件循环才会执行
result = asyncio.run(who_am_i())
print(f"   用 asyncio.run() 才会执行，结果: {result!r}")


# ═══════════════════════════════════════════════════════════════
# 4. ⚠️⚠️ 致命陷阱：在 async 函数里用同步阻塞调用！
# ═══════════════════════════════════════════════════════════════


async def bad_example() -> str:
    """❌ 错误示范：在 async 函数里用 time.sleep。"""
    time.sleep(0.2)          # ❌ 这会把整个事件循环卡死 0.2 秒！所有其他协程都被堵住
    return "bad"


async def good_example() -> str:
    """✅ 正确示范。"""
    await asyncio.sleep(0.2)  # ✅ 让出控制权
    return "good"


async def demo_blocking_disaster() -> None:
    """对比：阻塞 vs 非阻塞，并发 3 个任务时差距有多大。"""
    # ❌ 阻塞版：看起来并发，实际串行
    start = time.perf_counter()
    await asyncio.gather(bad_example(), bad_example(), bad_example())
    bad_time = time.perf_counter() - start

    # ✅ 非阻塞版
    start = time.perf_counter()
    await asyncio.gather(good_example(), good_example(), good_example())
    good_time = time.perf_counter() - start

    print(f"\n4. ★ 致命陷阱对比（3 个任务各 0.2 秒）:")
    print(f"   ❌ async 里用 time.sleep()      → {bad_time:.2f} 秒（被卡成串行！）")
    print(f"   ✅ async 里用 await asyncio.sleep → {good_time:.2f} 秒（真正并发）")
    print(f"   ⚠️ 这就是「假异步」——代码看起来对，性能全丢")


asyncio.run(demo_blocking_disaster())

print("""
   ★ Agent 开发实战中最容易踩的「假异步」：
       在 async 函数里调用同步库，比如：
         · requests.post(...)          → 应该用 httpx.AsyncClient()
         · time.sleep(...)             → 应该用 await asyncio.sleep()
         · 同步数据库驱动                → 应该用 asyncpg / psycopg 异步模式
         · 同步文件 IO                  → 用 asyncio.to_thread() 包一层
""")

# to_thread：把同步函数丢到线程池里，避免卡住事件循环
# Java 类比：CompletableFuture.supplyAsync(() -> blockingCall(), executor)


async def run_in_thread() -> str:
    """把同步阻塞函数丢到线程池，不卡事件循环。"""
    result = await asyncio.to_thread(fake_llm_call_sync, "线程池任务", 0.3)
    return result


print(f"   ✅ asyncio.to_thread 包同步函数 → {asyncio.run(run_in_thread())}")


# ═══════════════════════════════════════════════════════════════
# 5. ★ 实战：真正的异步 HTTP 调用（httpx.AsyncClient）
# ═══════════════════════════════════════════════════════════════


async def real_async_http() -> None:
    """并发请求 3 个公开 API，对比同步的耗时差异。"""
    import httpx

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    print(f"\n5. ★ 实战：异步 HTTP 并发（3 个耗时 1 秒的请求）")

    # ---- 异步版：一个 AsyncClient 复用连接，gather 并发 ----
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=20) as client:
        # ⚠️ 注意 asyncio.gather 里传的是「协程对象」，不是调用结果
        responses = await asyncio.gather(
            *[client.get(u) for u in urls]
        )
    async_elapsed = time.perf_counter() - start
    codes = [r.status_code for r in responses]
    print(f"   异步并发 → 状态码 {codes}，耗时 {async_elapsed:.2f} 秒")

    # ---- 同步版：一个个来 ----
    start = time.perf_counter()
    with httpx.Client(timeout=20) as client:
        codes_sync = [client.get(u).status_code for u in urls]
    sync_elapsed = time.perf_counter() - start
    print(f"   同步串行 → 状态码 {codes_sync}，耗时 {sync_elapsed:.2f} 秒")
    print(f"   ★ 加速比: {sync_elapsed / async_elapsed:.1f}x")

    print(f"""
   ⚠️ 这才是 AI Agent 真正需要的：同时调用多个工具 / 多个检索源。
      在 step1 的手写循环里，如果一轮要调 3 个工具，
      同步写就是 3 倍时间，异步写就是 1 倍时间。
""")

    print("""
   ★ httpx 的两种使用姿势（务必区分）：
       # 同步
       with httpx.Client() as client:
           r = client.get(url)

       # 异步
       async with httpx.AsyncClient() as client:
           r = await client.get(url)
       ↑ async with 对应 Java 的 try-with-resources，但它是异步的
""")


try:
    asyncio.run(real_async_http())
except Exception as e:
    print(f"\n5. 网络请求失败（可能无外网）: {type(e).__name__}: {e}")
    print("   跳过这一步不影响理解 async 概念")


# ═══════════════════════════════════════════════════════════════
# 6. 并发控制：别一次性发 1000 个请求把对方打挂
# ═══════════════════════════════════════════════════════════════


async def controlled_concurrency() -> None:
    """用 Semaphore 限制并发数。

    Java 类比：Semaphore 几乎一模一样（信号量），但 Python 的是协程级。
    """
    sem = asyncio.Semaphore(2)      # 最多同时 2 个
    running = 0
    max_running = 0

    async def limited_task(i: int) -> str:
        nonlocal running, max_running
        async with sem:             # 获取令牌，超过 2 个就在这排队
            running += 1
            max_running = max(max_running, running)
            await asyncio.sleep(0.1)
            running -= 1
            return f"任务{i}"

    results = await asyncio.gather(*[limited_task(i) for i in range(6)])
    print(f"\n6. Semaphore 限流: 6 个任务，限制并发 2")
    print(f"   实际最大并发数 = {max_running}  （验证限流生效）")
    print(f"   全部完成: {list(results)}")


asyncio.run(controlled_concurrency())

print("""
   ★ Agent 实战场景：一次要检索 50 个文档片段做 rerank，
      但不能同时发 50 个请求（对方 API 会限流 429）。
      → Semaphore(5) 限流，这就是标准做法。
""")


# ═══════════════════════════════════════════════════════════════
# 7. 异常处理：gather 默认「一个失败全失败」
# ═══════════════════════════════════════════════════════════════


async def maybe_fail(i: int) -> str:
    if i == 2:
        raise ValueError(f"任务 {i} 失败了")
    return f"任务 {i} 成功"


async def demo_exception() -> None:
    print(f"\n7. 异常处理:")

    # ❌ 默认行为：任一失败，gather 直接抛异常
    try:
        await asyncio.gather(maybe_fail(1), maybe_fail(2), maybe_fail(3))
    except ValueError as e:
        print(f"   默认 gather 行为: {e}  ← 其他任务的结果全丢了")

    # ✅ return_exceptions=True：把异常当结果返回，不中断其他任务
    results = await asyncio.gather(
        maybe_fail(1), maybe_fail(2), maybe_fail(3),
        return_exceptions=True,     # ★ Agent 开发强烈推荐
    )
    print(f"   return_exceptions=True: {[type(r).__name__ if isinstance(r, Exception) else r for r in results]}")
    print(f"   ↑ 成功和失败都能拿到，Agent 可以只把失败的那个告诉 LLM 重试")


asyncio.run(demo_exception())

print("""
   ★ Agent 实战：并发调 5 个工具，其中 1 个失败。
      用 return_exceptions=True → 4 个成功结果照常用，
      把失败的 1 个错误信息回传给 LLM，让它决定是否重试。
      这就是「优雅降级」，面试会问。
""")


# ═══════════════════════════════════════════════════════════════
# 8. 超时控制：AI 调用必须设超时，否则会挂死
# ═══════════════════════════════════════════════════════════════


async def slow_task() -> str:
    await asyncio.sleep(5)
    return "终于回来了"


async def demo_timeout() -> None:
    print(f"\n8. 超时控制:")
    try:
        # ★ asyncio.timeout 是 Python 3.11+ 的推荐写法
        async with asyncio.timeout(1.0):
            result = await slow_task()
        print(f"   {result}")
    except TimeoutError:
        print(f"   ✅ 1 秒超时触发，任务被取消（不会一直等）")
    print(f"   ★ Agent 实战：LLM 调用设 30-60 秒超时，工具调用设 5-10 秒")


asyncio.run(demo_timeout())


# ═══════════════════════════════════════════════════════════════
# 9. ★ 改写 step1：异步版 Agent 调用（这才是生产写法）
# ═══════════════════════════════════════════════════════════════

print(f"\n9. ★ 把 step1 的同步 Agent 改成异步（代码骨架，不真调 API）")


async def call_llm_async(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """异步调用 LLM —— 生产环境的写法。

    对比 step1 的同步版：
        # 同步（step1）
        resp = requests.post(url, json=payload, timeout=60)
        return resp.json()["choices"][0]["message"]

        # 异步（生产）
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload)
            return resp.json()["choices"][0]["message"]
    """
    # 这里不真调，只演示结构
    await asyncio.sleep(0.01)
    return {"role": "assistant", "content": "[模拟] 异步 LLM 返回"}


async def run_agent_async(user_input: str, max_turns: int = 10) -> str:
    """异步版 ReAct 循环。

    与 step1 的区别只有两点：
      1. call_llm → await call_llm_async
      2. 工具执行可以 asyncio.gather 并发（step1 是 for 循环串行）

    循环结构、终止条件、消息回填 **完全一样** —— 说明你真正理解了 Agent 循环，
    换同步/异步只是语法糖。
    """
    messages = [
        {"role": "system", "content": "你是助手。"},
        {"role": "user", "content": user_input},
    ]
    for turn in range(1, max_turns + 1):
        msg = await call_llm_async(messages)
        messages.append(msg)
        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            return msg.get("content") or ""
        # ★ 关键差异：这里可以并发执行所有工具
        # async with httpx.AsyncClient() as client:
        #     results = await asyncio.gather(*[
        #         execute_tool(tc, client) for tc in tool_calls
        #     ])
        for tc in tool_calls:
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": "...",
            })
    return "[达到最大轮数]"


print(f"   异步 Agent 骨架已定义（run_agent_async）")
print(f"   与 step1 差异：{2} 处（await LLM / gather 并发工具），循环逻辑完全相同")


# ═══════════════════════════════════════════════════════════════
# 10. Java ↔ Python 异步对照
# ═══════════════════════════════════════════════════════════════

print("""
10. ═══ Java ↔ Python 异步对照 ═══
┌──────────────────────────────┬────────────────────────────────────┐
│ Java                         │ Python                             │
├──────────────────────────────┼────────────────────────────────────┤
│ Thread / 线程池（每个请求    │ 协程 + 事件循环（单线程扛高并发，   │
│ 占一个 OS 线程，1MB 栈）      │ 协程只占几 KB）                     │
│ CompletableFuture<T>         │ 协程对象（awaitable）               │
│ .thenApply() / .thenCompose() │ await                              │
│ CompletableFuture.allOf()    │ asyncio.gather()                   │
│ ExecutorService.submit()     │ asyncio.create_task()              │
│ @Async (Spring)              │ async def                          │
│ Semaphore                    │ asyncio.Semaphore                  │
│ Thread.sleep()               │ await asyncio.sleep()  ← 别用 time.sleep │
│ 无对应（靠 Future.get(t,u)）  │ asyncio.timeout(n)  / wait_for     │
│ thread.join()                │ await task                         │
└──────────────────────────────┴────────────────────────────────────┘

★ 一句核心区别：
   Java 的并发是「多线程」，靠 OS 调度；
   Python 的并发是「协程」，靠事件循环在单线程内切换。
   前者线程贵、切换开销大；后者协程便宜，但一旦有个同步阻塞调用就全卡死。
""")


if __name__ == "__main__":
    print("=" * 62)
    print("Step 0-3 完成 —— 异步 IO")
    print("=" * 62)
    print(f"""
本机实测数据回顾：
  同步串行 3×0.5s = {sync_time:.2f}s
  异步并发 3×0.5s = {async_time:.2f}s
  → 加速 {sync_time / async_time:.1f}x，任务越多差距越大

★ 本课记住三件事：
  1. async def 定义协程，await 让出控制权（Java 的 CompletableFuture 思路）
  2. ★ 千万别在 async 里用同步阻塞调用（time.sleep / requests）——「假异步」
  3. Agent 并发调工具用 asyncio.gather(..., return_exceptions=True)
     配合 Semaphore 限流 + asyncio.timeout 超时

接下来：
  - 做 step0_03_exercises.py
  - 然后进 step0_04_feature.py（装饰器 / 生成器 / 上下文管理器）
""")
