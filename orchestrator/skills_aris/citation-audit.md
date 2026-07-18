# Citation and Source Audit

Verify cited papers, target metadata, artifacts, tools, datasets, and prior-evidence sources.

## Dangerous problems

- **Wrong-context**: real source, but it does not support the sentence.
- **Metadata drift**: title, authors, year, version, DOI, or source URL is wrong.
- **Version drift**: arXiv/source version changed and the report silently mixes versions.
- **Artifact drift**: repo/data link exists but branch, commit, release, or license differs.
- **Phantom identifier**: DOI/arXiv/repo URL looks plausible but does not resolve.
- **Citation-role confusion**: a citing paper merely mentions the target, but report treats it as support.

## Audit layers

1. **Existence**: source exists at claimed identifier/URL.
2. **Metadata**: title, authors, year, version, publication/source, URL, commit/release match canonical records.
3. **Context**: source actually supports the report sentence.
4. **Role**: support / contradiction / critique / reuse / mere mention / artifact metadata.

## Verdicts

- `KEEP`: clean and context-appropriate.
- `FIX`: metadata or source pointer needs correction.
- `REPLACE`: wrong-context; find a source that actually supports the sentence.
- `REMOVE`: hallucinated or unsupportable source.
- `SOFTEN`: source exists but evidence is weaker than sentence.

Wrong-context is more dangerous than metadata typo. A real paper used for a false support claim can corrupt the report.

## Rules

- Do real lookup when possible; do not memory-pattern-match.
- Distinguish peer-reviewed evidence, preprints, informal comments, repo issues, and metadata.
- Never mutate citations that require human approval; propose exact fix and reason.
- If online verification is unavailable, mark `UNCERTAIN` with what was checked.
