# AgonReproduce 训练数据手册

本手册规定 investigation / experiment 运行时如何把科研过程保存为可核查、可训练的数据。它只定义数据生产和整理，不改变两条科研 loop 的职责，也不授予任何科研 Agent 自行停止的权限。

## 0. 三分钟读懂整个机制

### 科研 loop 和数据 loop 不是一回事

investigation 和 experiment 负责做科研，它们一直运行，只有人类能叫停。

dataset loop 只整理一段已经发生的历史。它不继续查论文、不跑实验、不改变科学判断。整理完这一批后，它立刻把控制权还给原科研 loop。

```text
科研角色工作一段时间
  -> domain reviewer 评价当前版本
  -> training-data dispatcher 固定这段历史
  -> dataset-maker 整理候选训练数据
  -> fresh dataset-reviewer 回原始记录核对
       ├─ 有问题：maker 返修，fresh reviewer 再查
       └─ 全部通过：发布 current，封存本批
  -> 原科研 loop 从原 phase 继续
```

### 什么时候运行 dataset loop

它不在每个 auditor 后运行，只在一个完整 checkpoint 运行：

1. inves reviewer 完成；
2. experiment reviewer 完成；
3. human feedback 已经被实际落实；
4. 用户正常暂停；
5. 异常恢复发现记录尚未整理；
6. 人类手动触发。

### maker 和 reviewer 要转几轮

最少一轮：

```text
1 次 maker + 1 次 reviewer
```

reviewer 发现问题时再走：

```text
maker 修正 + 另一轮 fresh reviewer
```

没有固定轮数。固定批次中的每条数据最终必须进入 `accept/reject/uncertain`，reviewer 不能对没有变化的对象重复同一个 fix，所以数据 loop 有明确出口。它结束的是本批数据整理，不是科研。

### 三层数据分别是什么

| 位置 | 人话含义 | 是否会改 |
|------|----------|----------|
| raw trace / human feedback | 真实发生过什么，人类原话是什么 | 只追加，不覆盖 |
| `batches/<id>/` | maker 候选、reviewer 判断和完整历史 | 封存后不改 |
| `current/` | 目前经过复核、仍有效、允许直接训练的数据 | 新 batch 通过后整体更新 |

旧训练样本后来被证明错误时，不删除旧 batch。新 batch 写明替换或下架理由，并从 `current/` 移除旧样本。这样既不丢历史，也不会继续训练已经失效的标签。

### 四类正训练数据

| 数据 | 学什么 |
|------|--------|
| decision SFT | 在当时状态下，下一步应该做什么 |
| human correction SFT | 原行为收到人类纠正后，正确改法是什么 |
| preference | 面对同一目标，哪个行为更好 |
| verdict | 给定 claim 和 evidence，四个可靠性字段怎样判断 |

证据不足、权限不允许、未来信息泄漏或关联错误的数据不进入正训练文件，而是保留在 `rejected.jsonl` 供审计。

### 常见英文名词

| 字段/旧称 | 本手册中的实际意思 |
|-----------|--------------------|
| batch | 本次固定下来准备整理的一段记录 |
| candidate | maker 生成、尚未通过 reviewer 的候选数据 |
| current projection | reviewer 通过后准备发布的下一版正式训练数据 |
| current | 当前正式训练数据 |
| seal | 本批已复核并封存 |
| supersede | 新训练样本替换旧训练样本 |
| deactivation tombstone | 一条带证据的旧样本下架记录 |
| provenance | 这条数据来自哪些 event、文件和 commit |
| disposition | reviewer 对一条对象的处理结果 |

### 后面的内容怎么读

- §1-§7：原始 trace 和 human feedback 怎样可靠落盘；
- §8：什么时候切一批数据、怎样自动触发；
- §9-§13：maker/reviewer 怎样生成和复核训练数据；
- §14-§15：格式、Git 和中断恢复。

下面开始精确执行规则。Agent 必须按需读完相关章节；人类理解正常机制时，先读完本节即可。

## 1. 最高原则

1. investigation loop 和 experiment loop 永远不自行停止。训练批次只是截取一段历史，不代表研究完成。
2. Human feedback 是最高优先级的学习信号。dispatcher 先逐字落盘，再解释、转发或执行。
3. 原始记录只追加，不覆盖。后来的纠正通过 ID 指回旧记录。
4. Agent 不保存隐藏 chain-of-thought。只保存可审计的简短决定、候选行动、理由、预期和反证条件。
5. dataset-maker 不能认证自己的标签。每个批次必须由 fresh dataset-reviewer 对抗审查。
6. 未知字段写 `null`、空数组或 `unresolved`，禁止猜值补齐格式。
7. 训练输入只包含行动发生前真正可见的材料。后来获得的答案只能放在 target、outcome 或 label provenance。
8. Prompt 和模板优先。当前层不新增数据库、服务、daemon 或专用数据整理程序。

## 2. 数据放在哪里

训练数据写在父数据仓库，不写进 nested workspace git：

```text
AgonReproduce-artifact/
└── training/
    ├── global-human-feedback.jsonl
    ├── global/
    │   ├── TRAINING.md
    │   ├── TRAINING_RIGHTS.yaml
    │   ├── raw-trace.jsonl
    │   ├── raw-outputs/
    │   ├── recovery/
    │   ├── DATASET_CARD.md
    │   ├── prompt-patch-candidates.md
    │   ├── current/
    │   │   ├── CURRENT_DATASET.md
    │   │   ├── decision-sft.jsonl
    │   │   ├── human-correction-sft.jsonl
    │   │   ├── preference.jsonl
    │   │   └── verdict.jsonl
    │   └── batches/
    └── <slug>/
        ├── TRAINING.md
        ├── raw-trace.jsonl
        ├── human-feedback.jsonl
        ├── raw-outputs/
        ├── raw-inputs/
        ├── recovery/
        │   └── <dispatch-id>.txt-or-json
        ├── reliability-result.json
        ├── DATASET_CARD.md
        ├── prompt-patch-candidates.md
        ├── current/
        │   ├── CURRENT_DATASET.md
        │   ├── decision-sft.jsonl
        │   ├── human-correction-sft.jsonl
        │   ├── preference.jsonl
        │   └── verdict.jsonl
        └── batches/
            └── <batch-id>/
                ├── BATCH.md
                ├── decision-sft.jsonl
                ├── human-correction-sft.jsonl
                ├── preference.jsonl
                ├── verdict.jsonl
                ├── rejected.jsonl
                ├── review.jsonl
                ├── recovery/
                └── current-projection/
                    ├── CURRENT_DATASET.md
                    ├── decision-sft.jsonl
                    ├── human-correction-sft.jsonl
                    ├── preference.jsonl
                    └── verdict.jsonl
```

这样做有三个实际原因：

- investigation 和 experiment 共用同一个训练历史；
- experiment 切换、合并或放弃 `route/*` 时，不会丢失 human feedback 和 raw trace；
- dispatcher 能在父仓库中立即提交原始记录，不需要修改科研 workspace 的 STATE/INVES ownership。

