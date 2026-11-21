# Spec 0018: AWS hosting instructions

Intent: [0018-aws-hosting](../intent/0018-aws-hosting.md)
Status: Accepted
Accepted by: Thomas M, 2026-11-21

<!-- Copy to docs/exec-plans/spec/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts plan mode. -->

## Requirements

This change writes one instruction file and lists it in the README. It doesn't build
the hosting itself. A later session runs the file, as with the other four.

1. `docs/aws_hosting_implementation.md` exists. It follows the shape of
   `docs/agent_governance_implementation.md`: Before you start, How to run this file,
   inputs, numbered phases (H01 to H06), each with Build, Acceptance criteria and
   Ledger, then After the run, Verified facts, Known gaps and Sources.
2. The file is run in one session on the branch `hosting-aws`, under the plan
   `docs/exec-plans/active/H00-aws-hosting.md`. Every protected-path change goes to
   `proposals/H00/`. The run commits after each phase, and never pushes, deploys or
   runs `terraform apply`.
3. It runs after `docs/agent_governance_implementation.md`. It can also run against
   the placeholder agent. In that case the sandbox parts (SBX-001) are recorded as
   `deferred`.
4. It starts with a hosting interview in the style of the purpose interview. Each
   choice gets an explanation and a recommendation, and unanswered choices become
   open questions, never guesses. The choices are: AWS accounts and region, domain
   and certificate, user authentication, telemetry backend, model provider, and the
   dev and prod sizes.
5. It recommends ECS on Fargate. It has an "Alternatives" section that compares
   Bedrock AgentCore Runtime, App Runner, EKS and Lambda against ECS Fargate. For
   each, it says when to prefer it and which controls change.
6. Every ADK API, flag and default it names was checked against the installed
   `google-adk==2.14.0` source and is listed under Verified facts.
7. Every rule in `governance/rules.yaml` that applies at runtime still holds in the
   hosted agent. For each one, the file says how it's met, or records it as a known
   gap with a "close by".
8. It produces dev and prod from one set of Terraform modules. They differ only in
   their variables, and prod runs only an image digest that has already passed in dev.
9. The README's "Getting started" table lists the fifth file, and says it's optional
   and runs after file 4.
10. The new file is protected like the other implementation files, through
    `proposals/0018/` (GOV-002).

## Design

### What the file has the run build

| Phase | Builds | Main paths |
| --- | --- | --- |
| H01 Hosting profile | The interview, and a `hosting` block for the profile as a proposal | `proposals/H00/governance/profile.yaml` |
| H02 Container image | `Dockerfile`, `.dockerignore`, `scripts/serve.py`, a runtime lockfile, the baked governance hash, identity binding | repo root, `scripts/`, `app/governance.py`, `tests/unittests/` |
| H03 Terraform | State bootstrap, modules, `envs/dev` and `envs/prod` | `infra/terraform/` |
| H04 Telemetry and evidence | AWS collector config, retention, alerts | `ops/observability/aws/`, `infra/terraform/modules/observability/` |
| H05 Build and promote | A deploy workflow using GitHub OIDC, promotion by image digest | `proposals/H00/.github/workflows/deploy.yml` |
| H06 Verification and activation proposal | IaC checks, a local container run, `SECURITY.md` additions, ledger rows, report | `docs/` |

### Serving: ADK's own server, in one container

- `scripts/serve.py` builds the app with `get_fast_api_app(agents_dir=<repo root>,
  session_service_uri=..., artifact_service_uri=..., memory_service_uri=...,
  allow_origins=[<exact origins>], web=<dev only>, host='0.0.0.0', port=8000)` and
  runs it with uvicorn. This is ADK's documented custom-container route. It's chosen
  over `adk api_server` because the identity middleware (below) has to wrap the app.
  The local `adk web` path is unchanged.
- It sets all three service URIs explicitly. With a read-only root filesystem, ADK
  otherwise falls back silently to in-memory storage, which would lose sessions and
  break EVID-001.
- `web=False` in prod. The ADK web UI is for development only.
- ECS uses ADK's built-in `GET /health` route for health checks.
- The base image is `python:3.14-slim`, pinned by digest. The container runs as a
  non-root user, with a read-only root filesystem and `/tmp` as tmpfs. It installs
  from a runtime lockfile, `requirements.lock`, so prod gets exact pins (DEP-001).

### Governance hash without git (GOV-005)

`governance_hash()` calls git, and the image has none. The file has the run do this:

- The build stamps `git rev-parse HEAD:governance` into the image, as a file and as
  an image label. The build fails if `governance/` has uncommitted changes.
- `governance_hash()` reads the stamped file only when the repo has no `.git`. With
  neither git nor the stamped file, it raises `GovernanceError`, so the agent still
  fails closed. A unit test covers each case.
