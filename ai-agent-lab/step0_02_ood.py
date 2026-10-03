"""Step 0-2: 面向对象 + 类型注解 + pydantic（写给 Java 开发者）。

═══════════════════════════════════════════════════════════════
为什么这一课最重要？
═══════════════════════════════════════════════════════════════
因为 AI Agent 开发里，**工具的参数定义、LLM 的结构化输出**全靠这一课。
你不会 pydantic，看 LangGraph / LangChain 的源码就是天书。

运行：
    cd D:/ai-agent-lab
    ./.venv/Scripts/python.exe step0_02_ood.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

# ═══════════════════════════════════════════════════════════════
# 1. 类：Python 的 class 比 Java 简洁很多
# ═══════════════════════════════════════════════════════════════


class Dog:
    """演示传统 Python 类写法（了解即可，实战推荐 dataclass / pydantic）。

    Java 对照：
        public class Dog {
            private String name;
            private int age;
            public Dog(String name, int age) { this.name = name; this.age = age; }
            public void bark() { System.out.println(name + " 汪汪叫"); }
        }
    """

    # 类属性（所有实例共享）—— Java 的 static 字段
    species = "犬科"

    def __init__(self, name: str, age: int):
        """构造函数。

        ⚠️ 注意：
          - 是 __init__（双下划线包裹），不是构造函数重载
          - 第一个参数固定是 self（= Java 的 this，但必须显式写出来）
          - 属性直接 `self.name = name` 就创建了，不需要提前声明字段！
            （Java 必须先在类里声明 private String name;）
        """
        self.name = name      # ① 直接赋值就创建了实例属性
        self.age = age

    def bark(self) -> str:
        """实例方法。第一个参数必须是 self。"""
        return f"{self.name} 汪汪叫"

    def __repr__(self) -> str:
        """类似 Java 的 toString()，调试时显示用。"""
        return f"Dog(name={self.name!r}, age={self.age})"

    def __eq__(self, other: object) -> bool:
        """类似 Java 的 equals()。"""
        if not isinstance(other, Dog):
            return NotImplemented
        return self.name == other.name and self.age == other.age


dog = Dog("旺财", 3)
print(f"1. 传统类: {dog}, 调用方法: {dog.bark()}, 类属性: {Dog.species}")
print(f"   ⚠️ self 必须显式写：def bark(self)  /  Java 里 this 是隐式的")


# ═══════════════════════════════════════════════════════════════
# 2. dataclass：不用手写 __init__（≈ Java 16 的 record，但可变）
# ═══════════════════════════════════════════════════════════════


@dataclass
class ToolResult:
    """工具执行结果。

    Java 对照（Lombok）：
        @Data
        public class ToolResult {
            private String toolName;
            private boolean success;
            private String output;
        }

    Python 用 @dataclass 装饰器，自动生成 __init__ / __repr__ / __eq__。
    注意：@dataclass 只是「数据容器」，不做类型校验，传错类型不会报错！
    """

    tool_name: str
    success: bool
    output: str
    duration_ms: float = 0.0                        # 有默认值
    metadata: dict[str, Any] = field(default_factory=dict)   # ⚠️ 可变类型必须用 field()


r = ToolResult(tool_name="get_weather", success=True, output="晴，18°C")
print(f"2. dataclass: {r}")
print(f"   ⚠️ 可变默认值必须写 field(default_factory=dict)，不能写 = {{}}")
print(f"      （还记得 step0_01 讲的「可变默认参数陷阱」吗？同一个坑）")


# ---------- Enum：和 Java 的 enum 几乎一样 ----------
class ToolStatus(Enum):
    """工具执行状态。"""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


print(f"3. Enum: ToolStatus.SUCCESS.value = {ToolStatus.SUCCESS.value!r}")
print(f"   ToolStatus('failed') 反向查找 = {ToolStatus('failed')}")


# ═══════════════════════════════════════════════════════════════
# 4. 类型注解：Python 的类型是「提示」，不是「强制」
# ═══════════════════════════════════════════════════════════════


def process(name: str, count: int, tags: list[str]) -> dict[str, int]:
    """类型注解写在参数后面和 -> 后面。

    ⚠️ 关键认知：Python 解释器**完全不检查**这些注解！
        process(123, "abc", 456) 照样能跑（然后崩在运行时）
        Java 是编译期就报错。

    那为什么还要写？
        1. IDE 能提示、能跳转（你的 Java 直觉还能用）
        2. mypy / pyright 这类静态检查工具能查
        3. **pydantic / LLM 工具定义会真的读这些注解** ← AI 开发关键
    """
    return {t: len(t) for t in tags}


print(f"4. 类型注解是提示不是强制，运行时不校验")
print(f"   正确调用: {process('x', 1, ['a', 'bb'])}")


# ---------- 常用类型写法（对照 Java 泛型）----------
# Java                                    Python
# String                                  str
# int / long                              int
# double / float                          float
# boolean                                 bool
# List<String>                            list[str]
# Map<String, Integer>                    dict[str, int]
# Set<String>                             set[str]
# Optional<String>                        str | None   （Python 3.10+）
# Object                                  Any
# List<? extends Number>                  Sequence[int]（协变，进阶）

# ⚠️ Java 用 <? extends T> / <? super T>，Python 用 Protocol / TypeVar，概念不同


# ═══════════════════════════════════════════════════════════════
# 5. pydantic：带校验的类型（Java 的 @Valid + 运行时校验）
#    ★★★ 这一节是 AI Agent 开发的核心 ★★★
# ═══════════════════════════════════════════════════════════════


class WeatherArgs(BaseModel):
    """天气查询工具的参数。

    Java 对照（Spring + Validation）：
        public class WeatherArgs {
            @NotBlank(message = "city 不能为空")
            private String city;

            @Min(1) @Max(7) @Nullable
            private Integer days;
        }
        然后在 Controller 方法上加 @Valid 才会校验。

    pydantic 的区别：**实例化那一刻就校验**，不需要额外注解触发。
    """

    city: str = Field(description="城市名称，例如：北京")
    days: int = Field(default=1, ge=1, le=7, description="预报天数，1-7")

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, v: str) -> str:
        """自定义校验：类似 Java 的 @NotBlank。"""
        if not v.strip():
            raise ValueError("city 不能为空")
        return v.strip()


# 正常情况
args = WeatherArgs(city="北京", days=3)
print(f"5. pydantic 校验通过: {args}")
print(f"   访问属性: args.city={args.city!r}, args.days={args.days}")

# 类型自动转换（Java 不会自动做！）
args2 = WeatherArgs(city="上海", days="5")   # 传了字符串 "5"
print(f"   自动类型转换 days='5' → {args2.days!r} (类型 {type(args2.days).__name__})")

# 校验失败会抛异常
print(f"\n6. pydantic 校验失败会抛 ValidationError:")
try:
    WeatherArgs(city="北京", days=99)        # days 超过 7
except ValidationError as e:
    print(f"   捕获到 ValidationError:")
    # e.errors() 返回结构化错误列表 —— 可以喂给 LLM 让它自己改！
    for err in e.errors():
        print(f"     - 字段 {err['loc']}: {err['msg']}")
    print(f"   ⚠️ 这个错误信息可以直接回传给 LLM，让它修正参数（Agent 实战常用）")

try:
    WeatherArgs(city="", days=1)
except ValidationError as e:
    print(f"   空字符串也被 @field_validator 拦下: {e.errors()[0]['msg']}")


# ═══════════════════════════════════════════════════════════════
# 7. ★ pydantic → JSON Schema：LLM 工具定义的来源 ★
# ═══════════════════════════════════════════════════════════════


class CalcArgs(BaseModel):
    """数学计算工具的参数。"""

    expression: str = Field(description="要计算的数学表达式，例如：1234 * 5678")
    precision: int = Field(default=2, ge=0, le=10, description="小数位数")


print("\n7. ★ pydantic 自动生成 JSON Schema（LLM 工具定义的来源）★")
schema = CalcArgs.model_json_schema()
print(json.dumps(schema, ensure_ascii=False, indent=2))

print(f"""
   ⚠️ 这就是 step1 里我手写的 tools schema！当时是这样写的：
       {{
         "type": "function",
         "function": {{
           "name": "calculate",
           "description": "计算数学表达式...",
           "parameters": {{ "type": "object", "properties": {{...}} }}
         }}
       }}

   用 pydantic 可以自动生成 parameters 那一坨：
       "type": "function",
       "function": {{
           "name": "calculate",
           "description": CalcArgs.__doc__,
           "parameters": CalcArgs.model_json_schema(),   ← 一行搞定
       }}

   实际框架（LangChain / LangGraph）就是这么从函数签名 + docstring +
   类型注解自动生成工具 schema 的。所以：
       ★ 类型注解 + docstring + pydantic = AI 工具定义的三大件 ★
