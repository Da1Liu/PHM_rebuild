# 采集契约

采集代理只负责把协议和硬件数据转换成标准消息。它不创建数据库、不训练模型、不解释健康状态。

## 标量观测

```json
{
  "schemaVersion": "1.0",
  "messageId": "edge-01:spindle-speed:1720000000000",
  "machineId": "machine-01",
  "signalCode": "spindle_speed",
  "observedAt": "2026-07-10T08:00:00.000Z",
  "receivedAt": "2026-07-10T08:00:00.021Z",
  "value": 150.0,
  "quality": "good",
  "context": {"collectorId": "edge-01"}
}
```

`messageId` 是跨重试幂等键。质量为 `good` 时 value 必须是有限数；缺失值必须使用 `missing`，不能写零。

## 特征窗口

特征窗口有独立 `windowId`、起止时间、来源信号集合、epoch 和上下文。完整 JSON Schema 位于 `packages/contracts/schemas/`。

传输方式暂未锁定。HTTP、批量文件或消息队列必须复用相同消息语义。