所有相对路径都以父数据仓库根目录为基准。dispatcher 必须解析这个 repo 的绝对 `DATA_ROOT`，并把绝对 `TRAINING_DIR=<DATA_ROOT>/training/<slug>` 传给 subagent，不能依赖 subagent CWD。`training/<slug>/` 与 `workspace/<slug>/` 一一对应。没有 active case，或人类消息明确作用于整个系统时，写 `training/global-human-feedback.jsonl`，不随便借用某个 case。`training/global/` 是这些反馈及其后续应用结果的独立转换 lane；它不是论文 workspace，不产生 scientific verdict 或 reliability result。

## 3. 谁写什么

| 角色 | 必须产生的内容 | 禁止事项 |
|------|----------------|----------|
| investigation / experiment dispatcher | dispatch 客观信息、prompt/model/policy 版本、状态前后 hash、subagent 原始输出及其 `learning_record`、human feedback 原文 | 不替科研角色编造理由、preferred behavior 或结论 |
| scientist / investigator | 在最终回复中返回关键决策 `learning_record` | 不直接写 training 目录 |
| shared coder | 在最终回复中返回执行结果 `learning_record` | 不把执行失败解释成论文 verdict；不直接写 training 目录 |
| auditor | 在最终回复中返回因果审计 `learning_record` | 不把自己的判断冒充 known answer；不直接写 training 目录 |
| domain reviewer | 在最终回复中返回正交 reliability fields 和 review `learning_record` | 不把 0-10 readiness score 当可靠性真值；不直接写 training 目录 |
| deep-lit tick | 返回本轮 source discovery/read/integration 摘要，由外层 dispatcher 记录 | 不直接写 training 目录 |
| dataset-maker | 读取 raw records，生成批次训练文件、待审 current projection、case reliability projection、dataset card 和 prompt patch candidates | 不修改 canonical current、科研 evidence、STATE、INVES、results、audits、review/control files、git index 或 live prompts |
| dataset-reviewer | 逐条写 `accept/fix/reject/uncertain` 审查结果 | 不替 maker 静默改样本；不修改 candidate、control、科研文件或 git index |
| training-data dispatcher | 固定 batch range，调度 maker/reviewer，保存角色原始输出，独占更新 BATCH/TRAINING，并在 seal 时原样发布 reviewed current projection | 不生成/修改 sample 语义，不把整理过程追加进 research raw trace |

research raw/feedback JSONL 只有 dispatcher 追加。dataset-reviewer 是当前 batch `review.jsonl` 的唯一 writer；dataset-maker 是 unsealed candidate files 的唯一 writer。research dispatcher 只允许在文件不存在时从模板初始化 TRAINING.md；首次 batch 开始后，training-data dispatcher 是 BATCH/TRAINING 的唯一更新 writer。

## 4. 稳定 ID

ID 使用可读前缀和全局足够唯一的时间/随机后缀，不依赖数组序号：

```text
dispatch: DSP-<UTC timestamp>-<short suffix>
event:    EVT-<UTC timestamp>-<short suffix>
feedback: HF-<UTC timestamp>-<short suffix>
batch:    TB-<UTC timestamp>-<short suffix>
sample:   S-<UTC timestamp>-<short suffix>
review:   DR-<UTC timestamp>-<short suffix>
reject:   RJ-<UTC timestamp>-<short suffix>
```

同一 unsealed candidate 被 reviewer 修正时保留原 ID；sealed sample 后来被新证据纠正时，新版本另建 ID，并用 `supersedes_sample_ids` 指向旧 sample。旧 batch 不改，canonical current 排除被 supersede ID。

## 5. 原始事件

每次重要 dispatch 完成后，dispatcher 向 `training/<slug>/raw-trace.jsonl` 追加一行。重要事件包括：

- scientist / investigator 的路线决定；
- coder 的执行或阻塞结果；
- auditor 的因果审计；
- reviewer 的机器判断；
- deep-lit 的一轮大规模 source 补充；
- human feedback 的接收、应用和验证；
- loop 切换、用户暂停和训练批次 checkpoint。

dispatcher 负责客观字段：role、model、prompt path/hash、policy commit、task prompt、时间、可见输入 ref、STATE/INVES 前后 hash、输出 ref、commit 和成本。科研角色负责 `learning_record` 里的语义字段。

dispatcher 在删除临时 `$OUT` 前，先把它逐字复制到 `training/<slug>/raw-outputs/<dispatch-id>.*`。raw event 的 `subagent_output_ref` 指向该文件。原始输出不直接视为训练样本，但 dataset-maker/reviewer 必须能回到它核对角色摘要、human feedback 和后续 target；禁止只保存 Agent 自己压缩后的 learning record。

训练 input 还必须可重建。tracked workspace 文件由 `state_before.workspace_commit + path + sha256` 固定；本轮明确提供、但不能由该 commit 重建的 load-bearing text/config/log，dispatcher 在 subagent 启动前复制到 `training/<slug>/raw-inputs/<DSP-ID>/before/`，在 `state_before.snapshot_refs` 记录路径和 hash。大 artifact 不复制，记录 immutable content hash/manifest ref。只写可变路径而没有 commit、snapshot 或 content hash，不算可重建 context。

原始事件遵循 `orchestrator/templates/raw-event-template.jsonl`。不知道 token 或 GPU 成本就写 `null`，不能估算后冒充实测值。`raw-trace.jsonl` 只追加；若一行后来被证明错误，追加 correction event。

## 5A. Dispatcher 怎样保存每次科研调用

investigation-tick 和 experiment-tick 必须逐步执行本节，不得各自发明另一套格式。

### A. Case 初始化

拿到 canonical slug 和 workspace lock 后，dispatcher 在父数据仓库执行：

1. 解析父数据仓库绝对路径 `DATA_ROOT`，设 `TRAINING_DIR=<DATA_ROOT>/training/<slug>`，创建它、`raw-outputs/`、`raw-inputs/`、`recovery/`、`current/` 和 `batches/`。current JSONL 缺失时建空文件，CURRENT_DATASET 缺失时从 template 初始化；已有 current 不覆盖。
2. `TRAINING.md` 不存在时从 `training-state-template.md` copy，把 `case_id` 改成 canonical slug；从 topic 读取 `base_case_id/dataset_split`，base 为空时固定为 canonical slug，并写入 TRAINING。dataset split 只接受 `train/dev/test/unassigned`。一旦创建首个 batch，这两个值永久冻结；topic 后来变化只报告 mismatch，不回写历史。旧 TRAINING 缺字段且 cursors=0、没有 batch 时按 topic 补齐；已有 batch 时停止并要求人类明确一次 migration，不能根据现有样本猜 split。存在的其他字段不覆盖。
3. 确保 `raw-trace.jsonl` 和 `human-feedback.jsonl` 存在；已有内容只读/追加，不截断。
4. 从 `workspace/<slug>/topic.md` 读取 `training_rights`；workspace 尚未初始化时读 `topics/<slug>.md`。字段缺失写 `null`，不把 topic template 的默认值或自己的推断改成授权。
5. 保存启动当前 tick 的人类消息 receipt，再继续 env validation/bootstrap/dispatch。

初始化只能写父仓库 `training/<slug>/`，不能创建或修改 STATE/INVES。恢复时先读现有 TRAINING/cursors，不能重新 copy 模板。

