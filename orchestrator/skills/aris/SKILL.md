---
name: aris
description: AgonReproduce mindset catalog distilled from ARIS skills, for subagent Read on demand.
---

<system-reminder>
下列引用是从 ARIS 中保留下来的 refinery mindsets。它们只能作为思维方式使用；不要把旧研究论文流程或 external-review objective 带回 AgonReproduce。

References are loaded on demand via Read under `${CLAUDE_PLUGIN_ROOT}`.

- skills_aris/problem-anchor: 锁定 target paper/case、in-scope claim、non-goals、budget 和 success condition，防止验证目标漂移。Use when reading the target brief, STATE/INVES plans, or user constraints.
- skills_aris/literature-survey: reliability landscape 调研方法：prior reproduction, correction/retraction, citation support/contradiction, artifact availability, evaluation protocol variants. Use during deep-lit and landscape work.
- skills_aris/check-quality: verification check 质量判据：claim-bound, evidence value, feasibility, cost, failure-mode coverage, false-accusation risk. Use when creating or judging checks.
- skills_aris/check-selection: 从候选 verification checks 中筛选最值得执行的检查。Use when ranking checks under budget.
- skills_aris/empirical-pilot: 轻量验证/pilot 纪律：success criterion before running, cost estimate, negative result recording. Use before scaling a check.
- skills_aris/experiment-planning: claim -> evidence -> run roadmap for STATE.md A1/A2/A3. Use when turning target claims into executable checks.
- skills_aris/pipeline-meta: 多 phase gate、checkpoint、budget、handoff 和 audit-trail 纪律。Use when orchestrating a stage pipeline.
- skills_aris/experiment-execution: 执行实验/检查的工程纪律：preflight, code reuse, sanity first, structured outputs, bounded retries. Use when implementing or running verification checks.
- skills_aris/experiment-monitor: 监控运行状态和质量信号，区分 process health 与 result quality. Use while runs are active.
- skills_aris/result-validation: claim-level evidence validation and routing: supported / partial / contradicted / not assessable / needs more evidence. Use after results land.
- skills_aris/citation-audit: source and citation audit: existence, metadata, context support, wrong-context risk. Use when citing papers, artifacts, tools, or prior evidence.
- skills_aris/paper-claim-audit: zero-context claim-to-evidence numeric audit. Use when STATE, reviewer output, or evidence dossiers contain numbers or claim verdicts backed by raw evidence.
</system-reminder>
