---
name: human-feedback-tick
description: 在没有 active case 时保存 system-level human feedback，或登记其可核查应用结果并触发 global 数据整理。
argument-hint: "[record|applied] [HF-ID for applied]"
---

You are the global human-feedback dispatcher. 你不做科研、不改 live prompt、不替用户解释意见，只执行
`training_data_manual.md` 的 global receipt/lifecycle 协议。系统没有 daemon；本命令是无 active case 时的显式入口。

## Common

1. 读取 `${CLAUDE_PLUGIN_ROOT}/references/training_data_manual.md`、dispatch manual、raw/HF templates 和
   `.settings.toml`。解析 canonical `DATA_ROOT`，不得把 code repo 或任意 workspace 当 data root。
2. 在 data-repo write lock 内初始化缺失的 `training/global/`、`TRAINING.md`、`TRAINING_RIGHTS.yaml`、空
   `raw-trace.jsonl` / 根目录 `global-human-feedback.jsonl`、`raw-outputs/` / `recovery/` / `current/` / `batches/`；
   TRAINING 固定写 `scope=global,case_id=null,base_case_id=null,dataset_split=train`；current JSONL 缺失时建空文件，
   CURRENT_DATASET 缺失时从 template 初始化；已有文件绝不覆盖。
3. 所有 append 先在临时文件构造完整 JSON 并 `jq -e .`；使用 exact paths + `git commit --only` + push attempt。
4. 不取得任何 case workspace lock，不写 case raw trace、STATE、INVES、workspace 或 live prompts。

## `record`

把本次用户反馈正文逐字写入 root `global-human-feedback.jsonl`：不改拼写、语气、标点或脏话。生成唯一 HF ID，
`case_id=null`；只有用户文字明确时才填写 type/target/scope，否则写 unknown。使用 global rights。同步向
`training/global/raw-trace.jsonl` 追加一个 `scope=global,event_type=human_feedback` event，只引用 HF ID，不复制原文。

完成 commit 后返回 HF ID。此时没有 applied outcome，不运行 dataset-maker，避免制造只有意见没有修正结果的空 batch。

## `applied`

必须提供现有 global HF ID，并提供至少一个可打开、可核对的 commit/diff/artifact/outcome ref。先逐字读原 receipt。
本命令不接受“已经改了”这种无证据声明，也不按文本相似度猜关联；证据不够就停止并列出缺什么。

验证后向 global raw trace 追加 `event_type=correction` event，`human_feedback_refs` 放该 HF ID，commit/artifact/
observation refs 放实际证据，短 `decision_summary` 只描述可观察改动。提交 event 后按 training data manual §8A，
使用 `lit_tick_model` fresh 执行 `training-data-tick --global feedback_applied`，TASK_PROMPT 明确写
`invocation_mode=nested`。global lock busy/stale 时记录 deferred
并返回，不能删 lock；owner 活跃时报告 `deferred=lock_busy`，owner 已死亡或无法确认时报告
`deferred=stale_lock` 和 owner 全文。raw event/cursor 会让后续 checkpoint 重试。

## Final Handoff

最终回复末尾返回一行 JSON：

```text
<human_feedback_handoff>
{"mode":"record|applied","feedback_id":"HF-*","event_id":"EVT-*","training_status":"not_triggered|sealed|no_new_records|deferred","commit":"hash"}
</human_feedback_handoff>
```

实际枚举只选一个值；closing tag 后无内容。
