"""DATA-001: the telemetry stack sends data only to allowlisted services."""

import json
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).parent.parent.parent
STACK = PROJECT / 'ops/observability'
COLLECTOR = yaml.safe_load((STACK / 'collector.yaml').read_text())
COMPOSE = yaml.safe_load((STACK / 'docker-compose.yaml').read_text())
SERVICES = yaml.safe_load((PROJECT / 'governance/allowlists/services.yaml').read_text())


def test_collector_exporters_match_the_allowlist():
  endpoints = [exporter['endpoint'] for exporter in COLLECTOR['exporters'].values()]
  assert sorted(endpoints) == sorted(SERVICES['telemetry_exporters'])


def test_every_pipeline_uses_only_those_exporters():
  pipelines = COLLECTOR['service']['pipelines'].values()
  assert {exporter for pipeline in pipelines for exporter in pipeline['exporters']} == set(
    COLLECTOR['exporters']
  )


@pytest.mark.parametrize('name', COMPOSE['services'])
def test_compose_service_is_pinned_and_local(name):
  service = COMPOSE['services'][name]
  tag = service['image'].rsplit(':', 1)[1]
  assert tag[-1].isdigit(), service['image']
  assert all(port.startswith('127.0.0.1:') for port in service['ports'])
  assert service['restart'] == 'unless-stopped'


def test_compose_project_has_its_own_name():
  assert COMPOSE['name'] == 'agentic_bootstrap-observability'


def test_prometheus_receives_otlp():
  assert '--web.enable-otlp-receiver' in COMPOSE['services']['prometheus']['command']


def test_dashboard_parses():
  assert json.loads((STACK / 'grafana/dashboards/governance.json').read_text())['panels']
