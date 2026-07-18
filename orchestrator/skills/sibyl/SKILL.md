---
name: sibyl
description: AgonReproduce persona catalog distilled from Sibyl prompts, for subagent Read on demand.
---

<system-reminder>
下列引用是从 Sibyl 中保留下来的 refinery personas。它们只能服务 reliability audit、STATE/INVES planning、evidence review 和 report integrity；不要加载旧 external-review objective。

References are loaded on demand via Read under `${CLAUDE_PLUGIN_ROOT}`.

- skills_sibyl/sibyl-check-design: verification-check 构思视角：理论/机制、跨方法移植、跨领域证据来源。Use when generating audit checks.
- skills_sibyl/sibyl-debate: 多视角证据辩论：contrarian, signal extractor, statistical skeptic, landscape comparativist, strategist. Use when judging results or report verdicts.
- skills_sibyl/sibyl-methodology: falsification-first experiment design and method audit. Use when designing or auditing verification checks.
- skills_sibyl/sibyl-critique: report and evidence critique: structural flaws, claim/evidence mismatch, section-level review. Use when reviewing reports holistically.
- skills_sibyl/sibyl-judgment: backward reasoning from failed results + engineering realism. Use when reassessing hypotheses or feasibility.
- skills_sibyl/sibyl-latex: LaTeX/report typesetting discipline for tables, figures, references, and compilation.
- skills_sibyl/sibyl-experiments: execution discipline for reliable remote experiments/checks.
- skills_sibyl/sibyl-landscape: reliability landscape and prior-evidence mapping.
- skills_sibyl/sibyl-common: common conventions: budget, remote-server discipline, traceable outputs, git safety.
- skills_sibyl/sibyl-reflection: issue classification, fix tracking, and multi-perspective synthesis for audit pipelines.
</system-reminder>
