# 输入输出示例 / Input & Output Examples

以下均为**完全虚构的合成样例**，演示 `Qwen3.5-4B-Memory-V2` 的两类核心任务接口。

---

## 任务一：结构化事实抽取（Fact Extraction）

* **System Prompt**：使用 [prompts/fact_extraction_system.txt](../prompts/fact_extraction_system.txt)
* **User Input (JSON)**：

```json
{
  "bank": "demo-public",
  "document_id": "doc-quota-01",
  "evidence": [
    {
      "id": "s0",
      "path": ["note"],
      "text": "2026-03-01 记录：API 网关速率上限将于 2026-03-15 起调整为每分钟 120 次，原上限为每分钟 60 次。"
    }
  ]
}
```

* **Expected Output (JSON)**：

```json
{
  "facts": [
    {
      "text": "API 网关速率上限将于 2026-03-15 起调整为每分钟 120 次，原上限为每分钟 60 次。",
      "type": "world",
      "occurred_start": "2026-03-15",
      "occurred_end": null,
      "where": null,
      "entities": ["API 网关"],
      "evidence": ["s0"]
    }
  ]
}
```

> 关键点：记录日期（`2026-03-01`）与生效日期（`2026-03-15`）严格隔离，且每条事实均绑定可追溯的原文段 ID（`"evidence": ["s0"]`）。

---

## 任务二：写前事实验收与纠错（Fact Admission）

* **System Prompt**：使用 [prompts/fact_admission_system.txt](../prompts/fact_admission_system.txt)
* **User Input (JSON)**：

```json
{
  "evidence": [
    {
      "id": "s0",
      "path": ["note"],
      "text": "数据库主节点连接池上限设置为 200，只读副本上限为 500。"
    }
  ],
  "facts": {
    "0": {
      "text": "数据库主节点连接池上限设置为 500。",
      "type": "world",
      "occurred_start": null,
      "occurred_end": null,
      "where": null,
      "entities": ["数据库主节点"],
      "mentioned_at": "2026-05-03T08:00:00Z",
      "context": "demo",
      "tags": []
    }
  }
}
```

* **Expected Output (JSON)**：

```json
{
  "0": {
    "decision": "revise",
    "evidence": ["s0"],
    "replacement": "数据库主节点连接池上限设置为 200，只读副本上限为 500。"
  }
}
```

> 四类判定含义：`pass`（完全被证据支持）、`revise`（明确错误且可忠实修正）、`drop`（无证据支撑的编造声明）、`hold`（证据不完整或冲突，暂不放行）。
