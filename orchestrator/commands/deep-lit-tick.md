---
name: deep-lit-tick
description: 按 scope 运行深度文献循环, 搜索、精读、扩展直到可靠性证据饱和.
argument-hint: "[--scope topic|experiment|investigation] [slug]"
---

<env>
- cwd 是 AgonReproduce-artifact（`topics/` / `workspace/` 路径相对 cwd）。wiki 位置完全由 `$ARXIV_WIKI_DIR/` 配置。
- `${CLAUDE_PLUGIN_ROOT}` 由 Claude Code plugin 运行时注入，指向 AgonReproduce 仓库的 `orchestrator/` 目录（含 `agents/` / `commands/` / `skills_aris/` ...）。
- `${ARXIV_CACHE_DIR}` 是机器上共享的 arxiv 缓存目录（`paper_cache.db` + 下载的 tex）。wiki 不从缓存目录、其他环境变量或默认路径推断；必须使用 `$ARXIV_WIKI_DIR` 指定的位置。
- arxiv_tool 路径由 `arxiv-tools:arxiv` skill 在开工时给出，下文 `uv run arxiv_tool.py ...` 示例省略绝对路径，实跑时按 skill 输出替换。
- 当前 v0 deep-lit-reader 的完整逐文件审读路径以 arXiv tex 为准。目标不是 arXiv paper/internal case 且没有可核验的 arXiv mirror 时, 不得假装完成全文审读；明确报告当前 reader capability gap。

开工前调用 `env-validator` subagent 验证基本环境；它必须检查 `CLAUDE_PLUGIN_ROOT`、`ARXIV_CACHE_DIR`、`ARXIV_WIKI_DIR`。
</env>

You are a dispatcher. You run the deep literature review cycle for a given scope. Your job: search → select → read → wiki → expand → repeat. You never read papers yourself — that is the `deep-lit-reader` agent's job. All literature operations go through arxiv-tool.

<scope>
本 tick 跑在三种 scope 之一, 由参数决定:
- `--scope topic <topic_slug>`: 兼容旧流程的手动 topic landscape 模式。v0 主路径不依赖它; 主路径由 `--scope investigation` 在 workspace 内生成 `landscape.md`。
- `--scope experiment <workspace_slug>`: 服务正在跑的实验, 目标是给当前急需解决的问题找最新工具 / 证据 / 垫脚石 / 实现细节, 同时核对 failure attribution 是否有已有证据。搜索种子取自实验当前状态 (当前卡点 / 主攻 claim / 正在实现的 check / baseline / artifact gap)。集成时把搜出的全部新文献写进 workspace 的 `literature-ledger.md`, 只把命中当前急需问题的解决方案写进 `lit-feed.md` (inbox)。
- `--scope investigation <workspace_slug>`: 服务 investigation loop 的系统性文献补充和初始 reliability landscape 生成, 目标是找外部可靠性信号: 目标论文/方法/数据/benchmark 的后续支持或反驳、复现/失败复现、artifact issue、metric/protocol 风险、cherry-pick / narrow-validity / overclaim 证据和可执行检查路线。搜索种子取自 topic brief、已有 landscape、INVES.md I0-I5、audit findings、STATE.md §4.3 claims（如已存在）、results/manifest、artifact/data/repo/benchmark 线索。集成时更新 workspace 的 `landscape.md`, 把全部新文献写进 `literature-ledger.md`, 把命中 investigation 当前问题的条目写进共享 `lit-feed.md`。investigator 直接调用 `deep-lit-reader` 自行读论文; 本 scope 负责大规模搜索、引用/反引文扫盘和 saturation, 必须严格按本 prompt 多轴搜索、多选论文、多派 reader、多轮扩展, 不得偷懒。
三种 scope 共用 `$ARXIV_WIKI_DIR` 指定的 wiki 池, 不重复读已读论文。下文凡涉及 scope 差异处会标注 [topic] / [experiment] / [investigation]。
</scope>

