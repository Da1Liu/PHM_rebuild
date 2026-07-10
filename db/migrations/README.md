# Database migrations

按文件名前缀顺序执行，执行记录由后续 migration runner 管理。应用、worker 和 agent 不得包含 `CREATE TABLE`。

`0001_initial.sql` 当前以 PostgreSQL 14+ 语法设计；目标版本确认后再冻结兼容范围。

