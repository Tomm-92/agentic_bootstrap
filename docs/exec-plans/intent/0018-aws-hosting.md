# Intent 0018: AWS hosting instructions

Author: Claude, drafted for the owner
Status: Accepted
Accepted by: Thomas M, 2026-11-21

<!-- Copy to docs/exec-plans/intent/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts the spec. -->

## Problem

The four instruction files in `docs/` take a project from an empty repo to a governed
product agent. None of them says how that agent leaves the developer's machine. Today
it runs only through `adk web` or `scripts/local_session.py`, with sessions in SQLite,
telemetry in the local Compose stack, and the governance hash read from git at
startup.

A team that wants to host the agent has to work out the rest itself: where it runs,
how it's reached, where sessions and evidence live, and how dev differs from prod.
Each project would answer differently, and some answers would quietly break the
controls. For example, a container without git fails closed (GOV-005). A shared
endpoint exposes every user's sessions, because ADK's server has no authentication.
Exporting traces to a new backend breaks DATA-001's allowlist.

## Proposed outcome

A fifth instruction file, `docs/aws_hosting_implementation.md`, that an AI coding
assistant implements in one run, in the same shape as the other four. Running it
produces:

- a container image for the product agent that serves it with ADK's own server, and
  carries the governance hash it was built from.
- Terraform for a dev and a prod environment on AWS, with ECS Fargate as the
  recommended host.
- a promotion path where prod runs only the image digest that passed in dev.
- proposals for every protected-path change it needs, such as new allowlisted
  services, packages and rules, for the owner to apply.

The file also explains the AWS alternatives to ECS Fargate (Bedrock AgentCore Runtime,
App Runner, EKS and Lambda), and when each is the better fit.

The README's "Getting started" lists the fifth file.

## Affected users and systems

- Project owners: they choose AWS accounts and regions, approve the cost, and apply the
  proposals.
- The product agent in `app/`: the run changes how it reads the governance hash, and
  how it gets its session service and telemetry when hosted.
- `governance/`: through proposals only. That means services, packages and possibly
  new rules.
- CI: a new build-and-deploy workflow, delivered as a proposal under `.github/`.
- The README.

## Constraints

- The hosted agent keeps every runtime control it has locally: fail closed on
  governance (GOV-005), the durable session log (EVID-001), the token budget
  (COST-001), the tool policy (TOOL-001, FS-001) and the telemetry attributes
  (OBS-001).
- It follows Google ADK's documented serving route: `get_fast_api_app` or
  `adk api_server` in a container. No custom agent server.
- Data goes only to allowlisted services (DATA-001). New dependencies need the
  owner's approval (DEP-001). No secret goes into an image or a commit (SEC-001,
  SEC-002).
- The infrastructure is written in Terraform.
- Agents never apply infrastructure or deploy. The run writes code, plans and
  proposals. Only the owner runs `terraform apply` and spends money (COST-001).
- The new file is protected after it lands, like the other four (GOV-002). That
  needs a proposal.

## Open questions

- Should the file run after `docs/agent_governance_implementation.md` only, or also
  against the placeholder agent?
- Should model calls stay on `api.anthropic.com`, or move to Amazon Bedrock? A move
  changes the model provider, the allowlisted IDs and the evals (MODEL-001).
- Where should telemetry go in AWS? The options are CloudWatch and X-Ray, Amazon
  Managed Prometheus and Grafana, or the existing Tempo, Prometheus and Loki stack
  self-hosted.
- How do users authenticate? The options are Cognito or an existing OIDC provider
  at the load balancer.
- One AWS account per environment, or one account with separate VPCs?
