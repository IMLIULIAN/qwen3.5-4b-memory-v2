# Qwen3.5-4B-Memory-V2

English | [简体中文](README.md)

> **A lightweight local memory-processing model fine-tuned from `Qwen/Qwen3.5-4B` (Apache-2.0)**: specialized in **Structured Fact Extraction** and **Pre-Write Fact Admission / Revision**. At just **2.7 GB – 4.5 GB** (GGUF), it dramatically outperforms raw `Qwen3.5-9B` in JSON schema compliance, evidence grounding, and error interception while running **3×+ faster**.

---

## Highlights

- **Punches Far Above Its Weight**: Both `Q8_0` (4.48 GB) and `Q4_K_M` (2.71 GB) reach **100% extraction schema compliance** with **0 record-date leaks**. On pre-write fact admission, `Q8_0` achieves **97.25% slot decision accuracy** and **90.48% error interception** (vs. 0.0% on raw `Qwen3.5-9B`).
- **Zero Hallucinated Evidence IDs**: Every extracted claim is grounded to supplied source segment IDs (`s0, s1, ...`) with **0 hallucinated segment references** across the 50-case validation suite.
- **Resident Local-First Deployment**: Runs comfortably at 100% GPU via `Ollama` / `llama.cpp` (~3.4 GB VRAM for `Q4_K_M`, ~5.2 GB VRAM for `Q8_0` at `num_ctx=16384`), ideal for local AI memory engines and background agent pipelines.
- **Permissive License**: Distributed under **Apache-2.0**, inheriting full commercial and open-source compatibility from `Qwen/Qwen3.5-4B` (see [LICENSE](LICENSE) and [NOTICE](NOTICE)).

---

## Model Distribution

This GitHub repository hosts documentation, Ollama `Modelfile` templates, runtime system prompts, synthetic test cases, and a standalone verification script. Model weights are hosted on dedicated model hubs:

| Platform | Artifacts | Link / Command |
| :--- | :--- | :--- |
| **ModelScope** | ✅ **Full Release Live**: `Q8_0` / `Q4_K_M` GGUF + LoRA adapter | https://modelscope.cn/models/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **Hugging Face** | Global mirror (Model Card / Modelfile / LoRA; GGUF syncing) | https://huggingface.co/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **Ollama Library** | One-command pull & run | `ollama run imliulian/qwen3.5-4b-memory:v2` *(pending push)* |

### Checksums (SHA-256)

| File | Recommended Use | Size | SHA-256 |
| :--- | :--- | :---: | :--- |
| `qwen3.5-4b-memory-v2-Q8_0.gguf` | **Recommended**: highest accuracy & error interception | 4,482,402,624 B (~4.48 GB) | `be3259d5b1e2e78a49ee889247504188dd721a03c3df420a902b754d14d08ead` |
| `qwen3.5-4b-memory-v2-Q4_K_M.gguf` | **Low-VRAM / Fastest**: compact resident deployment | 2,708,803,904 B (~2.71 GB) | `58d2b7939b43069cc2c610107a2f802f6c869ac30707bd183fc36dd670784e66` |
| `adapter_model.safetensors` | **Researchers / Custom Merge**: PEFT LoRA (`r=16, alpha=32`) | 84,972,248 B (~81.0 MB) | `0806fd9f1e1cfd038da7f210b25e41cfcb893b360b5f49e7ca0f43d7c89fc235` |

---

## Benchmark Results (50-Case Frozen Suite, Unconstrained JSON)

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

---

## Quick Start (Ollama)

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
  - `temperature=0`, `presence_penalty=0`, `top_p=0.95`, `top_k=20`, `num_ctx=16384`

---

## Intended Scope & Limitations

- **Specialized Backend Model**: Designed strictly for structured fact extraction and pre-write fact verification/revision in memory pipelines. Not intended for general-purpose chat, creative writing, or general math/coding benchmarks.
- **Admission Behavior Note**: V2 is heavily optimized for `pass` and faithful `revise` interception; when a candidate contradicts a short evidence segment, it often prefers returning `revise` with a faithful grounded replacement rather than `drop`.
- **Training Method Scope**: Weights, inference prompts, synthetic examples, and verification tooling are publicly released under Apache-2.0; training scripts and datasets are not publicly released at this time.

---

## License & Attribution

- Licensed under the [Apache License 2.0](LICENSE).
- Built upon [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) by the Qwen Team, Alibaba Cloud (Apache-2.0). See [NOTICE](NOTICE).
