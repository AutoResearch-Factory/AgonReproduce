#!/usr/bin/env python3
"""Filter claude -p --output-format stream-json into human-readable live log.

Usage: claude -p ... --output-format stream-json --verbose | tee raw.jsonl | python3 stream-filter.py > live.log

Extracts: tool calls (name + first 80 chars of input), assistant text, result summary.
"""
import json, sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        continue

    t = obj.get("type")

    if t == "assistant":
        msg = obj.get("message", {})
        for block in msg.get("content", []):
            if block.get("type") == "text":
                print(block["text"], flush=True)
            elif block.get("type") == "tool_use":
                name = block.get("name", "?")
                inp = json.dumps(block.get("input", {}), ensure_ascii=False)
                if len(inp) > 120:
                    inp = inp[:120] + "..."
                print(f"[TOOL] {name}: {inp}", flush=True)

    elif t == "result":
        result = obj.get("result", "")
        cost = obj.get("total_cost_usd", 0)
        turns = obj.get("num_turns", 0)
        dur = obj.get("duration_ms", 0)
        print(f"\n[DONE] {turns} turns, {dur/1000:.0f}s, ${cost:.4f}", flush=True)
        if result:
            # Print first 500 chars of result
            r = result[:500] + ("..." if len(result) > 500 else "")
            print(r, flush=True)