- `governance/` is copied into the image, and the root filesystem is read-only, so
  the stamped hash can't drift from the files the plugin loads. `before_run_callback`'s
  re-check still runs.

### Identity: authenticate, then bind `user_id`

ADK's server has no authentication. Its own warning says that any client that can
reach it can read, change and delete any user's sessions. `user_id` comes from the
request path. So:

- The ALB authenticates every request with Amazon Cognito, or the owner's OIDC
  provider (`authenticate-oidc`).
- In `scripts/serve.py`, a middleware verifies the ALB's signed `x-amzn-oidc-data`
  token against the regional public key. It rejects any request where the path's
  `users/{user_id}` doesn't match the token's subject. A unit test covers the reject
  path.
- The tasks' security group accepts traffic only from the ALB.
- In prod, AWS WAF in front of the ALB rate-limits per client. That closes
  `SECURITY.md`'s "Nothing limits the number of sessions".

### Sessions and outputs (EVID-001, FS-001)

- Sessions use `DatabaseSessionService` on RDS for PostgreSQL, through
  `postgresql+asyncpg://`. `asyncpg` is a new runtime dependency, so it needs the
  owner's approval (DEP-001). The database password comes from the
  RDS-managed Secrets Manager secret and is never put in an environment file.
- RDS automated backups keep at most 35 days. So an AWS Backup plan keeps snapshots
  for `retention_days` (90). Storage is encrypted, and prod has Multi-AZ and deletion
  protection.
- `output_root` is an EFS access point mounted at `/app/output`, so FS-001's path
  check is unchanged and outputs survive a task restart. An S3 artifact service is
  recorded as a later option: ADK 2.14 ships no S3 `BaseArtifactService`.

### Secrets and cost (SEC-001, SEC-002, COST-001)

- Dev and prod each have their own `ANTHROPIC_API_KEY` in Secrets Manager, injected
  through ECS `secrets`, from separate Console workspaces with separate spend limits.
- No `.env` file goes into the image. `.dockerignore` excludes `.env`, `.sessions/`,
  `app/.adk/`, `.venv/` and `output/`.
- The governance layer still enforces `session_token_budget` per session.

### Telemetry (OBS-001, DATA-001)

- An AWS Distro for OpenTelemetry collector runs as a sidecar. The agent exports
  OTLP to `localhost:4317`, set through `OTEL_EXPORTER_OTLP_ENDPOINT` in the task
  definition, so ADK sets up its exporters at server start.
- Recommended backends: traces to X-Ray, metrics to Amazon Managed Service for
  Prometheus, and logs to CloudWatch Logs with 90-day retention. Amazon Managed
  Grafana loads the existing `governance.json` dashboard, and `alerts.yaml` loads
  into the managed Prometheus rule groups, with notifications going to SNS.
- The new exporter endpoints go into `allowlists/services.yaml` as a proposal.
  `test_observability.py` reads a second collector config, so the allowlist test
  covers both.
- `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false` is set in prod, which matches ADK's
  own deploy default. The owner decides for dev, through `SECURITY.md`.
- The `governance.session_tokens` gauge is labelled per session. That's a known gap,
  and it has to be fixed before metrics go to a shared backend. The file has the run
  fix it in H04.

### Network

- Each environment has a VPC: a public ALB, and private subnets for the tasks, RDS
  and EFS.
- VPC endpoints for ECR, Secrets Manager, CloudWatch Logs, X-Ray, managed Prometheus
  and S3 keep AWS traffic private.
- All other egress goes through a NAT gateway. In prod, it also passes AWS Network
  Firewall, with a domain allowlist built from `allowlists/services.yaml` (DATA-001).

### Verification sandbox (SBX-001)

Fargate can't run Docker inside a task, so A02's sandbox becomes its own ECS task
definition:

- It has no task role, so no AWS credentials, and no secrets.
- No `ExecuteCommand`, so nobody gets interactive access (DATA-001).
- It sits in a subnet whose only egress is the allowlisted package registries.
- The agent's tool starts it with `RunTask`, and waits for the result.

If A02 hasn't run yet, this part is recorded as `deferred`.

### Environments and promotion

- There's one AWS account per environment, under AWS Organizations, which is AWS's
  multi-account best practice. Each account has its own Terraform state in S3, with
  native lockfiles.
- `infra/terraform/modules/` is shared, and `envs/dev` and `envs/prod` differ only
  in their variables.
- Dev: one task, a small single-AZ database, the web UI allowed, and a lower spend
  limit. Prod: at least two tasks across AZs, Multi-AZ, WAF, Network Firewall and
  deletion protection.
- CI builds once, on a merge to `main`, and pushes to ECR. Tags are immutable and
  images are scanned on push. CI then deploys that digest to dev. Prod deploys the
  same digest, only through a `workflow_dispatch` that the owner runs.
- GitHub reaches AWS through OIDC roles, with no long-lived keys. Each environment's
  role can update only its own ECS service.
