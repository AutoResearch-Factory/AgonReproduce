# AgonReproduce 系统说明书

这是一个目标论文可靠性审查系统。项目名是 **AgonReproduce**；Claude Code plugin 和 skill namespace 使用机器名 `agon-reproduce`。

请仔细阅读本文件，了解各种文件的位置和自己的读取权限，防止与其他人撞车。

## 项目结构

一个目标论文/目标案例会经历:

`topic brief --> investigation workspace init + investigation deep-lit landscape --> investigator planning/checks --> experiment loop --> investigation post-loop --> report`

在 AgonReproduce 里，这些阶段的含义是:

- `topic brief`: 人类给定的目标论文/目标案例 brief，不是开放式选题。
- `reliability landscape`: 可靠性背景和前置证据图谱，包括目标论文、相关复现、代码/数据/benchmark、已知争议和可用审查工具。
- `workspace`: 单个目标论文/案例的执行目录，内含 topic、landscape、STATE、INVES、文献总账、实验代码和结果。实验计划分别写在 INVES.md 和 STATE.md。
- `experiment`: 在服务器/workspace 中执行验证计划，收集 manifest、trace、日志、结果和失败证据。
- `investigation`: 围绕同一个 workspace 做外部可靠性审查，包括文献关系、artifact/data/benchmark 线索、cherry-pick、overclaim、适用边界、后续支持/反驳和社区复现/issue。
- `report`: 诚实可靠性报告。目标是说明哪些 claim 被支持、部分支持、反驳、不可判定，以及为什么；不是包装性叙事。

对应这些步骤，项目分为 **experiment factory** 和 **investigation loop**:

- investigation loop 是 workspace 初始化入口。第一次运行时, 它从 `topics/<slug>.md` 准备 workspace 并初始化 `INVES.md`; 初始 `landscape.md` 由 `deep-lit-tick --scope investigation` 在 workspace 内生成, 然后 investigator 消费这些 source 并规划/整合外部检查。它不分 pre/post mode，而是根据当前 INVES、STATE、results、deep-lit/wiki、audit 和 review 反馈自己判断下一轮该查什么。结构上平行于 experiment loop: deep-lit 先提供大规模文献 source, investigator 消费 source 并规划/整合外部检查, shared coder 跑外部检查, inves-auditor 做过程审计, inves-reviewer 给 external reliability profile 打分。investigator 可直接调用 `deep-lit-reader` 读取自己认为该读的论文; 系统性搜索、引用/反引文扫盘或 saturation 走 `deep-lit-tick --scope investigation`, 且该 tick 必须严格按 prompt 大规模多读。
- experiment factory 输入已经初始化好的同一个 workspace，负责执行 STATE.md A1/A2/A3 里的实验计划、审计、可靠性评分和报告素材沉淀。experiment loop 内部仍保留 `needs_litfeed -> deep-lit-tick --scope experiment`。reviewer 的 `ready` 只表示当前 STATE version 可报告, loop 不会据此自停；只有人类决定何时退出实验阶段。
- training-data loop 不做科研。它在固定 checkpoint 上读取父仓库 raw records，用 dataset-maker / fresh
  dataset-reviewer 对抗整理出 SFT、human correction、preference、verdict、rejected 和 reliability projection。
  封存一个 training batch 不会停止或完成 investigation/experiment loop。

v0 不启用 topic radar / topic distiller / posts 生产线。保留相关概念只是为了兼容旧代码和未来扩展，当前核心入口是人类直接在 `topics/` 放目标论文 brief。

项目的文件结构是:

```
/
├── topics/
│   ├── mmdd-slug.md                # 人类给定的目标论文/案例 brief
│   └── ...
├── training/                        # 父数据仓库中的学习记录，不随 nested route branch 切换
│   ├── global-human-feedback.jsonl
│   ├── global/                     # system-level feedback 的独立训练转换 lane
│   │   ├── TRAINING.md
│   │   ├── TRAINING_RIGHTS.yaml
│   │   ├── raw-trace.jsonl
│   │   ├── current/                # reviewer-sealed canonical training JSONL
│   │   └── batches/
│   └── slug/
│       ├── TRAINING.md
│       ├── raw-trace.jsonl
│       ├── human-feedback.jsonl
│       ├── raw-outputs/
│       ├── raw-inputs/             # mutable/non-git visible context snapshots
│       ├── current/                # reviewed train split 入口；不直接读取历史 batch positives
│       └── batches/
└── workspace/                      # 每个文件夹对应一个目标论文/案例的执行阶段
    ├── workspaces.xml              # workspace metadata 数据库
    ├── slug/
    │   ├── topic.md               # 目标论文/案例 brief, 从 topics/ copy
    │   ├── landscape.md            # reliability landscape, 由 investigation-scope deep-lit 生成/维护
    │   ├── literature-ledger.md    # deep-lit 搜到的全部新文献总账
    │   ├── src/slug/{models,data,training,utils,...}/
    │   ├── conf/                   # config
    │   ├── scripts/{train.py,eval.py,sweep.sh,...}
    │   ├── data/
    │   │   ├── MANIFEST.md         # 每条数据/模型/外部资产的 metadata
    │   │   └── ...
    │   ├── checkpoints/
    │   ├── results/
    │   ├── audits/
    │   ├── investigations/
    │   ├── tests/
    │   ├── STATE.md              # 内部实验复现状态, scientist 场景 A 初始化
    │   ├── INVES.md              # 外部可靠性审查状态, investigation-tick 初始化
    │   ├── experiment-log.md     # 内部实验复现 loop 日志, 不入 git
    │   ├── inves-log.md          # 外部可靠性审查 loop 日志, 不入 git
    │   ├── lit-feed.md           # 共享文献 inbox
    │   └── README.md
    └── another-slug/
```

