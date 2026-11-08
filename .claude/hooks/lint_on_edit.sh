#!/bin/bash
# PostToolUse: autofix and format an edited project Python file and report what ruff can't fix.
f=$(jq -r '.tool_input.file_path // empty')
[[ "$f" == "$CLAUDE_PROJECT_DIR"/*.py && -f "$f" ]] || exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
# --config stops nested ruff configs overriding ruff.toml; --force-exclude applies
# its excludes to explicit paths.
out=$(.venv/bin/ruff check --config ruff.toml --fix --force-exclude --output-format concise "$f" 2>&1)
failed=$?
# Format after fixing, since fixes can leave code unformatted.
.venv/bin/ruff format --config ruff.toml --force-exclude --quiet "$f"
if (( failed )); then
  echo "ruff found issues in $f; fix them:" >&2
  echo "$out" >&2
  exit 2
fi
