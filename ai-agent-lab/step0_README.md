# Step 0：Python 基础（写给 Java 开发者）

> 目标：用最少时间把 Java 的直觉翻译成 Python，**只教 AI Agent 开发高频用到的部分**。
> 不教通用语法——Java 会的人自己能推，这里只讲「翻译差异」和「AI 生态特有的东西」。

## 文件清单

| 课 | 讲义（读 + 跑） | 作业（自己写） | 答案 |
|---|---|---|---|
| 01 基础语法 | `step0_01_basics.py` | `step0_01_exercises.py`（11 项） | `step0_01_solutions.py` |
| 02 面向对象 + pydantic | `step0_02_ood.py` | `step0_02_exercises.py`（15 项） | `step0_02_solutions.py` |
| 03 异步 IO | `step0_03_async.py` | `step0_03_exercises.py`（10 项） | `step0_03_solutions.py` |
| 04 装饰器 / 生成器 | `step0_04_feature.py` | `step0_04_exercises.py`（10 项） | `step0_04_solutions.py` |

外加一个 `_selftest_base.py`——4 课共用的自测运行器，**你不用打开它**。

## 作业文件 vs 答案文件，怎么分

两个文件名字像，运行出来的第一屏会告诉你身份：

```
step0_01  练习题 · 基础语法              ← 作业
这是你的作业文件。空模板得分低是正常的，全做对就满分。

step0_01  参考答案 · 基础语法            ← 我的答案
这是小助理的答案，全绿是应该的。你的作业在同课 exercises.py。
```

- 文件名以 `_exercises` 结尾 → **你的作业**
- 以 `_solutions` 结尾 → **我的答案，别把自己骗了**

## 怎么练

```
1. 打开 step0_01_basics.py，按 F5
   一边看输出一边读注释（注释就是讲义）

2. 读完了，打开 step0_01_exercises.py
   只改 TODO 那几行，别的不要动

3. 按 F5 → 看分数
   空模板是 0/11，全做对是 11/11

4. 红了：在出问题的行左边点一下打断点 → F5 → F10 单步走
   盯着左侧「变量」面板看数据怎么变的（比 print 强 10 倍）

5. 卡住超过 5 分钟，才允许打开 step0_01_solutions.py

6. 看完答案，关掉答案文件，凭记忆重敲一遍 ← 这步最重要

7. 全绿 → 进 step0_02_ood.py，重复 1-6
```

## 建议节奏

- 每课 **1-2 小时**：读 30 分钟 + 练习 60 分钟
- **不要跳练习**。看懂 ≠ 会写，尤其 Java 转过来的，语法会「看着眼熟但写不出」
- 4 课走完 **1-2 天**，性价比极高

## 学完你应该掌握什么

### 语法层
- f-string、`elif`、`None/True/False` 大写、没有 `++`
- `list` / `tuple` / `dict` / `set` 四种容器及推导式
- `len()` 是函数不是方法、负数索引、切片、解包
- 默认参数、关键字参数、`*args` / `**kwargs`、多返回值
- 三个必踩的坑：可变默认参数、`is` vs `==`、`/` 是浮点除法

### 工程层（★ 最重要）
- `@dataclass` / `class` / `Enum` / 鸭子类型
- 类型注解（运行时**不校验**，但 pydantic 会）
- **pydantic：`BaseModel` + `Field` + `field_validator`**
- **`.model_json_schema()` → LLM 工具定义**
- **`.model_validate_json()` → 解析 LLM 输出**
- `async def` / `await` / `asyncio.gather` / `Semaphore` / `asyncio.timeout`
- **识别「假异步」**：async 里用 `time.sleep` / `requests` 会卡死事件循环
- 装饰器（含三层嵌套的带参装饰器）、`functools.wraps`
- 生成器 `yield`（LLM 流式输出的机制）
- 上下文管理器（`with` / `@contextmanager`）

## 四课的「一句话核心」

| 课 | 一句话 |
|---|---|
| 01 | Java 的直觉全都能用，只是换套语法；三个陷阱记牢 |
| 02 | **pydantic 就是 AI 工具定义和结构化输出的基础设施** |
| 03 | **async 不是多线程**；async 里用同步阻塞调用 = 假异步 |
| 04 | `@tool` ≈ AOP，`yield` = 流式输出，`with` ≈ try-with-resources |

## 学完之后：回头重写 step1

重读 `step1_agent_loop.py`（手写 ReAct 循环），你会发现：
- `TOOLS` 那个字典 → 应该用 step0_02 的 pydantic 自动生成
- `requests.post` → 应该改成 `httpx.AsyncClient`（step0_03）
- `for tc in tool_calls` 串行 → 应该改成 `asyncio.gather`（step0_03）

**然后自己从空白文件重写一遍 step1——不看答案。这才是真正的入门。**
写不出来说明 step0 还有洞，回去补。

再往后就是 `step2_langgraph.py`，那时你会发现框架代码不再神秘：
`@tool` 是装饰器、`graph.add_node` 是往 dict 里塞函数、state 就是 pydantic 模型。