global lane 首次需要时初始化 `training/global/`：从同一 state template 建 `TRAINING.md`，设 `scope=global`、`case_id=null`、raw source 为 `training/global/raw-trace.jsonl`、feedback source 为 `training/global-human-feedback.jsonl`；从 `global-training-rights-template.yaml` 建 `TRAINING_RIGHTS.yaml`，并把其中 `base_case_id=null,dataset_split=train` 冻结进 global TRAINING。同时创建 `raw-outputs/`、`recovery/`、`current/` 和 `batches/`，按相同规则初始化 canonical current；已有文件绝不覆盖。global lane 不创建 workspace、STATE、INVES 或 reliability result。

父数据仓库可能同时服务不同 slug。任何 parent 文件 append/add/commit/push 前，必须用原子 `mkdir .agent-sessions/data-repo-write.lock` 获取短时全局 write lock，并写 owner/session/timestamp；已有 lock 时等待并读取 owner，不能并发碰 git index。只在当前 append 和 parent commit/push attempt 完成后核对 owner 并释放，绝不持锁等待科研 subagent。异常留下的 stale lock 先审计 owner 和 parent git 状态，禁止盲删。

### B. 收到人类消息

active dispatcher 收到每条用户消息后，任何解释、回复、转发或新 dispatch 之前：

1. 生成稳定 `HF-*` ID 和递增 `message_order`。
2. case-level 消息写 `training/<slug>/human-feedback.jsonl`；明确针对整个系统的消息写 `training/global-human-feedback.jsonl`，`case_id=null`。首次写 global receipt 前，在 data-repo write lock 内按本手册 global 初始化规则创建缺失的 `training/global/`、空 `raw-trace.jsonl` 和根目录空 `global-human-feedback.jsonl`；已有文件不覆盖。
3. `verbatim_text` 使用用户消息原文。dispatcher 不改字、不摘要、不翻译。
4. 仅在文字明确时填 message type/target/scope；否则用 `unclassified/unknown`。target event 暂不明确时 `receipt_status=pending_link` 和空数组。
5. 先在临时文件生成完整一行，用 `jq -e .` 验证，再一次性 append；禁止 `echo` 拼接未转义 JSON。active case 同时向该 case 的 raw trace 追加一个 `actor_role=dispatcher/event_type=human_feedback` event，`human_feedback_refs` 只放本 HF ID，不重复改写原文。system/global receipt 还必须向 `training/global/raw-trace.jsonl` 追加 global feedback event；若当时有 active case，该 global event 用 ref 指向 case event，不能复制科研内容。完全没有 active case 时仍有 global receipt + global event，不能只存 receipt。
6. 在 data-repo write lock 内只 add 本次 receipt、对应 feedback event 和首次初始化文件，检查 staged paths；存在无关 staged 内容时不改、不提交它们，使用 `git commit --only -- <本次精确路径>`。本地 commit 成功后立即尝试 push，然后才处理消息。没有 remote 或 push 失败时明确记录 `push_pending` 并继续，不能假装已 push，也不能让网络问题阻止人类的紧急指令。

如果用户要求立即终止，仍先落盘 receipt，然后不再启动新 subagent。当前已有 subagent 的停止方式按原 loop 规则处理；训练整理不能阻止紧急停止。

本协议从一个正在运行的 dispatcher/command 收到消息时开始；系统没有后台 daemon，完全没有进程运行且后续 session 也看不到的消息不可能被 prompt 自动捕获。没有 active case 但需要记录 system feedback 时，使用 `human-feedback-tick record` 作为 active global dispatcher。恢复只能补当前 session 可见消息；不可见历史明确记 provenance gap，不能声称已捕获。

global feedback 被实际应用、拒绝或验证后，执行者所在 dispatcher 同时向 case raw trace 和 global raw trace 追加 correction/outcome event；global event 只保存 HF ID、case event ref、应用动作和 outcome ref。这样反馈原话、旧行为、修正和结果能在后续 global batch 中闭合。只承诺“以后会改”不算 applied。

“applied”不靠 dispatcher 对文本相似度的猜测。只有以下任一可观察条件成立才写 lifecycle event：负责角色的 `learning_record.human_feedback_refs` 明确包含该 HF ID，且 state_after/commit/artifact/outcome ref 证明动作发生；或 dispatcher 自己完成了一条纯机械、可由 commit/diff 直接核对的用户指令。缺 HF ID、只有口头承诺、或行动可能来自独立推理时不关联；让后续 auditor/人类明确验证后再追加 event。无 case 的 system prompt/harness 修正由 `human-feedback-tick applied <HF-ID>` 写 global outcome event。

### C. 每次 subagent dispatch 前

生成 `DSP-*` ID，并记录：

- dispatcher session 和实际 actor role；
- subagent session ID，以及现有 Claude/Codex trace 能提供的稳定 `native_trace_refs`；
- 实际 backend/model（fallback 后写真实值）；
- code repo 当前 commit 作为 policy version；
- role/command prompt path 和 SHA-256；
- verbatim TASK_PROMPT；
- 当时真正提供给角色的 visible refs；
- nested workspace 当时的 git HEAD；STATE/INVES/topic/landscape 等 load-bearing 文件的 before SHA-256；
- 每个 visible ref 的重建方式：tracked 文件记录 workspace commit；不能从该 commit 重建的本地 load-bearing text/config/log 在启动 subagent 前复制进 `raw-inputs/<DSP-ID>/before/` 并记录 snapshot ref/hash；大 artifact 记录 immutable hash/manifest；
- 本轮明确转发的 human feedback IDs。

所有 role TASK_PROMPT 必须附：

```text
training_dir: <absolute DATA_ROOT>/training/<slug>（父数据仓库，只读；禁止写）
relevant_human_feedback_refs: [本轮真实 ID；没有则 []]
```

auditor/reviewer 必须读相关 raw events 和 feedback receipts；其他角色按本轮 refs 使用，不能自行把 human feedback 当 scientific truth。

### D. subagent 返回后

严格按顺序执行：

1. 记录 command exit status 和结束时间。失败也必须留下 raw event。
2. 在删除临时 `$OUT` 前，将其逐字复制为 `training/<slug>/raw-outputs/<DSP-ID>.out`。禁止清洗、覆盖或只存摘要。
3. 先按实际 backend 取得 normalized final message：Claude/`claude-*` 的 `$OUT` 是 JSON wrapper，使用 `jq -r '.result'` 读取最终回复并同时读取真实 session/usage 字段；Codex `--output-last-message` 的 `$OUT` 是纯文本，直接读取。原始 wrapper/text 仍保持不变。然后检查 normalized final message 恰有一个 `<learning_record>`，提取标签之间的单行 JSON 并用 `jq -e .` 验证；再检查 `record_type` 与 actor role相符；review record 还必须满足 experiment-reviewer -> `assessment_domain=experiment`、inves-reviewer -> `assessment_domain=investigation`。experiment 每个 profile 的 `source_domain_verdict` 必须是对应 STATE 7 值之一；investigation 每个 profile 必须为 JSON `null`。closing tag 必须是 normalized final message 的最后一个非空白内容。检查所有枚举字段都选了单个合法值；任一枚举字段仍含模板分隔符 `|` 时拒绝该 record，不能只验证 JSON syntax 和 `record_type`。普通摘要或 command 字符串中的 shell pipe 不适用这条检查。
4. learning record 缺失/损坏但科研输出有效时，要求同一个 subagent 只补交 record，把补交原文另存 `<DSP-ID>-record-repair.out`；dispatcher 禁止替它编写。补交仍失败则把本 dispatch 标为 failed，按原 subagent failure 规则重试新的 dispatch。
5. 重读 load-bearing 文件并记录 after workspace git HEAD、after SHA-256、真实 commit refs、artifact/evidence refs 和可实测成本。learning record 引用、但不能从 after commit 或 immutable artifact ref 重建的非 git outcome text/config/log，复制到 `raw-inputs/<DSP-ID>/after/` 并写 `state_after.snapshot_refs`；没有这类文件就写空数组。`state_before/state_after` 的 commit、refs、hashes、snapshot refs 必须能区分，不拿 after 文件冒充 before context。
6. 按 `raw-event-template.jsonl` 在临时文件生成一行，`jq -e .` 通过后一次性 append 到 raw trace。科研角色语义只来自原 learning record；dispatcher 只补客观字段。
7. 在 data-repo write lock 内只 add 本次 raw event、raw output、raw input snapshots、record repair 和首次初始化文件；检查 staged paths，并用 `git commit --only -- <本次精确路径>` 避免夹带其他会话。local commit 后立即尝试 push；push 失败记录 `push_pending`，不丢 event、不阻塞科研 loop。
8. 确认 parent commit 后再删除 `/tmp/$OUT` / prompt 临时文件。

