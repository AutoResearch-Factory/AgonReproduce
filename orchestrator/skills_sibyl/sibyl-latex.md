# LaTeX Report Typesetting

## Template discipline

Use a simple report/article structure unless the user provides a template. The template must not change report semantics or hide limitations.

## Table rules

Use `booktabs`. Keep provenance columns when they matter: claim_id, source_ref, evidence_ref, manifest path, status, limitation. Do not delete traceability columns for aesthetics.

## Figure rules

Labels and captions must identify what evidence is shown, where it came from, and what it does not prove. Process all visual elements before final compilation.

## Compilation

Compile after sections, figures, tables, and references are in place. Fix undefined references/citations, missing figures, and visible placeholders before accepting the PDF.
