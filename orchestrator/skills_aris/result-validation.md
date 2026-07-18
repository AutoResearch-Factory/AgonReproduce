# Result Validation

## Goal

Judge whether observed evidence supports a claim-level verdict and what should happen next.

## Collect evidence

Gather:

- run manifests,
- raw result files,
- logs,
- metric outputs,
- artifact/citation/metadata check records,
- STATE.md success criteria,
- STATE claim table.

## Reviewer input

For each claim provide:

- claim_id and source_refs,
- verification level,
- expected evidence,
- observed evidence,
- protocol/metric alignment,
- failed or blocked runs,
- known confounds,
- failure attribution draft.

## Verdict fields

- **claim_verdict**: SUPPORTED / PARTIAL / CONTRADICTED / NOT_REPRODUCIBLE / NOT_ASSESSABLE / OUT_OF_BUDGET.
- **what_evidence_supports**: exact supported statement.
- **what_evidence_does_not_support**: forbidden inference and remaining uncertainty.
- **failure_attribution**: agent/code/artifact/data/resource/metric/protocol/target-claim/unknown.
- **missing_evidence**: specific gaps.
- **next_action**: rerun, debug, narrow verdict, ask user, or report.
- **confidence**: high / medium / low.

## Integrity check

If audit reports a CRITICAL issue, downgrade confidence to low until fixed. Do not round `partial` up to `SUPPORTED`; do not round execution failure up to `CONTRADICTED`.

## Route by verdict

- `SUPPORTED`: report with evidence refs and limitations.
- `PARTIAL`: report supported subset; list gaps.
- `CONTRADICTED`: only if evidence chain is complete and alternative explanations are handled.
- `NOT_REPRODUCIBLE`: system did not reproduce; state failure attribution.
- `NOT_ASSESSABLE`: artifacts/data/protocol/access are insufficient; do not imply claim false.
- `OUT_OF_BUDGET`: resource-constrained non-verdict; state budget.

## Rules

- Evidence first, interpretation second.
- Reviewer judges support; executor supplies paths and observations.
- Always record negative and inconclusive results.
- Every final statement must be traceable to evidence_refs.
