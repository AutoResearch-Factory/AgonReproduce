# AgonReproduce

[中文](README_zh.md)

AgonReproduce is a prompt-first system for auditing the reliability of research claims. It
combines literature investigation, direct experiment reproduction, independent review, human
correction, and training-data curation in one traceable workflow.

The project is under active development. Its outputs are research evidence and reliability
assessments, not automatic findings of misconduct.

## Core Workflow

```text
target paper
  -> investigation loop
  -> experiment loop
  -> investigation loop
  -> reliability report

each checkpoint
  -> raw trace + human feedback
  -> dataset maker
  -> independent dataset reviewer
  -> reviewed training projections
```

The two research loops share one case workspace but keep separate state:

- `INVES.md` records literature, artifact, benchmark, citation, scope, and other external
  reliability checks.
- `STATE.md` records direct execution, numerical reproduction, robustness tests, and experiment
  evidence.

Both loops continue until a human stops or redirects them. Reviewer readiness is a checkpoint,
not an automatic terminal state.

## Design

- **Prompt first.** Core agents and commands are Markdown prompts. Small scripts are accessories
  for state validation and output filtering.
- **Minimal protocol.** Add a rule only when omitting it causes a concrete failure.
- **Claim-level evidence.** Stable claim and evidence IDs connect investigation, experiment,
  review, and training records.
- **Separated responsibility.** Producers, auditors, reviewers, and dataset agents have distinct
  read/write boundaries.
- **Human feedback is first-class data.** Corrections from the dispatcher conversation are
  preserved with their application and outcome.
- **No automatic accusation.** Execution failure, artifact failure, environmental failure, and
  claim contradiction are different outcomes.

The current protocol is documented in
[`orchestrator/references/project_manual.md`](orchestrator/references/project_manual.md).

## Repository Boundary

This repository contains the reusable orchestration prompts and generic templates. Case material,
execution traces, human feedback, credentials, and private infrastructure configuration belong in
a separate artifact repository, conventionally named `AgonReproduce-artifact`.

The names are fixed:

- product and framework repository: `AgonReproduce`;
- private case/artifact repository: `AgonReproduce-artifact`;
- Claude Code plugin and skill namespace: `agon-reproduce`.

The lowercase namespace follows the same machine-name convention as the `Agon` repository and
its `agon` plugin namespace. It is not a second product name.

Never commit:

- `orchestrator/.settings.toml`;
- `orchestrator/references/servers.local.md`;
- API keys, tokens, SSH material, or private host details;
- unreviewed case data, model outputs, or human conversations.

## Setup

Clone `AgonReproduce`. From the public
[`AgonReproduce-artifact-template`](https://github.com/AutoResearch-Factory/AgonReproduce-artifact-template),
select **Use this template**, create a private repository, and name it
`AgonReproduce-artifact`. Do not put real cases or credentials in the public template repository.
Keep the directories side by side:

```text
.
├── AgonReproduce/
└── AgonReproduce-artifact/
```

1. Create `AgonReproduce/orchestrator/.settings.toml` from
   `AgonReproduce/orchestrator/.settings.example.toml` and select the available model backends.
2. Create `AgonReproduce/orchestrator/references/servers.local.md` if remote execution is
   required.
3. Install the required literature and writing skills listed in `project_manual.md`.
4. Start Claude Code from the artifact repository:

   ```bash
   cd AgonReproduce-artifact
   export CLAUDE_PLUGIN_ROOT="$(realpath ../AgonReproduce/orchestrator)"
   claude --plugin-dir "$CLAUDE_PLUGIN_ROOT"
   ```

5. Put a target-paper brief in `topics/<slug>.md`, then run
   `/agon-reproduce:investigation-tick <slug>` inside Claude Code.

The public defaults use the standard `claude` and `codex` CLIs. Optional `deepseek` and `kimi`
routes expect locally supplied Claude-compatible wrappers named `claude-ds` and `claude-kimi`.

## Main Commands

- `/agon-reproduce:investigation-tick <slug>` initializes the workspace and runs the investigation loop.
- `/agon-reproduce:experiment-tick <slug>` runs direct reproduction and experiment review.
- `/agon-reproduce:deep-lit-tick --scope investigation|experiment <slug>` expands the literature evidence.
- `/agon-reproduce:human-feedback-tick ...` records and applies human corrections.
- `/agon-reproduce:training-data-tick <slug> <trigger>` converts a fixed checkpoint into reviewed dataset rows.

## Security

Target-paper repositories and their dependencies are untrusted code. Run them in an isolated
environment with least privilege and no unrelated credentials. See [SECURITY.md](SECURITY.md).

## License

AgonReproduce is licensed under Apache-2.0. Some refinery prompts were adapted from MIT-licensed
projects; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
