# Reliability Literature Survey

## Goal

Map the evidence environment around a target paper/case. The goal is reliability context, not new research-direction discovery.

## Sources

Use configured sources in fallback order. Skip unavailable sources instead of failing.

| Source | What to look for |
|---|---|
| Target paper/source/supplement | Claims, protocols, metrics, artifacts, data requirements |
| Local notes/PDFs | User-processed context and prior annotations |
| arXiv / publisher / DOI pages | versions, errata, official metadata |
| Semantic Scholar / OpenAlex | citing papers and citation context |
| PubPeer / corrections / retractions | community critique or formal warnings |
| GitHub / artifact pages | code/data availability, issues, commits, licenses |
| Web search | blog posts, replication notes, benchmark discussions |

## What to extract

For each relevant source:

- citation / URL / version / access date
- relation to target: supports, contradicts, reuses, critiques, corrects, merely mentions
- claim_id(s) affected
- evidence type: reproduction, extension, artifact note, metric/protocol variant, statistical critique, metadata
- strength and limitation
- whether it changes what is feasible to verify

## Search discipline

- Use multiple query formulations: title, authors, claim terms, artifact names, repo name, metric/dataset names.
- Check later papers that cite the target; classify citation role instead of treating citation count as support.
- Check artifact status directly: repo exists, data links resolve, issues mention reproducibility, license permits use.
- Distinguish peer-reviewed evidence from preprints, comments, and informal notes.

## Synthesis

Group findings by claim and failure mode:

- prior support
- prior contradiction
- artifact/data availability
- protocol ambiguity
- metric variants
- known implementation pitfalls
- unverified or unavailable areas

End with implications for verification checks: what should be checked first, what is high value, and what cannot be concluded from available evidence.
