#!/bin/bash
# GOV-002 and GOV-004. The owner's review is the only merge control, so the agent
# must never commit straight to main, push, skip the git hooks or repoint them.
# Matches anywhere in a compound command, through `git -C <dir>` and `git -c <x=y>`,
# because a permission deny rule matches only the command's literal start.
# COST-001. Paid-model commands run only in manual mode, where the ask rules prompt.
# Auto mode's classifier isn't a cost control, and a subagent's input may carry no
# mode, so anything but `default` is denied.
input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
deny() {
  jq -n --arg r "$1" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  exit 0
}
s='[[:space:]]+'
git="git($s-[cC]$s[^[:space:]]+)*$s"
# Quoted text is an argument, such as a commit message, and not a command.
plain=$(sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g" <<<"$cmd")

[[ $plain =~ ${git}push([[:space:]]|$) ]] && deny 'GOV-002: agents never push; the owner pushes.'

paid='pytest.*-m[[:space:]]*integration|local_session.*--real|adk[[:space:]]+(run|web)|eval_pass_rate'
[[ $(jq -r '.permission_mode // empty' <<<"$input") != default && $plain =~ $paid ]] &&
  deny "COST-001: paid-model commands run only in manual mode; record the check as deferred for the owner's terminal."

shopt -s nocasematch
key="['\"]?core\.hookspath"
[[ $cmd =~ git($s-[cC]$s[^[:space:]]+)*$s-c$s$key ]] &&
  deny 'GOV-004: git -c core.hooksPath is refused; it would bypass the commit hooks.'
# A bare `git config core.hooksPath` or `--get` only reads it.
if [[ $cmd =~ ${git}config($s--[^[:space:]]+)*$s$key ]]; then
  [[ $cmd =~ ${git}config$s$key[\"\']?[[:space:]]*($|[\;\&\|]) || $cmd =~ ${git}config($s--[^[:space:]]+)*$s--get ]] ||
    deny 'GOV-004: changing core.hooksPath is an owner action.'
fi
shopt -u nocasematch

[[ $plain =~ ${git}commit([[:space:]]|$) ]] || exit 0
[[ $plain =~ ${git}commit[^\;\&\|]*($s--no-verify|$s-[a-zA-Z]*n[a-zA-Z]*)([[:space:]]|$) ]] &&
  deny 'GOV-004: git commit --no-verify and -n are refused; they skip the commit hooks.'
cd "$CLAUDE_PROJECT_DIR" || exit 0
[[ $(git branch --show-current) == main ]] || exit 0
deny 'GOV-002: no commits on main. Create a branch and commit there; main changes only through a PR the owner merges.'
