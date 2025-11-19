## LangGraph + AgentScope 内容营销多智能体系统（MVP）

本项目在现有仓库上新增了可运行的最小演示（MVP），整合 LangGraph 工作流编排与 AgentScope 风格 Agents，提供统一 LLM 适配、事件总线（内存/Redis 可选）、状态与审计存储（Postgres + psycopg + migrations + event sourcing）、向量存储（内存实现，可替换 pgvector/FAISS）、监控收集（可扩展到 Prometheus）以及 docker-compose 基础编排。

### 目录结构（新增）
- `orchestrator/`：工作流编排（`ContentMarketingFlow`）
- `agents/`：五种角色 Agent（Strategy/Content/Critic/Execution/Interaction）
- `llm/`：`LLMClient` 统一调用适配（支持本地回退）
- `mq/`：`InMemoryEventBus` + `RedisEventBus`
- `storage/`：Postgres TaskStore + AuditLog（`migrations/` + `migrate.py`）与基于 boto3 的 `S3MediaStore`（支持本地回退）
- `vectorstore/`：`SimpleVectorStore` 内存向量库
- `monitoring/`：Metrics 事件收集器 + Prometheus Exporter（Grafana Dashboard 数据源）
- `run_demo.py`：端到端演示脚本
- `docker-compose.yml`：Redis/Postgres/pgvector/Prometheus/Grafana 等占位服务

### 安装依赖
```bash
pip install -r requirements-demo.txt
```

### 运行 Demo
```bash
# 默认使用内存事件总线
python run_demo.py

# 使用 Redis Pub/Sub（需先启动 Redis，参考 docker-compose）
set EVENT_BUS=redis
set REDIS_URL=redis://localhost:6379/0
python run_demo.py

# 如需自定义 Postgres 连接
set POSTGRES_DSN=postgresql://app:app@localhost:5432/appdb
```
首次运行会自动执行 `storage/migrations/`，也可手动 `python -m storage.migrate`。如需模拟真实 LLM（Qwen），设置 `QWEN_API_KEY` 并在 `llm/client.py` 接入真实 API；未设置时使用本地占位逻辑保证可重复演示。

### 媒体存储（S3 + 策略）
- 依赖 `boto3`，默认读取 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_REGION`/`AWS_DEFAULT_REGION`
- 通过 `S3_BUCKET`、`S3_PREFIX`、`S3_PUBLIC_URL_BASE` 配置 Bucket/前缀/对外访问 URL
- `S3MediaStore.build_key()` 统一生成 `mediaType/YYYY/MM/DD/task_id/filename` 结构，支持 `metadata` 扩展（用于审计、回放、风控）
- 若未提供 Bucket 或设置 `force_local=True`，自动落盘 `artifacts/` 目录作为开发回退

### 实时监控（Prometheus + Grafana）
- `monitoring/metrics.py` 会在进程内启动 Prometheus HTTP exporter，默认监听 `0.0.0.0:9000`
- 可通过环境变量调优：`PROMETHEUS_HOST`、`PROMETHEUS_PORT`（docker-compose 已映射为 9100/9101，Prometheus 配置见 `monitoring/prometheus.yml`）
- 暴露指标示例：
  - `agent_events_total{event_type="content.published"}`
  - `agent_task_status_value{task_id="..."}`（-1 error，0 pending，0.5 human，1 running，2 success）
  - `agent_task_last_event_timestamp{task_id="..."}`
- `docker-compose up` 后可通过 `http://localhost:9090` 查看 Prometheus，`http://localhost:3000` 查看 Grafana（默认空白，可接 Prometheus 数据源 `http://prometheus:9090`）

### 统一任务协议（示例）
```jsonc
{
  "task_id": "uuid",
  "type": "content.generate",
  "payload": { "topic": "AI在营销中的应用", "style": "科普风格", "platform": "twitter" },
  "meta": { "retries": 0, "status": "pending" }
}
```

### 工作流说明
`Strategy → Writer → Critic → HumanReview? → Publisher(带回滚) → Monitor`，特性：
- 每个节点默认 2 次重试
- 发布失败触发回滚
- 可选人工审核（`human_auto_approve=False` 即可模拟挂起/等待外部信号）
- 通过事件总线（内存或 Redis）广播 `plan/ draft/ refined/ publish/ analytics` 等事件，同时 `monitoring.metrics` 订阅统计、`storage.audit.AuditLog` 写入 `task_events`（事件溯源）

### 测试
```bash
pytest -q tests/test_llm_adapter.py \
        tests/test_agent_outputs_schema.py \
        tests/test_workflow_retry.py \
        tests/test_vector_memory.py
```
其中 `tests/test_workflow_retry.py` 依赖 Postgres，可通过 `POSTGRES_DSN` 或 docker-compose 中的 postgres 服务；若数据库不可达，测试会自动跳过。

### 下一步
- 扩展 TaskStore/AuditLog 的事件重放、查询 API 与告警能力
- 为媒体管道增加多版本封装（原始素材 + 压缩版 + CDN 回源）
- 为 `LLMClient` 增加 RAG 检索、pgvector/FAISS 记忆接入
- 接入真实社媒 API（ExecutionAgent）与互动引擎（InteractionAgent）


