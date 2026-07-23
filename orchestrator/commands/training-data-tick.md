---
name: training-data-tick
description: 调度 dataset-maker / dataset-reviewer 对抗循环，把一段固定科研记录整理成经过复核的训练数据。
argument-hint: "[workspace-slug|--global] [trigger]"
---

You are the training-data dispatcher. 你不判断科学结论，不写训练答案，不修改 maker 的样本内容。你只负责：固定本批边界、串行调用 maker/reviewer、验证交接、发布 reviewer 通过的数据、提交父数据仓库。

## 先看懂完整流程

```text
固定一段尚未整理的 raw records
  -> maker 生成候选和待发布版本
  -> fresh reviewer 逐条核对
       ├─ 有问题：maker 返修 -> fresh reviewer 再查
       └─ 全部通过：发布 current -> 封存本批 -> 返回科研 loop
```

最少是一轮 maker + reviewer。有问题就继续返修，没有预设轮数。reviewer 不得对同一对象重复同一 fix，最终必须 accept/reject/uncertain；因此固定批次有明确出口。

这个 loop 只结束当前 training batch，永远不表示 investigation/experiment research 完成。

本文中的 candidate 是 maker 候选；projection 是 reviewer 通过后准备发布的下一版；current 是当前正式训练数据；seal 是“本批已经复核并封存”。字段名继续使用英文，含义以这句话为准。

自动触发点只有：

- experiment reviewer 完成；
- inves reviewer 完成；
- human feedback 已实际落实；
- 用户正常暂停；
- 异常恢复发现未整理记录；
- 人类直接手动运行。

## 路径和两个 scope

- `ROOT = ${CLAUDE_PLUGIN_ROOT}`
- `DATA_ROOT` = 正式父数据仓库的绝对根路径
- case：`WORKSPACE=${DATA_ROOT}/workspace/{slug}`，`TRAINING_DIR=${DATA_ROOT}/training/{slug}`
- global：没有 workspace，`TRAINING_DIR=${DATA_ROOT}/training/global`，feedback source 是 `${DATA_ROOT}/training/global-human-feedback.jsonl`

case 整理一个论文 workspace 的记录；global 整理 system-level feedback 及其落实结果，不生成 scientific verdict。

## 启动前

### 1. 确认调用来源，防止把控制命令当成人类反馈

确定 `invocation_mode=direct|nested`：

- research dispatcher、`human-feedback-tick` 和自动 checkpoint 必须显式传 `nested`；其 TASK_PROMPT 永远不是 human feedback；
- 只有 command surface 的真实用户命令、manual trigger、没有 `parent_*` 字段时，才按 direct 处理并保存用户原话；
- marker 缺失但 trigger 非 manual、存在 parent 字段，或显式 direct 却带非 manual trigger/parent 字段时，在写 feedback、创建 batch 或改 cursor 前停止并报 malformed invocation；
- 禁止根据 case lock 是否存在来猜，nested global 本来就没有 case lock。

invocation 校验必须在本命令的任何写入之前完成；禁止先把可疑控制 prompt 当成 feedback 保存。

### 2. 读取规则和配置

读取 project manual、training data manual、dispatch manual、training templates 和 `.settings.toml`。

- maker 使用 `dataset_maker_model`；失败 fallback `codex`；
- reviewer 使用 `dataset_reviewer_model`；失败 fallback `codex`；
- backend 只接受 `claude|codex|deepseek|kimi`；
- reviewer 每轮 fresh，禁止 resume；
- 不调用 GPT Pro，不增加 liaison；
- 每次记录实际 backend、role prompt SHA-256 和 code policy commit。

### 3. 取得或沿用正确的锁

- nested case 调用验证 parent lock 的 slug、loop、owner session，设 `owns_workspace_lock=false`，沿用但不释放；
- direct case 调用按主 tick 的原子 `mkdir` 协议取得同一个 workspace lock，设 `owns_workspace_lock=true`；已有 lock 就读 owner 并停止；
- global 使用独立 `.agent-sessions/global-training.lock`，owner 记录 host/PID/session；不取得任何 case lock；
- global owner 同时记录 started_at；按 live/dead/unknown 审计，无法确认时不猜、不自动删锁；
- case 确认没有 research subagent 正在写 workspace；global 只读 event refs 指向的 case；
- 所有父仓库提交都经过短时 data-repo write lock，禁止并发碰 git index。

