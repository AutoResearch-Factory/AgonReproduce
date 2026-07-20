<!-- Target-paper topic template. paper-id and a concrete source are required for runtime initialization. -->
---
# 目标论文/案例。填写 arXiv ID、DOI 或 internal:<case-id>；非 arXiv target 必须在正文提供可核验、可打开的全文 source，禁止只凭摘要启动 claim 审查。
paper-id: ""
title: ""
authors: []
year: ""
artifact-url: ""

# 审查优先级与预算。
audit-priority: P0
verification-budget: "small / medium / large"
expected-verification-level: "L0-desk-check | L1-cpu-probe | L2-light-gpu | L3-full-repro | L4-comprehensive"

# 人类指定的 claim。为空时 investigator 首轮从目标原文拆 I0；scientist 后续独立建立 STATE claim matrix。
target-claims: []

# 明确非目标，防止 agent 自行扩大范围。
non-goals: []

# 数据划分在第一个 training batch 前冻结。普通独立 case 的 base_case_id 留空时使用 workspace slug；
# controlled mutation / variant 必须显式填写同一个 base_case_id。held-out case 在首次运行前改成 dev/test。
base_case_id: ""
dataset_split: train                 # train | dev | test | unassigned

# 本项目运行产生的 trace 与人类反馈默认授权用于内部能力提升；具体 case 可显式关闭。
# 这不授权公开或商业发布，也不自动授权复制外部论文/数据；公开/商业 projection 必须按 refs/rights 脱敏审查。
training_rights:
  trace_trainable: true
  human_feedback_trainable: true
  public_release: false
  commercial_use: false
  redaction_required: true
---

# <target paper / case title>

## Why Audit This

<1-5 段。说明为什么这篇论文/这个案例值得审查，哪些 claim 可能重要、可疑、昂贵、影响大，或者对后续项目有依赖。>

## Human Audit Requirements

- Must check:
- Nice to check:
- Must not spend time on:
- Required artifact/source:
- Reporting expectation:

## References

[1] <Author et al.> <Title>. arXiv:<ID> / DOI:<DOI> / URL:<URL>, <Year>.
