# Security Policy

## Untrusted Research Artifacts

AgonReproduce may inspect and execute third-party repositories, dependencies, datasets, and model
artifacts. Treat all of them as untrusted.

Use a dedicated container or equivalent sandbox for each case. Do not expose API keys, SSH keys,
the host home directory, unrelated datasets, or hidden evaluation material. Mount inputs
read-only where possible, isolate outputs, bound CPU/GPU/memory/disk/wall time, and grant network
access only when the run requires it.

Permission-bypass flags shown in orchestration examples are intended only for an already isolated,
dedicated execution environment. They are not a substitute for isolation.

## Sensitive Data

Do not report credentials or private case data in a public issue. Before committing, inspect both
the staged diff and the complete branch history. Removing a secret in a later commit does not
remove it from Git history.

Report security vulnerabilities privately to the repository maintainers through GitHub's private
vulnerability reporting feature.