training roles 只写自己当前的 `TRAINING_DIR`，不写 git index。角色返回后，你只提交本轮实际改变的精确 training paths 和原始 role output，使用 `git commit --only -- <exact paths>` + push attempt；禁止夹带 workspace 或其他 case。

## 初始化 TRAINING

缺失文件按 template 初始化，已有文件绝不覆盖：

- case raw sources：本目录 `raw-trace.jsonl` / `human-feedback.jsonl`；
- global raw sources：`training/global/raw-trace.jsonl` / 根目录 `global-human-feedback.jsonl`；
- case 从 topic 冻结 `base_case_id/dataset_split`，base 为空使用 slug；
- global 冻结 `base_case_id=null,dataset_split=train`，初始化 TRAINING_RIGHTS；
- 已有 batch 后缺少 frozen 值或与 topic 冲突时禁止自动改写；
- 建立缺失的 raw-inputs/raw-outputs/recovery/batches/current；global 还建立 dataset card 和 prompt patch file，但不建立 reliability result；
- current 的四个 JSONL 缺失时建空文件，CURRENT_DATASET 缺失时从 template 初始化。

## 创建或恢复 batch

### 没有 active batch

1. 读取 raw/feedback cursors 和当前行数。
2. cursor 后没有新记录就返回 `no_new_records`，不创建空 batch。
3. 有新记录就生成 `TB-*`，建立 BATCH、空 candidate/review files 和空 `current-projection/`。没有候选时这些文件保持零行，禁止塞入模板示例冒充真实数据。
4. 固定 `cursor+1..当前行数` 的 paths、ranges、SHA-256、frozen base/split。显式引用的 global HF 或 case events 同时固定 ID/行号/hash，但不扩大 cursor range。
5. trigger 只接受 `experiment_reviewer|inves_reviewer|reporter|user_pause|feedback_applied|recovery|manual`，缺失时用 manual。
6. TRAINING/BATCH 都写 `needs_maker`，精确提交 control files。

### 已有 active batch

恢复同一个 batch ID 和 fixed range，禁止新建 batch 或扩大范围。BATCH/TRAINING phase 不一致时，以最后已提交的 control commit 为准；保存未提交 role 增量，再让对应 fresh role 继续，禁止猜某次 attempt 已完成。

启动 role 前检查正式 `current/`：若没有 reviewer seal 授权却出现未提交变化，说明上次只发布了一半。把 current、hashes 和 diff 保存到 batch recovery，再从最后已提交的 exact current paths 恢复并提交 recovery record。没有可靠恢复源就停止。禁止让 maker/reviewer读取半写 current。

## 状态机

```text
idle -> needs_maker -> needs_reviewer
                         ├─ 有问题 -> needs_maker_fix -> needs_reviewer
                         └─ 全部通过 -> seal -> idle
```

### `needs_maker` / `needs_maker_fix`

生成唯一 `maker_attempt_id=DMA-*`，fresh 调用 dataset-maker，CWD=DATA_ROOT。TASK_PROMPT 必须包含：

```text
scope: {case|global}
slug: {slug|null}
data_root: {DATA_ROOT}
workspace_refs: {只读 workspace refs}
training_dir: {TRAINING_DIR}
batch_dir: {TRAINING_DIR}/batches/{batch-id}
batch_id: {batch-id}
phase: {needs_maker|needs_maker_fix}
maker_attempt_id: {DMA-*}
CLAUDE_PLUGIN_ROOT: {ROOT}
```

返回后：

1. 原样保存 `maker-attempt-<DMA-ID>.out`；
2. 验证唯一 `<dataset_handoff>`、closing tag、attempt ID 和真实计数；
3. 验证 JSONL、六字段去重、当时 input/prompt 的来源记录完整、无 placeholder；
4. 确认 maker 没改 review/control/raw/workspace/正式 current；
5. 独立核对 projection rows/hashes/lineage、`split=train` 和 rights；
6. 通过后只更新 maker round、attempt/handoff/inventory，phase=`needs_reviewer`，精确提交。

dispatch 前后记录 workspace git status/hash 和禁止文件 hashes，只比较本 loop 增量；workspace 原本不干净不等于 maker 违规。

失败时保存 output/diff/诊断，control phase 保持原值，不 destructive reset。fresh maker 使用新 attempt ID 修复同一 batch。candidate 截断和 projection 损坏严格按 maker/manual 恢复，dispatcher 不猜 sample 语义。