- CI runs `terraform fmt -check`, `terraform validate`, `tflint` and `checkov` on
  every pull request that touches `infra/`. Agents run `terraform plan` only with
  the owner's approval, and never `apply`.

### Proposed rules

These go in `proposals/H00/governance/rules-additions.yaml` for the owner to choose
from, as in A06:

- **HOST-001** (deny): hosted endpoints authenticate every request, and bind
  `user_id` to the verified identity.
- **DEPLOY-001** (deny): prod runs only an image digest that passed in dev, and is
  labelled with a committed governance hash.

### This change's protection proposal

`proposals/0018/` adds `docs/aws_hosting_implementation.md` in the same places as
`docs/agent_governance_implementation.md`:

- `AGENTS.md` (protected paths)
- `.claude/settings.json` (deny rule and sandbox `denyWrite`)
- `.github/CODEOWNERS`
- `.github/workflows/governance.yml` (protected-path diff list)
- `tests/governance/test_settings.py` (`PROTECTED`)

The test goes in the proposal too, so it changes in the same commit as the settings
it checks. The README's protected-paths paragraph is updated directly.

### Options rejected

- **`adk deploy`.** Its targets are Cloud Run, GKE, Agent Engine and a local Docker
  container. None of them targets AWS.
- **Bedrock AgentCore Runtime as the default.** It's managed and agent-specific, but
  it replaces ADK's documented server with its own invocation contract, and the
  owner already knows ECS. It's covered under Alternatives.
- **Lambda.** It has a 15-minute cap and a cold start for every session, and agent
  sessions that wait on human confirmations don't fit that model. It's covered under
  Alternatives as unsuitable.
- **Self-hosting Tempo, Prometheus and Loki on ECS.** It keeps the existing
  dashboards unchanged, but leaves the owner to run the stack. It's offered as an
  interview option, not the recommendation.
- **Moving models to Amazon Bedrock.** It changes the provider, the allowlisted IDs
  and the evals (MODEL-001). It's offered as an interview option, which leads to a
  proposal and an eval run.

## Out of scope

- Building any of the above in this change. This change writes the instruction file
  only.
- Running `terraform`, creating AWS accounts, or spending money.
- Rewriting the local observability stack, `adk web`, or `scripts/local_session.py`.
- Hosting on any cloud other than AWS.

## Policies checked

- `governance/rules.yaml`:
  - GOV-002: the protection proposal, and every protected change in the run goes to
    `proposals/H00/`.
  - GOV-004: per-phase commits with trailers.
  - GOV-005: the stamped hash keeps the agent failing closed.
  - EVID-001: Postgres sessions and the 90-day backup plan.
  - SEC-001 and SEC-002: Secrets Manager, and `.dockerignore`.
  - DATA-001: the exporter allowlist, the Network Firewall allowlist, and no
    `ExecuteCommand`.
  - DEP-001: `asyncpg`, the lockfile and the base image digest.
  - COST-001: per-environment spend limits, the token budget, and no apply by agents.
  - MODEL-001: stays on `api.anthropic.com` unless a proposal changes it.
  - TOOL-001 and FS-001: unchanged, with EFS at `output_root`.
  - SBX-001: the sandbox task.
  - OBS-001: the collector sidecar.
  - SCOPE-001 and SCOPE-002: the H00 plan's scope.
- `docs/SECURITY.md`: the run adds hosted items to retention, redaction, approved
  services, rate limits and incident response. In a hosted incident, the agent is
  stopped by scaling the ECS service to zero and revoking the key.
- `app/AGENTS.md`: the change to `governance_hash()` keeps the plugin as the single
  enforcement point, and `scripts/serve.py` uses ADK's `get_fast_api_app`, not a
  custom server.

## Concerns

- **Identity binding is custom code in front of ADK.** ADK 2.14 has no
  authentication hook for its server, so the middleware is the only thing stopping
  one user from reading another's sessions. It needs tests and the owner's review,
  and HOST-001 makes it a rule.
- **The stamped hash weakens GOV-005's re-check.** Inside the image,
  `before_run_callback` compares two values that can't change. That's safe only
  because the root filesystem is read-only, so the task definition must keep
  `readonlyRootFilesystem: true`. A test on the Terraform module can check this.
- **Free GitHub can't require reviewers on a prod environment.** Prod deploys
  therefore depend on the owner running `workflow_dispatch`, until the repo moves to
  a plan with environment protection.
- **Cost.** NAT gateways, Network Firewall, Multi-AZ RDS and the managed telemetry
  services cost money even when idle. Dev drops Network Firewall and Multi-AZ, and
  the file says what each environment costs at idle.
- **New tools for the run.** It needs `terraform`, `tflint` and `checkov`, which
  DEP-001 covers for development tools. The Claude Code sandbox blocks `docker`, so
  the local container run may be `deferred`.