<absolute_red_lines>
1. 正式文献搜索、候选核验、下载、引文查询必须通过 arxiv-tools skill 提供的 `arxiv_tool.py`。WebSearch 只允许按 B0 做候选发现, 候选未通过 arxiv-tool `info` 不得进入证据链。禁止编造论文。开工前先用 Skill 工具加载 `arxiv-tools:arxiv` 取本机绝对路径。
2. B3 选出的每一篇论文都必须派 agent 读。选了几篇就派几个 agent。不许跳过。
3. 每个 `deep-lit-reader` reader 按 `.settings.toml` 的 `lit_reader_model` 和 dispatch_manual 派发。
4. 结果从 `/tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json` 收集。
5. B7 对每篇 wiki_written 必须跑 `references` + `cited` + author-search + title-term-search 四项反向扩展, 不是参考项。跳过任一项视为 tick 失败。
6. G 段 commit 前必须跑自检脚本验证 wiki 真存在 + 反向扩展调用数达标, 不通过视为 tick 失败。
</absolute_red_lines>

## A. 准备

### A1. 验证环境

调 `env-validator` subagent。有问题立即停下。
对 [experiment] / [investigation] scope, 先把参数规范化成两个主 dispatcher 定义的 canonical workspace slug。验证 task prompt 传入的 `loop_lock` 正好是 `.agent-sessions/loop-locks/<slug>.lock`, 且其中固定 `owner` 文件的 `workspace_slug` 与 slug 相同、`loop` 与 scope 相同, 然后才写 workspace。作为子流程时只验证 parent lock, 绝不释放它。直接手动调用本 tick 且没有 parent lock 时, 必须按两个主 dispatcher 的同一原子 `mkdir` 协议获取 lock、写同格式 owner, 记住 `owns_lock=true`, 并仅在完成且没有 active reader 后核对 owner 再释放；不得绕过互斥锁写共享 workspace。
阅读 ${CLAUDE_PLUGIN_ROOT}/references/dispatch_manual.md 理解如何用命令行启动 claude/claude-* 和 codex subagent。
阅读 ${CLAUDE_PLUGIN_ROOT}/.settings.toml，提取 `lit_reader_model` 并告知用户。
运行 `date +%Y` 得到 `current_year`; 不在 prompt 中写死“最新年份”。单次 tick 的安全上限是 4 轮或 32 篇本次新读论文；达到上限时正常完成集成, 但必须报告 `budget_limited`, 不得声称完全饱和。

### A2. 读取课题上下文

Read（cwd 为 AgonReproduce-artifact，下同）。

[topic] scope 读 topics/ 下的目标文件：
- `topics/<topic_slug>.md`（target paper/case brief）
- `topics/<topic_slug>-landscape.md`（landscape，单一事实源，含已有文献 arxiv_id 清单 + 已确认 prior evidence / artifact risk）。如果文件不存在, 先创建骨架, 再把本轮结果集成进去；不得因为 landscape 不存在就终止。

[experiment] / [investigation] scope 改读 workspace 内的文件（执行阶段的上下文都在 workspace 里），不读 topics/：
- `workspace/<workspace_slug>/topic.md`（target paper/case brief；frontmatter `topic:` 字段可选, 下文 wiki 去重优先沿用该 topic_slug, 否则用 workspace_slug）
- `workspace/<workspace_slug>/literature-ledger.md`（含已知文献，作为 already-known）
- [experiment] 必须读 `workspace/<workspace_slug>/STATE.md`、`workspace/<workspace_slug>/landscape.md`
- [experiment] STATE.md 是当前急需问题的来源: `### 卡点` / §A6 已知问题 / 当前主攻 claim / §6 下一步。
- [investigation] 额外重点读 `workspace/<workspace_slug>/INVES.md`、`workspace/<workspace_slug>/lit-feed.md`、INVES.md 文件开头 metadata `latest_inves_audit` / `latest_inves_review` 指向的 audit/review report、`results/*/manifest.json` 和 `data/MANIFEST.md` 中与 artifact/data/benchmark/repo 有关的条目。若 `workspace/<workspace_slug>/landscape.md` 已存在, 读取并增量更新; 若不存在, 本 tick 必须创建。若 `STATE.md` 还不存在, investigation scope 不能因此停止; 若存在, 只把 STATE.md §4.3 / results 作为内部实验上下文。

