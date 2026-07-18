# Local Execution Environments

Copy this structure to the ignored `servers.local.md` and replace every placeholder locally.
Never commit the completed file.

## local-cpu

- type: local
- resources: `<CPU count, memory, disk>`
- workspace_root: `<absolute local path>`
- data_root: `<absolute local path>`
- launch: `<command template>`
- monitor: `<command template>`
- collect: `<command template>`
- cancel: `<command template>`
- cost: `<accounting rule>`
- constraints: `<network, wall time, or concurrency limits>`

## remote-gpu

- type: `<ssh | slurm | managed cloud>`
- target: `<local SSH alias or provider label>`
- resources: `<GPU type/count, CPU, memory, disk>`
- workspace_root: `<remote path>`
- data_root: `<remote path>`
- shared_caches: `<configured cache paths>`
- launch: `<command template>`
- monitor: `<command template>`
- collect: `<command template>`
- cancel: `<command template>`
- health: `<command returning current availability>`
- cost: `<currency per resource-hour or accounting rule>`
- constraints: `<queue, network, allocation, and concurrency limits>`
