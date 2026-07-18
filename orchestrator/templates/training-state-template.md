---
case_id: ""                         # global scope 写 null
scope: case                         # case | global
base_case_id: ""                    # case 首次初始化后冻结；global 写 null
dataset_split: train                # train | dev | test | unassigned；首次 batch 前冻结
phase: idle                         # idle | needs_maker | needs_reviewer | needs_maker_fix
raw_trace_source: "raw-trace.jsonl"  # global: training/global/raw-trace.jsonl
human_feedback_source: "human-feedback.jsonl"  # global: training/global-human-feedback.jsonl
raw_trace_cursor: 0                 # 已封存的 raw-trace.jsonl 行数
human_feedback_cursor: 0            # 已封存的 human-feedback.jsonl 行数
active_batch_id: ""
active_trigger: ""                 # experiment_reviewer | inves_reviewer | user_pause | feedback_applied | recovery | manual
maker_round: 0
reviewer_round: 0
latest_review: ""
latest_maker_attempt: ""
latest_review_attempt: ""
---

# Training data state

本文件只控制 `training/<slug>/` 的数据整理。它不表示科研是否完成，不得修改或覆盖 STATE/INVES phase。

## Active batch

| field | value |
|-------|-------|
| batch path | |
| input raw lines | |
| input feedback lines | |
| parent loop/lock | |
| started at | |
| last actor | |

## Recovery

<!-- 写清尚未完成的 maker/reviewer 轮次、已生成文件和下一步。idle 时写 none。 -->

## Sealed batches

| batch_id | trigger | raw lines | feedback lines | accepted | uncertain | rejected | sealed commit |
|----------|---------|-----------|----------------|----------|-----------|----------|---------------|
