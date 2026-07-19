---
name: server-health
description: Inspect configured execution environments before assigning or monitoring a run.
---

Read `${CLAUDE_PLUGIN_ROOT}/references/servers_manual.md` and, when present,
`${CLAUDE_PLUGIN_ROOT}/references/servers.local.md`.
When `${CLAUDE_PLUGIN_ROOT}/skills/server-health/SKILL.local.md` exists, read it for the
machine-specific health commands.

Use the health command recorded for each configured environment. Report only facts returned by
those commands: availability, queue state, CPU/GPU/memory capacity, active jobs, and last update
time. Do not invent unavailable measurements.

Choose an environment that satisfies the run specification, budget, data locality, and resource
requirements. When no environment qualifies, report the exact blocker instead of silently
changing the experiment.
