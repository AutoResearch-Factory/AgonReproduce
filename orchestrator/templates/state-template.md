---
phase: needs_scientist                # dispatcher 状态机: needs_scientist | coding_and_running | needs_auditor | needs_reviewer | needs_litfeed
version: 0                            # 当前送审次数, reviewer 维护
iteration: 0                          # 当前迭代号, scientist 维护
route: ""                             # 当前技术路线 (同 git branch)
git_branch: main                      # main | route/<name>
gpu_dollars_equivalent: 0.00          # 等效美元, coder 维护
latest_audit: ""                      # 最新 auditor 报告路径, auditor 维护
audit_verdict: ""                     # WARN | CRITICAL | BLOCKER, auditor 维护
---

<!--
========================================================================================
STATE.md —— experiment domain 的直接实验复现状态与计划文件
========================================================================================

读者：人类用户（做战略决策）+ agent（写代码跑验证）。

原则：
1. 新人友好：你的默认读者是第一天来的实习生——聪明但什么都不知道。写每一段之前，先对自己说一遍"我们到底在审查什么，为什么"。比喻、对比、流程图/示意图、"简单来说"比术语堆砌好 100 倍。
2. 言简意赅：重要信息只在最合适的地方出现一次，不反复讲，不遗漏。
3. 自包含：读完这一个文件 → 能指导下一步直接复现实验 + 能重写成诚实可靠性报告的 direct-reproduction 部分。investigation 部分在平级的 INVES.md。
4. 两层结构：前半部分给人读（战略），后半部分给 agent 读（执行）。没有中间层。

Experiment-domain 计划就在本文件 A1/A2/A3, 不使用单独 plan 文件。对应历史在 experiment-log.md / git；平级的 investigation-domain 状态与历史在 INVES.md / inves-log.md。
使用中文书写正文。Thinking 用 English。
-->

---

# 项目名：xxx

> 一句话：审查哪篇论文/哪个案例，当前最重要的可靠性判断是什么。

## 1. 目标与背景

### 1.1 目标论文/案例

| 字段 | 内容 |
|------|------|
| Paper/case id | ... |
| Title | ... |
| Source | arXiv / DOI / OpenReview / GitHub / benchmark report / internal |
| Artifact | code / data / model / config / none / unknown |
| Topic | `topic.md` |
| Landscape | `landscape.md` |

### 1.2 必要背景

<!-- 用最白的话。2-3 段，每段 ≤5 句。新人读完就知道这篇论文声称解决什么、为什么值得审查。 -->

### 1.3 核心概念

<!-- 只列本审查用到的，每个一句话。 -->

| 概念 | 一句话解释 |
|------|-----------|
| ... | ... |

### 1.4 审查问题

<!-- 目标 claim（1 句）→ 为什么重要（1 句）→ 当前最可能的风险/不确定性（1 句）。-->

## 2. 验证全景

### 2.1 验证流程

<!-- mermaid flowchart：论文 claim → artifact/source → checks/runs → evidence → verdict。
     节点粒度：每个语义阶段（读论文 / 获取资产 / 执行 / 指标 / 归因 / 报告）一个节点。
     不要画成方法创新流程。 -->

### 2.2 证据标准

| 检查/指标 | 含义 | 如何计算或判断 | 支持哪些 claim |
|-----------|------|----------------|----------------|
| ... | ... | ... | ... |

### 2.3 验证矩阵

<!-- 所有检查一行一个。状态用 OK / WARN / FAIL / BLOCKED / TODO。 -->

| 检查 | 问题 | 层级 | 数据/资产 | 状态 | 当前信号 |
|------|------|------|-----------|------|----------|

## 3. 资产、代码与环境

### 3.1 资产状态

| 资产 | 来源 | 路径/URL | manifest | 状态 |
|------|------|----------|----------|------|
| ... | ... | ... | `data/MANIFEST.md` | available / missing / suspect |

### 3.2 代码地图

<!-- "想知道 X → 打开 Y → 看 Z"。不是文件列表。 -->

| 想知道... | 文件 | 函数/类 |
|----------|------|--------|
| ... | `src/...` | `xxx()` |

### 3.3 计算环境

<!-- 瓶颈在哪，一个样本多久，完整检查多久。 -->

## 4. 当前证据

### 4.1 已完成检查

| 检查 | 记录数/样本数 | 关键数字或事实 | 结论 |
|------|--------------|----------------|------|

### 4.2 关键警告

<!-- 什么东西不对劲，需要在报告里诚实处理，或需要加验证。 -->

### 4.3 Claims 速查

