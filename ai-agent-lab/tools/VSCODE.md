# VS Code 使用速查（AI Agent Lab）

> 本项目的 `.vscode/` 已经配好了，**打开文件夹就能跑，不用手敲命令**。

## 一、第一次打开：3 步

1. VS Code → 「文件」→「打开文件夹」→ 选 `D:\ai-agent-lab`
2. 左侧「扩展」搜索 **Python**（Microsoft 官方）→ 安装
3. `Ctrl+Shift+P` → 输入 `Python: Select Interpreter` → 选
   `D:\ai-agent-lab\.venv\Scripts\python.exe`

   右下角状态栏应该显示 `Python 3.13.14 ('.venv')`。

> 如果第 3 步没找到 `.venv`，重启 VS Code 再看。还是不行就在 `settings.json`
> 里确认 `python.defaultInterpreterPath` 的值。

## 二、日常怎么跑代码（三种方式，任选）

### 方式 1：F5 调试运行（★ 最推荐，能打断点）

按 `F5` 就跑**当前打开的文件**。
左侧「运行和调试」面板的下拉框里还有预设好的：

```
▶ 运行当前打开的文件
0-1 基础语法      0-1 练习（自己做）
0-2 OOP + pydantic  0-2 练习（自己做）
0-3 异步 IO       0-3 练习（自己做）
0-4 装饰器/生成器   0-4 练习（自己做）
1 ReAct 循环（手写）
```

### 方式 2：右上角三角形按钮

打开任意 `.py` 文件，右上角有个 ▶ 按钮，点它就运行。
（第一次可能要选一下「以 Python 调试器运行」）

### 方式 3：终端手敲命令

`Ctrl+~` 打开集成终端。因为 `settings.json` 已经设了
`PYTHONIOENCODING=utf-8`，**直接跑就行，不用加前缀**：

```bash
python step0_01_basics.py
```

## 三、调试（比 print 强 10 倍）

这是 Java 转过来最该用的功能，和你用 IDEA 的体验一样：

1. 在代码行号左侧**点一下**，出现红点 = 断点
2. 按 `F5` 运行
3. 程序停在断点处，左侧可以看：
   - **变量**（局部变量的值）
   - **监视**（手动添加要盯的表达式）
   - **调用堆栈**（谁调用了谁）
4. 顶部工具栏：继续(`F5`)、单步跳过(`F10`)、单步进入(`F11`)、重启、停止

**建议**：step0_01 的练习题卡住时，别急着看答案，先打断点单步走一遍，
看变量怎么变的。这个习惯能让你学得快很多。

## 四、快捷键（IDEA 用户对照）

| 操作 | VS Code | IDEA |
|---|---|---|
| 运行 | `F5` | `Shift+F10` |
| 单步跳过 | `F10` | `F8` |
| 单步进入 | `F11` | `F7` |
| 注释 | `Ctrl+/` | `Ctrl+/` |
| 格式化 | `Shift+Alt+F` | `Ctrl+Alt+L` |
| 快速修复 | `Ctrl+.` | `Alt+Enter` |
| 全局搜索 | `Ctrl+Shift+F` | `Ctrl+Shift+F` |
| 跳转定义 | `F12` | `Ctrl+B` |

## 五、编码问题排查

如果终端里出现 `UnicodeEncodeError: 'gbk' codec can't encode...`：

**原因**：终端还在用 GBK。检查两处：

1. `settings.json` 里的这段是否还在：
   ```json
   "terminal.integrated.env.windows": {
     "PYTHONIOENCODING": "utf-8",
     "PYTHONUTF8": "1"
   }
   ```
2. 改完配置要**重启终端**（点终端面板的垃圾桶图标关掉，再 `Ctrl+~` 重开）

## 六、别搞混：作业文件 vs 答案文件

每课有两个长得像的文件：

| 文件名 | 是什么 | 你该做什么 |
|---|---|---|
| `step0_0X_exercises.py` | **你的作业** | 改这里的 TODO |
| `step0_0X_solutions.py` | 小助理的答案 | 卡住 5 分钟以上才看 |

运行出来的第一屏会自报身份：

```
step0_01  练习题 · 基础语法        ← 作业（空模板 0/11）
step0_01  参考答案 · 基础语法      ← 答案（11/11 是应该的）
```

**看到 11/11 全绿先别高兴**——确认一下标题写的是「练习题」还是「参考答案」。

## 七、学 step0 的建议流程

```
1. 打开 step0_01_basics.py
2. F5 运行，一边看输出一边读注释（注释就是讲义）
3. 读完 → 打开 step0_01_exercises.py（注意是 exercises，不是 solutions）
4. 自己填 TODO，F5 运行，看自测器打了几分（空模板 0/11）
5. 红了 → 打断点单步调试，实在不行才看 step0_01_solutions.py
6. 看完答案 → 关掉答案文件，凭记忆重敲一遍
7. 全绿 → 进 step0_02_ood.py，重复 1-6
```

四课都这样走完，然后**自己从空白文件重写 step1**（ReAct 循环）。
