# Prompt patch candidates: <case-or-project>

本文件只记录候选改动，不直接修改 live prompt。单个 case 只能提出候选，不能证明全局能力提高。

## Candidate <ID>

| field | value |
|-------|-------|
| target role/prompt | |
| repeated failure | |
| source event IDs | |
| human feedback refs | |
| audit/evidence refs | |
| current policy version | |
| proposed scope | this_case / this_role / all_cases / system |

### Why the current prompt failed

<!-- 指向具体缺规则、歧义、冲突或执行失败；不要把单次偶然错误包装成通用规律。 -->

### Minimal patch

```text
要增加、删除或改写的最少文字
```

### Expected behavior change

<!-- 改完后应该少犯什么错；什么观察会证明 patch 无效。 -->

### Risks

<!-- 可能造成的偷懒、过度约束、false accusation、证据质量下降或角色越界。 -->

### Held-out check

<!-- 用没有参与生成本候选的 base case 比较 before/after；未验证前写 pending。 -->

### Status

`candidate | testing | accepted | rejected | superseded`