若 `$OUT` 不存在，raw event 的 `subagent_output_ref=null`；若 learning record 不存在，写空对象并把 `subagent_exit_status=failed`。不能因为调用失败就让这段训练信号消失。

`native_trace_refs` 只链接现有 session 中可见的 message/tool/action/observation 事件。dataset-maker 不提取、依赖或训练隐藏 chain-of-thought；没有稳定 native trace ref 时写空数组，不猜本机路径。

### E. Dispatcher 自己改变状态

dispatcher 直接进行 phase handoff、loop switch、user pause 或 recovery 时，也追加 `actor_role=dispatcher/event_type=checkpoint` 的 raw event，`learning_record={}`，记录 before/after refs 和原因。它不为自己的机械路由编造 candidate actions。

### F. 恢复

启动/恢复时先完成三项核对：

1. 当前会话可见用户消息是否都已有 HF receipt；按 `message_order` 补缺。
2. `raw-outputs/` 中是否存在没有对应 raw event 的 dispatch output；存在则恢复 event，不重复跑科研角色。`raw-inputs/<DSP-ID>/` 存在但没有 output/event 时，记录一次 interrupted-before-result recovery event 并保留 snapshot；loop state 仍需要该角色时用新 DSP ID fresh dispatch，不把旧 snapshot 冒充新调用 input。
3. raw trace 与 human-feedback JSONL 是否逐行可解析。若且仅若存在一个因中断造成的无效最后尾行：在 data-repo write lock 内先把整个原文件逐字保存为 `recovery/<UTC>-<filename>.corrupt` 并记录 SHA-256，再把 canonical JSONL 重写为全部可解析的完整前缀，最后追加一个 recovery event（feedback 文件损坏时 event 写 raw trace），指向 corrupt snapshot/hash 和被丢弃的无效字节范围。无效尾字节不是有效历史记录；允许这样显式修复，但禁止静默 truncate。中间坏行、多个坏行或无法证明是 interrupted tail 时停止并询问用户，不能 append 到坏文件后面。

旧 transcript 不可访问时记录 provenance gap。恢复完成前不能声称 trace/human feedback 完整。

## 6. 科研角色的 learning_record

每个科研 subagent 的最终回复末尾必须包含且只包含一个：

```text
<learning_record>
{一行合法 JSON}
</learning_record>
```

`</learning_record>` 后只允许空白，禁止再写总结、签名或解释。

具体字段见 `orchestrator/templates/learning-record-template.md`。这是 decision summary，不是完整思维过程。模板里的 `a|b|c` 是枚举说明；角色实际输出必须选一个值，不能原样复制整串。

只记录影响科研路线或判断的动作。普通读文件、格式修复、机械同步不制造伪决策样本。若本轮没有关键决策，仍返回与角色相符的 execution/audit/review record，并把不适用字段写空；禁止编造 2-3 个虚假候选行动。

dispatcher 检查 JSON 可解析、字段与角色相符，再把它嵌入 raw event。缺失或损坏时，要求同一个 subagent 只补交 learning record；不得由 dispatcher 猜测补写。

## 7. Human feedback

### 7.1 立即保存

active dispatcher 收到人类消息时，先把原文追加到 `training/<slug>/human-feedback.jsonl`，再做其他动作。如果没有 active case，或消息明确作用于整个系统，则追加到 `training/global-human-feedback.jsonl`。

`verbatim_text` 必须逐字保留。不要改拼写、语气、语言、标点或脏话。Agent 的理解另写在 `agent_interpretation`；两者绝不能混为一段。

active loop 中的人类消息都保存，但并非每条都自动成为正负偏好标签：

- 明确指令、纠正、禁止、偏好、认可和事实主张是候选训练信号；
- 普通问题只记录，不强行推断 preferred behavior；
- 人类沉默不代表认可；
- 对科学事实的反馈是高优先级线索，仍需 evidence 才能成为科学真值；
- 对目标、优先级、角色边界和工作方式的反馈，人类是最终权威。

receipt 只保存人类原话和当时能确定的客观关联。dispatcher 仅在文字明确时填写 `message_type`、`target_role` 和 `authority_scope`；否则分别写 `unclassified` / `unknown`。`is_training_signal` 不确定时必须写 `unknown`。receipt 不写 Agent 对反馈的解释和 preferred behavior；dataset-maker 后续在 correction 或 preference 样本中另写，并保留 `human_feedback_refs`。

暂时找不到被纠正事件时，`receipt_status=pending_link`、`target_event_ids=[]`。先保存，后关联。

### 7.2 应用与验证

dispatcher 原文转发给负责修正的角色，不扩写。`human-feedback.jsonl` 的 receipt 行写入后永远不改，也不重复写同一个 `feedback_id`。修正、验证、撤销或 supersede 发生时，在 `raw-trace.jsonl` 追加新的 correction/feedback lifecycle event，并用 `human_feedback_refs` 指向原 receipt。dataset-maker 由这些 event 推导当前状态，不能原地抹掉历史。

dataset-maker 后续建立：

```text
错误/旧行为 -> human feedback 原文 -> 修正行为 -> commit/result -> 后续是否有效
```

只有确有 chosen/rejected 对比时才生成 preference。只有实际执行修正后才生成 correction target；仅仅承诺 “会改”不能成为 chosen answer。

## 8. 训练批次

科研 loop 连续运行；训练数据按 checkpoint 分批。checkpoint 包括：

- domain reviewer 完成一个 version；
- 用户要求暂停或切换科研 loop；
- 重大 human feedback 已被实际应用；
- dispatcher 从异常中恢复并发现未封存记录。

`TRAINING.md` 保存两个 append-only 输入的行号 cursor。新批次只处理 cursor 之后的记录；迟到 feedback 会作为新行进入下一批，仍能通过 ID 指向旧事件。

case lane 的两个 inputs 是本 case raw trace/feedback；global lane 的 inputs 是 global raw trace 和根目录 global feedback。case event 明确引用 global HF 时，batch 额外固定对应 receipt 的 ID/行号/hash；global event 指向旧 HF 或 case event 时同理。显式引用用于 provenance，不改变 cursor range，也不允许扫描未引用反馈替当前 case 下结论。

批次状态：

