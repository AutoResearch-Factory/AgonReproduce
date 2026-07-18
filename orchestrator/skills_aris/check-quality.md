# Verification Check Quality

## What makes a check well formed

A verification check specifies:

1. **Claim IDs**: target claim(s) and source_refs.
2. **Evidence question**: what uncertainty this route reduces.
3. **Verification level**: metadata/artifact check, smoke reproduction, metric reanalysis, full reproduction, or domain-specific equivalent.
4. **Expected evidence**: files, manifests, logs, numbers, citations, or failure records.
5. **Allowed verdicts**: what outcomes can be concluded.
6. **Forbidden inference**: what this route cannot prove.
7. **Cost/risk**: artifacts, data, hardware, time, and false-accusation risk.

If any field is missing, the check is not executable enough.

## What makes a check good

Prioritize checks that:

- bind to important target claims,
- produce high-value evidence under current constraints,
- expose a real failure mode,
- distinguish target-claim failure from artifact/environment/system failure,
- can leave a clean trace even if the result is negative,
- reduce false-accusation risk.

Novelty is irrelevant. A check can be valuable because it verifies a boring but decisive fact.