<!--
目标论文显式 claim 必须复用 INVES I0 已建立的稳定 C<number>。experiment-only 执行/
metric/implementation 子 claim 使用 EC<number>。同 ID 必须绑定同一核心 claim text/source_ref，且永不重编号。
source_refs 指向目标论文/案例原文位置。
evidence_refs 用 commit: / run: / result: / log: / trace: / audit:。
entailment 复制 latest audit/review 的保守判定。
failure_attribution 必须区分 paper claim wrong / artifact broken / environment mismatch / missing data / metric mismatch / our bug / insufficient budget / unknown。
-->

| claim_id | 目标 claim | source_refs | verification_level | evidence_refs | entailment | failure_attribution | 强度 |
|----------|------------|-------------|--------------------|---------------|------------|---------------------|------|
| C1 | ... | paper:§x/table-y | L1/L2/L3 | commit:abcdef1; run:results/run-a/manifest.json; trace:results/run-a/trace.jsonl | UNTESTED / SUPPORTED / PARTIAL / CONTRADICTED / NOT_REPRODUCIBLE / NOT_ASSESSABLE / OUT_OF_BUDGET | ... | 够 / 弱 / 不够 |

## 5. 战略决策（人类决定）

<!--
⚠️ 这一章只有人类用户能写。任何 agent（包括 scientist/auditor/coder/reviewer）都不能在这里加内容——它们只能读、遵循、在 A1 里实现。
这是人类用户的最高指令区。写在这里的任何验证方向、技术判断、优先级排序, agent 必须无条件执行。

如果人类要求 agent 写入, 则要一字不差(verbatim)地写入, 即便是更改拼写错误和语病都得告知人类!

Agent 规则：
- auditor：每次审计第一项检查——§5 里的指令被执行了吗？没执行 → BLOCKER。
- scientist：每轮读 §5 → 逐条确认状态 → 在 plan 里体现。
- coder：读 §5 → 确认自己要实现的东西和人类指令一致。
- dispatcher：不读 §5。dispatcher 只按 phase 路由。
-->

<!-- 示例：
- 最高优先：先验证 C1 的核心数字能否用作者 artifact 跑出来。找不到数据就记录 missing，不准假装复现。
- Claim 永远不许为了结论好看而降级。证据不足就标 PARTIAL / NOT_ASSESSABLE，不许把原 claim 改弱后声称 supported。
- 不准 cherry-pick seed。不准事后改 success criterion。不准把我们的 implementation bug 算成论文失败。
- 如果 artifact 缺关键配置，先做最小询证和 issue 追踪，再决定是否进入 independent implementation。
-->

- ...

## 6. 下一步行动

| 优先级 | 行动 | deadline | 完成标志 |
|--------|------|----------|----------|
| P0 | ... | ... | ... |

### 6.1 报告框架速览

<!-- reliability report 打算分几节，每节写什么。3-5 行，人话。 -->

---

## 自检清单（提交前必做，7/7 通过才能 commit）

1. 闭眼 30 秒，一句话说出目标论文/案例和当前可靠性判断。说不出来 → §1 没写好
2. 搜任一术语在 §1 首次出现处，有没有用一句话解释它是什么。没有 → 补
3. §1.2 超过 15 行？→ 你在写综述，删
4. 遮住核心概念表，任选一词能用大白话解释给外行吗？不能 → 删掉这个词或补解释
5. 任选 §2-§6 连续 3 句话，实习生读到会问"这跟审查 claim 有什么关系"？会 → 重写
6. 任选一段删掉，实习生仍能理解审查状态？能 → 删掉
7. `wc -l STATE.md` > 400？→ 删到 ≤400，不许挪到 A 段绕过

# Agent 执行层

<!--
以下给 agent 读。人不需要逐行看但应能看懂。
唯一 coder session 按 A1 写代码 → 部署/并行管理远端 runs → 维护 A3 Runs 表 → crash 时写 ad-hoc 诊断段。
-->

## A0. Audit Response

<!--
scientist 维护。每轮 scientist 必须逐条回应 latest_audit 中的 BLOCKER / CRITICAL / MAJOR。
不要改 auditor report；只在这里写 response / action / evidence。
下一轮 auditor 会检查这些回应是否充分，以及 coder 是否真的落实。
-->

| audit issue | scientist response | action/evidence | status |
|-------------|--------------------|-----------------|--------|

## A1. Experiments-to-do

<!-- scientist 维护。STATE.md 只放 experiment-domain direct-reproduction run；investigator-owned run 放 INVES.md I5。
     以 Task Group 组织——dispatcher 读 group + server health 后决定唯一 coder 本轮接哪些 run。
     can_split: true  → group 内 run 互相独立，coder 在不同环境并行推进
     can_split: false → group 内 run 有依赖/共享资源，coder 按依赖顺序推进
     depends_on:      → 这个 group 必须等另一个 group 跑完
     不想操心细节时，每个 run 放一个单 run group 就是退化情况，dispatcher 自己处理。 -->

### Task Group A: [一句话描述]

