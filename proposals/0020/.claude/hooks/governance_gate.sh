#!/bin/bash
# GOV-001, GOV-006, SCOPE-001 and SCOPE-002. SessionStart can't block, so it only
# injects the governance hash and active plan, and pins the session to that hash.
# UserPromptSubmit blocks prompts while governance is missing, uncommitted or
# changed since the pin, and otherwise restates the hash and plan, because
# rules injected once fade as the context grows. PreToolUse denies edits
# unless exactly one plan is active and the path is inside its scope_paths (plan
# files are exempt so a plan can be drafted).
input=$(cat)
cd "$CLAUDE_PROJECT_DIR" || exit 0
event=$(jq -r .hook_event_name <<<"$input")
session=$(jq -r .session_id <<<"$input")
pin=.claude/.session_governance/$session
mkdir -p .claude/.session_governance

if [[ ! -f governance/rules.yaml ]]; then
  problem='governance/rules.yaml is missing'
elif ! sha=$(git rev-parse -q --verify HEAD:governance); then
  problem='governance/ is not committed'
elif [[ -n $(git status --porcelain -- governance) ]]; then
  problem='governance/ has uncommitted changes'
fi
shopt -s nullglob
plans=(docs/execution-plans/plan/active/*.md)
case ${#plans[@]} in
  0) plan='No active execution plan: code edits are blocked until one exists.' ;;
  1) plan="Active execution plan: ${plans[0]}. Read it before working." ;;
  *) plan="Several active plans (${plans[*]}): ask which applies; code edits are blocked." ;;
esac
status="Governance in effect: $sha (governance/rules.yaml). Use it in the commit trailer. $plan"

deny() {
  jq -n --arg r "$1" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  exit 0
}

case $event in
  SessionStart)
    if [[ -n $problem ]]; then
      echo "Governance unavailable: $problem. Prompts are blocked until a human fixes and commits it." >&2
      exit 2
    fi
    echo "Claude session ID: $session"
    if [[ $(git config core.hooksPath) != .githooks ]]; then
      echo 'Warning: git hooks are off (GOV-004). The owner should run: git config core.hooksPath .githooks'
    fi
    # A new or cleared context starts under the current rules; a resumed or
    # compacted one keeps the rules it started with.
    source=$(jq -r .source <<<"$input")
    if [[ $source == startup || $source == clear || ! -f $pin ]]; then
      echo "$sha" >"$pin"
    fi
    if [[ $(<"$pin") == "$sha" ]]; then
      echo "$status"
    else
      echo "GOV-006: governance changed from $(<"$pin") to $sha after this session started. Prompts are blocked; start a new session, or /clear."
    fi
    ;;
  UserPromptSubmit)
    if [[ -n $problem ]]; then
      jq -n --arg r "No governance, no agent (GOV-001): $problem. Fix and commit governance/ yourself, then retry." \
        '{decision: "block", reason: $r}'
      exit 0
    fi
    # No pin yet when governance was first committed during this session.
    [[ -f $pin ]] || echo "$sha" >"$pin"
    if [[ $(<"$pin") != "$sha" ]]; then
      jq -n --arg r "GOV-006: governance changed from $(<"$pin") to $sha after this session started. Start a new session, or /clear, to work under the new rules." \
        '{decision: "block", reason: $r}'
      exit 0
    fi
    echo "$status"
    ;;
  PreToolUse)
    f=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' <<<"$input")
    # Normalised, so docs/execution-plans/../../x can't borrow the plan exemption.
    f=$(.venv/bin/python -I -c 'import os, sys; print(os.path.normpath(sys.argv[1]))' "$f") ||
      deny 'SCOPE-002: could not run .venv/bin/python to check the path.'
    rel=${f#"$CLAUDE_PROJECT_DIR"/}
    [[ $rel == docs/execution-plans/* ]] && exit 0
    # Plan mode's own plan file, which is written before any plan is active.
    [[ $f == "$HOME"/.claude/plans/*.md ]] && exit 0
    [[ ${#plans[@]} -eq 1 ]] ||
      deny "SCOPE-001: edits need exactly one plan in docs/execution-plans/plan/active/ (found ${#plans[@]}). Draft or choose one first."
    reason=$(.venv/bin/python -I - "${plans[0]}" "$rel" 2>&1 <<'PY'
import fnmatch, sys, yaml

plan, path = sys.argv[1:]
parts = open(plan).read().split('---\n', 2)
if parts[0] or len(parts) < 3:
    sys.exit(f'{plan} has no YAML front matter')
globs = yaml.safe_load(parts[1])['scope_paths']
if not any(fnmatch.fnmatch(path, glob) for glob in globs):
    sys.exit(f'{path} is outside the scope_paths of {plan}')
PY
    ) || deny "SCOPE-002: $(tail -1 <<<"$reason")"
    ;;
esac