`training/<slug>/` 与 `workspace/<slug>/` 平级且一一对应。科研 subagent 不写这里；它们在最终回复返回
`learning_record`，两条 loop 的 dispatcher 保存 human feedback、原始 `$OUT` 和客观 dispatch provenance。
训练目录不会因 experiment 的 `route/*` 切换或放弃而丢失。详细契约见
`orchestrator/references/training_data_manual.md`。
训练消费端只 glob `training/*/current/*.jsonl`；这些文件只发布 frozen `dataset_split=train` 的 reviewed rows。
dev/test/unassigned rows 留在不可变 batch history，不进入直接训练视图。`batches/` 是 provenance 和 reviewer history，
不是默认训练入口。

旧 `topic-signals/`、`posts/` 不是 v0 核心路径。不要让 agent 为了填这些目录而分心。

## XML Schema

`workspaces.xml`:

```xml
<workspace slug="example-slug">
  <one-line>One-sentence description of the current audit/execution status.</one-line>
</workspace>
```

## 目标论文审查手续

默认手续如下。除非人类在 `topics/` 或 `STATE.md §5` 明确改写优先级，agent 不应跳步。

1. 读取 `topics/mmdd-slug.md`，明确目标论文、目标 claim、审查预算、非目标。
2. 读取目标论文原文和 artifact 线索，不能只凭摘要或二手介绍。deep-lit-reader 精读 arXiv tex；非 arXiv target 由 investigator 读取 `materials/` 中已核验的全文 source/PDF，不伪造 landscape。
3. 运行 `investigation-tick mmdd-slug`。如果 workspace 还不存在, 它初始化 `workspace/mmdd-slug/`，把目标材料放入 `topic.md`，创建 `INVES.md`，然后先通过 `deep-lit-tick --scope investigation` 生成 workspace 内的 `landscape.md` / 文献 source, 再交给 investigator。loop 不会自停, 直到人类叫停或要求进入实验。
4. 运行 `experiment-tick mmdd-slug`。它只接管已初始化 workspace，首次进入时由 `experiment-scientist` 场景 A 创建自己的 `STATE.md` 和 `experiment-log.md`，随后按 STATE.md A1/A2/A3 执行复现/验证，保留 auditor、reviewer 和 experiment-scope `needs_litfeed`。
5. 实验阶段到达人类认可且 nested workspace 已回到 `main` 的检查点后，再运行同一个 `investigation-tick mmdd-slug` 继续 external investigation，重点审查 cherry-pick、overclaim、适用边界、外部反证和实验结果暴露的新风险。investigation 不在可能被放弃的 experiment route 上写 workspace 级外部状态, loop 同样不会自停。
6. 最终报告由后续 report agent 或人类从统一证据账本 / STATE / experiment reviewer verdict / INVES external review verdict 汇总生成，不启用独立写作工厂。

两条 loop 对同一目标 claim 共用稳定 ID：共享 target claim 用 `C*`，investigation-only 用 `IC*`，experiment-only
用 `EC*`。后进入的角色复用已有 C ID；同 ID 必须保持同一核心 claim text/source_ref，不能各自从 C1 重编。

`training-data-tick <slug> <trigger>` 整理 case records；`training-data-tick --global <trigger>` 整理 system-level
feedback/application records。它只写对应父仓库 training lane，workspace 全部只读；科研 dispatcher 的自动
reviewer/user checkpoint 以同一命令串行触发。

没有 active case 时，用 `human-feedback-tick record` 保存 system-level 用户原话；system prompt/harness 修正已有
可核查 commit/outcome 后，用 `human-feedback-tick applied <HF-ID>` 登记结果并触发 global conversion。没有运行中
的 command/dispatcher 时不存在后台监听，不能声称自动捕获不可见历史消息。

## 外部 skills

<!--为什么要写这个? 因为 subagents 的 context 默认没有任何 skill-->

- arxiv-tools:arxiv: 遇到 "search for papers"、"get paper info"、"download LaTeX source"、"generate BibTeX citation"、"find citing papers"、arXiv ID、arXiv URL 时, 直接使用这个 skill。**注意: web search 返回的论文信息不可靠: 摘要可能残缺, 作者/年份可能错配, arxiv ID 本身甚至可能是幻觉. 任何要写入 landscape / STATE / review / report 的论文引用, 都必须用 arxiv-tools 拉取原文核验, 不能仅凭 web search 结果落笔.**
- humanizer: Remove signs of AI-generated writing from text. Use when editing or reviewing text to make it sound more natural and human-written. Based on Wikipedia's comprehensive "Signs of AI writing" guide. Detects and fixes patterns including: inflated symbolism, promotional language, superficial -ing analyses, vague attributions, em dash overuse, rule of three, AI vocabulary words, negative parallelisms, and excessive conjunctive phrases.
- agon-reproduce:server-health: Use when you need server load history (CPU util, GPU busy count, Slurm allocation, mem GB) to pick a server, or to confirm your running task is still alive.

其他 skills 和 MCPs 是可选增强，不是 AgonReproduce 核心协议的一部分。

## 本地配置边界

仓库只保存通用协议。以下内容必须留在本地，不得提交:

- `orchestrator/.settings.toml`: 实际 model routing。
- `orchestrator/references/servers.local.md`: 主机名、账号、路径、价格和调度细节。
- API keys、SSH keys、tokens 和 provider credentials。
- 真实 case 的未脱敏论文、数据、trace、human feedback 和运行产物。

公开的 `.settings.example.toml`、`servers_manual.md` 和各类 template 只定义接口。模型调用方式见
`dispatch_manual.md`；运行陌生论文代码时，执行权限和隔离策略由操作者负责。
