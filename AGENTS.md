# AGENTS.md

## 项目定位

这是 PHM 平台的全新实现。旧仓库是事实和测试数据来源，不是目标架构模板。

## 工作规则

- 全程中文沟通，代码标识符和协议字段使用英文。
- 修改前先确认当前模块的公开契约和测试。
- 硬件协议只存在于 `agents/`。
- `packages/health-core` 不得依赖数据库、HTTP 框架或采集协议。
- 数据库结构只能由 `db/migrations/` 修改；应用不得运行时建表。
- `unknown`、`not_evaluable`、`insufficient_data` 不得表示为健康或零值。
- 不迁入旧前端、实验脚本、二进制、真实数据和真实配置。
- 新增跨进程字段时，同步更新 schema、示例和契约测试。

## 验证

```powershell
python -m pytest
```

