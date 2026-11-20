# Qwen3.5-4B-Memory-V2

[English](README_EN.md) | 简体中文

> **基于 `Qwen/Qwen3.5-4B`（Apache-2.0）微调的轻量级本地记忆处理专用模型**：专注**结构化事实抽取（Fact Extraction）**与**写前事实验收纠错（Fact Admission）**，以 **2.7 GB – 4.5 GB** 的超小体积，在结构化合规率、证据溯源与错误拦截率上大幅超越原版 `Qwen3.5-9B`，推理速度提升 **3 倍以上**。

---

## 核心亮点

- **小体积越级打大底座**：`Q8_0`（4.48 GB）与 `Q4_K_M`（2.71 GB）均实现 **100% 事实抽取 Schema 合规**与 **0 次记录日期串扰（Record-Date Leak）**；在写前事实验收任务上，`Q8_0` 槽位判定准确率达 **97.25%**、错误拦截率达 **90.48%**（原版 `9B` 为 0.0%）。
- **零幻觉证据绑定**：每条抽取事实均严格绑定输入原文段 ID（`s0, s1, ...`），在 50 题冻结验证集上实现 **0 条伪造证据引用**。
- **端侧常驻友好**：配合 `Ollama` / `llama.cpp` 可 100% GPU 常驻运行（`Q4_K_M` 约 3.4 GB 显存，`Q8_0` 约 5.2 GB 显存，`num_ctx=16384`），适合本地 AI 记忆系统、个人知识库与 Agent 后台整理服务。
- **友好开源协议**：沿用底座 **Apache-2.0** 协议，可自由研究、修改与商业使用（详见 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)）。

---

## 模型下载与托管分工

本仓库（GitHub）提供使用文档、`Modelfile`、标准推理 Prompt 合同、合成样例与验证脚本；大体积模型权重托管在以下模型平台：

| 平台 | 提供内容 | 链接 / 命令 |
| :--- | :--- | :--- |
| **Hugging Face** | ✅ **全量已上线**：`Q8_0` / `Q4_K_M` GGUF + LoRA 适配器 + Model Card | https://huggingface.co/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **ModelScope 魔搭** | ✅ **全量已上线**：国内高速镜像（`Q8_0` / `Q4_K_M` GGUF + LoRA） | https://modelscope.cn/models/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **Ollama 一键运行** | ✅ 直接拉取 Hugging Face GGUF 运行 | `ollama run hf.co/IMLIULIAN/qwen3.5-4b-memory-v2:Q8_0`（或 `:Q4_K_M`） |

### 权重文件与 SHA-256 校验值

| 产物 | 推荐场景 | 文件大小 | SHA-256 |
| :--- | :--- | :---: | :--- |
| `qwen3.5-4b-memory-v2-Q8_0.gguf` | **主力推荐**：最高事实验收与纠错精度 | 4,482,402,624 B (~4.48 GB) | `be3259d5b1e2e78a49ee889247504188dd721a03c3df420a902b754d14d08ead` |
| `qwen3.5-4b-memory-v2-Q4_K_M.gguf` | **低显存/轻量常驻**：极限压缩显存与最快速度 | 2,708,803,904 B (~2.71 GB) | `58d2b7939b43069cc2c610107a2f802f6c869ac30707bd183fc36dd670784e66` |
| `adapter_model.safetensors` | **研究者/二次集成**：PEFT LoRA 适配器（`r=16, alpha=32`） | 84,972,248 B (~81.0 MB) | `0806fd9f1e1cfd038da7f210b25e41cfcb893b360b5f49e7ca0f43d7c89fc235` |

---

## 评测表现（50 题冻结验证集，无语法约束解码）

以下指标均在**关闭受限语法解码（Constrained Grammar = Off）**的原始 JSON 生成条件下测得（20 题结构化事实抽取 + 30 题写前事实验收，共 109 个候选槽位；原始数字见 [eval/benchmark_summary.json](eval/benchmark_summary.json)）：

