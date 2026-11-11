#!/bin/bash
# GOV-004 and EVID-001. `--message <file>` checks a commit being made, whose parent is
# HEAD. Otherwise the arguments are a rev-list range, and each commit in it is checked
# against its own parent, because the trailer records the rules a commit was made under.
problems=0
check() {
  local label=$1 message=$2 parent=$3 trailers want plan
  [[ -n $parent ]] || return 0 # The repo's root commit.
  trailers=$(git interpret-trailers --parse <<<"$message")
  # A parent without governance/ has no hash to record.
  if want=$(git rev-parse -q --verify "$parent:governance"); then
    if [[ $(sed -n 's/^Governance: *//p' <<<"$trailers") != "$want" ]]; then
      echo "$label: needs the trailer 'Governance: $want'" >&2
      problems=1
    fi
  fi
  plan=$(sed -n 's/^Plan: *//p' <<<"$trailers")
  if [[ ! $plan =~ ^[[:alnum:]]+$ ]] || ! compgen -G "docs/exec-plans/*/$plan-*.md" | grep -qE '/(active|completed)/'; then
    echo "$label: needs a 'Plan: <ID>' trailer naming a plan in docs/exec-plans/active/ or completed/" >&2
    problems=1
  fi
}

if [[ $1 == --message ]]; then
  check 'commit message' "$(<"$2")" "$(git rev-parse -q --verify HEAD)"
else
  for commit in $(git rev-list "$@"); do
    check "$commit" "$(git log -1 --format=%B "$commit")" "$(git rev-parse -q --verify "$commit^1")"
  done
fi
exit "$problems"
