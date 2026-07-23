# Learning record 模板

科研 subagent 在最终回复末尾返回一个 `<learning_record>`。只写与本角色直接相关的字段；不适用字段写空，
禁止为了填模板编造候选行动、成本或结论。JSON 必须单行、可解析。

模板字符串中的 `a|b|c` 只表示允许值列表。实际输出必须选一个值，禁止把带 `|` 的整串照抄进记录。
`</learning_record>` 必须是最终回复最后一个非空白内容；closing tag 后禁止追加总结、签名或任何文字。

## Scientist / Investigator / Reliability reporter

```text
<learning_record>
{"record_type":"decision","decision_summary":"本轮改变科研路线的决定","important_gap":"当前最重要的 evidence gap","alternatives":[{"action":"候选行动 A","reason_not_chosen":null},{"action":"候选行动 B","reason_not_chosen":"未选择原因"}],"chosen_action":"实际选择的行动","choice_reason":"可审计的简短理由","expected_observation":"预计看到什么","falsifier":"什么观察会推翻当前判断","claim_refs":[],"question_refs":[],"evidence_refs":[],"artifact_refs":[],"human_feedback_refs":[]}
</learning_record>
```

只写真正考虑过的 alternatives；没有就写空数组。Reporter 用同一格式记录最终 score/label 决定，
domain reviewer 的 readiness score 不能冒充该决定。

## Shared coder

```text
<learning_record>
{"record_type":"execution","decision_summary":"实际执行了什么","work_item_refs":[],"actions":["命令或检查摘要"],"execution_status":"succeeded|failed|blocked","expected":"计划应观察到什么","observed":"实际观察","mismatch":"expected 与 observed 的差异；没有则为 null","blocker":null,"claim_refs":[],"question_refs":[],"evidence_refs":[],"artifact_refs":[],"human_feedback_refs":[]}
</learning_record>
```

coder 只报告直接执行事实，不给 paper claim 下结论。

## Auditor

```text
<learning_record>
{"record_type":"audit","decision_summary":"本轮最重要的因果审计结论","audited_event_ids":[],"error_layer":"none|claim_decomposition|action_selection|execution|artifact|environment|data|metric|protocol|evidence_interpretation|failure_attribution|feedback_compliance|prompt_rule|unknown","chosen_action_assessment":"合理、不合理或证据不足，并说明依据","better_alternative":null,"feedback_compliance":"complied|violated|not_applicable|unknown","claim_refs":[],"question_refs":[],"evidence_refs":[],"artifact_refs":[],"human_feedback_refs":[]}
</learning_record>
```

## Domain reviewer

```text
<learning_record>
{"record_type":"review","assessment_domain":"experiment|investigation","decision_summary":"当前版本最重要的独立判断","reviewed_event_ids":[],"reliability_profiles":[{"claim_id":"C1","source_domain_verdict":"UNTESTED|SUPPORTED|PARTIAL|CONTRADICTED|NOT_REPRODUCIBLE|NOT_ASSESSABLE|OUT_OF_BUDGET|null","execution_status":"succeeded|failed|blocked|not_attempted","result_match":"matched|partial|mismatched|unknown","claim_verdict":"supported|partially_supported|contradicted|insufficient_evidence","failure_attribution":"paper_claim|artifact|environment|data|metric|protocol|our_bug|budget|unknown","confidence":0.0,"evidence_refs":[],"human_feedback_refs":[]}],"readiness_score":null,"readiness_verdict":"ready|almost|not_ready","claim_refs":[],"question_refs":[],"evidence_refs":[],"artifact_refs":[],"human_feedback_refs":[]}
</learning_record>
```

`assessment_domain` 必须由角色固定：experiment-reviewer 写 `experiment`，inves-reviewer 写 `investigation`。
experiment profile 的 `source_domain_verdict` 逐字记录对应 STATE claim verdict；investigation profile 写 `null`。
`readiness_score` 是当前过程质量，不是论文可靠性分。每个 claim 的四个 reliability 字段分别判断。

## Deep-lit tick

```text
<learning_record>
{"record_type":"source_discovery","decision_summary":"本轮搜索、精读和集成覆盖了什么","search_axes":[],"sources_read":[],"sources_integrated":[],"remaining_gaps":[],"termination_reason":"candidate_saturated|evidence_saturated|budget_limited|search_failed","claim_refs":[],"question_refs":[],"evidence_refs":[],"artifact_refs":[],"human_feedback_refs":[]}
</learning_record>
```
