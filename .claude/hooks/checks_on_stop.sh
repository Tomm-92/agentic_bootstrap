#!/bin/bash
# Stop: if the working tree changed since the last check, block finishing while
# lint, format, dead-code, type or unit-test checks fail. After one blocked
# attempt, tell the user instead, and don't re-check until something changes again.
# `{"force": true}` runs the checks anyway, for the verifier and the build subagents.
input=$(cat)
active=$(jq -r '.stop_hook_active // false' <<<"$input")
force=$(jq -r '.force // false' <<<"$input")
cd "$CLAUDE_PROJECT_DIR" || exit 0
src=(app tests scripts)          # vulture targets
paths=(. ':!output')
saved=.claude/.checks_fingerprint
now=$({
  git diff HEAD -- "${paths[@]}"
  git ls-files -z --others --exclude-standard -- "${paths[@]}" | xargs -0 cat
} | shasum)
[[ $force != true && "$now" == "$(cat "$saved" 2>/dev/null)" ]] && exit 0
fail() {
  if [[ "$active" == true ]]; then
    echo "$now" >"$saved"
    jq -n --arg m "Checks still failing ($1)" '{systemMessage: $m}'
    exit 0
  fi
  printf '%s:\n%s\n' "$1" "$2" >&2
  exit 2
}
out=$(.venv/bin/ruff check --config ruff.toml --output-format concise . 2>&1) || fail ruff "$out"
out=$(.venv/bin/ruff format --check --config ruff.toml . 2>&1) || fail 'ruff format (run .venv/bin/ruff format .)' "$out"
out=$(git grep --untracked -niE -e '#[[:space:]]*type:[[:space:]]*ignore(\[[^]]*\])?[[:space:]]*$' -e '#[[:space:]]*noqa(:[[:space:]]*[A-Z]+[0-9]+([[:space:]]*,?[[:space:]]*[A-Z]+[0-9]+)*)?[[:space:]]*$' -- "${src[@]}") &&
  fail 'noqa and type: ignore need a reason after their codes: # noqa: E501 - <why>, # type: ignore[code]  # <why>' "$out"
out=$(.venv/bin/vulture $(ls -d "${src[@]}" 2>/dev/null) --min-confidence 80 2>&1) || fail vulture "$out"
out=$(.venv/bin/mypy 2>&1) || fail mypy "$out"
out=$(.venv/bin/pytest -q -x 2>&1) || fail pytest "$(tail -30 <<<"$out")"
echo "$now" >"$saved"
