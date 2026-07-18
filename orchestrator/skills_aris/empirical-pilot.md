# Verification Pilot

## Why pilot

Pilots reduce execution risk before a larger verification run. A pilot may be a metadata check, artifact smoke test, metric parser check, small-data reproduction, or one-seed run.

## Before launching

- Estimate cost before running.
- Define success criterion before seeing output.
- Define allowed verdicts and forbidden inference.
- Identify what evidence file or manifest will be written.

## Reading pilot results

- Positive pilot: route may scale, but do not overstate evidence strength.
- Negative pilot: diagnose root cause before treating it as claim evidence.
- Blocked pilot: record artifact/data/environment limitation explicitly.

Null and negative pilots are useful if they leave clear evidence and failure attribution.
