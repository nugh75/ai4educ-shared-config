#!/usr/bin/env bash
# commit-sync.sh — Committa AGENTS.md/CLAUDE.md riscritti da sync-project.sh
# direttamente sul branch di default (regola "Exception for the ai4educ sync").
# Uso: commit-sync.sh [--dry-run] [--projects-file FILE]
#   Solo quei due file, messaggio "chore: sync shared rules".
#   Commit + push se il repo è sul branch di default e allineato al remote
#   (se è solo indietro, prima pull --ff-only); commit locale se non ha remote.
#   Salta: branch di lavoro, repo divergenti, file già in stage, repo puliti.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_FILE="$(dirname "$SCRIPT_DIR")/projects.txt"
DRY_RUN=false
MSG=$'chore: sync shared rules\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --projects-file) PROJECTS_FILE="$2"; shift 2 ;;
        *) echo "Uso: commit-sync.sh [--dry-run] [--projects-file FILE]" >&2; exit 1 ;;
    esac
done

commit_files() {
    local p="$1"
    git -C "$p" add -- AGENTS.md CLAUDE.md && git -C "$p" commit -q -m "$MSG" -- AGENTS.md CLAUDE.md
}

process() {
    local p="$1" n b def up ab
    n=$(basename "$p")
    [[ -d "$p/.git" ]] || return 0
    [[ -n "$(git -C "$p" status --porcelain -- AGENTS.md CLAUDE.md)" ]] || return 0
    if [[ -n "$(git -C "$p" diff --cached --name-only)" ]]; then echo "SKIP-staged $n"; return 0; fi
    b=$(git -C "$p" branch --show-current)
    up=$(git -C "$p" rev-parse --abbrev-ref '@{u}' 2>/dev/null || true)

    if [[ -z "$up" ]]; then
        if [[ "$b" != main && "$b" != master ]]; then echo "SKIP-branch $n ($b)"; return 0; fi
        if $DRY_RUN; then echo "WOULD-COMMIT $n"; return 0; fi
        commit_files "$p" && echo "LOCAL $n" || echo "FAIL-commit $n"
        return 0
    fi

    def=$(git -C "$p" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
    [[ -n "$def" ]] || def=main
    if [[ "$b" != "$def" ]]; then echo "SKIP-branch $n ($b, default $def)"; return 0; fi

    git -C "$p" fetch -q 2>/dev/null || true
    ab=$(git -C "$p" rev-list --left-right --count 'HEAD...@{u}')
    if [[ "$ab" != $'0\t0' ]]; then
        # Solo indietro (0 commit locali in più): fast-forward, altrimenti divergente.
        if [[ "${ab%%$'\t'*}" == 0 ]] && ! $DRY_RUN && git -C "$p" pull -q --ff-only 2>/dev/null; then
            ab=$'0\t0'
        elif [[ "${ab%%$'\t'*}" == 0 ]] && $DRY_RUN; then
            ab=$'0\t0'
        fi
    fi
    if [[ "$ab" != $'0\t0' ]]; then echo "SKIP-diverged $n ($ab)"; return 0; fi

    if $DRY_RUN; then echo "WOULD-PUSH $n"; return 0; fi
    commit_files "$p" || { echo "FAIL-commit $n"; return 0; }
    git -C "$p" push -q 2>/dev/null && echo "PUSHED $n" || echo "FAIL-push $n"
}

while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    process "${line/#\~/$HOME}"
done < "$PROJECTS_FILE"