""")


# ═══════════════════════════════════════════════════════════════
# 8. ★ 解析 LLM 返回的 JSON：pydantic 的另一大用途 ★
# ═══════════════════════════════════════════════════════════════


class AgentDecision(BaseModel):
    """LLM 的决策输出（让 LLM 返回结构化 JSON 而不是自由文本）。

    面试点：为什么要用 pydantic 解析 LLM 输出？
        LLM 返回的是字符串，可能：
          - 字段缺失
          - 类型不对（该给 int 给了字符串）
          - 格式错误（JSON 不合法）
        pydantic 一把梭：校验 + 类型转换 + 明确报错
    """

    thought: str = Field(description="思考过程")
    action: Literal["call_tool", "final_answer"] = Field(description="下一步动作")
    tool_name: str | None = Field(default=None, description="要调用的工具名")


# 模拟 LLM 返回的 JSON 字符串（真实场景是 response.choices[0].message.content）
llm_output = '{"thought": "需要查天气", "action": "call_tool", "tool_name": "get_weather"}'

print(f"8. ★ 解析 LLM 返回的 JSON ★")
print(f"   LLM 原始输出: {llm_output}")
decision = AgentDecision.model_validate_json(llm_output)   # 一行完成解析+校验
print(f"   解析后: {decision}")
print(f"   类型安全: decision.action = {decision.action!r}")

# LLM 也可能返回非法内容
bad_outputs = [
    '{"thought": "x", "action": "unknown_action"}',    # action 不在枚举里
    '{"action": "call_tool"}',                          # 缺 thought
    'not a json at all',                                # 根本不是 JSON
]
print(f"\n   LLM 可能返回各种错误，pydantic 都能拦住：")
for i, bad in enumerate(bad_outputs, 1):
    try:
        AgentDecision.model_validate_json(bad)
        print(f"     {i}. 意外通过了！")
    except ValidationError as e:
        print(f"     {i}. 拦下: {bad[:40]}... → {e.errors()[0]['type']}")


# ═══════════════════════════════════════════════════════════════
# 9. ★ 从「函数签名」自动生成工具定义（框架的核心魔法）★
# ═══════════════════════════════════════════════════════════════


def search_knowledge(
    query: Annotated[str, "要检索的问题"],
    top_k: Annotated[int, "返回条数"] = 3,
) -> str:
    """在知识库中检索相关内容。

    这是 docstring —— 框架会读它当作工具的 description 字段！
    所以写 docstring 不是「加分项」，是「必需品」。
    """
    return f"[模拟] 检索 '{query}' 返回 {top_k} 条结果"


print("\n9. ★ 工具定义的工业化做法（LangChain 的 @tool 就是这么干的）★")
print(f"   函数名     → schema 的 name:        {search_knowledge.__name__}")
print(f"   docstring  → schema 的 description: {search_knowledge.__doc__.splitlines()[0]}")
print(f"   Annotated  → 每个参数的类型和描述:")
import inspect

sig = inspect.signature(search_knowledge)
for pname, param in sig.parameters.items():
    print(f"       {pname}: {param.annotation}  默认值={param.default}")

print(f"""
   ⚠️ 结论：在 AI Agent 开发里写 Python 函数，必须做到三件事：
      1. 加类型注解（str, int, list[str] ...）
      2. 写清楚 docstring（LLM 靠它判断什么时候用这个工具）
      3. 参数含义用 Annotated 或 pydantic Field 描述
   否则 LLM 根本不知道你的工具是干嘛的，就永远调不对。
