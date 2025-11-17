## LangGraph + AgentScope 内容营销多智能体系统（MVP）

本项目在现有仓库上新增了可运行的最小演示（MVP），主要整合 LangGraph 工作流编排与 AgentScope 风格 Agents，并提供统一 LLM 适配、事件总线（MQ stub）、状态存储（内存 stub）、向量存储（内存实现）、监控收集（内存实现）以及 docker-compose 基础编排。

### 目录结构（新增）
- `orchestrator/`：工作流编排（`ContentMarketingFlow`）
- `agents/`：五种角色 Agent（Strategy/Content/Critic/Execution/Interaction）
- `llm/`：`LLMClient` 统一调用适配（支持本地回退）
- `mq/`：`InMemoryEventBus`（可替换为 Redis）
- `storage/`：任务状态、审计、S3-like 本地文件存储
- `vectorstore/`：`SimpleVectorStore` 内存向量库
- `monitoring/`：Metrics 事件收集器（可接 Prometheus）
- `run_demo.py`：端到端演示脚本
- `docker-compose.yml`：Redis/Postgres/pgvector/Prometheus/Grafana 等占位服务

### 运行 Demo
```bash
python run_demo.py
```
如需模拟真实 LLM（Qwen），设置环境变量 `QWEN_API_KEY` 并在 `llm/client.py` 接入真实 API。

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
`Writer → Critic → HumanReview? → Publisher(带回滚) → Monitor`，内置重试（2次）、可选人工审核（demo 默认自动通过）。

### 测试
```bash
pytest -q tests/test_llm_adapter.py tests/test_agent_outputs_schema.py tests/test_workflow_retry.py tests/test_vector_memory.py
```

### 下一步
- 将 `InMemoryEventBus / TaskStore` 替换为 Redis / Postgres
- 为 `LLMClient` 增加 RAG 检索与长期记忆接入
- 对接 Prometheus 指标与 Grafana dashboard


