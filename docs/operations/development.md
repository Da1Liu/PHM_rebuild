# 本地开发

## Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

当前开发机检测到 Python 3.10 和 Node 20，但没有 .NET SDK。NI agent 的构建环境将在现场版本确认后单独定义。

