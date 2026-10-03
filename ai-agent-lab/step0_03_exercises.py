"""Step 0-3 练习：异步 IO

用法
    1. 只在 TODO 处补代码；标着「已给素材」的函数不要动
    2. 按 F5 运行，看得分（全做完 10/10）
    3. 卡住超过 5 分钟，再看 step0_03_solutions.py

六道题
    1 把同步函数改成异步     2 并发跑 3 个任务      3 并发 + 异常容错
    4 超时控制               5 Semaphore 限流       6 并发执行工具调用

★ 最容易踩的坑：异步函数里千万别用 time.sleep()，会卡死事件循环。
"""

from __future__ import annotations

import asyncio
import json
import time


# ---- 1. 把同步函数改成异步 ----
#   要求:  async_tool 和 sync_tool 行为一样（等 0.3 秒后返回 "{name} 完成"），
#          但要用 await asyncio.sleep(0.3)，不能用 time.sleep
async def async_tool(name: str) -> str:
    return ""       # TODO


# ---- 2. 并发跑 3 个任务 ----
#   要求:  并发调用 async_tool("A") / ("B") / ("C")
#          返回结果 list，顺序必须是 A、B、C
#   提示:  asyncio.gather(...)
async def run_three() -> list[str]:
    return []       # TODO


# ---- 3. 并发 + 异常容错（Agent 实战高频）----
#   已给素材: 三个任务，中间那个必定失败
async def task_ok_1() -> str:
    await asyncio.sleep(0.05)
    return "ok1"


async def task_fail() -> str:
    await asyncio.sleep(0.05)
    raise RuntimeError("网络超时")


async def task_ok_2() -> str:
    await asyncio.sleep(0.05)
    return "ok2"


#   要求:  并发跑上面三个，用 return_exceptions=True
#          成功的结果原样保留，失败的转成 "ERROR:<异常信息>"
#          最终返回 ["ok1", "ERROR:网络超时", "ok2"]
async def run_with_failures() -> list[str]:
    return []       # TODO


# ---- 4. 超时控制 ----
#   已给素材: 耗时 1 秒的慢操作
async def slow_op() -> str:
    await asyncio.sleep(1.0)
    return "慢操作完成"


#   要求:  调用 slow_op，但超过 0.2 秒就放弃，返回 "TIMEOUT"
#   提示:  async with asyncio.timeout(0.2):  /  或 asyncio.wait_for
async def call_with_timeout() -> str:
    return ""       # TODO


# ---- 5. Semaphore 限流（Agent 批量检索实战）----
MAX_CONCURRENT = 3
NUM_TASKS = 8


#   已给素材: 单个抓取任务
async def limited_fetch(i: int) -> str:
    await asyncio.sleep(0.05)
    return f"片段{i}"


#   要求:  用 asyncio.Semaphore(3) 限制并发，8 个任务全部跑完
#          同时统计「实际出现的最大并发数」，返回 (结果列表, 峰值)
#   提示:  nonlocal current, peak；进 sem 时 current += 1，退出时 -= 1
async def run_limited() -> tuple[list[str], int]:
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    current = 0
    peak = 0

    async def worker(i: int) -> str:
        nonlocal current, peak
        return ""   # TODO

    results = await asyncio.gather(*[worker(i) for i in range(NUM_TASKS)])
    return list(results), peak


# ---- 6. 并发执行工具调用（把 step1 的 for 循环改成并发）----
#   已给素材: 假的工具执行 + 安全解析参数
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


#   要求:  并发执行所有 tool_call，返回 OpenAI 格式的 tool 消息列表：
#          [{"role": "tool", "tool_call_id": "c1", "content": "北京：晴，18°C"}, ...]
#   提示:  asyncio.gather 的结果顺序和输入一致，所以 id 对应关系天然正确
async def execute_tool_calls_async(tool_calls: list[dict]) -> list[dict]:
    return []       # TODO


# ================= 以下不用看，按 F5 会自动跑 =================
if __name__ == "__main__":
    from _selftest_base import run_suite

    raise SystemExit(run_suite(globals(), "step0_03"))
