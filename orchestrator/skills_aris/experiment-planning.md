# Verification Experiment Planning

## Goal

Turn target claims into a claim -> evidence -> run-order roadmap.

The plan must support an honest reliability report, not a new contribution story.

## Load upstream context first

Extract:

- target paper/case and source links
- in-scope claim_ids and source_refs
- candidate verification checks
- artifacts/data/protocols/metrics required
- user constraints and budget
- forbidden inference

If claim_ids or source_refs are missing, fix topic.md or STATE.md §4.3 before planning runs.

## Freeze claims and verdict boundaries

For each claim:

- target claim text
- source_refs
- verification level
- allowed verdicts
- forbidden inference
- minimum evidence for each allowed verdict

Do not allow scientist/coder to downgrade the claim, metric, protocol, or success criterion without explicit authorization.

## Run block specification

Each run/check must specify:

- run_id
- claim_ids
- verification level
- purpose
- input artifacts/data
- exact protocol/metric
- expected evidence file(s)
- success criterion
- failure attribution plan
- resource estimate
- replay requirements

Runs may be metadata/artifact/citation/statcheck/repo-inspection/smoke/full execution. Every run still needs a manifest or equivalent evidence record.

## Execution order

Default order:

1. Source and claim binding check.
2. Artifact/data availability check.
3. Minimal protocol/metric smoke check.
4. Claim-specific reproduction or reanalysis.
5. Sensitivity/failure-mode checks only if needed.
6. Report evidence consolidation.

Prefer early checks that prevent wasted downstream work.

## Always

- Every run must answer a claim-level evidence question.
- Every failure must have attribution before it becomes report language.
- Negative results are useful; un-attributed failures are not.
- Never let a run plan imply that missing artifacts prove the target claim false.
- Reuse STATE.md constraints and existing traces; do not invent budgets or data availability.
