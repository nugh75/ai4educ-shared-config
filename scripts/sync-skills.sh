#!/usr/bin/env bash
# Fan out every canonical skill into each agent's discovery root, so that
# Claude, Codex, pi and opencode all see the same skill set.
set -euo pipefail

AGENTS_ROOT="${AGENTS_SKILLS_ROOT:-$HOME/.agents/skills}"
WORKSPACE_ROOT="${WORKSPACE_SKILLS_ROOT:-$HOME/ai4educ-console/workspace-skills}"

SOURCE_ROOTS=("$AGENTS_ROOT" "$WORKSPACE_ROOT")
TARGET_ROOTS=(
  "${CLAUDE_SKILLS_ROOT:-$HOME/.claude/skills}"
  "$AGENTS_ROOT"
  "${PI_SKILLS_ROOT:-$HOME/.pi/agent/skills}"
  "${OPENCODE_SKILLS_ROOT:-$HOME/.config/opencode/skills}"
)

CHECK_ONLY=0
case "${1:-}" in
  --check) CHECK_ONLY=1 ;;
  "") ;;
  *) printf '%s\n' "usage: $(basename "$0") [--check]" >&2; exit 2 ;;
esac

names=()
sources=()
drift=0

source_for() {
  local wanted="$1" i
  for i in "${!names[@]}"; do
    if [[ "${names[$i]}" == "$wanted" ]]; then
      printf '%s\n' "${sources[$i]}"
      return 0
    fi
  done
  return 1
}

for root in "${SOURCE_ROOTS[@]}"; do
  test -d "$root" || {
    printf '%s\n' "source root missing: $root" >&2
    exit 1
  }
  for entry in "$root"/*; do
    test -f "$entry/SKILL.md" || continue
    name="$(basename "$entry")"
    real="$(readlink -f "$entry")"

    if existing="$(source_for "$name")"; then
      test "$existing" = "$real" || {
        printf '%s\n' "name collision: $name -> $existing and $real" >&2
        exit 1
      }
      continue
    fi
    names+=("$name")
    sources+=("$real")
  done
done

test "${#names[@]}" -gt 0 || {
  printf '%s\n' "no skills found in source roots" >&2
  exit 1
}

for target_root in "${TARGET_ROOTS[@]}"; do
  if [[ "$CHECK_ONLY" -eq 0 ]]; then
    mkdir -p "$target_root"
  elif [[ ! -d "$target_root" ]]; then
    printf '%s\n' "missing target root: $target_root"
    drift=1
    continue
  fi

  for index in "${!names[@]}"; do
    name="${names[$index]}"
    source="${sources[$index]}"
    target="$target_root/$name"

    if [[ -e "$target" || -L "$target" ]]; then
      if [[ "$(readlink -f "$target")" == "$source" ]]; then
        continue
      fi
      printf '%s\n' "conflict: $target -> $(readlink -f "$target") (expected $source)" >&2
      drift=1
      continue
    fi

    if [[ "$CHECK_ONLY" -eq 1 ]]; then
      printf '%s\n' "missing: $target"
      drift=1
      continue
    fi
    ln -s "$source" "$target"
    printf '%s\n' "created: $target"
  done
done

if [[ "$drift" -ne 0 ]]; then
  printf '%s\n' "skills-sync=drift skills=${#names[@]}" >&2
  exit 1
fi
printf '%s\n' "skills-sync=ok skills=${#names[@]} roots=${#TARGET_ROOTS[@]}"