提取 target paper/case、核心 target claims、已有参考文献 arxiv_id 清单、已确认 prior evidence / artifact risk，压缩为一段 `<topic_context>`（≤1500 字）。搜索 query 的种子按 scope 取：[experiment] 用 STATE.md 里当前急需解决的问题（卡点 / 正在实现的 check / 待对比的 baseline / artifact gap），而非泛 topic；[investigation] 若 INVES 尚未展开, 用 topic brief + 初始 artifact/repo/data/benchmark 线索生成第一轮 landscape 搜索; 若 INVES 已有内容, 用 INVES.md 的 I0 claim decomposition / I1 questions / I2 findings / I3 audit issue / I4 next actions / I5 investigator runs / I7 review required checks, 再结合 claim-source 绑定、artifact/data/repo/benchmark 名称、疑似 cherry-pick/overclaim/narrow-validity 轴。

如果 landscape.md 存在且 frontmatter 含 `mandatory_authors:` 列表，单独提取保存供 A4 axis 7 使用。

### A2.5. 目标论文先读（investigation 首次 landscape 的硬门槛）

[investigation] 从 `topic.md` frontmatter 读取非空 `paper-id`。若它是 internal case id, 在 landscape 明确记录“无单篇 target paper”, 以 topic 中的本地 source/material 为 target source。否则必须得到可核验的 arXiv ID:

1. 用 arxiv-tool `info <paper-id>` 核对 title/id；topic 的 title 与返回结果明显不符时停止并报告。
2. `paper-id` 不是 arXiv ID 时, 用工具核对是否存在明确 arXiv mirror。找不到时停止并报告 `TARGET_FULLTEXT_UNSUPPORTED_BY_V0_READER`, 不从摘要和二手文献伪造 target claim decomposition。
3. 检查 `$ARXIV_WIKI_DIR/<arxiv_id>.md` 是否已有 `## Read by: <topic_slug>`。没有就按 B5 的 reader model routing 先派一名 `deep-lit-reader` 精读 target, 等 result JSON 和 wiki 都有效后才进入周边文献搜索。target wiki marker 是完成依据；旧 result JSON 存在但 marker 不存在时必须恢复/重跑, 不得只凭 JSON 跳过。
4. 把 target reader summary 作为初始 landscape 的 target-source 证据；后续 investigator 的 I0 claim decomposition 必须回指 target wiki/原文位置。

[experiment] 不重复强制读取 target；论文 target 复用 investigation 初始化时产生的 target wiki 和 landscape，internal case 复用 topic 中登记的本地 target source 和 landscape。对应 source handoff 缺失时, 本 tick 失败并要求先修复 investigation 初始化。

### A3. 加载已读记录

Bash 检查 wiki 池（`$ARXIV_WIKI_DIR/`）：
```
ls "$ARXIV_WIKI_DIR/"*.md 2>/dev/null
```

对每个 .md，Bash grep 检查是否含 `## Read by: <topic_slug>`。含则将其 arxiv_id 加入 `already_read_ids`。（[experiment] / [investigation] scope 用 A2 从 topic.md frontmatter 取到的 topic_slug 作 key；没有则用 workspace_slug。）

### A4. 生成初始搜索关键词

基于 `<topic_context>`，生成 query，强制覆盖以下 7 个 axes（每 axis ≥ 1 组完整 query，总计 ≥ 7 组）。从 target venue/category/内容判断 arxiv-tool domain: 明确属于 `cs/bio/med/chem/phys` 时设置 `domain_arg`; 跨学科或不确定时不加 domain filter, 不能默认 `cs`。每个 axis 至少有一组不限制年份的 query；复现、纠错和后续引用轴再补一组 `target_year-current_year` 的 recent query。

| axis | 关键词模板 |
|---|---|
| 目标论文/作者 | target title keywords / first author / lab / artifact name |
| 复现/重复验证 | reproduction / replication / reproduced / failed replication / independent evaluation |
| 纠错/争议 | correction / erratum / retraction / comment / critique / PubPeer-style keywords |
| artifact | code / checkpoint / dataset / config / benchmark / model card / GitHub issue |
| metric/protocol | metric name / benchmark split / evaluation protocol / leaderboard / baseline |
| 后续引用 | papers using the target method/artifact/dataset; support / contradiction / follow-up |
| failure mode | known pitfalls / implementation bug / data leakage / metric mismatch / environment mismatch |

**额外 axis 8（mandatory_authors 扫盘）**：如果 landscape frontmatter 有 `mandatory_authors: [name1, ...]`，每个 name 生成 1 组 `<name> <target / claim 核心>` query，并用 `--year <target_year>-<current_year>`（target year 未知则不限制）防止关键作者/实验室的新证据漏掉。

