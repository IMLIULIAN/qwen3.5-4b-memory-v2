---
license: apache-2.0
base_model: Qwen/Qwen3.5-4B
language:
  - zh
  - en
pipeline_tag: text-generation
tags:
  - qwen3.5
  - memory
  - zeromem
  - mcp
  - fact-extraction
  - fact-verification
  - structured-output
  - json
  - lora
  - gguf
  - ollama
---

# Qwen3.5-4B-Memory-V2

**Qwen3.5-4B-Memory-V2** is a specialized derivative of [`Qwen/Qwen3.5-4B`](https://huggingface.co/Qwen/Qwen3.5-4B) fine-tuned via PEFT LoRA (`r=16, alpha=32`) for two core local AI memory pipeline tasks:

1. **Structured Fact Extraction** — Extract grounded, atomic facts with strict JSON schema compliance, segment-level evidence IDs (`s0, s1, ...`), and separation between record dates and event effective dates.
2. **Pre-Write Fact Admission & Revision** — Audit candidate facts against original evidence segments and output per-slot verdicts (`pass` / `revise` / `drop` / `hold`) with concise faithful replacements for definite errors.

> **Companion Memory Engine**: Looking for an out-of-the-box local memory layer? See **[ZeroMem（零忆）](https://github.com/IMLIULIAN/zeromem)** ([简体中文](https://github.com/IMLIULIAN/zeromem/blob/main/README.md) | [English](https://github.com/IMLIULIAN/zeromem/blob/main/README_EN.md)).

## Companion Memory Engine: ZeroMem (Out-of-the-Box)

**[ZeroMem](https://github.com/IMLIULIAN/zeromem)** is a lightweight local memory engine built specifically around `Qwen3.5-4B-Memory-V2`:

- **Zero third-party Python dependencies**: Python 3.9+ stdlib and Ollama only (including the 4-tool MCP stdio server and native `tkinter` desktop workbench).
- **No external vector DB or embedding model**: Single SQLite file (WAL) with dual-track FTS5 indexing over extracted facts and bound original evidence.
- **Zero cloud API cost on write + local secret redaction**: Runs extraction and pre-write admission locally and redacts common credentials to `[REDACTED]` before storage.
- **Hardware auto-selection & 7 AI Agent connectors**: Auto-selects `Q8_0` vs `Q4_K_M` and safe `num_ctx`, with reversible (`.bak`) setup for Claude Desktop, Claude Code, Cursor, Windsurf, Codex CLI, Antigravity, and DeepSeek Harness (DSH).

### Quick Install ZeroMem (Auto-Pulls & Registers This Model)

**Windows (PowerShell)**:

```powershell
# Global (Hugging Face); for Mainland China mirror, set ZEROMEM_SOURCE="modelscope" or omit it
$env:ZEROMEM_MODE="mcp"; $env:ZEROMEM_SOURCE="hf"; $env:ZEROMEM_AUTO_DEPS="1"; $env:ZEROMEM_CONNECT_ALL="1"
irm https://raw.githubusercontent.com/IMLIULIAN/zeromem/main/install.ps1 | iex
```

**macOS / Linux**:

```bash
# Global (Hugging Face); for Mainland China mirror, set ZEROMEM_SOURCE=modelscope or omit it
ZEROMEM_MODE=mcp ZEROMEM_SOURCE=hf ZEROMEM_AUTO_DEPS=1 ZEROMEM_CONNECT_ALL=1 curl -fsSL https://raw.githubusercontent.com/IMLIULIAN/zeromem/main/install.sh | bash
```

**Alternative (`pip`)**:

```bash
pip install git+https://github.com/IMLIULIAN/zeromem.git
zmem setup --mode mcp --source hf --connect-all   # Plan 2: Agent MCP Mode (use --source modelscope in CN)
zmem setup --mode fast --source hf                # Plan 1: Single-Recall Mode (CLI / Python SDK)
```

### Controlled 52k-Char End-to-End Benchmark Summary (ZeroMem + DeepSeek API)

Evaluated on **71 synthetic engineering documents (51,947 chars / 385 extracted facts) × 12 objective questions** against DeepSeek API (`deepseek-flash`; local V2 write cloud cost `¥0`):

| Metric | Group A: Bare API | Group B: Full-Context | Plan 1 (Group C): Single-Recall | Plan 2 (Group D): Agent MCP |
| :--- | :---: | :---: | :---: | :---: |
| **Objective Accuracy** | 2/12 (16.7%) | 12/12 (100.0%) | **11/12 (91.7%)** | **12/12 (100.0%)** |
| **Avg Input Tokens / Q** | 1,629 | 31,720 | **1,821 (-94.3%)** | **4,296 (-86.5%)** |
| **12-Q Cold-Start Cost (No Cache)** | ¥0.053 | ¥0.770 | **¥0.054 (-93.0%)** | **¥0.120 (-84.4%)** |
| **12-Q Cached Cost** | ¥0.026 | ¥0.149 | **¥0.033 (-78.0%)** | **¥0.078 (-47.7%)** |
| **Avg Latency / Q** | 9.27s | 7.20s | **6.46s** | 9.84s (avg 2.17 tool calls) |
| **Cloud Plaintext Secret Exposure** | 0 | **24×** | **0×** | **0×** |
| **Bound Evidence Traceability** | 0/12 | 0/12 | **12/12** | **12/12** |

> **Scope Note**: This is a small, controlled benchmark (71 synthetic engineering notes, 12 objective questions) illustrating relative trade-offs in context size, estimated cost, and credential redaction—not a universal leaderboard. Real-world results vary with document structure, language mix, and query complexity.

## Available Artifacts

| Artifact | Format | Size | SHA-256 |
| :--- | :--- | :---: | :--- |
| `qwen3.5-4b-memory-v2-Q8_0.gguf` | GGUF (`Q8_0`, recommended) | 4.48 GB | `be3259d5b1e2e78a49ee889247504188dd721a03c3df420a902b754d14d08ead` |
| `qwen3.5-4b-memory-v2-Q4_K_M.gguf` | GGUF (`Q4_K_M`, compact) | 2.71 GB | `58d2b7939b43069cc2c610107a2f802f6c869ac30707bd183fc36dd670784e66` |
| `lora/adapter_model.safetensors` | PEFT LoRA (`r=16, alpha=32`) | 81.0 MB | `0806fd9f1e1cfd038da7f210b25e41cfcb893b360b5f49e7ca0f43d7c89fc235` |

## Model Benchmark Results (50-Case Frozen Validation Suite, Unconstrained JSON)

| Metric | `Qwen3.5-9B` (Raw) | `Qwen3.5-4B` (Raw Q4_K_M) | `V2 (Q4_K_M)` | `V2 (Q8_0)` |
| :--- | :---: | :---: | :---: | :---: |
| Extraction Schema Valid Rate | 45.0% | 45.0% | **100.0%** | **100.0%** |
| Extraction Record-Date Leaks | 7 | 5 | **0** | **0** |
| Extraction Evidence F1 | 0.4218 | 0.4287 | **0.6517** | **0.7006** |
| Extraction Mean Latency | 43.11 s | 23.81 s | **11.64 s** | **13.55 s** |
| Admission Schema Valid Rate | 20.0% | 0.0% | **96.7%** | **100.0%** |
| Admission Slot Accuracy | 33.0% | 0.0% | **93.6%** | **97.3%** |
| Admission Error Interception (`revise`) | 0.0% | 0.0% | **71.4%** | **90.5%** |
| Admission Clean-Pass Retention | 40.9% | 0.0% | **98.9%** | **98.9%** |

> **Note**: Evaluated on 20 fact-extraction and 30 pre-write admission cases (109 candidate slots) without constrained grammar decoding; reflects performance on these two structured memory subtasks rather than general chat benchmarks.

## Recommended Inference Settings

- Runtime: `Ollama` or `llama.cpp`
- `think`: `false`
- `temperature`: `0`
- `presence_penalty`: `0`
- `top_p`: `0.95`, `top_k`: `20`
- `num_ctx`: `16384` (or `8192` on tighter VRAM budgets)

## Intended Scope & Links

- **Scope**: Specialized backend model for structured fact extraction and pre-write fact admission/revision; not intended for general-purpose chat, creative writing, or math/coding benchmarks. Training scripts and datasets are not publicly released.
- **Companion Memory Engine (ZeroMem)**: `https://github.com/IMLIULIAN/zeromem`
- **Model Docs, Prompts, Modelfiles & Synthetic Verification Scripts**: `https://github.com/IMLIULIAN/qwen3.5-4b-memory-v2`
- **ModelScope Mirror**: `https://modelscope.cn/models/IMLIULIAN/qwen3.5-4b-memory-v2`
- **Hugging Face**: `https://huggingface.co/IMLIULIAN/qwen3.5-4b-memory-v2`

## License, Attribution & Compatibility

- **License**: Apache License 2.0 (`Apache-2.0`), derived from [`Qwen/Qwen3.5-4B`](https://huggingface.co/Qwen/Qwen3.5-4B) (Qwen Team, Alibaba Cloud, Apache-2.0). See [LICENSE](LICENSE) and [NOTICE](NOTICE).
- **Author**: **B站IM榴莲 (IMLIULIAN)** · **ZeroZoneX**
- **Companion Local Engines**: [`ZeroMem (零忆)`](https://github.com/IMLIULIAN/zeromem) (Apache-2.0) and [`@imliulian/dsh-zeromem`](https://github.com/IMLIULIAN/dsh-zeromem) (AGPL-3.0).
- **Schema Lineage & Compatibility**: The structured fact JSON schema (`bank`, `type: world | experience | observation`, `occurred_start` / `occurred_end` / `mentioned_at`, `where`, `entities`) is inspired by and conceptually compatible with [**Vectorize Hindsight**](https://github.com/vectorize-io/hindsight) (MIT License); no Hindsight source code is included.
- **Name Disambiguation**: The companion engine **ZeroMem (零忆)** is an independent local SQLite/FTS5 memory engine and is **not** affiliated with or derived from the academic paper *Zero-Mem: Zero-Token Memory Operations for LLM Agents* (Yilin Xiao et al., [arXiv:2607.29377](https://arxiv.org/abs/2607.29377), July 2026).
