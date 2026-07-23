---
unprocessed: 0                        # 仍至少有一个 intended_reader 未消费的条目数
---

# Lit Feed: [slug]

<!--
lit-feed.md: 共享文献/工具 inbox (收件箱), 不是知识库。
experiment-scope deep-lit、investigation-scope deep-lit、investigator direct reader 都往这里投递命中当前可靠性审查问题的条目。
investigation 先于 experiment：investigation-scope 条目可给 investigator、后续 scientist 或两者；
experiment-scope 条目只给 scientist。角色处理后把自己加入 `consumed_by`；所有 intended_reader 都已消费时删除条目并更新 unprocessed。

与同目录文档的分工:
- wiki (`$ARXIV_WIKI_DIR/`): 每篇论文全文精读笔记, 长期沉淀。wiki 池位置由 `$ARXIV_WIKI_DIR` 配置。
- workspace 内 literature-ledger.md: deep-lit 搜出的全部新文献/工具总账 (一篇不漏, 可追溯), 长期归档, 允许膨胀。
- 本文件 (inbox): 只装命中当前急需问题的条目, 流动, 处理完即清空, 不沉淀。条目必须标明 intended_reader: scientist / investigator / both。

inbox 永远是空或近空。膨胀的东西在 literature-ledger.md 总账和 wiki, 不在这里。
不要删除本注释, 一直保留作为本文件的填写指引。
-->

## Inbox

<!-- deep-lit / investigator direct reader 每条按下面格式追加。一个角色消费后先更新 consumed_by；只有所有 intended_reader 都出现后才整条删除。

### [arxiv_id or tool_id] 一句话标题
- intended_reader: scientist / investigator / both
- consumed_by: [] / [scientist] / [investigator] / [scientist, investigator]
- scope: experiment / investigation / both
- 解决哪个急需问题: [对应 STATE.md claim / INVES question / failure attribution / artifact gap / metric mismatch / baseline / overclaim / cherry-pick]
- 解决方案/工具/垫脚石: [它提供了什么可直接用的证据、协议、工具或对比]
- 来源: arxiv_id + wiki 路径 (`$ARXIV_WIKI_DIR/<id>.md`, 可打开看全文细节)
-->
