---
batch_id: ""
case_id: ""                       # global scope 写 null
scope: case                       # case | global
status: needs_maker               # needs_maker | needs_reviewer | needs_maker_fix | sealed
trigger: ""
raw_line_start: 0
raw_line_end: 0
feedback_line_start: 0
feedback_line_end: 0
maker_round: 0
reviewer_round: 0
latest_maker_attempt: ""
latest_review_attempt: ""
seal_state: open                  # open | receipt_pending | complete
sealed_content_commit: ""        # receipt_pending 时写 pending_dispatcher_content_commit
created_at: ""
sealed_at: ""
---

# 本次训练数据整理批次

## 本批固定了哪些原始记录

- 本批使用的固定 base case / dataset split：

| kind | path | line range / IDs | hash |
|------|------|------------------|------|

## Maker 生成了哪些文件

| file | rows | label quality | rights | status |
|------|------|---------------|--------|--------|

## Reviewer 通过后准备发布成什么

| file | rows | sha256 | source accepted/review refs | disposition |
|------|------|--------|-----------------------------|-------------|

<!-- maker 写 current-projection candidate；fresh reviewer 全部 accept 后 dispatcher 才发布到正式 current/. -->
<!-- rows/sha256 必须由 maker、reviewer、dispatcher 分别从实际文件重算；不能复制上一角色的摘要。 -->

### 旧格式是否经过受控补齐

<!-- 逐行列出 legacy source row hash -> projection row hash；只允许补缺失的 supersedes_sample_ids=[]。 -->

## Maker 交接

<!-- 生成了什么；哪些关联仍不确定；哪些内容明确未进入正训练集。 -->

## Reviewer 交接

<!-- review.jsonl 路径；accept/fix/reject/uncertain 数量；fix 的具体要求。 -->

## 本批封存记录

<!-- 每条候选都有 disposition 后填写。sealed 只结束本数据批次，不结束科研 loop。 -->