""")


# ═══════════════════════════════════════════════════════════════
# 10. 继承与多态：和 Java 基本相同
# ═══════════════════════════════════════════════════════════════


class BaseTool:
    """工具基类（≈ Java 的 abstract class / interface）。"""

    name: str = "base"

    def run(self, **kwargs) -> str:
        """执行工具。子类必须覆盖。"""
        raise NotImplementedError("子类必须实现 run()")   # ≈ Java 的 abstract


class WeatherTool(BaseTool):
    """天气工具。"""

    name = "weather"

    def run(self, **kwargs) -> str:
        city = kwargs.get("city", "未知")
        return f"{city}：晴，18°C"


class CalcTool(BaseTool):
    """计算工具。"""

    name = "calc"

    def run(self, **kwargs) -> str:
        return "42"


print(f"10. 继承与多态:")
for tool in [WeatherTool(), CalcTool()]:     # ← 注意没有 new！
    print(f"    {tool.name}: {tool.run(city='北京')}")

print(f"""
    ⚠️ 两个重要差异：
      1. 实例化不用 new：WeatherTool()  ← Java 是 new WeatherTool()
      2. **Python 没有 interface 关键字**，靠「鸭子类型」：
         只要对象有 run() 方法就能当工具用，不需要 implements 任何东西。
         这叫 Duck Typing —— "看起来像鸭子，叫起来像鸭子，就是鸭子"