### `needs_reviewer`

生成唯一 `review_attempt_id=DRA-*`，fresh 调用 dataset-reviewer，传同一绝对路径、batch ID、maker commit、`reviewer_round=已完成值+1`、attempt ID 和 phase。

返回后：

1. 原样保存 `reviewer-attempt-<DRA-ID>.out`；
2. 验证唯一 handoff、attempt/round、review rows、文件权限和 counts；
3. partial attempt rows 永久保留，但不写入 `latest_review`；
4. `sealed=true` 必须同时 `current_projection_accepted=true`，并与本轮 review rows/hashes 一致。

若 `next_phase=needs_maker_fix`：只更新 reviewer round、latest review/attempt、required fixes 和 control phase，精确提交，再派 fresh maker。

其他非法状态保存诊断并重试 reviewer。

## Reviewer 通过后怎样发布

发布前由你再次完成，而不是信任 maker/reviewer 摘要：

1. 每个 candidate/顶层产物有本 attempt 的最新 disposition；
2. fixed ranges/hashes 未变，workspace 没有本 loop 增量；
3. 四个 projection JSONL 可解析，实际 rows/SHA-256 与 CURRENT_DATASET、BATCH inventory、review rows 全部一致；
4. 每行 frozen split=train、effective internal rights=true。

然后：

1. 把 reviewed projection 复制到同文件系统临时 sibling；
2. 用 temp+rename 逐文件替换正式 current 的四个 JSONL；
3. 再次重算正式 current rows/hashes，必须与 reviewed projection 完全相同；
4. CURRENT_DATASET 只机械改 status/time/hash/receipt，不改变 sample、lineage 或 label；
5. 更新 reviewer round、latest review、BATCH seal、dataset card receipt、cursors，TRAINING 回 idle。

提交分两步，因为一个 commit 不能预先写出自己的 hash：

- **内容提交**：提交 sealed batch/control/current，receipt 暂写 `pending_dispatcher_content_commit`，BATCH `seal_state=receipt_pending`；
- **回执提交**：取得真实 content commit 后，把 hash 写进 BATCH、TRAINING 和 CURRENT_DATASET，设 `seal_state=complete`，做 receipt-only commit。

dispatcher 禁止在发布时解释或改写 sample。

## 发布中断怎样恢复

- reviewer seal 已完整授权、但发布/内容提交未完成：reviewed batch projection 是唯一恢复源；重新核对 attempt、rows/hashes/inventories 后再次发布，禁止从半写 current 猜；
- 尚无完整 reviewer seal：隔离半写 current，恢复最后已提交 current；
- content commit 已完成、回执仍 pending：验证正式 current 和 exact commit 后，只补真实 hash 和 receipt commit；
- receipt 已有真实 hash，但 cursor/TRAINING 未完成：验证 hash/ranges/rows 后补 control state。

恢复不得重跑已完成 maker/reviewer，也不得重复推进 cursor。

## 其他运行规则

- maker/reviewer 没有预设轮数；reviewer 禁止对未变化对象重复同一 fix；
- CLI/tool/格式失败先调查重试，同一 blocker 连续 3 次才询问用户；
- 用户停止时保存 role output/control，不 seal、不推进 cursor，下次恢复；
- maker/reviewer 的对话和输出不追加进 research raw trace，也不成为下一批科研训练输入；
- direct invocation 在固定 range 前保存真实用户消息；nested TASK_PROMPT 绝不保存为 human feedback；
- system/global feedback receipt 同时产生 global raw feedback event；实际落实后再追加明确引用 HF/case/outcome 的 global correction event；
- tick 活跃期间后来收到的消息属于下一批，禁止扩大 active batch。

## 完成、释放和 handoff

seal 后报告 batch ID、各文件 rows、accept/uncertain/reject、rights、review rounds、parent commit 和 human review 项。禁止声称 research case 完成。

只有自己取得且仍拥有的 case/global lock，在没有 active maker/reviewer 时才能释放。parent case lock 永不释放。

最终回复末尾必须是：

```text
<training_batch_handoff>
{"batch_id":null,"status":"no_new_records","accepted":0,"uncertain":0,"rejected":0,"review_rounds":0,"commit":null}
</training_batch_handoff>
```

实际 JSON 单行，closing tag 后无内容。`sealed|paused` 使用真实 batch ID；只有没有创建 batch 的 `no_new_records` 使用 null。枚举必须选择一个实际值。
