---
name: report
description: 从当前已评审证据一次性生成最终可靠性 REPORT.md.
argument-hint: "[workspace-slug]"
---

You are a dispatcher. 你只验证 checkpoint、fresh 调用 `reliability-reporter`、保存 trace 并触发一次数据整理；
不做科学判断，也不把本命令变成 loop。

## 启动检查

1. 按 `investigation-tick` 的规则把输入规范化为 data repo `workspace/` 的直接子目录 slug，并原子获取同一个
   `.agent-sessions/loop-locks/<slug>.lock`，owner 写 `loop=report`。已有 lock 时停止。
2. 读取 `${CLAUDE_PLUGIN_ROOT}/references/` 下的 `training_data_manual.md`、`project_manual.md`、
   `experiment_manual.md` 和 `dispatch_manual.md`。
   严格执行 training manual §5A A/B/F：保存本次用户消息和 startup event；每次 parent repo 写入都使用
   data-repo write lock。
3. 读取 `.settings.toml` 的 `reviewer_model`，完全复用 `experiment-tick` 的 reviewer routing/fallback。
   Reporter 不需要 env-validator，不探测服务器。
4. 要求 nested workspace 当前 branch=`main`，tracked worktree clean，`INVES.md` 存在。
5. 读取 INVES frontmatter，要求 `inves_review_verdict=ready`、`latest_inves_review` 非空且可打开；用
   `git log -1 --format=%H -- <path>` 分别检查 INVES 和该 review，两个非空 commit 必须相同。
6. 若 STATE 不存在，设 `experiment_status=not_performed`。若 STATE 存在，禁止把它当成“未做实验”：
   要求 frontmatter `git_branch=main`、`phase=needs_litfeed`，文件内恰有一个完整 `<review>...</review>`，
   verdict=`ready`，且最近一次修改 STATE 的 commit subject 符合 experiment reviewer commit 格式；否则停止。

任一检查失败时不要创建或覆盖 REPORT。没有 active child 后记录失败并释放自己的 lock。

## Dispatch

记录 `before_commit`，按 training manual §5A C 和 dispatch manual fresh 调用
`${CLAUDE_PLUGIN_ROOT}/agents/reliability-reporter.md`：

```text
slug: <slug>
workspace: <absolute workspace path>
training_dir: <absolute training dir>（父数据仓库，只读；禁止写）
relevant_human_feedback_refs: [本轮真实 IDs；没有则 []]
experiment_status: performed | not_performed
evidence_snapshot: <before_commit>
CLAUDE_PLUGIN_ROOT: <absolute plugin root>
```

使用 `reviewer_model`，永远不 resume。返回后按 §5A D 保存 raw output 和
`actor_role=reporter,event_type=report` event，验证其 `record_type=decision`，再核对：

- `REPORT.md` 存在且 frontmatter/八个正文 section 完整；
- nested repo 恰有一个新 commit；
- `before_commit..HEAD` 只修改 `REPORT.md`；
- tracked worktree clean。

失败时留下 failed event，再按 dispatch manual 调查；连续失败三次才报告用户。

成功后，在没有 active child 时按 training manual §8A 串行运行
`training-data-tick <slug> reporter`，沿用并验证本 report lock。handoff 完成后核对 owner、释放自己的 lock，
向用户返回 REPORT 路径、总评和 commit。不要修改 STATE、INVES 或 REPORT。

任何最终退出都只在确认没有 active child、owner 仍属于本 dispatcher 后释放自己的 lock；不删除其他 owner 或
未经审计的 stale lock。
