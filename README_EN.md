# Qwen3.5-4B-Memory-V2

English | [简体中文](README.md)

> **A lightweight local memory-processing model fine-tuned from `Qwen/Qwen3.5-4B` (Apache-2.0)**: focused on **Structured Fact Extraction** and **Pre-Write Fact Admission / Revision**. At **2.71 GB – 4.48 GB** (GGUF), it substantially improves JSON schema compliance, evidence grounding, and pre-write error interception over raw `Qwen3.5-9B` on our 50-case validation suite while running over **3× faster**.

---

## Key Characteristics

- **Task-Focused 4B Specialization**: On the 50-case frozen validation suite, both `Q8_0` (4.48 GB) and `Q4_K_M` (2.71 GB) reach **100% extraction schema compliance** with **0 record-date leaks**. On pre-write fact admission, `Q8_0` achieves **97.3% slot decision accuracy** (97.25%) and **90.5% error interception** (19/21, vs. 0/21 on raw `Qwen3.5-9B`).
- **Segment-Level Evidence Grounding**: Every extracted claim binds to supplied source segment IDs (`s0, s1, ...`), with **0 hallucinated segment references** on the 50-case validation suite.
- **Resident Local-First Deployment**: Runs locally on GPU via `Ollama` / `llama.cpp` (~3.4 GB VRAM for `Q4_K_M`, ~5.2 GB VRAM for `Q8_0` at `num_ctx=16384`; `8192` is a practical option on tighter VRAM budgets), suited for local memory stores and background agent indexing.
- **Companion Memory Engine (ZeroMem)**: Paired with **[ZeroMem](https://github.com/IMLIULIAN/zeromem/blob/main/README_EN.md)**, a lightweight zero-dependency local memory engine providing CLI / Python SDK, a 4-tool MCP server for 7 AI Agents, and a native `tkinter` desktop workbench.
- **Apache-2.0 License**: Distributed under **Apache-2.0**, inheriting full commercial and open-source compatibility from `Qwen/Qwen3.5-4B` (see [LICENSE](LICENSE) and [NOTICE](NOTICE)).

---

## Model Distribution

This GitHub repository hosts documentation, Ollama `Modelfile` templates, runtime system prompts, synthetic test cases, and a standalone verification script. Model weights and the companion runtime engine are hosted below:

| Platform / Repo | Artifacts | Link / Command |
| :--- | :--- | :--- |
| **ZeroMem (Companion Engine)** | Out-of-the-box local memory engine: zero third-party deps, MCP server, 7 AI Agent connectors, native desktop workbench | https://github.com/IMLIULIAN/zeromem ([English Docs](https://github.com/IMLIULIAN/zeromem/blob/main/README_EN.md)) |
| **Hugging Face** | Available: `Q8_0` / `Q4_K_M` GGUF + LoRA adapter + Model Card | https://huggingface.co/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **ModelScope** | Available: Mainland China mirror (`Q8_0` / `Q4_K_M` GGUF + LoRA) | https://modelscope.cn/models/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **Ollama (Direct Pull)** | Pull GGUF directly from Hugging Face | `ollama run hf.co/IMLIULIAN/qwen3.5-4b-memory-v2:Q8_0` (or `:Q4_K_M`) |

### Checksums (SHA-256)

| File | Recommended Use | Size | SHA-256 |
| :--- | :--- | :---: | :--- |
| `qwen3.5-4b-memory-v2-Q8_0.gguf` | **Recommended**: more stable pre-write admission & revision | 4,482,402,624 B (~4.48 GB) | `be3259d5b1e2e78a49ee889247504188dd721a03c3df420a902b754d14d08ead` |
| `qwen3.5-4b-memory-v2-Q4_K_M.gguf` | **Low-VRAM / Compact**: lower VRAM footprint & faster response | 2,708,803,904 B (~2.71 GB) | `58d2b7939b43069cc2c610107a2f802f6c869ac30707bd183fc36dd670784e66` |
| `adapter_model.safetensors` | **Researchers / Custom Merge**: PEFT LoRA (`r=16, alpha=32`) | 84,972,248 B (~81.0 MB) | `0806fd9f1e1cfd038da7f210b25e41cfcb893b360b5f49e7ca0f43d7c89fc235` |

---

## Companion Memory Engine: ZeroMem

If you want to use `Qwen3.5-4B-Memory-V2` directly as a local long-term memory layer without building chunking, dual-contract parsing, guardrails, and indexing from scratch, see **[ZeroMem](https://github.com/IMLIULIAN/zeromem/blob/main/README_EN.md)** ([简体中文](https://github.com/IMLIULIAN/zeromem)):

- **Zero third-party Python dependencies**: Python 3.9+ stdlib and Ollama only (including the MCP stdio server and native dark `tkinter` desktop workbench).
- **No external vector DB or embedding model**: Single SQLite file (WAL) + dual-track FTS5 indexing for both extracted facts and bound original evidence.
- **Zero cloud API cost on write + local secret redaction**: Local 4B extraction and pre-write admission, redacting common credential patterns to `[REDACTED]` before storage.
- **Hardware auto-detection & 7 AI Agent connectors**: Picks `Q8_0` vs `Q4_K_M` and a safe `num_ctx` automatically, with backed-up (`.bak`) setup for Claude Desktop, Claude Code, Cursor, Windsurf, Codex CLI, Antigravity, and DeepSeek Harness (DSH).

### Quick Install (Auto-Pulls & Registers This Model)

**Plan 2: Agent MCP Mode (Default — Hardware Detection + Model Pull + Agent Setup)**

Windows (PowerShell):

```powershell
$env:ZEROMEM_MODE="mcp"; $env:ZEROMEM_SOURCE="hf"; $env:ZEROMEM_AUTO_DEPS="1"; $env:ZEROMEM_CONNECT_ALL="1"
irm https://raw.githubusercontent.com/IMLIULIAN/zeromem/main/install.ps1 | iex
```

macOS / Linux:

```bash
ZEROMEM_MODE=mcp ZEROMEM_SOURCE=hf ZEROMEM_AUTO_DEPS=1 ZEROMEM_CONNECT_ALL=1 curl -fsSL https://raw.githubusercontent.com/IMLIULIAN/zeromem/main/install.sh | bash
```

**Alternative: `pip install` (Plan 2 Agent MCP / Plan 1 Single-Recall Mode)**

```bash
pip install git+https://github.com/IMLIULIAN/zeromem.git
zmem setup --mode mcp --source hf --connect-all   # Plan 2: Agent MCP Mode
zmem setup --mode fast --source hf                # Plan 1: Single-Recall Mode (CLI / Python SDK)
```

> Use `--source modelscope` (or omit `ZEROMEM_SOURCE`) in Mainland China to pull from the ModelScope mirror with automatic SHA-256 verification.

### Controlled 52k-Char End-to-End Benchmark Summary (ZeroMem + DeepSeek API)

Evaluated on **71 synthetic engineering documents (51,947 chars / 385 extracted facts) × 12 objective questions** with cloud DeepSeek API (`deepseek-flash`; local V2 write cloud cost `¥0`):

| Metric | Group A: Bare API | Group B: Full-Context Stuffing | Plan 1 (Group C): Single-Recall | Plan 2 (Group D): Agent MCP |
| :--- | :---: | :---: | :---: | :---: |
| **Objective Accuracy** | 2/12 (16.7%) | 12/12 (100.0%) | **11/12 (91.7%)** | **12/12 (100.0%)** |
| **Avg Input Tokens / Q** | 1,629 | 31,720 | **1,821 (-94.3%)** | **4,296 (-86.5%)** |
| **12-Q Cold-Start Cost (No Cache)** | ¥0.053 | ¥0.770 | **¥0.054 (-93.0%)** | **¥0.120 (-84.4%)** |
| **12-Q Cached Cost** | ¥0.026 | ¥0.149 | **¥0.033 (-78.0%)** | **¥0.078 (-47.7%)** |
| **Avg Latency / Q** | 9.27s | 7.20s | **6.46s** | 9.84s (avg 2.17 tool calls) |
| **Cloud Plaintext Secret Exposure** | 0 | **24×** | **0×** | **0×** |
| **Bound Evidence Traceability** | 0/12 | 0/12 | **12/12** | **12/12** |

> **Scope Note**: This is a small, controlled benchmark (71 synthetic engineering notes, 12 objective questions) intended to illustrate relative trade-offs in context size, estimated cost, and credential redaction—not a universal leaderboard. Real-world results will vary with document structure, language mix, and query complexity. Full charts and details are in [IMLIULIAN/zeromem](https://github.com/IMLIULIAN/zeromem/blob/main/README_EN.md).

---

## Model Benchmark Results (50-Case Frozen Suite, Unconstrained JSON)

Evaluated without constrained grammar decoding (`20` fact extraction + `30` fact admission cases, `109` candidate slots total; full aggregate JSON in [eval/benchmark_summary.json](eval/benchmark_summary.json)):

| Metric | `Qwen3.5-9B` (Raw) | `Qwen3.5-4B` (Raw Q4_K_M) | **`V2 (Q4_K_M)`** | **`V2 (Q8_0, Rec.)`** |
| :--- | :---: | :---: | :---: | :---: |
| **GGUF Size** | ~6.6 GB | ~3.3 GB | **2.71 GB** | **4.48 GB** |
| **Extraction · Schema Valid Rate** | 45.0% (9/20) | 45.0% (9/20) | **100.0% (20/20)** | **100.0% (20/20)** |
| **Extraction · Record-Date Leaks** | 7 | 5 | **0** | **0** |
| **Extraction · Hallucinated Evidence** | 0 | 0 | **0** | **0** |
| **Extraction · Token F1 / Evidence F1** | 0.1485 / 0.4218 | 0.1159 / 0.4287 | **0.4121 / 0.6517** | **0.4339 / 0.7006** |
| **Extraction · Mean Latency** | 43.11 s | 23.81 s | **11.64 s (3.7× faster)** | **13.55 s (3.2× faster)** |
| **Admission · Schema Valid Rate** | 20.0% (6/30) | 0.0% (0/30) | **96.7% (29/30)** | **100.0% (30/30)** |
| **Admission · Exact Batch Match** | 20.0% (6/30) | 0.0% (0/30) | **83.3% (25/30)** | **93.3% (28/30)** |
| **Admission · Slot Decision Accuracy** | 33.0% | 0.0% | **93.6%** | **97.3%** |
| **Admission · Error Interception (`revise`)** | 0.0% (0/21) | 0.0% (0/21) | **71.4% (15/21)** | **90.5% (19/21)** |
| **Admission · Clean-Pass Retention** | 40.9% | 0.0% | **98.9% (87/88)** | **98.9% (87/88)** |
| **Composite Score** | — | — | **0.7134** | **0.7746** |

> **Note**: This 50-case frozen validation suite measures structured extraction and pre-write admission under this repository's prompt contracts only; it does not represent general chat or broad benchmark capability.

---

## Manual Ollama Setup & Verification

If you integrate the weights directly into your own pipeline:

```bash
# 1. Create the Ollama model from the downloaded GGUF
ollama create qwen3.5:4b-memory-v2 -f modelfiles/Modelfile.q8_0

# 2. Verify with the 8 built-in public synthetic test cases
python scripts/verify_ollama.py --model qwen3.5:4b-memory-v2 --num-ctx 16384
```

See [examples/sample_io.md](examples/sample_io.md) for JSON request/response walkthroughs and `prompts/` for the production system prompt contracts.

---

## Model Specifications & Recommended Inference Settings

- **Base Model**: `Qwen/Qwen3.5-4B` (Apache-2.0)
- **Adapter**: PEFT LoRA (`r=16`, `lora_alpha=32`, targeting language model attention & MLP projections)
- **Recommended Runtime Parameters**:
  - `think=false` (disable reasoning trace for direct strict JSON output)
  - `temperature=0`, `presence_penalty=0`, `top_p=0.95`, `top_k=20`, `num_ctx=16384` (or `8192` on tighter VRAM budgets)

---

## Intended Scope & Limitations

- **Specialized Backend Model**: Designed strictly for structured fact extraction and pre-write fact verification/revision in memory pipelines. Not intended for general-purpose chat, creative writing, or general math/coding benchmarks.
- **Admission Behavior Note**: V2 is specifically fine-tuned for `pass` and faithful `revise` interception; when a candidate contradicts a short evidence segment, it often prefers returning `revise` with a faithful grounded replacement rather than `drop`.
- **Training Method Scope**: Weights, inference prompts, synthetic examples, and verification tooling are publicly released under Apache-2.0; training scripts and datasets are not publicly released at this time.

---

## License & Attribution

- Licensed under the [Apache License 2.0](LICENSE).
- Built upon [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) by the Qwen Team, Alibaba Cloud (Apache-2.0). See [NOTICE](NOTICE).
