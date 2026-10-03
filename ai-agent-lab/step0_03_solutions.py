"""Step 0-3 参考答案

先自己做，卡住 5 分钟以上再看。
看完关掉这个文件，凭记忆重敲一遍。
"""

from __future__ import annotations

import asyncio
import json


# ---- 1. 同步改异步 ----
async def async_tool(name: str) -> str:
    await asyncio.sleep(0.3)      # ★ 不能写 time.sleep！那是假异步
    return f"{name} 完成"


# ---- 2. 并发跑 3 个任务 ----
async def run_three() -> list[str]:
    results = await asyncio.gather(
        async_tool("A"),
        async_tool("B"),
        async_tool("C"),
    )
    return list(results)
    # gather 保持输入顺序，所以结果一定是 A、B、C


# ---- 3. 并发 + 异常容错 ----
async def task_ok_1() -> str:
    await asyncio.sleep(0.05)
    return "ok1"


async def task_fail() -> str:
    await asyncio.sleep(0.05)
    raise RuntimeError("网络超时")


async def task_ok_2() -> str:
    await asyncio.sleep(0.05)
    return "ok2"


async def run_with_failures() -> list[str]:
    raw = await asyncio.gather(
        task_ok_1(),
        task_fail(),
        task_ok_2(),
        return_exceptions=True,     # ★ 异常当结果返回，不中断其他任务
    )
    out: list[str] = []
    for item in raw:
        if isinstance(item, BaseException):
            out.append(f"ERROR:{item}")
        else:
            out.append(item)
    return out
    # Agent 实战：并发调 5 个工具、1 个失败 → 4 个成功结果照常用，
    # 把失败的那条错误信息回传 LLM 让它决定是否重试。这叫优雅降级。


# ---- 4. 超时控制 ----
async def slow_op() -> str:
    await asyncio.sleep(1.0)
    return "慢操作完成"


async def call_with_timeout() -> str:
    try:
        async with asyncio.timeout(0.2):      # Python 3.11+ 推荐写法
            return await slow_op()
    except TimeoutError:
        return "TIMEOUT"
    # 老写法（等价）：
    #   try:
    #       return await asyncio.wait_for(slow_op(), timeout=0.2)
    #   except asyncio.TimeoutError:
    #       return "TIMEOUT"


# ---- 5. Semaphore 限流 ----
MAX_CONCURRENT = 3
NUM_TASKS = 8


async def limited_fetch(i: int) -> str:
    await asyncio.sleep(0.05)
    return f"片段{i}"


async def run_limited() -> tuple[list[str], int]:
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    current = 0
    peak = 0

    async def worker(i: int) -> str:
        nonlocal current, peak           # ★ 改外层变量必须声明 nonlocal
        async with sem:                  # 拿不到令牌就在这排队
            current += 1
            peak = max(peak, current)
            try:
                return await limited_fetch(i)
            finally:
                current -= 1             # finally 保证异常时也减回来

    results = await asyncio.gather(*[worker(i) for i in range(NUM_TASKS)])
    return list(results), peak
    # 实战场景：要 rerank 50 个片段，但不能同时发 50 个请求（对方 429）。
    # Semaphore(5) 就是这么用的。


# ---- 6. 并发执行工具调用 ----
async def fake_execute(name: str, args: dict) -> str:
    await asyncio.sleep(0.05)
    if name == "get_weather":
        return f"{args.get('city', '?')}：晴，18°C"
    return f"未知工具 {name}"


def parse_args_safe(raw: str) -> dict:
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}


async def execute_tool_calls_async(tool_calls: list[dict]) -> list[dict]:
    async def exec_one(tc: dict) -> dict:
        name = tc["function"]["name"]
        args = parse_args_safe(tc["function"]["arguments"])
        try:
            content = await fake_execute(name, args)
        except Exception as e:
            content = f"工具执行异常：{type(e).__name__}: {e}"
        return {
            "role": "tool",
            "tool_call_id": tc["id"],     # ★ 必须回填 id
            "content": str(content),      # ★ 必须转字符串
        }

    return await asyncio.gather(*[exec_one(tc) for tc in tool_calls])
    # 对比 step1 的串行 for 循环：3 个工具从 3 倍时间变成 1 倍时间


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_03", mode="solution"))
