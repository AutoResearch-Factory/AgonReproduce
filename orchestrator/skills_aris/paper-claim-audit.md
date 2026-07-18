# Claim Evidence Audit

Zero-context evidence audit: verify that every number, status, and claim-level verdict in STATE, reviewer output, or an evidence dossier matches raw evidence.

## Why zero-context

The same system may execute checks and summarize findings. That creates confirmation bias: rounding numbers upward, reporting best seeds as averages, citing the wrong config, or upgrading `PARTIAL` to `SUPPORTED`. A fresh reviewer catches this by comparing claim statements to raw evidence only.

## Core principle

The auditor receives claim statements (`STATE.md`, reviewer blocks, evidence dossiers, run manifests) and raw evidence (`results/`, manifests, logs, tables, traces). It does not rely on executor summaries or prior conversation.

Question: does the claim statement describe the evidence truthfully and precisely?

## Failure modes

- **Number inflation**: report number differs from raw evidence beyond standard rounding.
- **Best-seed cherry-pick**: report claims average/typical result but cites best run.
- **Config mismatch**: reported comparison uses incompatible data, protocol, metric, or hyperparameters.
- **Aggregation mismatch**: report says N runs/seeds but evidence shows a different count.
- **Delta error**: relative or absolute improvement arithmetic is wrong.
- **Table/dossier mismatch**: table, summary row, or dossier entry says more than the evidence supports.
- **Scope overclaim**: summary generalizes beyond in-scope claims.
- **Verdict overclaim**: weak evidence becomes `SUPPORTED` or failed execution becomes `CONTRADICTED`.

Rounding rule: only standard rounding to displayed precision is allowed.