```text
idle -> needs_maker -> needs_reviewer -> needs_maker_fix -> needs_reviewer -> sealed
```

`sealed` 只说明当前训练批次每条样本已有去向，不说明科研完成。封存后 `TRAINING.md` 回到 `idle`，科研 loop 继续。中断时保留 active batch 和 cursor，下一次恢复同一批，禁止重做后制造重复样本。

一个批次允许零条 accepted 样本。maker 必须解释为什么没有可靠 target，reviewer 核对后仍可封存；禁止为了让文件非空而制造候选、偏好或强标签。

`TRAINING.md.phase` 只表示当前是否有 active 整理工作，所以取 `idle/needs_maker/needs_reviewer/needs_maker_fix`。`batches/<batch-id>/BATCH.md.status` 记录单个批次归档状态，在相同三个 active 状态外增加 `sealed`。封存时先把 BATCH 置为 `sealed`，再推进 cursors 并把 TRAINING 置回 `idle`。

BATCH/TRAINING 只由 training-data dispatcher 写。maker/reviewer 各自用唯一 attempt ID 返回 handoff；dispatcher 验证 role output、允许文件 diff 和 JSONL 后才递增 completed round 并改变 phase。role 中断留下的 partial files/rows 保留审计，但没有被 `latest_*_attempt` 引用就不代表一次完成轮次。fresh maker 去重并修复 unsealed candidate；fresh reviewer 用新 attempt ID 重审，不能把中断 attempt 的 partial rows 当 disposition。fresh reviewer 在独立形成当轮判断前不读未被 `latest_review` 引用的 partial rows，避免中断 attempt 锚定新审查。

maker 中断造成 JSONL 尾行截断时，fresh maker 先把整个损坏文件逐字保存到 batch `recovery/`，再保留逐行可解析的完整前缀并从 fixed inputs 重建尾部；中间损坏或多个坏行必须报 blocker。dispatcher 不替 maker 猜 sample 语义，损坏快照永不进入正训练文件。

`current-projection/*.jsonl` 是 derived view，不适用“保留有效前缀”。任一 projection 文件损坏时，maker 必须把整套 projection、各文件 hash 和诊断保存到 batch `recovery/`，然后只从 canonical current、有效 candidates/rejections 和有效 review rows 全量重建。损坏 projection 永远不能成为 active-set provenance。

两阶段 seal 的恢复 marker 必须持久写在 BATCH frontmatter：第一阶段前设 `seal_state=receipt_pending,sealed_content_commit=pending_dispatcher_content_commit` 并随 sealed content 提交；第二阶段写真实 content hash、设 `seal_state=complete`。不能把 pending 状态只放在内存、临时 prompt 或 lockfile。

training-data loop 与两条科研 loop 使用同一个 `.agent-sessions/loop-locks/<slug>.lock`。从科研 dispatcher 内部触发时沿用并验证 parent lock；直接运行时按同一原子协议获取 lock。它与科研 subagent 串行，不并发写。global lane 使用独立 `.agent-sessions/global-training.lock`，不占用论文 workspace lock；所有 lane 的 parent git 写入仍经过同一个短时 data-repo write lock。

## 8A. 科研 dispatcher 什么时候自动整理数据

research dispatcher 只在下列节点触发训练整理：

1. 写启动 receipt 前分别记录 case/global 既有 phase/cursors/line counts，形成两个 prestart backlog flags；workspace/bootstrap 完成、首个科研 subagent 前，只有启动消息到来前已经存在 active batch 或 cursor backlog 的 lane 才 trigger=`recovery`。本次启动消息留给后续正常 checkpoint，不能仅因刚写了一条“启动 loop”receipt 就制造零信息 recovery batch；
2. experiment-reviewer event 完整落盘后，trigger=`experiment_reviewer`；
3. inves-reviewer event 完整落盘后，trigger=`inves_reviewer`；
4. human feedback 被实际执行并产生 correction/outcome event 后，trigger=`feedback_applied`；
5. 用户正常暂停，在 pause receipt/checkpoint event 落盘后，trigger=`user_pause`。

立即终止不启动 maker/reviewer；先保存 feedback/event，下一次 recovery 补做。普通 role 返回、只收到尚未落实的意见、或训练 batch 自己封存都不递归触发新 batch。

每个 lane 的 prestart flag 必须按同一公式计算，不能只看 phase：

```text
prestart_backlog =
  phase != idle
  OR active_batch_id != ""
  OR raw_trace_cursor < raw_trace_line_count
  OR human_feedback_cursor < human_feedback_line_count
```

source 文件不存在时对应 line count 为 0。deep-lit/investigator/scientist/coder/auditor 普通返回不立即切 batch 是刻意设计：等待 domain reviewer 才能把 decision -> execution -> audit -> outcome 放进同一 fixed batch；raw trace 已经逐事件提交，不会因延迟转换而丢失，异常由 recovery、正常中断由 user_pause 兜底。

每次 checkpoint 必须在没有 active research subagent 时串行执行。case lane 沿用 parent workspace lock，TASK_PROMPT 传 lock path、owner 全文和 parent dispatcher session；training child 验证后不得释放它。global lane 另取 global lock。一个 checkpoint 同时有 case/global 新记录时，先 case、后 global，不能并行启动两个 maker/reviewer loop。

科研 dispatcher 按 `lit_tick_model` 和 dispatch manual fresh 执行 `${ROOT}/commands/training-data-tick.md`：

```text
完整执行 training-data-tick: <slug|--global> <trigger>。
invocation_mode: nested
data_root: <absolute DATA_ROOT>
parent_loop_lock: <case lock path or null>
parent_lock_owner: <case owner file verbatim or null>
parent_dispatcher_session: <session id>
CLAUDE_PLUGIN_ROOT: <absolute ROOT>
```

所有 nested TASK_PROMPT 必须显式传 `invocation_mode=nested`，child 不得把控制 prompt 当 human feedback；用户直接从 command surface 运行时由入口设 `direct` 并保存真实用户消息。marker 缺失时，只有可验证的顶层用户命令、manual trigger、无任何 `parent_*` 字段才可按 direct 处理；trigger 非 manual 或存在 parent 字段就必须在写 feedback 前停止。显式 direct 与非 manual trigger/parent 字段组合也非法。不能用 parent lock 是否为 null 推断，因为 nested global checkpoint 本来就没有 case lock。

子命令 output 必须 exit 0、非空；按 §5A D 的 backend 规则先规范化 Claude JSON wrapper / Codex text，再确认 normalized final message 末尾只有一个可解析 `<training_batch_handoff>`。case handoff 后再次核对 parent lock owner 未变、workspace 没有 training child 增量；global handoff 核对 global lock 已由 child 正确释放。失败按 training-data-tick 的 active batch 恢复协议 fresh 重试，同一 blocker 连续三次才询问用户。

科研 dispatcher 不把 training-data-tick、maker 或 dataset-reviewer 的输出追加到 research `raw-trace.jsonl`，也不把它们当科研 phase。BATCH/review/attempt outputs 已经保存转换 provenance。batch sealed 或 no_new_records 后，原 investigation/experiment phase 原样继续；reviewer 的训练 checkpoint 不能替代后续 lit-feed/investigator。

system/global feedback 实际应用后，同一 checkpoint 先处理 case application event，再运行 `--global feedback_applied`。启动和正常暂停时，如果 global TRAINING 有 active batch 或 global cursor 后有记录，也在 case checkpoint 后运行 global recovery/user_pause；没有 global 新记录时不创建空 batch。