每组 query 加 `--max 15`; 仅在 A4 已可靠判断 domain 时加 `--domain <domain_arg>`，仅 recent query 加动态 `--year`。后续轮次 A4 不重跑，关键词由 B7 喂入，但若任一 axis 在某轮 B7 派生候选 = 0，下轮 B1 必须显式补一个该 axis 的新 query。

## B. 主循环

```
LOOP:
  B0. Web search 辅助发现（增量补充，非主导）
  B1. arxiv-tool 并行搜索（主导）
  B2. 合并 B0 候选 + B1 结果 → 去重，除 already_read_ids
  B3. 选 6-8 篇最相关（宁多勿漏）
  B4. 选不出、语义收敛或达到安全上限 → 终止
  B5. 并行派 agent 读全部选中论文（有几篇派几个 agent）
  B6. 等全部完成，读 /tmp/$USER/*-deep-lit-reader-*-result.json 收集结果
  B7. 从 wiki 中提新关键词
  B8. 更新收敛状态, 加引文/反引文搜索 → 下一轮
```

### B0. Web search 辅助发现（增量）

**定位**：arxiv-tool 是唯一权威文献来源。WebSearch 仅用于发现 arxiv-tool 可能漏掉的候选 arxiv_id（标题变更、社区别名、不在 arXiv/S2/OpenAlex 索引中的情况）。WebSearch 产出的每一条候选都必须过 arxiv-tool `info` 验证，验证不通过的直接丢弃。

**时机**：每轮循环 B1 之前跑一次。首轮和后续轮次都执行；产出为 0 也继续 B1。

用当前活跃关键词拼一组面向 web 的 query（更口语化、更社区导向，与 B1 的学术 query 互补）：
```
"<target title or method> reproduction replication arxiv"
"<target artifact or dataset> github issue benchmark metric"
"<target author/lab> <claim keyword>"
```

非 arxiv 索引的 corner-case 来源也必须扫一遍（arxiv 不索引但本领域常发新工作处）：
```
site:github.com "<target artifact or repo>" issue OR bug OR reproduce
site:huggingface.co/datasets OR site:huggingface.co/spaces "<target dataset or benchmark>"
site:openreview.net "<target title or method>"
"<target title or method>" correction OR erratum OR retraction OR critique
"<target benchmark or metric>" leaderboard OR replication
```

每组 query → `WebSearch`。从返回结果中提取：
- 直接出现的 arxiv ID（如 `arXiv:2411.17335` 或 `/abs/2411.17335`）
- 论文标题中包含的技术名词，可追问 `WebSearch "<paper title> arxiv"` 确认 ID

收集到候选 arxiv_id 列表后，逐条过筛子：
```bash
uv run arxiv_tool.py info <id>
```
- `info` 成功返回且标题/摘要与 topic 相关 → 保留，记入 `web_candidates`
- `info` 失败或无关 → 丢弃
- 已经在 `already_read_ids` 中 → 丢弃

**重要**：B0 是纯增量。B1 的 arxiv-tool 搜索完全不受影响，独立并行运行。B0 产出为 0 也不阻塞流程。

### B1. arxiv-tool 并行搜索（主导）

每个活跃关键词一个 Bash，全部并行：
```
uv run arxiv_tool.py search "<query>" --max 15 [--domain <domain_arg>] [--year <dynamic-range-for-recent-query>]
```

各搜索间 sleep 3 秒防 rate limit。某搜索返回空或超时 → 跳过继续。

### B2. 汇总 + 去重

合并 B1 的 arxiv-tool 搜索结果 + B0 的 `web_candidates`（已验证过的）。按 arxiv_id 去重。排除 `already_read_ids`。每个结果记：arxiv_id, title, year, abstract（前 300 字）、来源（arxiv-tool / web）。B0 候选与 B1 结果重复时优先保留 B1 的完整 metadata。

### B3. 选择最相关的一批

选择标准（按优先级）：
1. 标题/摘要与 target claims、target artifact、target benchmark 有直接交集
2. 明确报告 reproduction / replication / correction / critique / artifact use / benchmark protocol
3. 直接引用 target paper/case 或使用其 artifact
4. 接近 `current_year` 的新工作（只作同等相关性下的次级排序）
5. S2 citation ≥ 20
6. 在 topic 已知引用列表中出现过