""")


# ═══════════════════════════════════════════════════════════════
# 11. Java ↔ Python OOP 对照速查
# ═══════════════════════════════════════════════════════════════

print("""
11. ═══ Java ↔ Python 面向对象速查 ═══
┌──────────────────────────┬────────────────────────────────────┐
│ Java                     │ Python                             │
├──────────────────────────┼────────────────────────────────────┤
│ this                     │ self（必须显式写在参数第一位）      │
│ new Foo()                │ Foo()                              │
│ private String name;     │ 无声明，self.name = x 直接就创建    │
│ public / private         │ 没有！靠 _x / __x 命名约定          │
│ toString()               │ __repr__ / __str__                 │
│ equals() / hashCode()    │ __eq__ / __hash__                  │
│ @Data (Lombok)           │ @dataclass                         │
│ record Foo(...)          │ @dataclass(frozen=True)            │
│ interface                │ 鸭子类型 / abc.ABC / Protocol      │
│ abstract class           │ 类 + raise NotImplementedError     │
│ implements               │ 直接继承，不用关键字                │
│ @Override                │ 直接重写，不用注解                  │
│ instanceof               │ isinstance(x, Foo)                 │
│ enum                     │ class Foo(Enum)                    │
│ @Valid + @NotNull        │ pydantic BaseModel + Field         │
│ 编译期类型检查            │ 运行时才检查（pydantic 补这个洞）   │
└──────────────────────────┴────────────────────────────────────┘
""")


if __name__ == "__main__":
    print("=" * 62)
    print("Step 0-2 完成 —— 面向对象 + 类型注解 + pydantic")
    print("=" * 62)
    print("""
★ 本课最重要的一句话：
   在 AI Agent 开发里，「类型注解 + docstring + pydantic」
   就是工具定义和结构化输出的全部基础设施。
   看不懂 pydantic，就看不懂 LangGraph / LangChain 的源码。

接下来：
  - 做 step0_02_exercises.py 的练习
  - 然后进 step0_03_async.py（异步 IO，AI 开发的命脉）
""")
