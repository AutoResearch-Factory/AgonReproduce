#!/usr/bin/env python3
"""STATE.md YAML frontmatter get/set/validate tool.

Replaces ad-hoc sed/awk parsing with correct YAML value handling.
Preserves field order and body content on writes.

Usage:
    state-tool.py get      <state-file> <field>
    state-tool.py set      <state-file> <field> <value>
    state-tool.py validate <state-file>
"""
import os
import re
import sys


VALID_PHASES = {
    "needs_scientist",
    "coding_and_running",
    "needs_auditor",
    "needs_reviewer",
    "needs_dataset",
    "needs_litfeed",
}


def _split(text):
    """Split STATE.md into (frontmatter_lines, body).

    Returns (None, None) if format is invalid.
    """
    m = re.match(r"^---\n(.*?\n)---\n?(.*)", text, re.DOTALL)
    if not m:
        return None, None
    return m.group(1).splitlines(), m.group(2)


def _strip_inline_comment(val):
    """Strip a YAML comment while preserving # inside quoted scalars."""
    quote = None
    escaped = False
    for i, char in enumerate(val):
        if escaped:
            escaped = False
            continue
        if quote == '"' and char == "\\":
            escaped = True
            continue
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            continue
        if char == "#" and quote is None and (i == 0 or val[i - 1].isspace()):
            return val[:i].rstrip()
    return val.rstrip()


def _unquote(val):
    """Strip inline comments and surrounding YAML quotes."""
    val = _strip_inline_comment(val.strip())
    if len(val) >= 2:
        if (val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'"):
            return val[1:-1]
    return val


def get_field(state_path, field):
    with open(state_path) as f:
        lines, _ = _split(f.read())
    if lines is None:
        return ""
    prefix = field + ":"
    for line in lines:
        if line.startswith(prefix):
            val = line[len(prefix) :].strip()
            return _unquote(val)
    return ""


def set_field(state_path, field, value):
    with open(state_path) as f:
        text = f.read()
    lines, body = _split(text)
    if lines is None:
        print("ERROR: Invalid STATE.md format", file=sys.stderr)
        sys.exit(1)

    prefix = field + ":"
    found = False
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            lines[i] = f"{field}: {value}"
            found = True
            break
    if not found:
        lines.append(f"{field}: {value}")

    tmp = state_path + ".tmp"
    with open(tmp, "w") as f:
        f.write("---\n")
        f.write("\n".join(lines))
        f.write("\n---\n")
        f.write(body)
    os.rename(tmp, state_path)


def validate(state_path):
    with open(state_path) as f:
        lines, _ = _split(f.read())
    if lines is None:
        sys.exit(1)
    phase = ""
    for line in lines:
        if line.startswith("phase:"):
            phase = _unquote(line[len("phase:") :].strip())
            break
    if phase not in VALID_PHASES:
        print(f"ERROR: invalid or missing phase: {phase!r}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    state_path = sys.argv[2]

    if cmd == "get":
        print(get_field(state_path, sys.argv[3]))
    elif cmd == "set":
        set_field(state_path, sys.argv[3], sys.argv[4])
    elif cmd == "validate":
        validate(state_path)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
