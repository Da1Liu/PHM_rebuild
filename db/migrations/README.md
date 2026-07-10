# Database migrations

按文件名前缀顺序执行，执行记录由 `tools/migrate.py` 写入 `phm.schema_migration`。应用、worker 和 agent 不得包含 `CREATE TABLE`。

当前目标数据库为独立的 `phm_rebuild`，服务版本 PostgreSQL 16.3。

```powershell
$env:PHM_DATABASE_URL = "postgresql://.../phm_rebuild"
python tools/migrate.py
```

runner 校验已执行文件的 SHA-256；已执行 migration 内容变化会拒绝继续。数据库事务由 runner 统一管理，SQL 文件不要自行 `BEGIN/COMMIT`。
