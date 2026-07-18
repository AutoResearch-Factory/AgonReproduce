# Execution Environments

This file defines the shared interface for execution environments. It must not contain real
hostnames, usernames, private paths, credentials, or account-specific prices.

Before assigning a remote run, read `servers.local.md` when it exists. That ignored local file
must define each available environment:

- stable label used in `STATE.md` or `INVES.md`;
- execution type, such as local, SSH, Slurm, or managed cloud;
- resource limits and current allocation policy;
- workspace and data roots;
- launch, monitor, collect, and cancel commands;
- cost rate or accounting rule;
- environment variables and shared caches;
- known operational constraints.

If `servers.local.md` is absent or does not define a suitable environment, do not invent a
hostname or path. Record the missing execution environment as a blocker and ask the user to
configure one.

Treat target-paper repositories and dependencies as untrusted. Use an isolated environment,
do not expose unrelated credentials or the host home directory, and grant network access only
when the run requires it.
