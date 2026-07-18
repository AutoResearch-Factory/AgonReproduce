# Verification Check Selection

## Axes

Evaluate each candidate check on:

- **Claim importance**: does this affect a central target claim?
- **Evidence value**: would the result change report confidence?
- **Feasibility**: are required artifacts/data/tools available?
- **Cost**: time, compute, human intervention, specialized environment.
- **Failure-mode coverage**: what ambiguity does it resolve?
- **False-accusation risk**: could failure be misread as target paper failure?

Eliminate checks whose required artifacts are unavailable unless the check's purpose is to document that unavailability.

## Selection

Prefer a small check set that covers distinct claim/failure modes. Do not run five similar smoke checks while leaving source binding or metric mismatch unchecked.

## Devil's advocate

For every survivor ask:

- What result would this check actually justify?
- What alternative explanation would remain?
- What evidence file would prove we executed it correctly?
- If it fails, what must we avoid saying?

Record rejected checks and why; they become useful report context.
