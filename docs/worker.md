# 评价 Worker

`packages/application` 定义评价用例和 repository ports；`packages/persistence` 提供 PostgreSQL 适配器。应用服务的流程为：

1. 以 `(window_id, baseline_identity)` 查询已有结果。
2. 数据质量非 `good` 时写入 `not_evaluable`。
3. 没有活动基线时写入 `insufficient_data`。
4. 特征 schema 与模型不一致时写入 `invalid_data`。
5. 输入合法时调用 `health-core`，写入统计量和贡献证据。
6. repository 通过唯一约束和 `ON CONFLICT` 保证并发幂等。

当前实现不负责选择活动基线和批量领取窗口；这些能力将在数据库连接方式确认后加入。内存 repository 用于快速单元测试，不代表生产存储方案。

