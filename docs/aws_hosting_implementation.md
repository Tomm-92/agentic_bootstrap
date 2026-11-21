# AWS hosting implementation instructions

These instructions take the governed product agent off the developer's machine
and host it on AWS, in a dev and a prod environment. An AI coding assistant
implements all of them **in one run**, from H01 to H06. They follow
`docs/agent_governance_implementation.md`. Every runtime control that file and
`docs/governance_implementation.md` built must still hold in the hosted agent.

The run writes code, Terraform and proposals. It never deploys, never runs
`terraform apply`, and never spends money. The owner does all of those after
the run.

The recommended host is **Amazon ECS on AWS Fargate**, behind an Application
Load Balancer, with the infrastructure in Terraform. "Alternatives to ECS
Fargate" compares the other AWS options.

The owner's proposal from plan 0018 makes this file read-only for agents.

## Before you start

The owner does these before the run, because the assistant must not:

- [ ] `docs/agent_governance_implementation.md` has run, and its "After the run"
      is done. Against the placeholder agent, the run still works, and records
      the sandbox parts (SBX-001) as `deferred`.
- [ ] There is one AWS account for dev and one for prod, under AWS Organizations,
      and the owner can name the region. The run needs only the account IDs. It
      never needs credentials.
- [ ] `terraform` (1.10 or later, for S3 native state locking), `tflint` and
      `checkov` are installed, for example with
      `brew install terraform tflint checkov`.
- [ ] A container runtime is reachable from the session. Without one, the image
      build and the local container run are `deferred`.

## How to run this file

Start one session at the repo root with:

> *"Implement docs/aws_hosting_implementation.md in one run, from H01 to H06."*

If the owner has already written some hosting inputs down, they can add *"The
hosting inputs are in <path>."* The interview then asks only about the rest.

### How one run stays governed

The controls from the earlier files are armed, and nothing here turns them off.
The gate, deny rules, scope check, sandbox and commit trailers all apply
throughout. After the hosting interview, the run needs no help from the owner
until it ends:

1. **Protected changes are proposals.** Every change to a protected path goes
   under `proposals/H00/` at the same relative path:
   `governance/profile.yaml`, `governance/allowlists/services.yaml`,
   `.github/workflows/deploy.yml`, `.github/workflows/infra.yml`,
   `governance/rules-additions.yaml` and, last, `governance/rules.yaml`.
2. **The governance hash doesn't change.** Nothing here commits to
   `governance/`, so one session can do all the work (GOV-006).
3. **Nothing reaches AWS.** The run uses no AWS credentials. Terraform is checked
   with `terraform init -backend=false`, `validate`, `tflint` and `checkov`,
   which need no account. A `terraform plan` against a real account is an owner
   action.
4. **The owner reviews once.** "After the run" applies everything in one commit,
   then deploys.

### Rules for the run

"Rules for the run" in `docs/agent_governance_implementation.md` applies here,
with `H00` in place of `A00` and these additions:

- **No apply, no deploy, no push.** Never run `terraform apply`,
  `terraform destroy`, `aws`, `docker push` or anything that changes an AWS
  account (COST-001).
- **No secrets anywhere.** Terraform creates secrets empty. Their values are
  owner actions. No `.env` file goes into an image, a commit or a variable file
  (SEC-001, SEC-002).
- **ADK's own server.** Serve the agent with `get_fast_api_app`. Don't write
  your own agent server, and don't change how ADK runs the agent.
- **Same modules, different variables.** Dev and prod differ only in their
  `terraform.tfvars`. A resource that exists in only one environment is switched
  on by a variable, never by copying a module.
