# 目标架构

```text
OPC UA / NI-DAQmx
        │
        ▼
 acquisition agents ──► ingest contract ──► PostgreSQL
                                              │
                                              ▼
                                      evaluation worker
                                              │
                                              ▼
                                         center API
                                              │
                                              ▼
                                      future web client
```

## 依赖规则

- agent 依赖采集契约，不依赖健康算法和中心查询模型。
- worker 依赖领域模型、持久化接口和 `health-core`。
- `health-core` 只依赖数值计算库。
- API 通过 repository 访问数据库，不包含训练逻辑。
- 数据库 migration 是 schema 的唯一所有者。

第一版采用模块化单仓库和独立硬件代理，不预先拆分微服务。