“先 case、后 global”只规定串行顺序，不建立成功依赖；case checkpoint 返回 failure/paused 时，仍要尝试独立的 global backlog。启动 global child 前先非阻塞检查 `.agent-sessions/global-training.lock`：不存在才启动；存在且 owner 仍活跃时向用户报告 `global_checkpoint_deferred=lock_busy` 并继续原 case research，不等待；owner 已死亡或无法确认时报告 `global_checkpoint_deferred=stale_lock` 与 owner，不自动删除，也不阻塞 case。不要为 deferred 状态追加 research raw event；已有 global raw/feedback records 与 cursors 会让下一 checkpoint 再试。已经启动的 global child 若异常退出并留下 stale lock，同样 deferred；不要在持有 case lock 时无限重试 global lock。

## 9. Dataset-maker 怎样生成训练数据

dataset-maker 必须为每个候选样本保留：

- 当时可见的 input；
- 经人类反馈或后续证据支持的 target；
- source event IDs；
- evidence / feedback refs；
- model、prompt、policy version；
- label quality；
- rights；
- case/base-case/split 信息；
- 若可得，成本和后续 outcome。

每条正样本还必须写 `decision_event_id` 和 `visible_event_ids`。`visible_event_ids` 只包含 decision 开始前已经结束，或 decision event 的 visible context 明确引用的 event。后来 correction/outcome/review/known answer 只能出现在 label/outcome provenance，不能进入训练 input。`source_event_ids` 可覆盖整条证据链，不能拿它冒充 visible set。

“直接训练”要求 model-facing 字段包含实际内容。decision/correction 的 system message 必须从 code repo `policy_version + prompt_path` 重建并通过 `prompt_sha256`；user message、preference prompt 和 verdict `evidence_items/execution_metadata` 必须用 `state_before.workspace_commit`、raw-input snapshots、raw observations 和 immutable artifact refs 重建成足以理解 target 的自包含输入。refs 继续保留在 metadata 供审计，但“见某路径”、模板占位词、当前 prompt、after state 或无法重建的可变文件不能代替训练输入。重建失败就 reject/uncertain。

跨 batch 去重的 canonical source signature 固定为 `(sample_type, assessment_domain-or-null, decision_event_id, claim_id-or-null, sorted(human_feedback_refs), sorted(label_source_refs))`。maker/reviewer 都只按这个 exact tuple 判断重复；标签来源改变的后续版本另建 sample ID 并保留 supersedes provenance。dedup 同时扫描整个 `DATA_ROOT/training/**` 的全部 sealed batches 和 canonical current views，不局限当前 case/global scope。

这些 provenance 字段使用如下含义：

- 普通 decision/verdict 的 `model_id/policy_version/prompt_sha256` 指产生 source behavior/judgment 的角色版本；
- correction/preference 同时记录被纠正行为和修正行为各自的 model/policy/prompt；
- `cost` 统一使用 raw event 的对象结构；多事件合并时只汇总可核对的实测值，无法可靠汇总就保留 `null`；
- `outcome_refs` 指行动之后用于判断其好坏的 event/result/review；
- `correction_refs` 指实际落实 human feedback 的 action event、commit 或 result，不指“准备修改”的承诺；
- human-correction 的 `corrects` 指被纠正的 event/behavior ID，不控制训练样本下架；只有 `supersedes_sample_ids` 控制旧 training sample 从 current 退出。两者不得互换。

训练文件模板：

- `decision-sft-template.jsonl`：状态到下一步行动；
- `human-correction-sft-template.jsonl`：旧行为、人类纠正、修正后行为；
- `preference-template.jsonl`：同一可见上下文下的 chosen/rejected；
- `verdict-template.jsonl`：claim + evidence 到正交可靠性判断；
- `rejected-template.jsonl`：不能进入正训练集的候选及原因；
- `dataset-review-template.jsonl`：dataset-reviewer 对每个候选的 disposition 和具体依据；
- `reliability-result-template.json`：当前 case 的机器可靠性投影；
- `dataset-card-template.md`：数据来源、可信度、rights、偏差和遗漏。
- `prompt-patch-candidates-template.md`：重复错误到 prompt 改动建议的证据链；不自动改 live prompt。
- `current-dataset-template.md`：当前 canonical 训练视图的 lineage、counts、hashes 和 publication receipt。

prompt patch 只能写到 `prompt-patch-candidates.md`。dataset-maker 禁止直接修改 live prompt。

### 9.1 怎样生成当前正式训练数据 `current/`

`batches/` 永久保存当时的 candidate、review 和 rejected history，不能直接当累计训练集：后续 evidence 可能让旧正样本 superseded。默认训练入口固定为：

```text
training/*/current/decision-sft.jsonl
training/*/current/human-correction-sft.jsonl
training/*/current/preference.jsonl
training/*/current/verdict.jsonl
```

每轮 maker 在当前 batch 的 `current-projection/` 重建 active set；fresh reviewer 逐文件、逐 lineage 审查。只有 reviewer 全部 accept 后，dispatcher 才把四个 JSONL 原样发布到 scope 顶层 `current/`，并机械填写 CURRENT_DATASET 的 sealed receipt。content commit 未产生前 receipt 使用 `pending_dispatcher_content_commit`，随后在同一个 receipt-only commit 中与 BATCH/TRAINING 一起写真实 hash，禁止猜自引用 commit。历史 batch 不改，canonical current 可随新 sealed batch 重写，git history 保留每个版本。训练 consumer 禁止直接 glob `batches/*/*sft.jsonl`。

active set 只含：latest accepted、frozen `dataset_split=train`、当前 effective internal training rights=true、未 rejected/uncertain、未被 later accepted `supersedes_sample_ids` 或 reviewer-accepted deactivation tombstone 指向的 sample。新 evidence 足以让旧 sample 退出、但不足以形成替代 target 时，maker 在 rejected 写 `deactivates_sample_ids`；reviewer 核对后 current 直接移除旧 ID，不为了保持非空而留下过期标签。`deactivates_sample_ids` 非空时，`deactivation_evidence_refs` 必须非空且逐项可打开，并来自 current fixed range 或 fixed event 显式引用的 prior sealed/committed evidence；line_end 后的信息不能偷进当前 tombstone。普通 rejection 两者都为空。tombstone 的 `candidate_sample_id` 指被新 evidence 否定的原候选或 prior current sample，真正控制下架范围的字段始终是 `deactivates_sample_ids`。reviewer reject tombstone 时恢复其目标旧样本，除非另一个 accepted exclusion 生效；reviewer 对 tombstone uncertain 时保守地暂时下架旧样本，并要求下一轮核对 uncertain 归档和 projection。

dev/test/unassigned 样本即使 reviewer accept，也只留在 immutable batch history，不进入 `current/`。maker 每批还要重新读取 prior current row 的 frozen split 和当前 rights declarations；rights 被撤销/变 unknown 或来源 case 是 held-out 时立即从 projection 排除，不改历史 row。global candidate 含 case-specific content 时继承来源 case 的 base/split/rights；混合不同 base case 的单条 candidate 拒绝。pure system feedback 才使用 `base_case_id=null,split=train`。

