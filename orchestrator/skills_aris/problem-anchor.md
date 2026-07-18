# Problem Anchor

## Why anchor

An audit project drifts easily: a target claim becomes a broader paper judgment, a missing artifact becomes an accusation, or a verification check becomes a new research project. Carry the same anchor through every round.

## What to anchor

Before planning or executing, freeze:

- **Target**: paper/case title, source links, artifact links, and user-provided audit brief.
- **In-scope claims**: claim_id, claim text, and source_refs.
- **Non-goals**: claims not covered, judgments not allowed, unsupported accusations to avoid.
- **Constraints**: compute, data access, time, tools, artifacts, and user instructions.
- **Success condition**: what evidence would make the current audit route useful, even if the result is negative or inconclusive.

Copy these into STATE.md, run specs, and report material.

## When input is too vague

If the topic file lacks a target paper/case, source links, or audit scope, stop and ask for the missing target information. Do not invent a target or broaden the project into open-ended literature work.

## Drift detection

Flag drift if a later change:

- changes the target claim being evaluated,
- downgrades the metric/protocol without authorization,
- turns an execution failure into a claim verdict,
- changes `NOT_ASSESSABLE` into `CONTRADICTED`,
- expands a scoped report into a full paper-level judgment.

Adapt the route or plan, not the target claim.
