---
scope: case                       # case | global
case_id: ""                       # global 写 null
status: empty                     # empty | candidate | sealed
source_batch_id: ""
source_content_commit: ""
published_at: ""
---

# 当前正式训练数据

训练程序只读取本目录的四个 JSONL。这里仅保留：已经 reviewer 复核、`dataset_split=train`、当前仍获内部训练授权、没有被后续证据替换或下架的数据。dev/test/unassigned 和所有历史版本留在 `batches/`，不进入直接训练。

## 四个文件现在各有多少条

| file | rows | sha256 |
|------|------|--------|
| decision-sft.jsonl | 0 | |
| human-correction-sft.jsonl | 0 | |
| preference.jsonl | 0 | |
| verdict.jsonl | 0 | |

<!-- global scope 的 verdict.jsonl 必须始终为 0 行；case scope 按 reviewed active set 填写。 -->

## 每条当前数据从哪里来

| active sample ID | base case | split | source batch | source candidate ref | reviewer ref | source row sha256 | projection row sha256 | normalization | supersedes sample IDs |
|------------------|-----------|-------|--------------|----------------------|--------------|-------------------|-----------------------|---------------|-----------------------|

<!-- normalization 只允许 none，或给旧格式补一个空的 supersedes_sample_ids 数组；禁止修改标签或内容。 -->

## 这次没有发布哪些数据

<!-- 列出 dev/test/unassigned / rejected / uncertain / rights-blocked / superseded / deactivated IDs；不复制 secret/private payload。 -->

## 谁在什么时候发布了这一版

<!-- reviewer 全部通过后由 dispatcher 发布。先提交真实内容，再用第二次提交登记真实 content commit hash。 -->
