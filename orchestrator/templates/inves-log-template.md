# INVES Log: [slug]

<!--
inves-log.md: investigation domain 的跨 branch 持久日志.
新条目 **prepend** (时间倒序, 最新在顶部).

只记录 INVES / investigation loop:
- investigator / inves-auditor / inves-reviewer
- state_file=INVES.md 的 coder run

STATE / experiment loop 写 experiment-log.md。
-->

## [Inves Review] YYYY-MM-DD HH:MM — verdict=ready/almost/not_ready — score=N/10 (iter N)

- Report: investigations/review_iterN_YYYYMMDD_HHMM.md
- Primary concern:
- Required next checks:


## [Inves Audit] YYYY-MM-DD HH:MM — verdict=WARN/CRITICAL/BLOCKER (iter N)

- Report: investigations/audit_iterN_YYYYMMDD_HHMM.md
- Load-bearing issues:
- Required investigator response:


## [Investigation] YYYY-MM-DD HH:MM — iter N

- Focus:
- Evidence opened:
- Updates:
- Next phase:


## [Inves Run Crash] YYYY-MM-DD HH:MM — run <run-name>

- Error type:
- Root cause:
- Log path:
- Next fix:


## [Inves Run Sync] YYYY-MM-DD HH:MM — run <run-name> on <server>

- Manifest: results/<run-name>/manifest.json
- Synced workspace paths:
- Remote-only assets:
- Missing / suspect files:


## [Inves Run Collected] YYYY-MM-DD HH:MM — run <run-name> on <server>

- Wall time:
- Cost:
- Manifest: results/<run-name>/manifest.json
- Key evidence:
