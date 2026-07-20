# AgonReproduce

[English](README.md)

AgonReproduce 是一个以提示词为核心的科研可靠性审查系统。它把文献调查、直接实验复现、独立审查、人类纠正和训练数据整理放进同一条可追踪流程。

项目仍在持续开发。系统输出的是科研证据和可靠性判断，不是对学术不端的自动裁决。

## 核心流程

```text
目标论文
  -> investigation loop
  -> experiment loop
  -> investigation loop
  -> reliability report

每个检查点
  -> raw trace + human feedback
  -> dataset maker
  -> independent dataset reviewer
  -> reviewed training projections
```

当前 v0 不包含 report-writing factory。最终文字报告由人类或后续 report agent 根据统一证据账本和两个 domain reviewer 的输出汇总。

两条科研 loop 共用同一个 case workspace，但状态彼此分开：

- `INVES.md` 记录文献、artifact、benchmark、引用关系、适用范围和其他外部可靠性检查。
- `STATE.md` 记录直接执行、数值复现、稳健性测试和实验性证据。

两条 loop 都持续运行，直到人类叫停或改变方向。Reviewer 的 `ready` 只是检查点，不会自动终止科研。

## 设计原则

- **提示词优先。** 核心 agents 和 commands 都是 Markdown 提示词；少量脚本只负责状态校验和输出过滤。
- **最小协议。** 只有在缺少某条规则会导致具体失败时，才增加规则。
- **Claim-level evidence。** 稳定的 claim/evidence ID 连接调查、实验、review 和训练记录。
- **角色边界清楚。** Producer、auditor、reviewer 和 dataset agent 各自拥有明确的读写权限。
- **Human feedback 是一等数据。** Dispatcher 会话中的人类纠正与其落实过程、结果一起保留。
- **不自动指控。** 执行失败、artifact 失败、环境失败和论文 claim 被反驳是不同结论。

当前运行协议见
[`orchestrator/references/project_manual.md`](orchestrator/references/project_manual.md)。

## 仓库边界和名称

本仓库只保存可复用的框架提示词和通用模板。真实 case、执行 trace、human feedback、凭证和私人基础设施配置全部放在独立的私有 artifact 仓库。

名称固定如下：

- 产品和框架仓库：`AgonReproduce`
- 私有 case/artifact 仓库：`AgonReproduce-artifact`
- Claude Code plugin 和 skill namespace：`agon-reproduce`

小写 namespace 遵循公开版 `Agon` 仓库与 `agon` plugin namespace 的机器命名惯例，不是第二个产品名。

以下内容不得提交到框架仓库：

- `orchestrator/.settings.toml`
- `orchestrator/references/servers.local.md`
- API key、token、SSH 材料和私人主机信息
- 真实 case 数据、未审查模型输出和人类会话

## 启动

Clone `AgonReproduce`，然后创建或 clone 自己的私有 `AgonReproduce-artifact` 仓库。两个目录并列放置：

```text
.
├── AgonReproduce/
└── AgonReproduce-artifact/
```

1. 从 `AgonReproduce/orchestrator/.settings.example.toml` 创建本地且不入 Git 的
   `AgonReproduce/orchestrator/.settings.toml`。
2. 需要远程执行时，创建本地且不入 Git 的
   `AgonReproduce/orchestrator/references/servers.local.md`。
3. 安装 `project_manual.md` 列出的文献和写作 skills。
4. 从 artifact 仓库启动 Claude Code：

   ```bash
   cd AgonReproduce-artifact
   export CLAUDE_PLUGIN_ROOT="$(realpath ../AgonReproduce/orchestrator)"
   claude --plugin-dir "$CLAUDE_PLUGIN_ROOT"
   ```

5. 把目标论文 brief 写入 `topics/<slug>.md`，然后在 Claude Code 中运行
   `/agon-reproduce:investigation-tick <slug>`。

公开默认配置使用标准 `claude` 和 `codex` CLI。可选的 `deepseek` 和 `kimi` route 分别要求本地提供 `claude-ds` 和 `claude-kimi` 兼容 wrapper。

## 主要命令

- `/agon-reproduce:investigation-tick <slug>`：初始化 workspace 并运行 investigation loop。
- `/agon-reproduce:experiment-tick <slug>`：运行直接复现和实验审查。
- `/agon-reproduce:deep-lit-tick --scope investigation|experiment <slug>`：补充大规模文献证据。
- `/agon-reproduce:human-feedback-tick ...`：保存和落实人类纠正。
- `/agon-reproduce:training-data-tick <slug> <trigger>`：把固定检查点整理成经过 review 的训练数据。

## 安全和许可

目标论文代码和依赖都必须视为不可信代码。应在最小权限的隔离环境中执行，并且不能暴露无关凭证。详见 [SECURITY.md](SECURITY.md)。

AgonReproduce 使用 Apache-2.0 许可证。部分 refinery prompts 来自 MIT-licensed 项目，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
