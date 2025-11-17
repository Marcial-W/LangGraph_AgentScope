## LangGraph + AgentScope 内容营销多智能体系统（MVP）

本项目在现有仓库上新增了可运行的最小演示（MVP），整合 LangGraph 工作流编排与 AgentScope 风格 Agents，提供统一 LLM 适配、事件总线（可选内存或 Redis）、状态存储（内存 stub，可迁移到 Postgres）、向量存储（内存实现，可替换 pgvector/FAISS）、监控收集（可扩展到 Prometheus）以及 docker-compose 基础编排。

### 目录结构（新增）
- `orchestrator/`：工作流编排（`ContentMarketingFlow`）
- `agents/`：五种角色 Agent（Strategy/Content/Critic/Execution/Interaction）
- `llm/`：`LLMClient` 统一调用适配（支持本地回退）
- `mq/`：`InMemoryEventBus` + `RedisEventBus`
- `storage/`：任务状态、审计、S3-like 本地文件存储
- `vectorstore/`：`SimpleVectorStore` 内存向量库
- `monitoring/`：Metrics 事件收集器（可接 Prometheus）
- `run_demo.py`：端到端演示脚本
- `docker-compose.yml`：Redis/Postgres/pgvector/Prometheus/Grafana 等占位服务

### 运行 Demo
```bash
# 默认使用内存事件总线
python run_demo.py

# 使用 Redis Pub/Sub（需先启动 Redis，参考 docker-compose）
set EVENT_BUS=redis
set REDIS_URL=redis://localhost:6379/0
python run_demo.py
```
如需模拟真实 LLM（Qwen），设置环境变量 `QWEN_API_KEY` 并在 `llm/client.py` 接入真实 API；未设置时使用本地占位逻辑保证可重复演示。

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
- 通过事件总线（内存或 Redis）广播 `plan/ draft/ refined/ publish/ analytics` 等事件，`monitoring.metrics` 订阅统计

### 测试
```bash
pytest -q tests/test_llm_adapter.py \
        tests/test_agent_outputs_schema.py \
        tests/test_workflow_retry.py \
        tests/test_vector_memory.py
```

### 下一步
- 将 `TaskStore` / `AuditLog` 替换为 Postgres（psycopg + migrations + event sourcing）
- 把 `S3Like` 替换成真实 S3（boto3）并扩展媒体上传/下载策略
- 为 `LLMClient` 增加 RAG 检索、pgvector/FAISS 记忆接入
- 把 `monitoring.metrics` 对接 Prometheus + Grafana，实现实时监控/告警
- 接入真实社媒 API（ExecutionAgent）与互动引擎（InteractionAgent）


