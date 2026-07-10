# 健康计算内核

`packages/health-core` 是纯计算包，不读取数据库，也不知道采集协议或 HTTP。

第一版提供可替换的 PCA T²/SPE 基线实现。稳定接口是“训练模型”和“对单个特征窗口产生评价与证据”，具体算法不是不可变的产品约束。

- 模型未拟合：`insufficient_data`，分数为空。
- 输入维度错误或包含非有限数：`invalid_data`。
- 综合分 `max(T²/UCL_T², SPE/UCL_SPE)` 不超过 1：`normal`。
- 综合分超过 1：`deviating`。

贡献用于解释统计量，不代表故障源。窗口质量、上下文、epoch 和准入由内核上层负责。