- runs: [run-a1, run-a2]
- can_split: true
- depends_on: none
- priority: P0

### Run: [run-name]

<!-- scientist 写 Plan，scientist-owned coder 执行。每个 run 必须写明所属 Task Group——不然 dispatcher 无法关联。-->

- Task Group: A/B/C/...（必填）
- Owner: scientist（必填；旧行缺省按 scientist 处理）
- Purpose: reproduction / baseline / ablation / artifact_reproduction / data_reconciliation / robustness_test / smoke / metric_audit
- Claim IDs: [C1, C2]（匹配 §4.3）
- Verification level: static / smoke / direct reproduction / full reproduction
- Cost tier: L1 / L2 / L3 / L4
- Prior gate evidence: exact INVES/result/source refs
- Advances: 回答什么问题，对应 §4.3 哪些 claim
- Config / procedure: 命令行参数或人工检查步骤
- Input assets: data/checkpoint ids or exact paths from `data/MANIFEST.md`
- Expected outputs: `results/<run-name>/manifest.json`, key result files/logs/traces, remote-only assets if any
- Allowed verdicts: SUPPORTED / PARTIAL / CONTRADICTED / NOT_REPRODUCIBLE / NOT_ASSESSABLE / OUT_OF_BUDGET
- Forbidden inference: 这个 run 不允许推出什么
- Failure attribution plan: 如何区分 paper claim wrong / artifact broken / environment mismatch / missing data / metric mismatch / our bug / insufficient budget / unknown
- Priority: MUST-RUN / NICE-TO-HAVE
- Compute cost cap: dollars + CPU/GPU-hours
- Server: primary + fallback
- remote_dir:
- Success criterion: 硬判据（事后不改）
- Failure interpretation: 如果失败/空，说明什么
- Risk: OOM / 数据 / 兼容性 / 资产缺失

### 代码改动

<!-- 跨所有 Task Group 的代码改动写在这里。per-run 的改动写在对应 Run 的 Config/Input assets 字段里。-->

## A2. 验证详细规格

<!-- 每个检查/实验的完整技术规格。agent 写代码时的参考。-->

### E?: [Name]

- 模型 / 数据 / 超参 / seeds
- 对比系统（reported artifact / baseline / ablation / independent implementation）
- 输入资产、输出文件与 source 路径
- 结果（关键数字，带 source）
- 失败归因规则

## A3. Runs

<!-- scientist 初始化 run 行，scientist-owned coder 维护运行字段。investigator run 不写这里, 只写 INVES.md I5。scientist run name 禁止使用 `inves_` 前缀。collected 表示证据链已同步/登记完整；保留 collected 行作为 manifest 索引和调度历史。-->

| run | owner | purpose | server | remote_dir | launched_at | session_id | crash_count | phase |
|-----|-------|---------|--------|------------|-------------|------------|-------------|-------|

字段责任：

| 字段 | scientist 初始化 | coder 维护 |
|------|------------------|------------|
| `run` | ✓ | — |
| `owner` | ✓ | — |
| `purpose` | ✓ | — |
| `server` | ✓ | 切 server 时改 |
| `remote_dir` | ✓ | 切 server 时改 |
| `launched_at` | 空 | ✓ |
| `session_id` | 空 | ✓ |
| `crash_count` | `0` | ✓ crash +=1 |

Per-run phase: `needs_impl` → `queued` → `running` → `needs_sync` → `collected`（或 `needs_fix` → `queued`）

## A4. 环境

| 服务器 | GPU | 显存 | 远程路径 | HF_HOME | 注意 |
|--------|-----|------|----------|---------|------|

```bash
# server-side dry-run / smoke test in the selected workspace
uv run python scripts/xxx.py --config conf/xxx.yaml --dry-run

# server-side lint + test
uv run ruff check . && uv run pytest
```

## A5. 运行历史

| 时间 | 实验 | 事件 | 备注 |
|------|------|------|------|

## A6. 已知问题与修复

| 问题 | 根因 | 修复 | 状态 |
|------|------|------|------|

<!--
ad-hoc 诊断段（coder 遇到对应触发条件时临时 insert，scientist 分析后删除）：

| 段名 | 谁写 | 触发 |
|------|------|------|
| `### 卡点` | coder | crash 判代码问题或无法推进。root-cause-first：已确认事实 / 已排除假设 / 最可能根因 / 最小下一步 / 禁用的替代 |
| `### Coder 旁注` | coder | 每次完成代码或扫描后：做了什么 / 困难 / 疑惑 / 对 plan 的建议 |
| `### 疑似调度问题` | 任一 agent | 怀疑 dispatcher 状态机 bug 而非实验 bug |
-->

<review score="X.X" date="YYYY-MM-DD">

由 reviewer 填写。最近一轮可靠性评审，旧 review 整体替换不堆叠。

</review>
