# Security: operational readiness review

The owner signs this checklist off before each release (DATA-001). Phase A05 adds the
sandbox and output items.

**Signed off by:** not yet signed. **Date:** not yet signed.

## Data handling and retention

- [ ] `retention_days` in `governance/thresholds.yaml` is 90. Nothing expires evidence
      automatically, so the owner has decided how this is met for `.sessions/`, the stack's
      Docker volumes, CI artifacts and coding-agent transcripts.
- [ ] Session logs live at `.sessions/sessions.db` (`scripts/local_session.py`) and
      `app/.adk/session.db` (`adk web`). Git ignores both because they hold prompts.

## Redaction

- [ ] Session logs hold prompts and tool results unredacted. The owner accepts this, or
      has added redaction.
- [ ] ADK records prompts and responses in its spans by default, so traces in Tempo hold
      them. `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false` turns this off. The owner has
      decided this deliberately, and has turned it off for any backend outside this machine.
- [ ] No secret reaches a session or trace. Gitleaks scans commits, and phase A02 adds
      output scanning.

## Approved services

- [ ] `governance/allowlists/services.yaml` lists every service that receives data.
      Today that's `api.anthropic.com` and the local stack.
- [ ] `tests/governance/test_observability.py` passes, so collector exporters match it.

## Model-provider outage

- [ ] During an outage, the model call fails, `on_model_error_callback` marks the span
      `failure.source: model`, and the session ends with the error. There is no fallback
      model, because one could fall outside `allowlists/models.yaml` (MODEL-001).
      The owner accepts this behaviour.

## Rate limits and cost caps

- [ ] `session_token_budget` is 200000 tokens per session, enforced by the governance layer.
      Nothing limits the number of sessions.
- [ ] The Console workspace behind the API key has a spend limit.
- [ ] The `SessionTokenSpike` alert in `observability/alerts.yaml` is being watched.

## Incident response

1. Stop the agent: revoke the API key, or make `governance/` dirty so it refuses to start.
2. Keep the evidence: copy `.sessions/` and `app/.adk/session.db`, and export the traces.
3. Attribute the failure with `failure.source` on the session's spans.
4. Rotate any credential that may have been exposed.
5. Record what happened, and draft any rule change under `proposals/`.
