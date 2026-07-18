# Pipeline Meta

## Pipeline order

Default AgonReproduce flow:

```text
target brief -> target reading -> reliability landscape -> STATE/INVES planning -> execution/review -> reliability report
```

Each phase narrows uncertainty. Skipping a phase usually moves the error downstream.

## Checkpoints

After every phase, summarize:

- what was learned,
- what claim_ids are affected,
- what evidence exists,
- what remains unknown,
- whether the next phase is justified.

Checkpoint summaries let the user redirect and let future agents reconstruct decisions.

## Don't run downstream on unstable upstream

Do not execute runs before claim/source binding is stable. Do not write final report verdicts before evidence and failure attribution are stable.

## Gate before expensive work

Before expensive verification, confirm:

- check value,
- artifact/data availability,
- expected evidence,
- budget,
- forbidden inference.

## Document everything

Dead routes, failed runs, blocked artifacts, and inconclusive checks are report-relevant. Record why they happened and what they do or do not imply.

## Stage handoff

Every stage should leave a self-contained output file. If a stage fails, report the failure and remaining uncertainty instead of forcing the next stage.

## Harness evolution

System improvements must be log-driven, minimal, reversible, and committed. Do not add new tools or schema because they seem useful; cite observed failure modes.