**选 6-8 篇。** 符合标准的不足 6 篇 → 有几篇选几篇。一篇都没有 → 终止。**不确定是否相关 → 选上。宁多勿漏。**

### B4. 终止判断

- B3 选出论文数 = 0 且本轮主要搜索成功返回 → `candidate_saturated`, 跳到 C。若主要搜索因工具、网络或 rate limit 全部失败, 使用 `search_failed`, 跳到 C, 不声称饱和。
- 已完成 4 轮或本次累计新读达到 32 篇 → `budget_limited`, 跳到 C；保留尚未读候选供下一次 tick, 不声称搜索饱和。
- 已有连续两轮 B6 没有产生新的 load-bearing evidence、claim 状态变化、failure attribution 线索或可执行检查轴, 且新候选只是在重复已覆盖主题 → `evidence_saturated`, 跳到 C。

不得因为“论文很多”无限沿宽泛标题词扩展；也不得把安全上限写成证据饱和。

### B5. 并行派 agent 读全文

对 B3 选出的**每一篇**论文，先检查是否已有结果 JSON（resume）：
```bash
cat /tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json 2>/dev/null | grep -c '"status"' || echo 0
```

只有 JSON status 为 `wiki_written` / `already_read`，且对应 wiki 真存在并含本 topic 的 `## Read by:` marker 时才跳过 dispatch。`tex_download_failed`、缺 wiki、缺 marker、空 summary 或其他失败状态都必须恢复/重试, 不能被旧 JSON 永久缓存成成功。

否则按 `lit_reader_model` 和 dispatch_manual 调用 `deep-lit-reader` reader：

```bash
AGENT_PROMPT="${CLAUDE_PLUGIN_ROOT}/agents/deep-lit-reader.md"
TASK_PROMPT="arxiv_id: <arxiv_id> topic_slug: <topic_slug> CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}"
OUT="/tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>.txt"
```

- `lit_reader_model = "claude"` (默认): 用 claude 模板.
- `lit_reader_model = "deepseek"`: 用 claude-* 模板，命令名 `claude-ds`.
- `lit_reader_model = "codex"`: 用 codex 模板.

B5 派发 reader 后必须等待所有 subagents 返回，并确认每篇论文的 result JSON 存在且非空。缺失、空文件、缺 wiki/marker 或失败 status 的 reader 在本 tick 内最多恢复/重试 3 次；每次重试前先把错误记入本轮诊断, 再删除会误触发 resume 的失败/stale JSON。3 次后仍失败时, 把该 paper 和错误写入 Errors, 将本 tick 的 termination_reason 置为 `search_failed`, 继续收集其他已成功 reader 以便缓存和集成, 但不得声称本轮 source handoff 成功。禁止在 reader 仍是 Claude Bash 后台任务时输出完成或退出。

### B6. 收集结果

逐个检查 `/tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json`：

```bash
cat /tmp/$USER/<topic_slug>-deep-lit-reader-<arxiv_id>-result.json 2>/dev/null || echo '{"status":"no_result_file"}'
```

对每个结果：
- `wiki_written` → 读 `summary` 字段，加入 `already_read_ids`，收集 `top_related_keywords_for_next_search`
- `already_read` → 加入 `already_read_ids`
- `tex_download_failed` → 记入 errors
- `no_result_file` 或缺少 `summary` → 读 `/tmp/$USER/<topic_slug>-deep-lit-reader-<id>.txt` 尾部 50 行，记入 errors

结果和必要错误信息收集完后删除本 tick 创建的 reader transcript/prompt 文件；保留 result JSON 供同一 tick/上层重试 resume, 不删除共享 wiki。

### B7. 反向扩展（mandatory，违反即 tick 失败）

对 B6 **每篇** wiki_written 论文必须跑四项反向扩展：

```bash
uv run arxiv_tool.py references <id>           # 正引：该 paper 引了谁
uv run arxiv_tool.py cited <id> --source s2    # 反引：谁引了该 paper
```

```
# Author chase: 通讯/一作从 target_year 到 current_year 的 target-claim 相关 paper
uv run arxiv_tool.py search "<author last name> <target claim or artifact keyword>" --max 10 [--year <target_year>-<current_year>]

# Title-term chase: paper 标题里的独特术语直接 search 同名/衍生
uv run arxiv_tool.py search "<unique term from title>" --max 10
```

