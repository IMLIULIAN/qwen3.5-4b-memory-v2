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

## Available Artifacts

| Artifact | Format | Size | SHA-256 |
| :--- | :--- | :---: | :--- |
| `qwen3.5-4b-memory-v2-Q8_0.gguf` | GGUF (`Q8_0`, recommended) | 4.48 GB | `be3259d5b1e2e78a49ee889247504188dd721a03c3df420a902b754d14d08ead` |
| `qwen3.5-4b-memory-v2-Q4_K_M.gguf` | GGUF (`Q4_K_M`, compact) | 2.71 GB | `58d2b7939b43069cc2c610107a2f802f6c869ac30707bd183fc36dd670784e66` |
| `lora/adapter_model.safetensors` | PEFT LoRA (`r=16, alpha=32`) | 81.0 MB | `0806fd9f1e1cfd038da7f210b25e41cfcb893b360b5f49e7ca0f43d7c89fc235` |

## Benchmark Highlights (50-Case Frozen Validation Suite, Unconstrained JSON)

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

## Recommended Inference Settings

- Runtime: `Ollama` or `llama.cpp`
- `think`: `false`
- `temperature`: `0`
- `presence_penalty`: `0`
- `top_p`: `0.95`, `top_k`: `20`
- `num_ctx`: `16384`

Full usage guides, system prompt contracts, `Modelfile` templates, and public synthetic verification scripts are hosted on GitHub:
`https://github.com/lifdjgfndgn/qwen3.5-4b-memory-v2`

## License

Apache License 2.0 (`Apache-2.0`), derived from `Qwen/Qwen3.5-4B` (Apache-2.0).
