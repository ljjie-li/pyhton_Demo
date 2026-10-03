"""Step 1: 手写一个 ReAct Agent 循环（不依赖任何 Agent 框架）。

为什么手写？
    Agent 的本质是一个 while 循环：
        LLM 思考 → 决定调工具 → 执行工具 → 结果喂回 LLM → 再思考 ...
    框架（LangGraph/LangChain）只是把这个循环封装成图。
    手写一遍，你才能真正理解：
      - messages 数组怎么维护
      - tool_calls 怎么解析
      - 工具结果怎么回填（role=tool）
      - 循环何时终止

用法：
    cd D:/ai-agent-lab
    .venv/Scripts/python.exe step1_agent_loop.py

面试高频问题（本文件全部覆盖）：
    1. Agent 和普通 LLM 调用的区别是什么？
    2. ReAct 循环的终止条件有哪些？
    3. 为什么要限制最大轮数？
    4. 工具调用的错误怎么处理？
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

import requests
from dotenv import load_dotenv

# ---------- 配置 ----------
load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

MAX_TURNS = 10  # 最大循环轮数，防止无限循环


# ---------- 工具定义 ----------
# 工具 = 1) 给 LLM 看的 JSON Schema + 2) 真实执行的 Python 函数

def tool_get_weather(city: str) -> str:
    """查询城市天气（模拟数据，真实场景应调天气 API）。"""
    fake_data = {
        "北京": "晴，18°C，北风 3 级",
        "上海": "多云，22°C，东南风 2 级",
        "广州": "雷阵雨，28°C，南风 4 级",
        "义乌": "晴，20°C，微风",
    }
    return fake_data.get(city, f"未收录城市「{city}」的天气数据")


def tool_calculate(expression: str) -> str:
    """计算数学表达式。注意：生产环境不要直接用 eval！"""
    try:
        # 仅允许数字和基本运算符，防注入
        allowed = set("0123456789+-*/(). %")
        if not set(expression) <= allowed:
            return "错误：表达式包含不允许的字符"
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算失败：{type(e).__name__}: {e}"


def tool_read_file(path: str) -> str:
    """读取工作目录下的文本文件（限制在 lab 目录内，防越权）。"""
    base = Path(__file__).parent.resolve()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        return "错误：只能读取项目目录内的文件"
    if not target.exists():
        return f"错误：文件不存在 {path}"
    try:
        return target.read_text(encoding="utf-8")[:2000]
    except Exception as e:
        return f"读取失败：{e}"


# 工具注册表：名称 -> (执行函数, OpenAI 格式的 schema)
TOOLS: dict[str, tuple[Callable[..., str], dict[str, Any]]] = {
    "get_weather": (
        tool_get_weather,
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "查询指定城市的当前天气。当用户询问天气时使用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，例如：北京、上海",
                        }
                    },
                    "required": ["city"],
                },
            },
        },
    ),
    "calculate": (
        tool_calculate,
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "计算数学表达式，支持 + - * / ( ) 和百分比。需要精确计算时使用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "要计算的表达式，例如：1234 * 5678",
                        }
                    },
                    "required": ["expression"],
                },
            },
        },
    ),
    "read_file": (
        tool_read_file,
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取项目目录下的文本文件内容。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "相对项目根目录的文件路径",
                        }
                    },
                    "required": ["path"],
                },
            },
        },
    ),
}


# ---------- LLM 调用 ----------
def call_llm(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """调用 DeepSeek Chat API（OpenAI 兼容格式）。"""
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": messages,
            "tools": [spec for _, spec in TOOLS.values()],
            "temperature": 0,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]


# ---------- Agent 主循环 ----------
def run_agent(user_input: str, verbose: bool = True) -> str:
    """ReAct 循环：思考 → 调工具 → 观察 → 再思考，直到给出最终答案。"""
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "你是一个助手，可以调用工具来完成任务。"
                "需要精确计算或查询外部信息时，调用相应工具。"
                "拿到工具结果后，用自然语言回答用户。"
            ),
        },
        {"role": "user", "content": user_input},
    ]

    for turn in range(1, MAX_TURNS + 1):
        if verbose:
            print(f"\n{'='*60}\n[第 {turn} 轮] 调用 LLM ...")

        msg = call_llm(messages)
        messages.append(msg)

        tool_calls = msg.get("tool_calls") or []

        # ---- 终止条件：LLM 没要求调工具，就是最终答案 ----
        if not tool_calls:
            if verbose:
                print(f"[第 {turn} 轮] LLM 给出最终答案，循环结束")
            return msg.get("content") or ""

        # ---- 执行工具 -----
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            raw_args = tc["function"]["arguments"]

            if verbose:
                print(f"  → 调用工具: {fn_name}({raw_args})")

            # 解析参数（LLM 可能返回非法 JSON，必须容错）
            try:
                args = json.loads(raw_args) if raw_args else {}
            except json.JSONDecodeError:
                result = f"错误：工具参数不是合法 JSON: {raw_args}"
            else:
                if fn_name not in TOOLS:
                    result = f"错误：未知工具 {fn_name}"
                else:
                    fn, _ = TOOLS[fn_name]
                    try:
                        result = fn(**args)
                    except TypeError as e:
                        result = f"错误：参数不匹配 {e}"
                    except Exception as e:
                        result = f"工具执行异常：{type(e).__name__}: {e}"

            if verbose:
                print(f"  ← 工具返回: {str(result)[:120]}")

            # 关键：工具结果必须以 role=tool 回填，并带上 tool_call_id
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result),
                }
            )

    return f"[达到最大轮数 {MAX_TURNS}，仍未得到最终答案]"


# ---------- 演示 ----------
DEMO_QUESTIONS = [
    "北京今天天气怎么样？",                          # 单工具
    "北京和广州的天气分别怎么样？",                    # 多工具（同一轮）
    "义乌天气如何？如果气温是 20 度，那华氏度是多少？",  # 混合：工具 + 推理
    "1234 * 5678 等于多少？",                        # 纯计算
    "你好，请介绍一下你自己。",                       # 不调工具，直接回答
]


def main() -> int:
    if not API_KEY or API_KEY.startswith("sk-your"):
        print("[错误] 请在 .env 中配置 DEEPSEEK_API_KEY")
        return 1

    print("=" * 60)
    print("Step 1: 手写 ReAct Agent 循环")
    print(f"模型: {MODEL} @ {BASE_URL}")
    print(f"工具: {', '.join(TOOLS.keys())}")
    print(f"最大轮数: {MAX_TURNS}")
    print("=" * 60)

    # 命令行传参则只跑那一条
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(f"\n问题: {q}")
        answer = run_agent(q)
        print(f"\n最终回答:\n{answer}")
        return 0

    # 否则跑内置演示
    for i, q in enumerate(DEMO_QUESTIONS, 1):
        print(f"\n\n{'#'*60}")
        print(f"### 用例 {i}/{len(DEMO_QUESTIONS)}: {q}")
        print(f"{'#'*60}")
        answer = run_agent(q)
        print(f"\n>>> 最终回答: {answer}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