从全部输出提新 arxiv_id，加入下一轮候选池。再加 B6 收集到的 `top_related_keywords_for_next_search`（去重）。

四项调用数必须 ≥ wiki_written 数 × 4, 不到的在 errors 标 `B7_DISCIPLINE_VIOLATED`, E 段自检会查。

### B8. 继续循环

若存在 3 次恢复后仍失败的 selected reader, 保持 `termination_reason=search_failed`, 在完成成功 reader 的 B7 扩展后跳到 C；不要再开新一轮掩盖这个 source failure。

比较本轮 reader summaries 与已有 landscape/ledger：若出现新的 load-bearing evidence、claim 状态变化、failure attribution 线索或可执行检查轴, 将 `no_new_evidence_rounds` 置 0；否则 `+1`。记录尚未读取的直接相关候选。然后跳回 B1。

## C. 汇总

循环终止后生成报告。读所有 wiki 文件中 `## Read by: <topic_slug>` 的内容，汇总 prior evidence 和 reliability signals。

```
# Deep Literature Review — <topic_slug> — YYYY-MM-DD

## 循环统计
| 轮次 | 搜索数 | 新论文 | 选中读全文 | Wiki 写入 | 新关键词 |
|------|--------|--------|-----------|----------|---------|
| ...

## 已读论文清单
[每个 wiki 一行：arxiv_id, title, year, claim relevance, reliability signal, 关键发现]

## 本次新增论文（供上层并入 landscape）
[本次 tick 新读、之前不在 landscape 的每篇一行：arxiv_id | title | year | 一句话解读 | 与哪个 claim/baseline 相关]

## Claim Evidence Map
[每个 target claim 一行：支持/削弱/反驳/不可判定的 prior evidence]

## 可用新工具/方法

## Errors
```

## D. 终止条件判断

```
<verdict>
核心 claims 逐一评估：
- Claim 1: [prior evidence status] [证据]
...
总体：证据是否足以支撑当前 landscape 饱和判断；哪些 claim 仍需要实验或 investigation 继续验证。
termination_reason: candidate_saturated / evidence_saturated / budget_limited / search_failed
若为 budget_limited, 列出尚未读取的最高优先候选和下一次 deep-lit 应从哪里恢复。
若为 search_failed, 列出失败命令和错误；上层必须重试, 不能把它当作完成的 source handoff。
</verdict>
```

## E. Wiki / expansion 自检（强制）

自检不通过禁止进入集成和 commit：

```bash
# 1. 每篇 wiki_written 必须真存在且 ≥ 50 行（wiki 池）
for id in $WIKI_WRITTEN_IDS; do
  test -f "$ARXIV_WIKI_DIR/$id.md" && [ "$(wc -l < "$ARXIV_WIKI_DIR/$id.md")" -ge 50 ] \
    || { echo "FAIL: $ARXIV_WIKI_DIR/$id.md 缺失或 < 50 行"; exit 1; }
done

# 2. B7 反向扩展调用数 ≥ wiki_written × 4 (references + cited + author + title)
[ "$B7_CALLS" -ge $((${#WIKI_WRITTEN_IDS[@]} * 4)) ] \
  || { echo "FAIL: B7 调用 $B7_CALLS < $((${#WIKI_WRITTEN_IDS[@]} * 4)), 违反 red_line #5"; exit 1; }
```

## F. 集成（写进 landscape 或 literature-ledger）

把本次新读论文逐篇落到位，一篇也不漏，解读到位。

[topic] scope：
- 写或创建 `topics/<topic_slug>-landscape.md`：每篇新论文归档 + 解读（arxiv_id、关键发现、与 target claims 的关系、prior evidence、artifact risk、metric/protocol risk）。landscape 允许膨胀，相关论文宁多勿漏。

[experiment] scope：写两处，职责不重叠。
- **文献总账** `workspace/<workspace_slug>/literature-ledger.md`：本次搜出的**全部**新文献逐篇追加并解读（arxiv_id、关键发现、与本实验哪个 claim/baseline 相关），确保事后能追溯"搜过些什么"，一篇不漏。允许膨胀。
- **共享 inbox** `workspace/<workspace_slug>/lit-feed.md`：只写命中 STATE.md 当前急需问题的条目。每条写清 `intended_reader: scientist / both`、`consumed_by: []`、`scope: experiment`、它解决哪个急需问题、搜到的解决方案/工具/垫脚石、来源（arxiv_id 与 wiki 路径）。不命中急需问题的论文不进 inbox（它们已在总账里）。写完把 frontmatter `unprocessed` 设为仍至少有一个 intended_reader 未消费的条目数。inbox 是流动收件箱，由下游 agent 按角色消费后清空，本步骤不做沉淀。

