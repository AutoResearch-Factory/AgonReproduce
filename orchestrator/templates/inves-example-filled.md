---
inves_phase: needs_deeplit
inves_iter: 2
latest_inves_audit: investigations/audit_iter2_20260703_1210.md
inves_audit_verdict: CRITICAL
latest_inves_review: investigations/review_iter1_20260703_1300.md
inves_review_verdict: almost
inves_review_score: 6
---

<!-- 示例文件，只演示 INVES.md 写法。论文、数字、路径均为占位示例，不代表真实审查结果。 -->

# INVES: example-paper-audit

> 一句话：investigation 风险集中在 Widget-5 split/preprocessing 是否被后续工作复用，以及作者 artifact 缺 config 是否已被社区报告。

## I0. Claim Decomposition

| claim_ref | claim text / implied claim | source_ref | stated scope | possible overclaim / ambiguity | investigation checks |
|-----------|----------------------------|------------|--------------|--------------------------------|-----------------|
| EXT-C1 | ExampleNet 在 Widget-5 上优于强基线 | paper:Table2 | Widget-5 reported split | split seed / preprocessing 不清时, 读者可能误解为任意 Widget-5 split 都稳健 | 查后续引用是否复用同一 split; 查 repo issue; 查独立 baseline parity 证据 |
| EXT-C2 | artifact 足以复现主表 | paper:AppendixA; repo:README | released checkpoint + script | README 没列 normalization/config, 可能只是部分 artifact | repo inspection; issue search; author follow-up |

## I1. Investigation Questions

| question_id | 问题 | 为什么影响可靠性 | 当前状态 |
|-------------|------|------------------|----------|
| Q1 | 后续论文是否独立复现 Widget-5 数字? | 独立复现能区分 artifact 缺口和 paper claim 本身 | needs_deeplit |
| Q2 | repo issue 是否报告 preprocessing/config 缺失? | artifact 缺失会影响 C1/C2 failure attribution | coding_and_running |

## I2. External Reliability Findings

| finding_id | question_id | evidence_refs | strength | implication | next_action |
|------------|-------------|---------------|----------|-------------|-------------|
| F1 | Q2 | repo:issue-17; result:results/inves_repo_issue_audit/manifest.json | plausible | config 缺失更可能解释 R1 mismatch | 做引用/反引文扫盘确认独立复现情况 |

## I3. Audit Findings / Investigator Response

| audit issue | investigator response | action/evidence | status |
|--------------|-----------------------|-----------------|--------|
| [INV-MAJOR-001] Q1 还没有覆盖引用图 | Accept | request investigation deep-lit | open |

## I4. Next Investigation Actions

| priority | action | owner | completion evidence |
|----------|--------|-------|---------------------|
| P0 | deep-lit-tick --scope investigation 找独立复现/失败复现 | dispatcher | lit-feed.md unprocessed entries |
| P0 | repo issue snapshot + config gap manifest | investigator/coder | results/inves_repo_issue_audit/manifest.json |

## I5. Investigator Runs

### Task Groups

### Task Group A: artifact issue audit

- runs: [inves_repo_issue_audit]
- can_split: false
- depends_on: none
- priority: P0

### Run Specs

### Run: inves_repo_issue_audit

- Task Group: A
- Owner: investigator
- Purpose: artifact_audit
- Claim IDs: [EXT-C2]
- Investigation question IDs: [Q2]
- Source / artifact / repo / benchmark: https://github.com/example/example-method/issues
- Expected evidence path: results/inves_repo_issue_audit/manifest.json
- Success criterion: saved issue snapshot and exact evidence for/against missing preprocessing/config reports
- Failure interpretation: no issue found does not prove artifact completeness; it only weakens the community-report signal
- Forbidden inference: cannot conclude paper claim wrong from missing issue alone
- Priority: P0
- Server: local
- remote_dir: workspace/example-paper-audit

### Runs

| run | owner | purpose | server | remote_dir | launched_at | session_id | crash_count | phase |
|-----|-------|---------|--------|------------|-------------|------------|-------------|-------|
| inves_repo_issue_audit | investigator | artifact_audit | local | workspace/example-paper-audit | 2026-07-03 11:30 | local-shell | 0 | collected |

## I6. Investigator Coder Notes

No open coder notes.

## I7. External Reliability Review

| version | verdict | score | primary concern | next action |
|---------|---------|-------|-----------------|-------------|
| 1 | almost | 6/10 | 后续引用与 artifact issue 已有初步证据, 但缺直接失败复现和邻近 split 检查 | 补 cited-by sweep 和 inves_repo_issue_audit |
