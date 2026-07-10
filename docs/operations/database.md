# 数据库

## 当前开发实例

- PostgreSQL：16.3
- 数据库：`phm_rebuild`
- schema：`phm`
- migration：`0001_initial`

新系统不写入旧 `vibration_db`，旧库只作为后续迁移来源。

## 初始化

先以具备 `CREATE DATABASE` 权限的管理员创建空数据库，再使用新系统的应用账号执行：

```powershell
$env:PHM_DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/phm_rebuild"
python tools/migrate.py
```

重复运行会返回 `applied=none`。如果已经执行的 SQL 文件内容发生变化，runner 会拒绝继续。

当前本机首次初始化使用了现有管理员连接。正式应用账号、最小权限和口令尚未创建；服务代码不得长期使用 `postgres` 超级用户。

## 验证

```powershell
$env:PHM_TEST_DATABASE_URL = $env:PHM_DATABASE_URL
python -m pytest tests/integration/test_postgres.py
```

集成测试只创建带随机 ID 的临时数据并在结束时清理。