projection row 默认逐字等于 source candidate row。唯一受控 legacy normalization 是 source row 缺少 `supersedes_sample_ids` 时补空数组；任何既有 key/value 都不得改变。CURRENT_DATASET 对每个 active row 记录 source row hash、projection row hash 和 normalization 名称，reviewer 按解析后的对象验证只增加了这个默认字段。其他 schema 迁移必须先产生新协议，不能借 normalization 静默改历史标签。dispatcher 不生成 ideal answer。global scope 的 verdict 文件恒为空。`all_cases/system` human correction/preference 只归 global lane，case lane 不重复生成。

CURRENT_DATASET Inventory、BATCH Current projection 和四个实际 projection JSONL 的 row count/SHA-256 必须逐项一致。reviewer 与 dispatcher 分别独立重算，不能互相信任摘要；dispatcher 发布后还要重算 canonical current 并与 reviewed projection 比较，任一不一致都禁止 seal。

promotion 中断时，只有已经由完整 reviewer attempt 和 control state 授权的 reviewed batch projection + review rows/hashes 才是恢复源；canonical current 的半写状态不能反向成为真值。若还没有这种授权，dispatcher 把 partial current、hash 和 diff 隔离到 batch recovery，再从最后一次已提交的 exact current paths 恢复，不能交给 maker 修。四个 JSONL 使用同文件系统 temp+rename 逐文件发布，content commit 必须同时包含它们和 sealed control。

maker/reviewer 的原始输出按唯一 attempt ID 保存在 `batches/<batch-id>/maker-attempt-*.out` 和 `reviewer-attempt-*.out`，不追加到 research `raw-trace.jsonl`，防止下一批递归训练数据整理过程。`review.jsonl` 由 reviewer 只追加；candidate files 可在 seal 前按 review 修正，seal 后不可改，只能由后续 batch 产生新样本。

`forbidden_inferences` 由 dataset-maker 按当前证据填写，dataset-reviewer 核对。每条 verdict 和 reliability result 至少保留 `fraud_without_formal_investigation`；执行失败却没有 paper-claim evidence 时，再加入 `paper_claim_from_execution_failure`。它列的是当前证据禁止推出的结论，不是 target label，也不能因为数组存在就暗示论文有 integrity 问题。

`reliability-result.json` 是跨批次当前投影，不是第三个 scientific reviewer。每个 claim 的 `assessments[]` 和每个 profile dimension 的条目分别保留 `assessment_domain=experiment|investigation`；新 batch 只更新同对象、同 domain 的条目，另一 domain 及未重审 claim/profile 保留，并累计 source batch refs。maker 禁止求平均、互相覆盖或发明 overall verdict；两个 domain 冲突进入 `human_review_required`。

claim identity 先遵守 experiment manual：共享 target claim 用 `C*`，investigation-only 用 `IC*`，experiment-only 用 `EC*`。同一个 `C*` 只有在核心 claim text 和 source_refs 跨 STATE/INVES 一致时才 merge；同 ID 不同 claim 是 schema conflict，相关 verdict 进入 rejected，reliability result 标 human review，不能靠 assessment_domain 掩盖碰撞。

## 10. 标签可信度

| `label_quality` | 含义 | 允许用途 |
|-----------------|------|----------|
| `known_answer` | controlled case、隐藏答案或人类已完整验证 | 训练和正式评价 |
| `human_feedback` | 人类明确纠正目标、流程、偏好或行为 | 高优先级训练；科学事实仍需 evidence |
| `evidence_verified` | 原始结果可独立核对，并经审计/评审 | 训练 |
| `reviewer_agreement` | 独立 reviewer 一致但无外部真值 | 较弱训练；不作 benchmark gold |
| `uncertain` | 证据不足、关联不确定或角色分歧 | 训练 abstention 或保留研究 |
| `rejected` | 泄漏、错误关联、无依据、格式损坏或无训练权 | 不进入正训练集 |

一致不等于真值。scientist、auditor 和 reviewer 都同意时，最高仍只能是 `reviewer_agreement`，除非存在独立可核查 evidence、human feedback 或 known answer。

auditor 的 `error_layer=claim_decomposition` 表示我们的 Agent 把目标 claim 拆错，是流程错误；它不等于 `failure_attribution=paper_claim`。后者表示证据归因到目标论文 claim 本身，只有 domain reviewer/verdict 在证据足够时使用。

## 11. Dataset-reviewer 怎样复核

dataset-reviewer 对每条样本只给 `accept`、`fix`、`reject` 或 `uncertain`，并写具体依据。

它必须检查：

1. `decision_event_id/visible_event_ids` 是否与原 event 时间和 visible refs 一致，input 是否泄漏后续信息；source role prompt/context 是否能从 before commit/snapshot 重建，model-facing payload 是否实际、充分、无占位符；
2. human feedback 是否逐字保留且链接到正确 event；
3. chosen/rejected 是否真有证据区分，correction/preference scope 是否与 feedback authority scope 一致；
4. verdict 四个字段是否彼此独立，没有把执行失败偷换成论文错误；assessment domain 是否匹配 source reviewer；experiment 的 source verdict 是否回到 source commit 的 STATE 逐 claim crosswalk，investigation 是否为 null；
5. label quality 是否被抬高；
6. evidence refs 是否存在并支持 target；
7. rights、secret、个人信息和未公开材料是否正确处理；
8. frozen base case/split 是否一致，current 是否只含 train，global 是否绕过 held-out case；
9. JSON/JSONL 是否可解析，ID 是否唯一；
10. rejected/uncertain 是否被诚实保留；是否按 `(sample_type, assessment_domain-or-null, decision_event_id, claim_id-or-null, sorted(human_feedback_refs), sorted(label_source_refs))` 检查全部 sealed batch 和 canonical current 的重复。
11. batch `current-projection/` 是否精确实现 active set，受控 legacy normalization 是否只补空 `supersedes_sample_ids`，lineage/source-output row hashes 是否一致，canonical current 是否仍未被 maker 修改。
12. reviewer 是否已从实际文件独立重算 projection rows/SHA-256，并与 CURRENT_DATASET/BATCH inventory 逐项核对；deactivation evidence 是否可打开，tombstone reject/uncertain 是否分别触发旧样本恢复/保守暂时排除。
13. reliability result 是否按 claim/profile/domain merge，是否保留另一 domain 和未重审对象，是否错误产生全局 verdict；C/IC/EC namespace 与跨域 claim text/source 是否一致。

`fix` 返回 maker 修正，再由 fresh reviewer 重查。maker 不得自行把 `fix` 改成 `accept`。对象和 evidence 未变化时，reviewer 不得连续两轮重复同一 fix；上一要求已落实后必须 accept、给出由新证据支持的不同 fix、reject 或 uncertain，不能用措辞变化制造无限整理循环。

`reliability-result.json.human_review_required` 由 dataset-maker 写成对象数组，dataset-reviewer 核对。出现 integrity anomaly、准备公开的 negative verdict、两个 domain reviewer 冲突、human feedback 冲突、rights 不明确或可能涉及个人/未公开信息时必须列出对应 claim/event 和原因；没有这些触发项时才写空数组。

## 12. 四个互不替代的可靠性字段

reviewer/verdict 数据把不同问题拆开：

