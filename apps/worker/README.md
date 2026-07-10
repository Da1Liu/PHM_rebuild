# Evaluation Worker

负责聚合、训练、评分、重放和幂等结果写入。

当前应用服务位于 `packages/application`，以 ports 描述依赖；生产数据库适配器位于 `packages/persistence`。CLI 将在数据库连接策略确定后加入。