| 指标 | `Qwen3.5-9B` (原版) | `Qwen3.5-4B` (原版 Q4_K_M) | **`V2 (Q4_K_M)`** | **`V2 (Q8_0 推荐)`** |
| :--- | :---: | :---: | :---: | :---: |
| **GGUF 体积** | ~6.6 GB | ~3.3 GB | **2.71 GB** | **4.48 GB** |
| **抽取 · Schema 合规率** | 45.0% (9/20) | 45.0% (9/20) | **100.0% (20/20)** | **100.0% (20/20)** |
| **抽取 · 记录日期串扰数** | 7 | 5 | **0** | **0** |
| **抽取 · 幻觉证据引用数** | 0 | 0 | **0** | **0** |
| **抽取 · Token F1 / Evidence F1** | 0.1485 / 0.4218 | 0.1159 / 0.4287 | **0.4121 / 0.6517** | **0.4339 / 0.7006** |
| **抽取 · 单题平均延迟** | 43.11 s | 23.81 s | **11.64 s (快 3.7×)** | **13.55 s (快 3.2×)** |
| **验收 · Schema 合规率** | 20.0% (6/30) | 0.0% (0/30) | **96.7% (29/30)** | **100.0% (30/30)** |
| **验收 · 整批完全一致率** | 20.0% (6/30) | 0.0% (0/30) | **83.3% (25/30)** | **93.3% (28/30)** |
| **验收 · 槽位判定准确率** | 33.0% | 0.0% | **93.6%** | **97.3%** |
| **验收 · 错误拦截率 (`revise`)** | 0.0% (0/21) | 0.0% (0/21) | **71.4% (15/21)** | **90.5% (19/21)** |
| **验收 · 正确事实保留率 (`pass`)** | 40.9% | 0.0% | **98.9% (87/88)** | **98.9% (87/88)** |
| **综合得分（Composite）** | — | — | **0.7134** | **0.7746** |

---

## 30 秒快速上手（Ollama）

### 1. 从本地 GGUF 注册模型

下载 `qwen3.5-4b-memory-v2-Q8_0.gguf`（或 `Q4_K_M`）后，将其与对应 `Modelfile` 放在同一目录：

```bash
# 注册 Q8_0 版本（推荐）
ollama create qwen3.5:4b-memory-v2 -f modelfiles/Modelfile.q8_0

# 或注册 Q4_K_M 轻量版本
ollama create qwen3.5:4b-memory-v2-q4 -f modelfiles/Modelfile.q4_k_m
```

### 2. 一键运行公开合成样例验证

仓库内置 8 条完全虚构的公开合成测试样例（4 条事实抽取 + 4 条写前验收），拉下来即可验证部署是否正常：

```bash
python scripts/verify_ollama.py --model qwen3.5:4b-memory-v2 --num-ctx 16384
```

详细输入/输出 JSON 格式示例见 [examples/sample_io.md](examples/sample_io.md)，两类核心任务的完整 System Prompt 合同见：
- 事实抽取：[prompts/fact_extraction_system.txt](prompts/fact_extraction_system.txt)
- 写前验收：[prompts/fact_admission_system.txt](prompts/fact_admission_system.txt)

---

## 模型规格与推荐推理参数

- **底座模型（Base Model）**：`Qwen/Qwen3.5-4B`（Apache-2.0）
- **适配结构**：PEFT LoRA（`r=16`, `lora_alpha=32`, 作用于语言主干注意力与 MLP 投影层）
- **推荐推理配置**：
  - `think`: `false`（关闭思考标签，直接输出严格 JSON）
  - `temperature`: `0`（确定性抽取与判定）
  - `presence_penalty`: `0`（避免惩罚合法 JSON 重复字段键名）
  - `top_p`: `0.95`, `top_k`: `20`
  - `num_ctx`: `16384`（常驻部署建议统一上下文长度，防止重复加载）

---

## 适用边界与局限说明

- **专用任务模型**：本模型专门针对“原文分段 → 结构化事实抽取”和“候选事实对照原文 → 放行/修订/丢弃/挂起”两类后端记忆流水线任务优化，**不推荐用于开放域闲聊、创意写作或复杂数学/编程推理**。
- **遵循输入证据**：模型强依赖结构化的 `evidence` 分段 JSON 输入；建议严格沿用 `prompts/` 中的 System Prompt 与输入字段约定以获得最佳合规率。
- **验收判定倾向**：V2 在 `pass`（忠实放行）与 `revise`（精准改错拦截）上经过重点强化；遇到与单段原文冲突的错误候选时，模型通常倾向直接返回 `revise` 并给出忠实替换文本，而非 `drop`。
- **训练方法与数据说明**：本仓库公开模型权重、推理合同、合成评测样例与验证脚本，训练数据及训练方法暂不公开。

---

## 许可证与致谢

- 本项目及其发布权重遵循 [Apache License 2.0](LICENSE)。
- 衍生自阿里云通义千问团队开源的 [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)（Apache-2.0），详见 [NOTICE](NOTICE)。
