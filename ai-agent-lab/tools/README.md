# tools/ 目录说明

存放辅助脚本（诊断、验证、批处理等）。

## 常用命令速查

### 安装依赖（注意：本机 pip 26 与清华镜像不兼容，必须用官方源）
```bash
cd /d/ai-agent-lab
./.venv/Scripts/python.exe -m pip install --index-url https://pypi.org/simple/ <package>
```

### 运行 Agent
```bash
# 交互式（跑内置 5 个演示用例）
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe step1_agent_loop.py

# 单条提问
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe step1_agent_loop.py "北京天气怎么样"
```

> Windows 下必须加 `PYTHONIOENCODING=utf-8`，否则中文输出会 GBK 编码报错。
