"""Step 0-1: Python 基础语法（写给 Java 开发者）。

═══════════════════════════════════════════════════════════════
怎么用这个文件？
═══════════════════════════════════════════════════════════════
1. 先读代码，每个知识点都是「Java 写法 → Python 写法 → 差异说明」
2. 然后运行：
       cd D:/ai-agent-lab
       ./.venv/Scripts/python.exe step0_01_basics.py
3. 再看 step0_01_exercises.py 的练习题，自己动手写。

⚠️ 不要一次性背完。Java 你已经会了，Python 只是换套皮。
   本文件只讲「Java 开发者最容易踩坑 + AI 开发最高频」的部分。

包内序号：
    step0_01_basics.py       ← 你在这里（变量/类型/容器/控制流/函数）
    step0_02_ood.py          面向对象 + 类型注解 + pydantic
    step0_03_async.py        异步 IO（AI 开发命脉）
    step0_04_feature.py      装饰器 / 生成器 / 上下文管理器
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════
# 1. 变量与类型：Python 是动态类型，没有 int x = 1
# ═══════════════════════════════════════════════════════════════

# Java:  int age = 18;  String name = "张三";  double pi = 3.14;
age = 18            # int
name = "张三"        # str（Python 里字符串就叫 str，没有 String）
pi = 3.14           # float（Python 的 float 就是 Java 的 double，64 位）
is_ok = True        # bool（首字母大写！Java 是小写 true/false）
nothing = None      # null（大写 N！Java 是 null 小写）

flag = True
print(f"有长度嘛{len(str(flag))}")
notting2 = None


# ⚠️ Python 没有「声明类型」，变量本质是「贴在对象上的标签」
# 这跟 Java 的「变量盒子里装值」是根本区别，后面讲引用语义时会再遇到
x = 1
x = "hello"         # 合法！同一个变量可以换类型（Java 编译不过）

# Java 的 int / long / double 区分，Python 只有 int（无长度限制）
big = 10 ** 100     # 10 的 100 次方，Java 的 int/long 早就溢出了
print(f"1. Python int 无上限: 10**100 有 {len(str(big))} 位")

print(f"{len('wowowowowowo我是谁')}")


# ═══════════════════════════════════════════════════════════════
# 2. 字符串：f-string 是 Java 没有的大杀器
# ══════════════════════════════════════════

user_name = "李俊杰"
user_age = 30

# Java:  String s = String.format("我叫 %s，今年 %d 岁", name, age);
#       或 "我叫 " + name + "，今年 " + age + " 岁"
# Python: f-string，前缀 f，变量直接写在 {} 里
msg = f"我叫 {user_name}，今年 {user_age} 岁"
print(f"2. f-string: {msg}")

# f-string 里可以写表达式！AI 开发拼 Prompt 天天用
print(f"   明年我 {user_age + 1} 岁，名字长度 {len(user_name)} 个字")
print(f"   调试神器: {user_age=} 会直接带变量名（Python 3.8+）")

# 常用字符串方法（Java 也有，但名字不同）
text = "  Hello World  "
print(f"3. 字符串方法:")
print(f"   strip()      = Java trim()        → '{text.strip()}'")
print(f"   lower()      = Java toLowerCase() → '{text.lower()}'")
print(f"   replace()    = Java replace()     → '{text.replace('World', 'Python')}'")
print(f"   split()      = Java split()       → {text.split()}")
print(f"   startswith() = Java startsWith()  → {text.strip().startswith('Hello')}")

# 多行字符串：三引号，Java 15+ 的 text block 类似但没这么灵活
prompt = """
你是一个助手。
请回答用户的问题。
""".strip()
print(f"4. 三引号多行字符串（拼 Prompt 常用）: {prompt.splitlines()[1]}")


# ═══════════════════════════════════════════════════════════════
# 5. 四种容器：list / tuple / dict / set
#    ⚠️ 这是 Java 开发者最需要重新建立直觉的地方
# ═══════════════════════════════════════════════════════════════

# ---------- list：对应 Java 的 ArrayList ----------
# Java:  List<String> list = new ArrayList<>();  list.add("a");
# Python: 直接用 []，不用 new，不用泛型声明
fruits = ["苹果", "香蕉", "橙子"]
fruits.append("葡萄")             # = ArrayList.add()
fruits.insert(0, "西瓜")          # = list.add(0, x)，但 Java 是 add(index, element)
print(f"5. list（≈ ArrayList）: {fruits}")
print(f"   len() 取长度 = Java size()  → {len(fruits)}")
print(f"   fruits[-1] 负数索引取倒数第一个 → {fruits[-1]}   ← Java 没有！")
print(f"   切片 fruits[1:3] 取下标 1、2（不含 3）→ {fruits[1:3]}   ← Java 要 subList")
print(f"   反转 fruits[::-1] → {fruits[::-1]}")

# ⚠️ 关键差异：Python 的 list 什么都能装（Java 泛型约束类型）
# 标注 list[object] ≈ Java 的 List<Object>，告诉类型检查器"我知道里面装的是杂七杂八"
mixed: list[object] = [1, "字符串", 3.14, True, None, [1, 2]]
print(f"   list 可以混装任意类型（Java 泛型不允许）: {mixed}")

# ---------- tuple：不可变的 list，Java 没有直接对应 ----------
# 类比：Java 的 record / 或者 final 数组，但更轻量
point = (3, 5)                     # 元组，圆括号
print(f"6. tuple（不可变，Java 没有对应物）: {point}, point[0]={point[0]}")
# point[0] = 10                    # ❌ 会报错 TypeError，元组不可修改
# 用途：函数返回多个值、作为 dict 的 key（list 不能当 key）

# 解包：Java 没有，AI 开发高频
a, b = point                       # 把 (3,5) 拆给 a、b
print(f"   解包 a, b = point → a={a}, b={b}")
first, *rest = [1, 2, 3, 4]        # *rest 收集剩下的
print(f"   星号解包 first, *rest = [1,2,3,4] → first={first}, rest={rest}")

# 交换变量，Java 要借临时变量
p, q = 1, 2
p, q = q, p
print(f"   交换变量 p, q = q, p → p={p}, q={q}   ← Java 要 tmp 变量")

# ---------- dict：对应 Java 的 HashMap ----------
# Java:  Map<String, Integer> map = new HashMap<>();  map.put("a", 1);
# 标注 dict[str, str | int] ≈ Java 的 Map<String, Object>：key 是 str，value 是 str 或 int
user: dict[str, str | int] = {"name": "李俊杰", "age": 30, "city": "义乌"}
print(f"7. dict（≈ HashMap）: {user}")
print(f"   取值 user['name'] → {user['name']}")
print(f"   .get() 取不到不报错 → {user.get('email', '未填写')}   ← Java 是 getOrDefault")

user["job"] = "开发工程师"          # = map.put()
print(f"   新增/修改 user['job'] = ... → job={user['job']}")
print(f"   .keys()   = keySet()     → {list(user.keys())}")
print(f"   .values() = values()     → {list(user.values())}")
print(f"   .items()  同时拿键值      → {list(user.items())[0]}   ← Java 是 entrySet")

# ⚠️ AI 开发的核心数据结构就是这个 dict！
# OpenAI/DeepSeek 的 message 格式就是 dict：
message = {"role": "user", "content": "你好"}
print(f"   AI 的 message 就是 dict: {message}")
print(f"   拼一个 tool 结果: {{'role': 'tool', 'tool_call_id': 'x', 'content': '...'}}")

# ---------- set：对应 Java 的 HashSet ----------
# Java:  Set<String> set = new HashSet<>(Arrays.asList("a","b"));
tags = {"python", "ai", "python", "agent"}   # 自动去重
print(f"8. set（≈ HashSet）: {tags}   ← 重复的 python 被去掉")
print(f"   交集 & → {tags & {'python', 'java'}}")
print(f"   并集 | → {tags | {'java'}}")
print(f"   差集 - → {tags - {'python'}}")
print(f"   判断包含 in → {'ai' in tags}   ← Java 是 contains()")


# ═══════════════════════════════════════════════════════════════
# 9. 推导式：Java Stream API 的「一行版」，AI 开发必会
# ═══════════════════════════════════════════════════════════════

# Java 写法：
#   List<Integer> squares = nums.stream()
#       .map(n -> n * n)
#       .collect(Collectors.toList());
# Python 写法：
nums = [1, 2, 3, 4, 5]
squares = [n * n for n in nums]
print(f"9. 列表推导式 [n*n for n in nums] → {squares}")

# 带过滤（= Java 的 filter）
evens = [n for n in nums if n % 2 == 0]
print(f"   带过滤 [n for n in nums if n%2==0] → {evens}")

# 字典推导式：把 list 变成 dict
names = ["张三", "李四"]
name_len = {n: len(n) for n in names}
print(f"   字典推导式 {{n: len(n) for n in names}} → {name_len}")

# 集合推导式（输出是 set，自动去重）
mods = {n % 3 for n in nums}
print(f"   集合推导式 {{n % 3 for n in nums}} → {mods}")

# ⚠️ 面试点：推导式 vs 显式循环，什么时候用哪个？
#   简单转换/过滤 → 推导式（更快、更 Pythonic）
#   有副作用/复杂逻辑/多层嵌套 → 老老实实写 for 循环

# 实际 AI 开发例子：从 LLM 返回里抽出所有工具名
tool_calls = [
    {"function": {"name": "get_weather"}},
    {"function": {"name": "calculate"}},
]
tool_names = [tc["function"]["name"] for tc in tool_calls]
print(f"   AI 实战：从 tool_calls 提取工具名 → {tool_names}")


# ═══════════════════════════════════════════════════════════════
# 10. 控制流：if / for / while（注意：没有花括号，靠缩进！）
# ═══════════════════════════════════════════════════════════════

score = 85

# ⚠️ Python 用「4 个空格缩进」划分代码块，没有 {}！
#    这是 Java 开发者第一天最不适应的地方，也是 Python 最被诟病/最优雅的地方
if score >= 90:
    grade = "A"
elif score >= 80:          # ← 是 elif，不是 else if！
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "D"
print(f"10. if/elif/else → {score} 分是 {grade} 档")

# ⚠️ Python 判断「空」：空 list/dict/str/None 都是假值（Java 必须显式判断）
empty_list: list[int] = []
if not empty_list:
    print("    空 list 是假值，if not x 就能判断（Java 要 x.isEmpty()）")
if user.get("email"):
    print("    dict.get 返回 None 也是假值")
else:
    print("    user 没有 email → 假值分支")

# ---------- for 循环：Python 的 for 是「foreach」，没有三段式 ----------
# Java:  for (int i = 0; i < 3; i++) { ... }
# Python: for 只能遍历可迭代对象
print("11. for 循环:")
for fruit in ["苹果", "香蕉"]:            # 直接遍历元素，不用下标
    print(f"    for fruit in [...]: {fruit}")

# 需要下标时用 enumerate（Java 没这么方便）
for i, fruit in enumerate(["苹果", "香蕉"], start=1):
    print(f"    enumerate 带下标: {i}. {fruit}")

# 同时遍历两个 list 用 zip（Java 要自己处理）
cities = ["北京", "上海"]
temps = ["晴", "多云"]
for city, temp in zip(cities, temps):
    print(f"    zip 并行遍历: {city} = {temp}")

# range：生成数字序列（Java 的 for i 循环等价物）
for i in range(3):                        # 0, 1, 2
    print(f"    range(3) 生成: {i}", end="  ")
print()
for i in range(1, 4):                     # 1, 2, 3
    print(f"    range(1,4) 生成: {i}", end="  ")
print()

# 遍历 dict
for key, value in user.items():
    pass  # 这里不打印，避免刷屏
print(f"    遍历 dict: for k, v in user.items() → 拿到的第一对是 {list(user.items())[0]}")


# ═══════════════════════════════════════════════════════════════
# 12. 函数：默认参数 / 关键字参数 / 可变参数
# ═══════════════════════════════════════════════════════════════

# Java:  public String greet(String name, String prefix) { return prefix + name; }
# Python: def 定义，无返回类型声明，无 public/private
def greet(name: str, prefix: str = "你好") -> str:
    """打招呼。默认参数 prefix 是 Python 特色（Java 只能靠重载）。

    Args:
        name: 名字
        prefix: 前缀，默认「你好」

    Returns:
        拼接后的问候语
    """
    return f"{prefix}，{name}"


# 三种调用方式
print(f"12. 函数调用:")
print(f"    位置参数 greet('张三')              → {greet('张三')}")
print(f"    关键字参数 greet(name='张三')       → {greet(name='张三')}")
print(f"    覆盖默认值 greet('张三', '早上好')   → {greet('张三', '早上好')}")
print(f"    关键字乱序 greet(prefix='嗨', name='张三') → {greet(prefix='嗨', name='张三')}")

# ⚠️ Java 没有「关键字参数」，这是 Python 大幅度提升可读性的地方
#    调用 `send_email(to="a@b.com", subject="hi", body="...")` 一眼看懂


# ---------- *args / **kwargs：Java 是 `String... args` 和 Map ----------
def log_all(*args: object, **kwargs: object) -> None:
    """*args 收集位置参数成 tuple，**kwargs 收集关键字参数成 dict。

    Java 类比：Object... args 只能收位置参数，没有 kwargs 对应物。
    """
    print(f"    *args  → {args}          (类型 {type(args).__name__})")
    print(f"    **kwargs → {kwargs}      (类型 {type(kwargs).__name__})")


print(f"13. 可变参数:")
log_all(1, 2, 3, name="张三", age=30)

# ⚠️ **kwargs 在 AI 开发里极度重要：
#    框架几乎都用它来传递「透传参数」，比如
#        def call_llm(messages, **options): ...
#        call_llm(msgs, temperature=0, max_tokens=100)


# ---------- 多返回值：Python 直接返回 tuple，Java 要造类 ----------
def divide(a: float, b: float) -> tuple[float | None, str]:
    """返回 (结果, 错误信息)。Java 要么抛异常，要么造一个 Result 类。"""
    if b == 0:
        return None, "除数不能为 0"
    return a / b, ""


result, error = divide(10, 2)
print(f"14. 多返回值: divide(10,2) → result={result}, error='{error}'")
result, error = divide(10, 0)
print(f"    divide(10,0) → result={result}, error='{error}'")


# ═══════════════════════════════════════════════════════════════
# 15. 常见陷阱：Java 开发者最容易踩的 3 个坑
# ═══════════════════════════════════════════════════════════════

print("15. 陷阱演示:")

# ---- 陷阱 1：可变默认参数（Python 最著名的坑）----
def bad_append(item: object, target: list[object] = []) -> list[object]:   # ❌ 默认值在函数定义时求值一次，全程复用同一个 list！
    target.append(item)
    return target


print(f"    陷阱1 bad_append('a') → {bad_append('a')}")
print(f"         bad_append('b') → {bad_append('b')}   ← 啊，'a' 还在！")
print(f"         （Java 不会有这个问题，因为 Java 的默认值靠重载实现）")


def good_append(item: object, target: list[object] | None = None) -> list[object]:   # ✅ 正确写法
    if target is None:
        target = []
    target.append(item)
    return target


print(f"    正确写法 → {good_append('a')} / {good_append('b')}")

# ---- 陷阱 2：is 和 == 不是一回事 ----
# Java: == 比较引用（对象），equals() 比较值
# Python: == 比较值，is 比较「是不是同一个对象」
list1 = [1, 2, 3]
list2 = [1, 2, 3]
print(f"    陷阱2 list1 == list2 → {list1 == list2}   （值相同）")
print(f"         list1 is list2 → {list1 is list2}   （不是同一个对象）")
print(f"         注意：只有和 None / True / False 比较才用 is：x is None（不要 x == None）")

# ---- 陷阱 3：整除与浮点 ----
print(f"    陷阱3 7 / 2 = {7 / 2}         ← Python 3 的 / 永远是浮点除法")
print(f"         7 // 2 = {7 // 2}        ← // 才是整除（Java 的 int/int）")
print(f"         7 % 2 = {7 % 2}          ← 取余，和 Java 一样")
print(f"         0.1 + 0.2 = {0.1 + 0.2}  ← 浮点精度问题，Java 也一样")


# ═══════════════════════════════════════════════════════════════
# 16. 与 Java 的语法对照速查表
# ═══════════════════════════════════════════════════════════════

print("""
16. ═══ Java → Python 速查表 ═══
┌────────────────────────┬──────────────────────────────────┐
│ Java                   │ Python                           │
├────────────────────────┼──────────────────────────────────┤
│ String s = "a";        │ s = "a"        （无类型声明）     │
│ System.out.println(x)  │ print(x)                         │
│ list.size()            │ len(list)      （函数，非方法）   │
│ map.put(k, v)          │ d[k] = v                         │
│ true / false / null    │ True / False / None   （大写！）  │
│ else if                │ elif                             │
│ for (int i=0;...)      │ for x in list / range(n)         │
│ String[] arr = {...}   │ arr = [...]    （是 list）        │
│ i++ / i--              │ i += 1 / i -= 1  （没有 ++）      │
│ int x = 5;             │ x: int = 5     （注解可省略）     │
│ && / || / !            │ and / or / not                   │
│ 方法重载               │ 默认参数 + *args/**kwargs        │
│ 接口 default 方法      │ 鸭子类型（协议）                  │
│ package com.foo;       │ 目录结构 + __init__.py           │
│ try/catch/finally      │ try/except/finally               │
│ throw new XxxError()   │ raise XxxError()                 │
└────────────────────────┴──────────────────────────────────┘
""")


if __name__ == "__main__":
    print("=" * 62)
    print("Step 0-1 完成 —— 基础语法。下一课：step0_02_ood.py")
    print("=" * 62)
    print("""
接下来请做两件事：
  1. 运行 step0_01_exercises.py，自己写代码（关键！光看不会）
  2. 打开 step0_02_ood.py，学面向对象 + 类型注解 + pydantic

记住：不要背。你写 Java 时的所有直觉，换套语法就是 Python。
""")
