# AI Agent Lab

AI Agent 开发学习项目。从手写循环到框架、RAG、评测，逐步构建。

## 环境

- Python 3.13（独立 venv 在 `.venv/`）
- LLM：DeepSeek `deepseek-chat`（线上 API，key 在 `.env`）
- 备用：本地 Ollama qwen3:8b
- 向量库：本机 PostgreSQL 18 + pgvector（阶段 3 启用）

## ⚠️ 本机注意事项

### 1. pip 必须用官方源
本机 pip 26.1.2 与清华镜像的索引格式**不兼容**（报 `No matching distribution found`），
但网络是通的（Python 直连索引页返回 200）。

```bash
./.venv/Scripts/python.exe -m pip install --index-url https://pypi.org/simple/ <package>
```

阿里云镜像可用作备选。

### 2. 中文输出必须加 PYTHONIOENCODING
Windows GBK 控制台下，不加会 `UnicodeEncodeError`。

```bash
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe step1_agent_loop.py
```

## 学习路线

| 阶段 | 文件 | 内容 | 状态 |
|---|---|---|---|
| **0** | `step0_*.py` | **Python 基础（Java 开发者版）** | ✅ 完成 → 见 `step0_README.md` |
| 1 | `step1_agent_loop.py` | **手写 ReAct 循环**（核心概念） | ✅ 已写（**待你自己重写一遍**） |
| 2 | `step2_langgraph.py` | LangGraph 版 Agent | 待做 |
| 3 | `step3_rag_pgvector.py` | RAG：切分 + 向量化 + pgvector 检索 | 待做 |
| 4 | `step4_memory.py` | 短期/长期记忆 | 待做 |
| 5 | `evals/` | 评测集 + pass@k | 待做 |

> ⚠️ **阶段 0 是后补的**。`step1_agent_loop.py` 由小助理编写，
> 大王目前是「读过」而非「写过」。正确顺序：
> 先走完 step0 → 回头**自己动手重写 step1** → 再进 step2。

## 为什么先手写而不是直接用框架

面试必问「**Agent 的循环是怎么工作的**」。只会 `graph.compile()` 答不上来。
手写一遍理解：messages 维护 → tool_calls 解析 → 工具执行 → role=tool 回填 → 循环终止条件。

## 阶段 1 已覆盖的面试点

- Agent 与普通 LLM 调用的区别：**LLM 可以主动决定调用外部工具**
- ReAct 循环终止条件：LLM 返回**不含 tool_calls** 的消息
- 为什么要限最大轮数：防止无限循环 / 死循环烧钱
- 工具错误处理：JSON 解析失败、未知工具、参数不匹配、执行异常**四层容错**
- 单轮多工具：LLM 可在一轮返回多个 tool_calls（实测：并行查北京+广州天气）
- 工具结果回填：必须带 `tool_call_id`，否则 LLM 无法对应

## 实测结果（2026-10-01）

5/5 用例通过：
- 单工具调用 ✅
- 同轮多工具并行 ✅
- 工具+推理混合（LLM 自推导出摄氏转华氏公式）✅
- 纯计算 ✅
- 不调工具直接回答 ✅
