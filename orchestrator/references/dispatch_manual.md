## How to start a claude-*/codex subagent?

本文档教你如何用命令行启动 claude、codex 和可选的 Claude-compatible wrapper 作为 subagents.

下列 permission-bypass flags 只能在已经隔离、专用于当前 case 的执行环境中使用。运行陌生论文代码时，先遵守
`servers_manual.md` 和 `SECURITY.md` 的隔离要求；这些 flags 本身不是 sandbox。

首先你需要准备:
- AGENT_PROMPT="${CLAUDE_PLUGIN_ROOT}/agents/${AGENT_NAME}.md"
- TASK_PROMPT="本次具体任务指令"
- OUT="/tmp/$USER/${problem-slug}-${AGENT_NAME}-${time:hhmmss}.txt"

调用返回后先读取 `$OUT` 作为 response, 再 `rm "$OUT"` 防止之后混淆.

codex 的 session id 打印在 stderr banner 里. 加 `2>&1` 合并到 stdout, 用 `grep 'session id:' | awk '{print $NF}'` 提取. Resume 时传入该 id.

### codex

Codex CLI 没有 `--append-system-prompt-file`. 同时传 argv prompt 和 stdin 时,
stdin 只会被追加成 `<stdin>` 块, 不会成为 system message。为防止 role prompt 被放在
task 后面或被弱化, 先构造一个 role-first 的临时 prompt, 再从 stdin 传给 Codex:

```
PROMPT_FILE="/tmp/$USER/${problem-slug}-${AGENT_NAME}-${time:hhmmss}.prompt"
cp "$AGENT_PROMPT" "$PROMPT_FILE"
printf '\n\n<task>\n%s\n</task>\n' "$TASK_PROMPT" >> "$PROMPT_FILE"

codex exec --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.6-sol -c model_reasoning_effort=max \
  --output-last-message "$OUT" \
  - < "$PROMPT_FILE" 2>&1

rm "$PROMPT_FILE"
```

Resume 已有 session:

```
codex exec resume --dangerously-bypass-approvals-and-sandbox \
  -m gpt-5.6-sol -c model_reasoning_effort=max \
  --output-last-message "$OUT" \
  "<session_id>" \
  "$TASK_PROMPT" \
  2>&1
```

`resume` 只用于恢复同一次被中断的 role dispatch, 且必须使用刚才记录的明确
session id。跨 iteration 的 scientist/auditor/investigator 依靠 STATE/INVES/log/audit
接力, 重新 fresh 启动；不要用 cwd 最近会话或 `--last` 猜 session。

## claude & claude-*

```
claude --dangerously-skip-permissions \
  --plugin-dir "${CLAUDE_PLUGIN_ROOT}" \
  --output-format json \
  --effort max \
  --append-system-prompt-file "$AGENT_PROMPT" \
  -p "$TASK_PROMPT" > "$OUT"
```

Resume 已有 session:

```
claude --dangerously-skip-permissions \
  --plugin-dir "${CLAUDE_PLUGIN_ROOT}" \
  --output-format json \
  --effort max \
  --resume "<session_id>" \
  -p "$TASK_PROMPT" > "$OUT"
```

可选 wrapper 与 claude 接口保持一致。`deepseek` route 使用 `claude-ds`，`kimi` route 使用
`claude-kimi`；只有本地已安装且 `.settings.toml` 启用时才调用。

`codex`/`claude` 用 `nohup ... 2>&1 &` 跑; `claude-*` 用 Bash background (run_in_background) 跑; 总之尽量绕过前台 Bash tool 调用的 10 分钟上限.
