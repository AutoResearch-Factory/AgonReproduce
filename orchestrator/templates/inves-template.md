---
inves_phase: needs_deeplit      # needs_deeplit | needs_investigator | coding_and_running | needs_auditor | needs_reviewer
inves_iter: 0                   # investigator 维护; auditor/reviewer 使用当前值命名报告
latest_inves_audit: ""          # 最新 inves-auditor 报告路径
inves_audit_verdict: ""         # WARN | CRITICAL | BLOCKER
latest_inves_review: ""         # 最新 inves-reviewer 报告路径
inves_review_verdict: ""        # ready | almost | not_ready
inves_review_score: ""          # 0-10, reviewer 维护
---

<!--
========================================================================================
INVES.md —— investigation domain 的可靠性审查状态与计划文件
========================================================================================

读者：investigator / inves-auditor / inves-reviewer / investigation-tick / investigator-owned coder。

INVES.md 只记录 investigation domain：文献关系、artifact/data/benchmark 异常、cherry-pick、overclaim、
适用边界、后续论文支持/反驳、社区复现/issue、investigator-owned runs。

INVES.md 是第一阶段的完整调查状态，不读取后续 experiment domain 的 STATE.md。它先为目标论文 claim
建立稳定 C ID；scientist 进入实验后读取并复用。

这个 loop 不宣布 done。investigator 根据当前 INVES / 本域 results / audit / review / deep-lit/wiki
判断下一轮该查什么。新 workspace 首轮先跑 needs_deeplit,
由 deep-lit-tick 直接根据 topic.md 搜索并写 landscape.md, 然后 investigator 再消费这些 source。

只有 bounded CPU/API 静态取证需要 coder 时, investigator 才在 I4/I5 加 run。核心方法/协议执行、
weights、inference、任何模型拟合/训练和 GPU 只在 I1/I2 记 `not assessed: experiment evidence required`, 不进 I5。
investigator-owned coder 只写 INVES.md, 不写 STATE.md。

investigator 直接调用 deep-lit-reader 精读关键论文；需要系统性文献搜索、引用/反引文扫盘和
大规模补证据时, 在 I4 写清检索问题并设置 inves_phase: needs_deeplit。
-->

# INVES: [slug]

> 一句话：当前 investigation domain 最重要的可靠性风险轴和下一步。

## I0. Claim Decomposition

| claim_ref | claim text / implied claim | source_ref | stated scope | possible overclaim / ambiguity | investigation checks |
|-----------|----------------------------|------------|--------------|--------------------------------|-----------------|

<!-- investigator 首轮填写并为目标论文显式 claim 分配稳定 C<number>；后续 scientist 原样复用。
implicit generality/overclaim 等 investigation-only claim 使用 IC<number>。同 ID 必须绑定同一核心 claim
text/source_ref，不得重编号。 -->

## I1. Investigation Questions

| question_id | 问题 | 为什么影响可靠性 | 当前状态 |
|-------------|------|------------------|----------|

## I2. External Reliability Findings

| finding_id | question_id | evidence_refs | strength | implication | next_action |
|------------|-------------|---------------|----------|-------------|-------------|

strength: confirmed / plausible / speculative。含义分别是已核实 / 有证据但仍需确认 / 只是线索。
只是线索的内容只能触发下一步检查, 不能写成 target paper 的确定缺陷。

## I3. Audit Findings / Investigator Response

| audit issue | investigator response | action/evidence | status |
|--------------|-----------------------|-----------------|--------|

## I4. Next Investigation Actions

| priority | action | owner | completion evidence |
|----------|--------|-------|---------------------|

## I5. Investigator Runs

<!-- investigator 初始化 run 行, investigator-owned coder 维护运行字段。所有 investigator run name 必须以 `inves_` 开头, 输出写入 `results/inves_<...>/`, 避免和 STATE.md scientist run 覆盖。collected 表示证据链已同步/登记完整；保留 collected 行作为 manifest 索引和调度历史。-->

### Task Groups

<!--
### Task Group X: <name>

- runs: [inves_run_a, inves_run_b]
- can_split: true/false
- depends_on: none / [inves_run_x]
- priority: P0/P1/P2
-->

### Run Specs

<!--
### Run: inves_<run_name>

- Task Group:
- Owner: investigator
- Purpose: protocol_probe / artifact_audit / data_audit / citation_probe / robustness_test / cherry_pick_probe / overclaim_probe / external_validity_probe
- Cost tier: L1
- Compute cost cap: dollars + CPU-minutes
- Prior gate evidence: L0 exact source refs
- Claim IDs:
- Investigation question IDs:
- Source / artifact / repo / benchmark:
- Expected evidence path: results/inves_<run_name>/manifest.json
- Success criterion:
- Failure interpretation:
- Forbidden inference:
- Priority:
- Server:
- remote_dir:
-->

### Runs

| run | owner | purpose | server | remote_dir | launched_at | session_id | crash_count | phase |
|-----|-------|---------|--------|------------|-------------|------------|-------------|-------|

Per-run phase: `needs_impl` -> `queued` -> `running` -> `needs_sync` -> `collected` (or `needs_fix` -> `queued`)

## I6. Investigator Coder Notes

<!-- investigator-owned coder 写临时卡点/旁注。investigator 消化后删除或整合进 I2/I4/I5。 -->

## I7. External Reliability Review

<!-- inves-reviewer 每次送审后整体替换本节摘要；完整 review 存在 investigations/review_iter*.md。 -->

| version | verdict | score | primary concern | next action |
|---------|---------|-------|-----------------|-------------|