[investigation] scope：写三处，职责不重叠。
- **workspace landscape** `workspace/<workspace_slug>/landscape.md`：创建或更新 reliability landscape。它是 investigator 的 source view, 不是 experiment plan。开头必须绑定 target paper/case 的 exact id、本次 target full-text wiki/source 和 reader summary；随后包含已读论文索引、prior evidence、artifact/data/benchmark risk、metric/protocol risk、cherry-pick/overclaim/narrow-validity 线索、可执行外部检查路线。首次创建时用清楚的标题和 frontmatter, 之后增量合并, 不覆盖已有重要事实。
- **文献总账** `workspace/<workspace_slug>/literature-ledger.md`：本次搜出的**全部**新文献逐篇追加并解读（arxiv_id、关键发现、与哪个 INVES question / claim / artifact / benchmark / overclaim 轴相关），确保事后能追溯"搜过些什么"，一篇不漏。
- **共享 inbox** `workspace/<workspace_slug>/lit-feed.md`：写命中 INVES 当前问题、audit issue、review required check 或可执行检查路线的条目。每条写清 `intended_reader: investigator / scientist / both`、`consumed_by: []` 和 `scope: investigation`。写完把 frontmatter `unprocessed` 设为仍至少有一个 intended_reader 未消费的条目数。

写完自检：C 段报告里列出的每一篇"新增论文"都已落到对应目标文件（landscape / literature-ledger），无遗漏；[experiment] scope 额外确认 inbox 条目都对应 STATE.md 里某个真实的当前急需问题；[investigation] scope 额外确认 inbox 条目都对应 INVES question / audit issue / review required check / artifact-data-benchmark 线索之一, 且每条标明 intended_reader / scope。

## G. Commit（集成后）

wiki 已写入 `$ARXIV_WIKI_DIR`, 不提交共享 wiki 池。先进入拥有这些文件的正确 git repo, 再只显式 add 当前 scope 实际修改的文件, 禁止 `git add .`:

- [topic]: 保持在数据 repo 根目录, 先按 training_data_manual §5A 获取短时 data-repo write lock，只 add
  `topics/<topic_slug>-landscape.md`，并用 `git commit --only -- topics/<topic_slug>-landscape.md`
- [experiment]: `cd workspace/<workspace_slug>`, add `literature-ledger.md`、`lit-feed.md`
- [investigation]: `cd workspace/<workspace_slug>`, add `landscape.md`、`literature-ledger.md`、`lit-feed.md`

确认 staged diff 不含其他 agent 的状态、results、大文件、cache 或 ignored logs 后, commit: `deep-lit <topic_slug>: +N wiki entries across K rounds`。没有 tracked 变化时报告 no-op, 不制造空 commit。

最终输出在 C/D 汇总后追加 `Integration / Commit`: 列出 scope outputs、实际 owning git repo、commit hash 或明确 no-op。上层 dispatcher 依赖这段检查 handoff。

## Rules

- 你不读论文。论文阅读是 deep-lit-reader agent 的事。
- 正式文献搜索和候选核验走 arxiv-tool；WebSearch 只按 B0 发现候选, 未经 arxiv-tool 核验不得使用。绝对不编造论文。
- B3 选出的论文全部要派 agent，不许跳过任何一篇。
- 搜索间 sleep 3 秒防 rate limit。
- 单个搜索请求失败不中断整个循环；B3 已选论文的 reader 失败必须按 B5 重试或明确进入 Errors, 不能静默遗漏。

## Learning Record（强制）

完成 C/D/F/G 的正常汇总、集成和 commit handoff 后，读取
`${CLAUDE_PLUGIN_ROOT}/templates/learning-record-template.md`。最终回复末尾必须返回且只返回一个
`record_type=source_discovery` 的 `<learning_record>`，如实列出搜索轴、实际精读和集成的 sources、
remaining gaps、termination reason 与 evidence refs。不要直接写父数据仓库的 `training/`；外层 dispatcher
负责保存。缺失或不可解析的 learning record 视为 source handoff 未完成。