- **Verify before use.** Check every ADK API against the installed source in
  `.venv/lib/python3.14/site-packages/google/adk/`, and every AWS resource
  argument against the pinned provider's schema (`terraform providers schema
  -json`).

**At the start of each part,** re-read `governance/rules.yaml` and the plan, and
name the part and the rule IDs you're working under.

**At the end of each part,** tick it in the plan, update its rows in
`docs/governance-activation.md`, and make a checkpoint commit on the branch with
the trailers `Governance: <git rev-parse HEAD:governance>` and `Plan: H00`.

**To resume,** read the plan and continue from the first unticked part.

### When a part can't finish

The table in `docs/agent_governance_implementation.md` applies. Also:

| Situation | What to do |
| --- | --- |
| A check needs an AWS account, such as `terraform plan` or a deploy | Record it as `deferred`, with the exact command for the owner. Continue. |
| A choice needs a hosting input the owner didn't give, such as a domain | Use a clearly named variable with no default, so `terraform plan` fails until the owner sets it. Record it as an open question. |

## Hosting inputs

The run collects these in a **hosting interview** before H01 builds anything.
It works like the purpose interview in `docs/agent_governance_implementation.md`.
Explain each input in a sentence, recommend a value and say why, offer the main
alternatives, and let the owner accept, choose or answer in their own words.
Then confirm the whole set in one summary, and write it to the plan under
"Hosting inputs".

| Input | Goes to | What to recommend |
| --- | --- | --- |
| AWS account IDs, dev and prod | `infra/terraform/envs/<env>/terraform.tfvars` | **Required.** One account per environment, so a mistake in dev can't touch prod. |
| Region | Both `terraform.tfvars` | **Required.** The region closest to the users that has every service below. |
| Domain and hosted zone | `terraform.tfvars` | A subdomain per environment, such as `agent.dev.example.com`, in a Route 53 hosted zone, with an ACM certificate. |
| User authentication | `terraform.tfvars`, H02 | **Amazon Cognito** user pool through the ALB, unless the organisation already has an OIDC provider, such as Okta or Entra ID. Use that through the ALB's `authenticate-oidc`. |
| Telemetry backend | H04 | **AWS-managed:** X-Ray for traces, Amazon Managed Service for Prometheus for metrics, CloudWatch Logs for logs, and Amazon Managed Grafana for the existing dashboard. The alternative is self-hosting the Tempo, Prometheus and Loki stack from `ops/observability/` on ECS, which keeps everything as-is but leaves the owner to run it. |
| Model provider | H01 | **Keep `api.anthropic.com`.** It's what `allowlists/models.yaml` and the evals are calibrated against. Moving to Amazon Bedrock changes the provider, the model IDs and the eval baseline (MODEL-001). If the owner wants it, record it as a separate plan, not part of this run. |
| Message content in traces | H04, `docs/SECURITY.md` | Off in prod (`ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`, which is ADK's own deploy default). The owner's choice in dev. |
| Sizes | Both `terraform.tfvars` | Dev: one 0.5 vCPU, 1 GB task, and a `db.t4g.micro` single-AZ database. Prod: at least two 1 vCPU, 2 GB tasks across two AZs, and a `db.t4g.small` Multi-AZ database. Explain that these are starting points to tune from the dashboards. |
| Spend limits | `docs/SECURITY.md` | A separate Anthropic Console workspace and API key per environment, with dev's limit well below prod's. An AWS Budgets alert per account. |

## Phase H01: Hosting profile and plan

**Goal:** governance records how and where the agent is hosted, and the run has a
plan and a branch.

**Rules:** GOV-002, SCOPE-001.

**Scope paths:** `proposals/H00/**`, `docs/exec-plans/**`,
`docs/governance-activation.md`.

### Build

1. **Interview, plan and branch.** Run the hosting interview. Switch to the branch
   `hosting-aws`, and write `docs/exec-plans/active/H00-aws-hosting.md` from the
   plan template, with:
   - `id: 'H00'` and every rule ID this file names
   - the confirmed hosting inputs
   - a checklist of H01 to H06 with their acceptance criteria
   - the union of their scope paths, plus the protected paths the proposal
     changes, so the applied commit stays in scope
2. **`proposals/H00/governance/profile.yaml`.** A copy of the live profile with a
   `hosting` block:

   ```yaml
   hosting:
     provider: 'aws'
     compute: 'ecs-fargate'
     region: '<region>'
     environments: [dev, prod]
     auth: '<cognito | oidc>'
     telemetry: '<aws-managed | self-hosted>'
   ```

3. **Ledger rows.** Add a row to `docs/governance-activation.md` for each control
   this file builds, with status `pending`.

### Acceptance criteria

- [ ] The plan has every hosting input, or an open question in its place.
- [ ] `tests/governance/test_rules.py` passes against the proposed profile.

### Ledger

None yet: H01 only records inputs.

---

## Phase H02: Container image

**Goal:** one image serves the agent with ADK's own server, carries the
governance hash it was built from, and accepts a request only when the
authenticated user owns the session it names.

**Rules:** GOV-005, EVID-001, SEC-001, SEC-002, DEP-001, DATA-001, and HOST-001
once accepted.

**Scope paths:** `Dockerfile`, `.dockerignore`, `requirements.txt`,
`requirements.lock`, `scripts/**`, `app/governance.py`, `tests/**`,
`docs/exec-plans/**`.

### Build

1. **Runtime dependencies (DEP-001).** Add `asyncpg` (the async PostgreSQL driver
   `DatabaseSessionService` requires) and `pyjwt[crypto]` (for H02 step 5) to
   `requirements.txt` with version ranges. Write `requirements.lock` by installing
   `requirements.txt` into a clean Python 3.14 virtualenv and running `pip freeze`,
   so the image gets exact pins. Both are new dependencies, so the owner approves
   them when merging.
2. **Governance hash without git (GOV-005).** In `app/governance.py`,
   `governance_hash(repo)` keeps its current behaviour when `repo/.git` exists.
   When it doesn't, it reads `repo/governance/.sha`, a file only the image build
   writes, and raises `GovernanceError` if that file is missing or empty. So the
   agent still fails closed with neither git nor a stamped hash.
   - `.gitignore` gets `governance/.sha`, so it can never be committed.
   - Unit tests cover:
     - a repo with git
     - a directory with no git and a stamped hash
     - a directory with neither, which raises
3. **`scripts/serve.py`.** The hosted entry point, next to
   `scripts/local_session.py`, which is the local one. It builds the app with
   ADK's documented custom-container route:

   ```python
   app = get_fast_api_app(
     agents_dir=str(agent.REPO),
     session_service_uri=os.environ['SESSION_SERVICE_URI'],
     artifact_service_uri=os.environ['ARTIFACT_SERVICE_URI'],
     memory_service_uri='memory://',
     use_local_storage=False,
     allow_origins=os.environ['ALLOW_ORIGINS'].split(','),
     web=os.environ.get('ADK_WEB_UI') == '1',
     host='0.0.0.0',  # noqa: S104 - only the ALB's security group can reach it
     port=8000,
   )
   ```

   - **All three service URIs are set explicitly**, and `use_local_storage=False`.
     With a read-only root filesystem, ADK otherwise falls back silently to
     in-memory storage, which loses every session (EVID-001).
     - `SESSION_SERVICE_URI` is `postgresql+asyncpg://...`. The task definition
       builds it from the RDS secret.
     - `ARTIFACT_SERVICE_URI` is `file:///app/output/.artifacts`, on the EFS
       volume.
   - **`allow_origins` lists exact origins.** Never `*`, which also switches off
     ADK's DNS-rebinding guard.
   - **The web UI is off unless `ADK_WEB_UI=1`.** H03 sets that in dev only.
   - **ECS health checks use ADK's built-in `GET /health`.**
4. **Route allowlist.** The server exposes development routes, such as
   `/dev-ui`, `/list-apps` and `/agent-identity/finalize`, as well as the session
   API. Wrap the app in a middleware that refuses, with 404, every route except:
   - `/health`
   - `/run` and `/run_sse`
   - `/run_live`
   - `/apps/{app_name}/users/{user_id}/sessions` and the paths under it
   - with `ADK_WEB_UI=1` only, the `/dev-ui` routes and `/list-apps`

   Check the route list against `cli/api_server.py` in the installed ADK. Routes
   change between versions.
5. **Identity binding (HOST-001).** ADK's server has no authentication. Its own
   warning says that any client that can reach it can read, change and delete any
   user's sessions. The ALB authenticates every request (H03), so the same
   middleware:
   - Verifies the ALB's `x-amzn-oidc-data` header. It's an ES256 JWT. Fetch its
     public key from `https://public-keys.auth.elb.<region>.amazonaws.com/<kid>`
     and cache it by `kid`. The `signer` header field must equal the ALB's ARN,
     passed in as `ALB_ARN`.
   - Takes the user ID from the token's `sub` claim.
   - Refuses with 403 any request where `user_id` differs from `sub`. Check all
     three places ADK reads it from:
     - the path, for `/apps/{app}/users/{user_id}/...`
     - the JSON body, for `/run` and `/run_sse`
     - the query string, for `/run_live`
   - Refuses with 401 a request with no valid token, except `/health`.
   - Unit tests use a locally generated ES256 key. They cover a matching user, a
     mismatched user in each of the three places, a bad signature, a wrong
     signer, and a missing token. No test calls the AWS key endpoint.
6. **`Dockerfile`.** It follows the shape of the one ADK generates
   (`cli/deployers/_dockerfile_template.py`), with these changes:
   - `FROM python:3.14-slim@sha256:<digest>`. Pin the digest, and record how to
     bump it.
   - Install from `requirements.lock` with `--no-cache-dir`.
   - Copy only `app/`, `scripts/serve.py` and `governance/`.
   - `ARG GOVERNANCE_SHA`, then write it to `governance/.sha`. Add
     `LABEL org.opencontainers.image.revision` and `LABEL governance.sha`. The
     build fails if the argument is empty.
   - Run as a non-root user. `EXPOSE 8000`. Use the exec form
     `CMD ["python", "-m", "scripts.serve"]`.
7. **`.dockerignore`.** Exclude `.env*`, `.git`, `.venv`, `.sessions/`,
   `app/.adk/`, `output/`, `proposals/`, `docs/`, `ops/`, `infra/`, `tests/`
   and caches (SEC-001).
8. **`scripts/build_image.sh`.** Refuses to build unless `governance/` is clean
   and committed, then runs:

   ```bash
   docker build --build-arg GOVERNANCE_SHA="$(git rev-parse HEAD:governance)" ...
   ```

   This is the same check the agent makes at startup, moved to build time.

### Acceptance criteria

- [ ] The unit tests for the hash, the route allowlist and identity binding pass
      with no network.
- [ ] `scripts/build_image.sh` refuses to build with a dirty `governance/`.
- [ ] The image builds, and `docker run --read-only --tmpfs /tmp` against a local
      PostgreSQL answers `/health`. Or both are `deferred`, with the commands.
- [ ] `docker run` without a stamped hash refuses to start.

### Ledger

GOV-005 (hosted fail-closed), and HOST-001 (identity binding) once proposed.

---

## Phase H03: Terraform

**Goal:** dev and prod are built from one set of modules, and differ only in their
variables.

**Rules:** EVID-001, SEC-001, SEC-002, DATA-001, COST-001, FS-001.

**Scope paths:** `infra/terraform/**`, `docs/exec-plans/**`.

### Build

Layout:

```text
infra/terraform/
  bootstrap/            state bucket per account; applied once by the owner
  modules/
    network/            VPC, subnets, NAT, VPC endpoints, Network Firewall (prod)
    registry/           ECR repository
    data/               RDS PostgreSQL, AWS Backup plan, EFS
    service/            ECS cluster, task definition, service, ALB, auth, WAF
    observability/      log groups, managed Prometheus, Grafana, X-Ray (H04)
    sandbox/            verification sandbox task definition (SBX-001)
    ci/                 GitHub OIDC provider and roles (H05)
  envs/
    dev/                main.tf calls the modules; terraform.tfvars holds dev values
    prod/
```

1. **Providers and state.** Pin `hashicorp/aws` with `~>` and commit
   `.terraform.lock.hcl` (DEP-001). Each environment keeps its state in its own
   account's S3 bucket, with `use_lockfile = true` for native locking,
   versioning on and public access blocked. `bootstrap/` creates the bucket.
2. **`network`.**
   - A VPC across two AZs, with public subnets for the ALB and NAT, and private
     subnets for tasks, RDS and EFS.
   - Interface endpoints for ECR (`api` and `dkr`), Secrets Manager, CloudWatch
     Logs, X-Ray and managed Prometheus, and a gateway endpoint for S3, so AWS
     traffic stays private.
   - Other egress leaves through the NAT gateway. When
     `enable_network_firewall` is true (prod), it passes AWS Network Firewall
     first. The firewall has a stateful domain allowlist built from
     `governance/allowlists/services.yaml`: `model_providers`, then
     `package_registries` and `external_targets` (DATA-001). Read the file with
     `yamldecode(file(...))`, so the allowlist has one source.
3. **`registry`.** An ECR repository with immutable tags, scan on push, and a
   lifecycle policy that keeps the last 50 images. Prod pulls from dev's
   repository through a cross-account repository policy, so promotion copies
   nothing.
4. **`data`.**
   - **RDS PostgreSQL**, with these settings:
     - `storage_encrypted = true` and `manage_master_user_password = true`, so
       RDS holds the password in Secrets Manager and Terraform never sees it
     - `deletion_protection` and `multi_az` as variables, both true in prod
     - `iam_database_authentication_enabled = true`
     - reachable only from the task security group
   - **AWS Backup.** RDS's automated backups keep at most 35 days, so an AWS
     Backup plan keeps daily snapshots for `retention_days` from
     `governance/thresholds.yaml`, read with `yamldecode` (EVID-001).
   - **EFS.** An encrypted file system, with one access point owned by the
     container's user, mounted at `/app/output`. FS-001's path check still sees
     `output/<work item>/`, and outputs survive a task restart. AWS Backup
     covers it too.
5. **`service`.**
   - **ECS task definition.**
     - The container image is given by digest, not tag.
     - `readonlyRootFilesystem = true`, with `/tmp` as a writable volume. This
       is what keeps the stamped governance hash honest: see "Known gaps".
     - The environment holds `SESSION_SERVICE_URI` parts, `ARTIFACT_SERVICE_URI`,
       `ALLOW_ORIGINS`, `ALB_ARN`, `OTEL_EXPORTER_OTLP_ENDPOINT`,
       `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS`, and `ADK_WEB_UI` in dev only.
     - `secrets` takes `ANTHROPIC_API_KEY` and the database password from
       Secrets Manager. Terraform creates the API key secret with no value.
     - The task role can only read its two secrets, write to EFS and write
       telemetry.
     - No `enableExecuteCommand`, so nobody gets a shell in a task (DATA-001).
   - **ECS service.**
     - It uses the deployment circuit breaker with rollback.
     - `desired_count` is a variable, and tasks are placed across AZs.
     - Its security group accepts port 8000 only from the ALB.
   - **ALB.**
     - It runs HTTPS only, with the ACM certificate and a TLS 1.2+ policy. HTTP
       redirects to HTTPS.
     - Its default action is `authenticate-cognito` or `authenticate-oidc`,
       then forward. The health check uses `/health`.
     - Its access logs go to an S3 bucket with a `retention_days` lifecycle.
   - **WAF.** When `enable_waf` is true (prod), AWS WAF uses the AWS managed
     common rule set and a rate-based rule per client IP. That closes
     "Nothing limits the number of sessions" in `docs/SECURITY.md`.
6. **`sandbox` (SBX-001).** Fargate can't run Docker inside a task, so the
   verification sandbox from A02 becomes its own task definition. The agent's
   `run_verify` tool starts it with `RunTask` and waits for its exit code.
   - It has no task role and no secrets, so no credentials.
   - It has no `ExecuteCommand`.
   - It runs in a subnet whose security group allows egress only through the
     firewall to `package_registries`.
   - It has `readonlyRootFilesystem`, and the work item comes in on its own EFS
     access point, read-only.
   - The `run_verify` tool's change to call `RunTask` is part of this phase:
     `docker run` stays the local path, chosen by an environment variable.
   - If A02 hasn't run, record this module as `deferred`.
7. **Environments.** `envs/dev` and `envs/prod` each call every module. Every
   difference is a variable in `terraform.tfvars`:
   - sizes and `desired_count`
   - `multi_az`, `deletion_protection`, `enable_waf` and
     `enable_network_firewall`
   - `web_ui`
   - the domain
   - the image digest, which H05's workflow sets
8. **Cost note.** In the plan, list what each environment costs at idle: NAT
   gateways, Network Firewall endpoints, Multi-AZ RDS, the ALB, interface
   endpoints and managed Grafana. Use the AWS Pricing Calculator's figures for the
   chosen region. Name the variables that cut it in dev.

### Acceptance criteria

- [ ] `terraform fmt -check -recursive` and, in each of `envs/dev`, `envs/prod`
      and `bootstrap`, `terraform init -backend=false && terraform validate`
      pass.
- [ ] `tflint --recursive` passes.
- [ ] `checkov -d infra/terraform` passes, or each skipped check carries its
      reason inline (`#checkov:skip=<id>: <why>`).
- [ ] A test, `tests/governance/test_infra.py`, parses the `service` module and
      checks that:
      - the task definition sets `readonlyRootFilesystem = true`
      - no `enableExecuteCommand` is set
      - the ALB has an authenticate action
- [ ] The two `terraform.tfvars` files set the same variables.

### Ledger

EVID-001 (hosted session log and retention), DATA-001 (hosted egress allowlist,
no `ExecuteCommand`), SBX-001 (hosted sandbox).

---

## Phase H04: Telemetry and evidence

**Goal:** every span, metric and log the local stack receives reaches an AWS
backend, through an allowlisted exporter, with nothing lost.

**Rules:** OBS-001, DATA-001, EVID-001, COST-001.

**Scope paths:** `ops/observability/aws/**`, `infra/terraform/**`,
`app/governance.py`, `ops/observability/alerts.yaml`, `tests/**`,
`proposals/H00/**`, `docs/exec-plans/**`.

### Build

1. **Collector sidecar.** The task definition runs the AWS Distro for
   OpenTelemetry collector (`public.ecr.aws/aws-observability/aws-otel-collector`,
   pinned by digest) next to the agent. The agent sets
   `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`. ADK sets up its exporters
   at server start from that variable, as `ops/observability/README.md`
   describes.
2. **`ops/observability/aws/collector.yaml`.** Receives OTLP and exports:
   - traces to X-Ray (`awsxray`)
   - metrics to managed Prometheus (`prometheusremotewrite`, with the
     `sigv4auth` extension)
   - logs to CloudWatch Logs (`awscloudwatchlogs`)

   Give every exporter an explicit `endpoint`, so the allowlist test can read it.
   With the self-hosted option, this file instead points at the stack's services
   on ECS.
3. **Allowlist (DATA-001).** `proposals/H00/governance/allowlists/services.yaml`
   adds each new exporter endpoint to `telemetry_exporters`.
   `tests/governance/test_observability.py` checks both collector configs
   against it, so each test runs once per file.
4. **Session token metric.** `governance.session_tokens` is a gauge labelled
   with `session.id`, so its cardinality grows with every session. That's fine
   locally, but costly in a shared backend (see the tech-debt tracker).
   - Replace it with a histogram, `governance.session_tokens`, recorded at each
     model call's end with no `session.id` label. The span still carries the
     session.
   - Update `SessionTokenSpike` in `alerts.yaml` to use the histogram's maximum
     bucket, and update the in-memory exporter test.
5. **Alerts and dashboard.**
   - Load `ops/observability/alerts.yaml` into managed Prometheus as a rule
     group namespace, and send its alerts to an SNS topic the owner subscribes
     to. That closes "alerts notify nobody".
   - Load `ops/observability/grafana/dashboards/governance.json` into managed
     Grafana.
   - Change the dashboard's datasource UIDs to variables if they're
     hard-coded.
6. **Retention (EVID-001).** CloudWatch log groups and X-Ray keep data for
   `retention_days`. X-Ray's own retention is fixed at 30 days, so turn on
   CloudWatch Transaction Search to keep spans in CloudWatch Logs for the full
   period. Check that it's available in the region, and record it as an open
   question if not. Managed Prometheus retention is set to at least
   `retention_days`.
7. **Message content.** The task definition sets
   `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS` from the hosting input: `false` in prod.

### Acceptance criteria

- [ ] `tests/governance/test_observability.py` passes for both collector configs
      against the proposed allowlist.
- [ ] The in-memory exporter test passes with the histogram, and every OBS-001
      attribute is still present.
- [ ] `otelcol validate` passes for `ops/observability/aws/collector.yaml`, using
      the pinned ADOT image, or it's `deferred`.

### Ledger

OBS-001 (hosted), DATA-001 (hosted exporters).

---

## Phase H05: Build and promote

**Goal:** an image is built once, from a clean governance tree. Prod runs only the
digest that passed in dev, and only when the owner says so.

**Rules:** GOV-002, GOV-004, DEP-001, COST-001, and DEPLOY-001 once accepted.

**Scope paths:** `proposals/H00/**`, `infra/terraform/**`, `docs/exec-plans/**`.

### Build

1. **`ci` module.** Creates the GitHub OIDC identity provider and, per account,
   one role. The trust policy is limited to this repository and to:
   - in dev, the `main` branch
   - in prod, the `prod` GitHub environment

   Each role can push to or pull from ECR, register the task definition, update
   only its own ECS service, and pass only its own task role. There are no
   long-lived access keys.
2. **`proposals/H00/.github/workflows/deploy.yml`.**
   - **On push to `main`:**
     1. Run `scripts/build_image.sh`, push to dev's ECR, and record the digest.
     2. Register a dev task definition with that digest, deploy it, and wait for
        the service to be stable.
     3. Wait until the target group reports the new tasks healthy. The ALB's
        health checks call `/health` on each task directly, without the
        authenticate action, so this needs no login.
   - **On `workflow_dispatch`:** takes a `digest` input and deploys it to prod.
     The job refuses a digest that:
     - isn't in dev's ECR
     - wasn't the last digest deployed to dev successfully
     - has no `governance.sha` label, or a label that doesn't match
       `git rev-parse HEAD:governance` on `main`
   - **On every job:** use `permissions: id-token: write, contents: read`, pin
     third-party actions by commit SHA, and write a job summary with the digest
     and governance hash.
3. **`proposals/H00/.github/workflows/infra.yml`.** On pull requests that touch
   `infra/`, run `terraform fmt -check`, `validate`, `tflint` and `checkov`.
   There's no `plan` or `apply` in CI. The owner runs both by hand until the
   owner decides otherwise.
4. **`proposals/H00/governance/rules-additions.yaml`.** The owner chooses which
   of these to adopt, as in A06:

   ```yaml
   - id: HOST-001
     applies_to: [runtime]
     rule: Hosted endpoints authenticate every request and bind user_id to the verified identity
     because: ADK's server has no authentication, so any caller who reaches it can read or change any user's sessions.
     tier: deny
     kind: safety
     controls:
       - {type: D, at: runtime, by: ALB authenticate action (H03), status: planned}
       - {type: D, at: runtime, by: identity-binding middleware in scripts/serve.py (H02), status: planned}
   - id: DEPLOY-001
     applies_to: [runtime]
     rule: Prod runs only an image digest that passed in dev and carries a committed governance hash
     because: an image built or changed outside the pipeline carries rules nobody approved.
     tier: deny
     kind: safety
     controls:
       - {type: D, at: ci, by: deploy workflow digest and label check (H05), status: planned}
       - {type: H, at: merge, by: owner runs the prod workflow_dispatch, status: planned}
   ```

### Acceptance criteria

- [ ] `actionlint` passes on both proposed workflows.
- [ ] The workflows reference only actions pinned by SHA.
- [ ] `terraform validate` passes with the `ci` module in both environments.

### Ledger

DEP-001 (pinned image and actions), and DEPLOY-001 once proposed.

---

## Phase H06: Full verification and activation proposal

**Goal:** everything is checked together, and the owner gets one reviewable
statement of what is proven, what is deferred, and what to do next.

**Rules:** GOV-002, GOV-003, EVID-001, DATA-001.

**Scope paths:** `docs/**`, `tests/**`, `proposals/H00/**`.

### Build

1. **Run everything.** The full unit and governance suites, the Terraform
   checks, `actionlint`, and the image build and local container run if a
   container runtime is reachable. Fix what this run broke. Never fix a failure
   by weakening a control, a test or a checkov rule.
2. **`docs/SECURITY.md`.** Add a "Hosted environments" section for the owner to
   sign off:
   - retention in RDS, AWS Backup, EFS, CloudWatch and S3
   - message content in traces
   - the approved AWS services
   - WAF rate limits
   - per-environment spend limits and AWS Budgets
   - incident response for a hosted agent:
     1. Scale the ECS service to 0.
     2. Revoke the environment's Anthropic key.
     3. Snapshot RDS and EFS.
     4. Export the traces.
3. **Complete the ledger.** Every control this file builds has a result and
   evidence that exists.
4. **`proposals/H00/governance/rules.yaml`.** As in A06: only this file's
   controls with a `pass` result and owner check `none` become `active`. Controls
   that need a deployed environment, such as the ALB authenticate action, stay
   `planned` until the owner's first deploy proves them.
5. **Tech-debt tracker.** Add every deferred item and every gap found, and the
   rows from "Known gaps" below.
6. **Close the plan.**
   - List every owner action from "After the run", and each deferred check.
   - Tick the parts, and move the plan to `docs/exec-plans/completed/`.
   - Commit with the trailers.
7. **Stop.** Give the final report:
   - parts completed, deferred and blocked
   - the controls proposed as `active`, and why the rest stay `planned`
   - the idle cost per environment
   - the owner actions, in order

### Acceptance criteria

- [ ] `scripts/check_activation.py proposals/H00/governance/rules.yaml` passes.
- [ ] The final report lists every item the ledger doesn't show as `pass`.

---

## Alternatives to ECS Fargate

ECS Fargate is recommended because it runs ADK's documented container unchanged,
and supports the collector sidecar, EFS and per-task security groups. It also
needs no cluster to manage. The others fit some projects better.

| Option | Prefer it when | What changes for the controls | Verdict |
| --- | --- | --- | --- |
| **Amazon Bedrock AgentCore Runtime** | You want a managed, agent-specific host with per-session isolation, long-running sessions and built-in identity, and you'll run models on Bedrock. | AgentCore invokes the container through its own HTTP contract instead of ADK's routes, so `scripts/serve.py` becomes an adapter that calls ADK's `Runner`. AgentCore Identity replaces the ALB auth and the identity middleware (HOST-001). Its memory and observability services would need allowlisting (DATA-001). Sessions should still go to RDS, so EVID-001 doesn't depend on AgentCore's retention. | **The strongest alternative.** Worth a separate plan once the agent is stable, especially alongside a move to Bedrock models. Check the contract against AWS's current docs, because the service is young. |
| **AWS App Runner** | A small internal tool, where the lowest operational effort matters more than control. | No sidecars, so telemetry must export straight from the agent, and no EFS, so `output_root` and artifacts need S3 and a custom `BaseArtifactService`. No Network Firewall, so DATA-001's egress allowlist is lost. | **Not recommended.** It loses SBX-001's and DATA-001's network controls. Check App Runner's current availability before considering it. |
| **Amazon EKS** | The organisation already runs EKS and has a platform team. | ADK's `adk deploy gke` manifests are a starting point. Pod security standards replace the task settings, NetworkPolicies and an egress gateway replace the firewall, and IRSA or Pod Identity replace task roles. Everything else is the same. | **Fine where EKS already exists.** Otherwise it's a cluster to run for one service. |
| **AWS Lambda** | Never, for this agent. | It has a 15-minute cap per invocation, cold starts, and nowhere to hold a session that waits on a human confirmation (TOOL-001's `confirm` tier). There's no sidecar for the collector. | **Unsuitable.** |
| **ECS on EC2** | Sustained high load, where reserved capacity is cheaper, or the sandbox needs Docker-in-Docker. | Hosts to patch, and the sandbox could use Docker on the host, which needs careful isolation (SBX-001). | **A cost optimisation later,** not a starting point. |

---

## After the run

These are for the owner, in this order. The run lists them and does not attempt
them.

1. **Review the branch.** Check everything in `proposals/H00/`, the identity
   middleware and its tests, the `service` and `network` modules, and the idle
   cost in the plan.
2. **Choose the additional rules.** Add those you accept from
   `proposals/H00/governance/rules-additions.yaml` to
   `proposals/H00/governance/rules.yaml`, give each a ledger row, then delete the
   additions file.
3. **Check the proposal, then apply it in one commit:**

   ```bash
   .venv/bin/python scripts/check_activation.py proposals/H00/governance/rules.yaml
   cp -R proposals/H00/. . && rm -rf proposals/H00
   ```

4. **Push, open a pull request and merge.** Running sessions stop at their next
   prompt once the hash changes (GOV-006).
5. **Bootstrap each account,** with an admin role, from your own machine:

   ```bash
   cd infra/terraform/bootstrap && terraform init && terraform apply
   cd ../envs/dev && terraform init && terraform plan -out tfplan
   ```

   Read the plan, then apply it. Do dev first, and prod only after dev works.
6. **Set the secrets.** Put each environment's Anthropic API key into its empty
   Secrets Manager secret. Use a separate Console workspace per environment, each
   with a spend limit. Set an AWS Budgets alert per account (COST-001).
7. **Wire up CI.** Add the dev and prod role ARNs as repository variables. Create
   the `prod` GitHub environment. The first push to `main` builds the image and
   deploys dev.
8. **Prove the controls in dev.** For each control the ledger left `planned`
   because it needed a deployed environment, run its check:
   - Unauthenticated requests get the login redirect.
   - Another user's `user_id` gets 403.
   - A task has no shell.
   - Spans, metrics and alerts arrive.
   - Egress to a non-allowlisted host fails, in prod.

   Set each to `active` in a governance commit when it passes.
9. **Promote to prod** with the deploy workflow's `workflow_dispatch`, using the
   digest dev is running.
10. **Sign off the "Hosted environments" section of `docs/SECURITY.md`** before
    the first prod release. Then hold an evidence review that covers a hosted
    session.

After that, normal working applies. Each change to `infra/` is its own plan. Each
image reaches prod only through dev.

---

## Verified facts

These were checked against the installed `google-adk==2.14.0` source, except where
a fact says otherwise. Re-check any you rely on after an upgrade.

- **Serving:**
  - `get_fast_api_app` (`google/adk/cli/fast_api.py`) takes these keyword
    arguments: `agents_dir`, `session_service_uri`, `artifact_service_uri`,
    `memory_service_uri`, `use_local_storage` (default `True`), `allow_origins`,
    `web` (required), `host` (default `127.0.0.1`), `bind_host` and `port`
    (default `8000`), among others.
  - A non-loopback `bind_host` makes it log that the server has no
    authentication, and that any client can read, change and delete any user's
    sessions and artifacts.
  - The server always registers `GET /health` (it returns
    `{"status": "ok"}`) and `GET /version` (`cli/api_server.py`).
- **`user_id` appears in three places:**
  - the path of the `/apps/{app_name}/users/{user_id}/...` session, artifact and
    memory routes
  - the JSON body of `/run` and `/run_sse` (`RunAgentRequest.user_id`)
  - a query parameter of the `/run_live` websocket
- **The DNS-rebinding guard** (`_is_dns_rebinding_request`) applies only to a
  loopback bind. A literal `"*"` in `allow_origins` switches it off.
- **`adk deploy` targets** are `cloud_run`, `docker` (a local container),
  `agent_engine` and `gke`. None of them targets AWS.
  - Its generated Dockerfile uses `python:<version>-slim`, a non-root user and
    exec-form `CMD` (`cli/deployers/_dockerfile_template.py`).
  - Its deployers set `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false` unless it's
    already set (`cli/cli_deploy.py`).
- **Storage:**
  - An unset service URI falls back to local `.adk` storage.
  - When the directory isn't writable (`EACCES`, `EPERM` or `EROFS`), ADK falls
    back to in-memory storage, unless `ADK_FORCE_LOCAL_STORAGE` or
    `ADK_DISABLE_LOCAL_STORAGE` is set (`cli/utils/service_factory.py`).
- **`DatabaseSessionService`** needs an async driver. A URL that names none is
  refused. PostgreSQL uses `asyncpg`, so the URL is `postgresql+asyncpg://`.
- **Artifact services** in Python are in-memory, GCS and file
  (`google/adk/artifacts/`). There is no S3 artifact service.
- **Telemetry:** the API server sets up OpenTelemetry exporters at start from
  `OTEL_EXPORTER_OTLP_ENDPOINT` and the per-signal variables
  (`telemetry/setup.py`).
- **AWS facts,** from AWS documentation, not checked in this repo:
  - RDS automated backups keep at most 35 days.
  - The ALB's `x-amzn-oidc-data` is an ES256 JWT, with public keys at
    `public-keys.auth.elb.<region>.amazonaws.com/<kid>`, and a `signer` field
    that names the ALB's ARN.
  - Lambda invocations are capped at 15 minutes.
  - Terraform 1.10 added S3 native state locking.

## Known gaps

Seed `docs/exec-plans/tech-debt-tracker.md` with these:

| Gap | Rule | Close by |
| --- | --- | --- |
| Inside the image, `before_run_callback`'s governance re-check compares two values that can't change. It's sound only while the root filesystem is read-only. | GOV-005 | The `test_infra.py` check on `readonlyRootFilesystem`; never turn it off |
| Identity binding is custom middleware in front of ADK, because ADK 2.14's server has no authentication hook. A new ADK route that carries `user_id` somewhere else would bypass it. | HOST-001 | The route allowlist refuses unknown routes; re-check routes on every ADK upgrade |
| Private GitHub Free can't require reviewers on the `prod` environment, so prod deploys rest on the owner running `workflow_dispatch`. | DEPLOY-001 | A GitHub plan with environment protection rules |
| X-Ray keeps traces for 30 days. Keeping spans for `retention_days` relies on CloudWatch Transaction Search. | EVID-001 | Confirm Transaction Search in the region, or export spans to S3 |
| Session logs in RDS hold prompts unredacted, as they do locally. | DATA-001 | `docs/SECURITY.md` sign-off |
| The verification sandbox on Fargate is a different runtime from A02's local Docker sandbox, so a check could pass in one and fail in the other. | SBX-001 | Run the sandbox tests against both before the first prod release |

## Sources

- Google ADK documentation, "Deploy", "API server", "Sessions" and "Traces"
  (adk.dev), and the installed `google-adk` 2.14 source.
- AWS Well-Architected Framework, Security and Reliability pillars.
- AWS documentation: ALB user authentication, ECS task definitions, AWS Backup,
  Network Firewall, AWS Distro for OpenTelemetry, and Bedrock AgentCore.
- `docs/governance_implementation.md` and
  `docs/agent_governance_implementation.md`, whose run conventions this file
  follows.