```text
execution_status: succeeded | failed | blocked | not_attempted
result_match: matched | partial | mismatched | unknown
claim_verdict: supported | partially_supported | contradicted | insufficient_evidence
failure_attribution: paper_claim | artifact | environment | data | metric | protocol | our_bug | budget | unknown
confidence: 0.0-1.0
```

`execution_status=failed` 不推出 `claim_verdict=contradicted`。数据缺失、环境失败或预算不足通常对应 `result_match=unknown` 和 `claim_verdict=insufficient_evidence`。系统记录 integrity anomaly，但不自动输出 fraud。

experiment reviewer 写 STATE 时继续使用既有 7 值 workspace verdict，但 training learning record 必须拆成上面四个正交字段：`UNTESTED/NOT_ASSESSABLE` 通常是 `not_attempted|blocked + unknown + insufficient_evidence`；`OUT_OF_BUDGET` 还必须 attribution=`budget`；`NOT_REPRODUCIBLE` 没有固定 claim 映射，reviewer 必须回到 evidence，artifact/environment/data/metric/protocol/our_bug failure 通常仍是 `insufficient_evidence`，只有有效执行直接反驳 paper claim 才是 `contradicted`。`SUPPORTED/PARTIAL/CONTRADICTED` 也必须核证后映射。旧 enum 只保留在 `source_domain_verdict` provenance，不能进入 `claim_verdict`。experiment reviewer final handoff 和 dataset-reviewer 必须分别执行一次逐 claim crosswalk；后一角色从 source workspace commit 的 STATE 与 evidence 独立核对，不能把 producer 的 learning record 当真值。

## 13. 数据使用权限和 train/dev/test 划分

所有 raw record 和训练样本统一保存完整 `rights` 对象，不再压缩成 `internal_trainable/public_trainable` 等单一枚举。新 topic template 与 global rights template 已按项目所有者指令授权本系统 trace/human feedback 用于内部能力提升，同时禁止默认公开/商业发布，并要求公开/商业 projection 先脱敏；具体 case 可显式关闭。旧 case 或外部输入没有 rights 声明时，各布尔值写 `null`：原始记录允许内部留存，但任何训练、公开或商业导出都按未授权处理。

```yaml
training_rights:
  trace_trainable: true | false
  human_feedback_trainable: true | false
  public_release: true | false
  commercial_use: true | false
  redaction_required: true | false
```

模板中的 `rights` 还包含 `rights_ref`，指回上述声明。用途判断直接读取布尔字段：

- decision/verdict 等 trace 样本只有 `trace_trainable=true` 才进入训练导出；
- correction/preference 涉及人类原话时，必须同时满足 `trace_trainable=true` 和 `human_feedback_trainable=true`；
- 公开数据还要求 `public_release=true`；商业数据还要求 `commercial_use=true`；
- `redaction_required=true` 时，在 dataset-reviewer 确认独立脱敏 projection 前禁止公开或商业导出；它不撤销 `trace_trainable/human_feedback_trainable=true` 已授予的内部训练权。canonical internal sample 与 immutable receipt 保留原文，公开/商业版本另建 sample ID 和映射，不原地改写。

训练样本另写 `rights_source_refs`，列出参与 effective rights 的全部声明。普通 case 至少包含自己的 topic rights；global 样本一旦引用 case event/content，必须同时包含 global rights 和每个来源 case rights，并逐字段取交集：任一 false 得 false；无 false 但任一 null 得 null；全部 true 才得 true。global lane 不能绕过 case opt-out。

禁止由 Agent 用单一字符串概括这些权限，因为那会丢失公开、商业和脱敏维度。

case 的 `base_case_id/dataset_split` 在 TRAINING 初始化时从 topic 冻结；首个 batch 后不得改。topic template 默认 `train`，准备 held-out case 时必须在首次运行前明确改为 `dev/test`。同一 `base_case_id` 的不同 variant 必须在 topic 中显式使用同一 base 和同一 split；maker/reviewer 扫描全部 TRAINING 声明，冲突就停止，不自行随机分配。split 未明确写 `unassigned`，且不进入 current。普通独立 case 的 base 留空时冻结为 `case_id`。只有 pure system-level、完全不含 case-specific input 的 human-feedback 样本才写 `base_case_id=null,split=train`；global 样本引用 case 时继承该 case frozen base/split，不得用 null 隐藏来源。human feedback 中的账号、密钥、私人路径、未公开工作和个人信息必须在公开/商业导出前审查；原始行保留内部 provenance，脱敏样本另建 ID 和映射记录。

`scope` 只用于 human correction/preference，表示人类纠正的适用范围；普通科研 decision 和 claim verdict 不使用该字段，它们靠 case/claim refs 定位。

`rejected.jsonl.reasons` 是多值数组，允许值为 `leakage/wrong_link/unsupported_label/rights/secret/privacy/ format/duplicate/conflict/insufficient_evidence/other`。`preserved_payload` 在没有 secret/privacy/rights 风险时保存原候选对象；存在上述风险时写 `null`，只保留受控的内部 `candidate_ref` 和拒绝原因。普通 rejected candidate 的 `deactivates_sample_ids=[]`、`deactivation_evidence_refs=[]`。只有新 evidence 要求 prior current sample 退出时才写 tombstone；两个数组都必须非空，且 evidence ref 必须独立可读。`candidate_sample_id` 用于定位原候选，`deactivates_sample_ids` 才是 active-set 下架指令。

## 14. 最小格式检查

不用新代码。写完后使用现有工具检查：

```bash
jq -c . training/<slug>/raw-trace.jsonl >/dev/null
jq -c . training/<slug>/human-feedback.jsonl >/dev/null
find training/<slug>/batches -name '*.jsonl' -type f -exec sh -c 'jq -c . "$1" >/dev/null' _ {} \;
find training/<slug>/current -name '*.jsonl' -type f -exec sh -c 'jq -c . "$1" >/dev/null' _ {} \;
jq . training/<slug>/reliability-result.json >/dev/null
```

空 JSONL 合法。解析失败、重复 ID、打不开的 evidence ref 或无人负责的字段都必须在封存前修复。

## 15. Git 和恢复

- dispatcher 在 human feedback 或 raw event 落盘后，只 add 对应 `training/<slug>/` 文件并提交父数据仓库。
- dataset-maker/reviewer 写各自允许的 training 文件但不碰 git index。training-data dispatcher 每轮保存角色 output，获取 data-repo write lock，只 add 本轮实际改变的当前 case/batch 精确路径，并用 `git commit --only -- <exact paths>`；不夹带 workspace 或其他 case。
- 原始记录优先于整理：紧急停止时至少完成 verbatim feedback/raw event 落盘；下次恢复同一 batch。
- dispatcher 恢复时，把当前会话中最后一个已记录 `message_order` 之后的用户消息逐条与 receipt 对照，先补齐缺失原文再继续 dispatch。若旧会话 transcript 已不可访问，明确记录该 provenance gap，不能声称反馈完整。
- 不得因为训练整理失败阻塞人类要求的紧急停止。
- 不得删除旧 batch record 来“修复”历史；使用 rejected、`supersedes_sample_ids` 和新的 commit 保留 lineage，只在 reviewed canonical current projection 中排除失效 sample。
- role 启动前若 canonical current 存在未提交、未获完整 reviewer/control 授权的 partial promotion，dispatcher 先把全部 current 快照、hash 和 diff 放进当前 batch recovery，再恢复最后一次已提交 current；没有可验证恢复源就停止。
