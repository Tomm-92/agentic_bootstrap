# Initial install instructions

These instructions turn a folder holding the project's instruction files into a
git repo with Python, the latest Google ADK and a first commit. They come first
in the project's setup:

| Order | File | What it adds | Start a session with |
| --- | --- | --- | --- |
| 1 | `docs/initial_install.md` | Git, Python, Google ADK, first commit | *"Implement initial_install.md."* |
| 2 | `docs/codequality.md` | Lint, type and test gates | *"Implement docs/codequality.md."* |
| 3 | `docs/governance_implementation.md` | Every control that doesn't depend on the agent's purpose | *"Implement docs/governance_implementation.md in one run, from Stage 1 to Stage 11."* |
| 4 | `docs/agent_governance_implementation.md` | The controls that do, once the purpose is known | *"Implement docs/agent_governance_implementation.md in one run, from A01 to A06."* |

Use a new session, opened at the repo root, for each file. Do only step 1 here.

## Before you start

The folder holds these four files at its top level, and nothing else that
matters:

- `initial_install.md`
- `codequality.md`
- `governance_implementation.md`
- `agent_governance_implementation.md`

## Rules for this session

- **Ask, don't guess.** Stop and ask the owner if a check below fails, and say
  which one.
- **Don't overwrite a project.** If the folder is already a git repo with
  commits, or holds source code, stop and ask.
- **Ask before installing anything system-wide.** Everything else stays inside
  this folder.
- **Never push,** create a remote, read or create `.env`, or make a model call.

## Why Python 3.14

Use Python 3.14, even if the latest ADK supports newer versions. The later files
assume it in their `.venv` paths, lint settings and CI workflow, so a different
version would mean changing them too. If the latest ADK no longer supports 3.14,
or a dependency won't install on it, stop and ask the owner.

## Build

Run these from the repo root.

1. **Check the tools.** Install nothing yet: run every check, then ask the owner
   once about everything that's missing.

   These are needed by this file and every later one. Git must be 2.32 or newer,
   because the owner's last step in `docs/governance_implementation.md` uses
   `git commit --trailer`.

   ```bash
   python3.14 --version
   ```

   ```bash
   jq --version
   ```

   ```bash
   git --version
   ```

   ```bash
   shasum --version
   ```

   On macOS with Homebrew that is `brew install python@3.14`, `brew install jq` or
   `brew install git`. `shasum` comes with macOS, and with Perl on Linux.

   These let the governance run prove its own checks instead of leaving them to the
   owner afterwards. Its CI workflows, local telemetry stack and verification sandbox
   use them:

   ```bash
   actionlint --version
   ```

   ```bash
   gitleaks version
   ```

   ```bash
   osv-scanner --version
   ```

   ```bash
   docker compose version
   ```

   On macOS with Homebrew the first three are
   `brew install actionlint gitleaks osv-scanner`. The last needs a container runtime
   with Compose, such as Docker Desktop. This file doesn't need it running, but the
   governance run does.

   On Linux or WSL2, also check these. Claude Code's sandbox needs them, and once
   governance is armed, a session won't start without them:

   ```bash
   bwrap --version
   ```

   ```bash
   socat -V
   ```

   If the owner declines to install one of the governance tools, carry on and report
   it. The governance run defers whatever depends on it.

2. **Check the git identity.** The first commit uses it.

   ```bash
   git config user.name && git config user.email
   ```

   If either is empty, ask the owner what to use. Don't invent one.

3. **Create the repo.**

   ```bash
   git init -b main
   ```

4. **Move the instruction files into `docs/`,** where the later files expect
   them.

   ```bash
   mkdir -p docs && mv initial_install.md codequality.md governance_implementation.md agent_governance_implementation.md docs/
   ```

5. **`.gitignore`.** Create it with these lines. `docs/codequality.md` adds more
   later.

   ```text
   .venv/
   __pycache__/
   .env
   .DS_Store
   ```

6. **Create the virtual environment.**

   ```bash
   python3.14 -m venv .venv
   ```

   ```bash
   .venv/bin/pip install --upgrade pip
   ```

7. **Install the latest Google ADK.** Install it without extras; later files add
   what they need.

   ```bash
   .venv/bin/pip install --upgrade google-adk
   ```

8. **`requirements.txt`.** Give the ADK a range that allows minor and patch
   updates but not the next major, starting from the installed version. For
   example, version 2.14.0 gives:

   ```text
   google-adk>=2.14,<3
   ```

   Read the installed version from:

   ```bash
   .venv/bin/pip show google-adk
   ```

9. **Check the install.**

   ```bash
   .venv/bin/pip index versions google-adk
   ```

   ```bash
   .venv/bin/pip check
   ```

   ```bash
   .venv/bin/python -c "from google.adk.agents import Agent; print('ADK import OK')"
   ```

   ```bash
   .venv/bin/adk --version
   ```

   The first command's `LATEST` and `INSTALLED` versions must match. If `pip
   check` reports a conflict, stop and ask rather than pinning around it.

10. **Create the first commit,** on `main`, with no co-author or tool attribution
    lines. This is the only commit these instructions make, and later files
    need it to exist. From here on, commits follow the later files' rules.

    ```bash
    git add .gitignore requirements.txt docs
    ```

    ```bash
    git commit -m "Set up Python, Google ADK and project instructions"
    ```

## Acceptance criteria

- [ ] `git log --oneline` shows one commit, on `main`.
- [ ] `git status --short` prints nothing, so `.venv/` is ignored and the tree is
      clean.
- [ ] `git ls-files` lists exactly `.gitignore`, `requirements.txt` and the four
      files in `docs/`.
- [ ] `.venv/bin/python --version` reports Python 3.14.
- [ ] `.venv/bin/adk --version` reports the same version as PyPI's latest.
- [ ] Every tool in step 1 reports a version, or the owner declined it.

## When you finish

Report the Python and ADK versions, the commit hash and any tool from step 1 that's
still missing, then stop. Tell the owner
the next step is a new session at the repo root, started with: *"Implement
docs/codequality.md."*
