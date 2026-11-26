# Qwen3.5-4B-Memory-V2

[English](README_EN.md) | 简体中文

> **基于 `Qwen/Qwen3.5-4B`（Apache-2.0）微调的轻量本地记忆处理专用模型**：面向 **结构化事实抽取**（Fact Extraction）与 **写前事实验收纠错**（Fact Admission）两类后端任务。在 **2.71 GB – 4.48 GB**（GGUF）体积下，在本项目 50 题冻结验证集上的结构化合规率、证据溯源与错误拦截表现明显高于未微调的 `Qwen3.5-9B`，单题抽取耗时缩短约 **3 倍以上**。

---

## 核心特性

- **面向记忆流水线的专项微调**：在 50 题冻结验证集上，`Q8_0`（4.48 GB）与 `Q4_K_M`（2.71 GB）均达到 **100% 事实抽取 Schema 合规**与 **0 次记录日期串扰**（Record-Date Leak）；在写前事实验收任务上，`Q8_0` 槽位判定准确率为 **97.3%**（97.25%）、错误拦截率为 **90.5%**（19/21，同集未微调 `Qwen3.5-9B` 为 0/21）。
- **原文段 ID 证据绑定**：每条抽取事实均绑定输入原文段 ID（`s0, s1, ...`），在 50 题冻结验证集上未出现伪造证据引用（**0 条**）。
- **端侧常驻运行友好**：配合 `Ollama` / `llama.cpp` 可在本地 GPU 常驻运行（`Q4_K_M` 约 3.4 GB 显存，`Q8_0` 约 5.2 GB 显存，`num_ctx=16384`；显存较紧时可设为 `8192`），适合个人记忆系统、本地知识库与 Agent 后台整理服务。
- **配套开箱即用引擎**：提供轻量开源记忆引擎 **[ZeroMem（零忆）](https://github.com/IMLIULIAN/zeromem)**，免去手动拼接提示词、切块与存储流程，支持 CLI / Python SDK、4 工具 MCP 服务与原生桌面工作台。
- **Apache-2.0 开源协议**：沿用底座 **Apache-2.0** 协议，可自由研究、修改与商业使用（详见 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)）。

---

## 模型下载与托管分工

本仓库（GitHub）提供使用文档、`Modelfile`、标准推理 Prompt 合同、合成样例与验证脚本；模型权重与配套运行引擎托管在以下仓库：

| 平台 / 仓库 | 提供内容 | 链接 / 命令 |
| :--- | :--- | :--- |
| **ZeroMem（配套本地记忆引擎）** | 开箱即用轻量引擎：零第三方依赖、MCP 服务、7 款 Agent 接入、原生桌面工作台 | https://github.com/IMLIULIAN/zeromem |
| **ModelScope 魔搭** | 已上线：国内镜像（`Q8_0` / `Q4_K_M` GGUF + LoRA） | https://modelscope.cn/models/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **Hugging Face** | 已上线：`Q8_0` / `Q4_K_M` GGUF + LoRA 适配器 + Model Card | https://huggingface.co/IMLIULIAN/qwen3.5-4b-memory-v2 |
| **Ollama 直接拉取** | 直接从 Hugging Face 拉取 GGUF 运行 | `ollama run hf.co/IMLIULIAN/qwen3.5-4b-memory-v2:Q8_0`（或 `:Q4_K_M`） |

### 权重文件与 SHA-256 校验值

| 产物 | 推荐场景 | 文件大小 | SHA-256 |
| :--- | :--- | :---: | :--- |
| `qwen3.5-4b-memory-v2-Q8_0.gguf` | **常规推荐**：写前事实验收与纠错表现更稳 | 4,482,402,624 B (~4.48 GB) | `be3259d5b1e2e78a49ee889247504188dd721a03c3df420a902b754d14d08ead` |
| `qwen3.5-4b-memory-v2-Q4_K_M.gguf` | **低显存 / 轻量常驻**：更低显存占用与更快响应 | 2,708,803,904 B (~2.71 GB) | `58d2b7939b43069cc2c610107a2f802f6c869ac30707bd183fc36dd670784e66` |
| `adapter_model.safetensors` | **研究者 / 二次集成**：PEFT LoRA 适配器（`r=16, alpha=32`） | 84,972,248 B (~81.0 MB) | `0806fd9f1e1cfd038da7f210b25e41cfcb893b360b5f49e7ca0f43d7c89fc235` |

---

## 配套本地记忆引擎：ZeroMem（零忆）

