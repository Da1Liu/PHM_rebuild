# PHM Rebuild

重型机床状态采集与健康证据平台的全新实现。本仓库不继承旧项目的应用结构，只迁移经验证且仍有价值的业务事实与计算能力。

当前阶段只建设后端地基：领域模型、采集契约、数据库迁移和纯 Python 健康计算。前端将在 API 与产品任务稳定后单独设计。

## 组件

- `agents/`：现场协议与硬件采集代理。
- `apps/api/`：中心管理与查询 API（待实现）。
- `apps/worker/`：窗口聚合、训练和评分任务（待实现）。
- `packages/domain/`：跨组件共享的领域语义。
- `packages/contracts/`：采集消息等跨进程契约。
- `packages/health-core/`：无数据库、无 Web 框架依赖的健康计算。
- `db/migrations/`：数据库结构的唯一创建和演进入口。

## 本地验证

要求 Python 3.10+。当前首批测试只依赖 `numpy` 和 `pytest`。

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## 旧项目来源

旧仓库仅作为迁移来源，基线 commit 为 `3f5857f85fce893b54f573e76abb190c5a16b418`。迁移原则和清单见 `docs/migration-from-legacy.md`。

