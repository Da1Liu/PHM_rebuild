# 数据模型

## 核心对象

- Machine：被监测机床。
- Signal：具备稳定语义和来源地址的信号定义。
- CollectorInstance：现场采集进程实例及其状态。
- ScalarObservation：单个标量观测。
- FeatureWindow：一段时间窗内产生的特征集合。
- WaveformBlock：原始高频波形块。
- BaselineModel：特定上下文和 epoch 下的版本化模型。
- EvaluationResult：某个窗口的可评价状态、分数和证据。

## 时间语义

- `observed_at`：观测所代表的设备时间。
- `received_at`：agent 接收到数据的边缘时间。
- `persisted_at`：中心成功持久化时间。

三个时间不得互相替代。第一版排序和幂等主要使用 `observed_at`，延迟和链路状态使用后两个时间。

## 评价状态

- `not_evaluable`：当前输入无法形成评价。
- `insufficient_data`：输入合法，但基线样本不足。
- `normal`：在当前模型和上下文的控制范围内。
- `deviating`：超过当前模型的统计控制范围。
- `invalid_data`：输入质量、数值或 schema 无效。