如果你希望直接把本模型用作 AI 助手或本地项目的长期记忆层，而无需自行实现微切块、双合同调用、规则守卫与索引检索，可直接使用配套开源仓库 **[ZeroMem（零忆）](https://github.com/IMLIULIAN/zeromem)**（[English Docs](https://github.com/IMLIULIAN/zeromem/blob/main/README_EN.md)）：

- **无第三方 Python 依赖**：仅依赖 Python 3.9+ 标准库与 Ollama（含 MCP stdio 服务端与基于 `tkinter` 的原生桌面记忆工作台）。
- **无向量库与 Embedding 模型**：采用单文件 SQLite（WAL）+ 双轨 FTS5 索引，兼顾精炼事实与原文片段溯源。
- **写入零云端 API 费用 + 本地脱敏**：由本地 `Qwen3.5-4B-Memory-V2` 完成抽取与写前审校，入库前自动将常见凭据脱敏为 `[REDACTED]`。
- **自动硬件选档与 7 款主流 Agent 接入**：按显存/统一内存自动推荐 `Q8_0` 或 `Q4_K_M` 及 `num_ctx`，支持自动备份 `.bak` 并接入 Claude Desktop、Claude Code、Cursor、Windsurf、Codex CLI、Antigravity、DeepSeek Harness (DSH)。

### 快速安装 ZeroMem（自动拉取并注册本模型）

**方案二：Agent MCP 版（默认，自动检测硬件、拉取模型并配置已装 Agent）**

Windows (PowerShell)：

```powershell
$env:ZEROMEM_MODE="mcp"; $env:ZEROMEM_AUTO_DEPS="1"; $env:ZEROMEM_CONNECT_ALL="1"
irm https://raw.githubusercontent.com/IMLIULIAN/zeromem/main/install.ps1 | iex
```

macOS / Linux：

```bash
ZEROMEM_MODE=mcp ZEROMEM_AUTO_DEPS=1 ZEROMEM_CONNECT_ALL=1 curl -fsSL https://raw.githubusercontent.com/IMLIULIAN/zeromem/main/install.sh | bash
```

**备选：`pip` 安装（支持方案二 Agent MCP 版 / 方案一轻量省钱版）**

```bash
pip install git+https://github.com/IMLIULIAN/zeromem.git
zmem setup --mode mcp --connect-all   # 方案二：Agent MCP 版
zmem setup --mode fast                # 方案一：轻量省钱版（CLI / Python SDK 单次预注）
```

> 海外网络环境可追加 `ZEROMEM_SOURCE=hf`（或 `--source hf`）从 Hugging Face 拉取；国内环境默认走自动源/魔搭镜像并校验 SHA-256。

### 5.2 万字端到端对照实测摘要（ZeroMem + DeepSeek API）

在一组 **71 篇合成工程文档（51,947 字 / 385 条事实）× 12 道客观题** 上，使用云端 DeepSeek API（`deepseek-flash`）对比了 4 种接入方式（本地 V2 写入云端费 `¥0`）：

| 核心指标 | A 组：裸调（新会话） | B 组：全量历史注入 | 方案一（C 组）：单次检索预注 | 方案二（D 组）：MCP 自主拆查 |
| :--- | :---: | :---: | :---: | :---: |
| **客观准确率** | 2/12 (16.7%) | 12/12 (100.0%) | **11/12 (91.7%)** | **12/12 (100.0%)** |
| **单题平均输入 Token** | 1,629 | 31,720 | **1,821（-94.3%）** | **4,296（-86.5%）** |
| **12 题冷启动费用（无缓存）** | ¥0.053 | ¥0.770 | **¥0.054（-93.0%）** | **¥0.120（-84.4%）** |
| **12 题含缓存实付估算** | ¥0.026 | ¥0.149 | **¥0.033（-78.0%）** | **¥0.078（-47.7%）** |
| **单题平均耗时** | 9.27s | 7.20s | **6.46s** | 9.84s（含多轮工具调用） |
| **云端明文密钥暴露** | 0 | **24 次** | **0 次** | **0 次** |
| **附带原文证据溯源** | 0/12 | 0/12 | **12/12** | **12/12** |

> **评测边界说明**：这是一组小规模受控对照实验（71 篇合成工程文档、12 道客观题），主要用于观察不同接入模式在上下文开销、费用趋势与凭据脱敏上的相对差异，不作为通用能力排名；实际表现会随业务语料结构、语种比例与提问复杂度而变化。完整图表、规模对比与使用说明见 [IMLIULIAN/zeromem](https://github.com/IMLIULIAN/zeromem)。

---

## 模型单测表现（50 题冻结验证集，无语法约束解码）

以下指标均在 **关闭受限语法解码**（Constrained Grammar = Off）的原始 JSON 生成条件下测得（20 题结构化事实抽取 + 30 题写前事实验收，共 109 个候选槽位；原始汇总见 [eval/benchmark_summary.json](eval/benchmark_summary.json)）：

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

> **说明**：上述 50 题冻结验证集仅衡量本项目两项记忆子任务在相同 Prompt 合同下的结构化输出与纠错表现，不用于表征模型的通用对话或综合基准能力。

---

## 手动接入与验证（Ollama）

如果你希望在自有流水线中直接调用模型，可手动注册并运行合成校验脚本：

### 1. 从本地 GGUF 注册模型

下载 `qwen3.5-4b-memory-v2-Q8_0.gguf`（或 `Q4_K_M`）后，将其与对应 `Modelfile` 放在同一目录：

```bash
# 注册 Q8_0 版本（推荐）
ollama create qwen3.5:4b-memory-v2 -f modelfiles/Modelfile.q8_0

# 或注册 Q4_K_M 轻量版本
ollama create qwen3.5:4b-memory-v2-q4 -f modelfiles/Modelfile.q4_k_m
```

### 2. 运行公开合成样例验证

仓库内置 8 条完全虚构的公开合成测试样例（4 条事实抽取 + 4 条写前验收），拉取后可直接核验本地部署是否正常：

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
  - `num_ctx`: `16384`（常驻部署建议统一上下文长度以减少重载；显存较紧时可按硬件设为 `8192`）

---

## 适用边界与局限说明

- **专用任务模型**：本模型针对“原文分段 → 结构化事实抽取”和“候选事实对照原文 → 放行/修订/丢弃/挂起”两类后端记忆流水线任务微调，**不推荐用于开放域闲聊、创意写作或复杂数学/编程推理**。
- **遵循输入证据**：模型强依赖结构化的 `evidence` 分段 JSON 输入；建议沿用 `prompts/` 中的 System Prompt 与输入字段约定（或直接通过 [ZeroMem](https://github.com/IMLIULIAN/zeromem) 调用）以获得更稳定的格式合规率。
- **验收判定倾向**：V2 在 `pass`（忠实放行）与 `revise`（改错修订拦截）上经过重点微调；遇到与单段原文冲突的错误候选时，模型通常倾向直接返回 `revise` 并给出忠实替换文本，而非 `drop`。
- **训练方法与数据说明**：本仓库公开模型权重、推理合同、合成评测样例与验证脚本，训练数据及训练方法暂不公开。

---

## 许可证、血缘归属与生态说明

- **作者**：**B站IM榴莲 (IMLIULIAN)** · **ZeroZoneX**
- **开源协议**：本项目及其发布权重遵循 [Apache License 2.0](LICENSE)，衍生自阿里云通义千问团队开源的 [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)（Apache-2.0），详见 [NOTICE](NOTICE)。
- **配套本地引擎**：[`ZeroMem（零忆）`](https://github.com/IMLIULIAN/zeromem)（Python 零依赖单文件 SQLite/FTS5 引擎，Apache-2.0）与 [`@imliulian/dsh-zeromem`](https://github.com/IMLIULIAN/dsh-zeromem)（DeepSeek Harness 插件，AGPL-3.0）。
- **Schema 血缘与兼容致谢**：本模型事实抽取/写前审校协议中的结构化字段约定（`bank`、`type: world | experience | observation`、`occurred_start` / `occurred_end` / `mentioned_at`、`where`、`entities`）受开源项目 [**Vectorize Hindsight**](https://github.com/vectorize-io/hindsight)（MIT License）启发并保持概念/Schema 兼容，便于接入 Hindsight 兼容记忆流水线及 ZeroMem 本地引擎；本仓库不含 Hindsight 源码。
- **同名论文消歧**：配套引擎 **ZeroMem（零忆）** 是由 **B站IM榴莲 (IMLIULIAN) / ZeroZoneX** 独立开发的本地记忆引擎，与学术论文 *Zero-Mem: Zero-Token Memory Operations for LLM Agents*（Yilin Xiao et al., [arXiv:2607.29377](https://arxiv.org/abs/2607.29377), 2026 年 7 月）名称相近，但两者完全独立，无作者、代码、模型或隶属关系。
