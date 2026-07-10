# 旧项目迁移清单

## 基线

- 来源：`D:\Proj\PHM_realtest`
- 分支：`main`
- commit：`3f5857f85fce893b54f573e76abb190c5a16b418`
- 审计时旧仓库存在未跟踪的前端与原型文件；新仓库不迁入这些内容。

## 迁入并重写

| 旧能力 | 来源 | 新位置 | 方法 |
|---|---|---|---|
| PCA、T²、SPE、贡献分解 | `PHM_claude/phm_pipeline/model.py` | `packages/health-core` | 按新接口重写并加数值测试 |
| 特征与窗口语义 | `features.py`、`segment.py` | `packages/health-core` | 只迁纯计算规则 |
| OPC UA 白名单订阅 | `WebDashboard/api/src/opcua` | `agents/opcua-agent` | 后续迁移，不带 Web/API 职责 |
| NI 采集与窗口聚合 | `WebDashboard/collector` | `agents/nidaq-agent` | 后续迁移，不带建表和 DB 控制位 |
| PostgreSQL 业务事实 | `_integration_probe/*.sql` | `db/migrations` | 重新建模，不复制旧 schema |

## 仅作验收参考

- `regression_anchor.py`、`smoke_test.py` 的数值性质。
- 旧 API 路由和响应字段。
- 现场通道配置、时间戳问题和设备协议事实。
- 旧 `phm_v2` 数据用于迁移工具与影子对比。

## 不迁入

- 所有现有前端与 UX prototype。
- `step1` 至 `step9` 实验脚本原件。
- SQLite 控制台和旧 Flask 采集控制台。
- `CNCDataGet` 的 jar、Mosquitto、网页副本和安装文件。
- WindowsForms 旧工程及内嵌依赖。
- bridge 过渡链路、运行时建表逻辑和 JSONB 数据库控制总线。
- 二进制、依赖目录、真实数据、办公文件、截图和密钥。

## 后续必须确认

- PostgreSQL 目标版本和新旧库并存方式。
- agent 到中心的传输方式及离线缓存要求。
- 旧历史数据的保留范围。
- NI 驱动、DAQmx、采样参数和现场 Windows 环境。

