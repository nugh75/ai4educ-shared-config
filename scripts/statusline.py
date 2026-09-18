#!/usr/bin/env python3
"""Status line per Claude Code — Token Optimization carta 1.1.

Mostra: directory | modello | % contesto | costo sessione.
La % di contesto è calcolata dall'ultimo usage nel transcript (input + cache).
Installato in ~/.claude/statusline.py; registrato in ~/.claude/settings.json.
"""
import json
import os
import sys

CONTEXT_WINDOW = 200_000


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    parts = []
    cwd = (data.get("workspace") or {}).get("current_dir") or ""
    if cwd:
        parts.append(os.path.basename(cwd))
    model = (data.get("model") or {}).get("display_name")
    if model:
        parts.append(model)

    # Context occupancy: ultimo usage presente nel transcript
    used = None
    tp = data.get("transcript_path")
    if tp and os.path.exists(tp):
        try:
            with open(tp) as f:
                for line in f:
                    try:
                        e = json.loads(line)
                    except Exception:
                        continue
                    u = (e.get("message") or {}).get("usage") or e.get("usage")
                    if u and u.get("input_tokens") is not None:
                        used = u
        except OSError:
            pass
    if used:
        ctx = (
            used.get("input_tokens", 0)
            + used.get("cache_read_input_tokens", 0)
            + used.get("cache_creation_input_tokens", 0)
        )
        pct = ctx / CONTEXT_WINDOW * 100
        parts.append(f"ctx {pct:.0f}% ({ctx // 1000}k/{CONTEXT_WINDOW // 1000}k)")

    cost = (data.get("cost") or {}).get("total_cost_usd") or 0
    if cost:
        parts.append(f"${cost:.2f}")

    print(" │ ".join(parts))


if __name__ == "__main__":
    main()
