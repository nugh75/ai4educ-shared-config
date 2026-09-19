#!/usr/bin/env python3
"""Claude PreToolUse adapter: request CLI conversion without reading the PDF.

Do not convert or redirect inside PreToolUse: it runs before permissions are
checked, and rewriting file_path would evaluate rules against the new path.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import sys


def response(event):
    if os.environ.get("PDF2MD_NATIVE_READ") == "1":
        return None
    if event.get("hook_event_name") != "PreToolUse" or event.get("tool_name") != "Read":
        return None
    params = event.get("tool_input", {})
    name = params.get("file_path", "")
    if not isinstance(name, str) or Path(name).suffix.lower() != ".pdf":
        return None
    source = Path(name).expanduser()
    if not source.is_absolute():
        source = Path(event.get("cwd", os.getcwd())) / source
    pages = str(params.get("pages") or "")
    key = hashlib.sha256((str(source) + "\0" + pages).encode()).hexdigest()[:24]
    cache = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "pdf2md"
    output = cache / f"{key}.md"
    cli = Path(__file__).resolve().with_name("pdf2md")
    command = [str(cli), str(source), "-o", str(output)]
    if pages:
        command += ["--pages", pages]
    instruction = (
        "Read this PDF as extracted Markdown first. Run the following command through "
        "the normal shell tool and its permission checks, then Read the Markdown file: "
        f"mkdir -p {shlex.quote(str(cache))} && {shlex.join(command)}\n"
        "The converter does not interpret figures or perform OCR. For visual inspection, "
        "render the requested PDF pages with an available tool; PDF2MD_NATIVE_READ=1 "
        "disables this hook for native PDF reads."
    )
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": instruction,
    }}


def main():
    try:
        result = response(json.load(sys.stdin))
        if result:
            print(json.dumps(result))
    except (ValueError, TypeError, AttributeError) as exc:
        print(f"pdf2md hook: payload non valido ({exc})", file=sys.stderr)


if __name__ == "__main__":
    main()
