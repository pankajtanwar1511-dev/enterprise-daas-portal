# Phase 3 Implementation Plan

**Created:** February 22, 2026
**Status:** 📋 **PLANNING** - Ready to start implementation
**Phase 2 Completion:** 100% - All 7 backend features implemented

---

## Executive Summary

Phase 2 successfully delivered all 7 enterprise governance features with 58 new API endpoints. Phase 3 focuses on **frontend visualization**, **external integrations**, **testing**, and **production readiness**.

### Phase Transition

```
Phase 2 (COMPLETE):
├── ✅ Backend services implemented (7 features)
├── ✅ API endpoints operational (58 endpoints)
├── ✅ Database schema complete (11 new tables)
└── ✅ Core functionality verified

Phase 3 (PLANNED):
├── 🎨 Frontend Components & Visualizations
├── 🔌 External System Integrations
├── 🧪 Comprehensive Testing Suite
└── 🚀 Production Deployment & Documentation
```

---

## 🎨 Track 1: Frontend Components & Visualizations

**Priority:** HIGH
**Estimated Effort:** 3-4 weeks
**Dependencies:** Phase 2 backend complete ✅

### 1.1 Impact Analysis Visualization

**Component:** `ImpactAnalysisVisualizer.jsx`
**Technology:** React + D3.js or React Flow
**Location:** `frontend/src/components/impact/`

#### Features to Implement:
- **Dependency Graph Visualization**
  - Interactive node-link diagram showing asset dependencies
  - Color coding by impact level (LOW=green, MEDIUM=yellow, HIGH=orange, CRITICAL=red)
  - Zoom/pan controls for large graphs (1000+ nodes)
  - Node tooltips showing asset details on hover
  - Expand/collapse nodes to control graph complexity

- **Impact Analysis Dashboard**
  - Summary cards: Total dependencies, Impact score, Migration hours
  - Recommendations panel with actionable steps
  - Stakeholder list with contact information
  - Change type selector (deprecation, schema_change, deletion, etc.)

- **Analysis History Viewer**
  - Timeline of past impact analyses
  - Comparison tool to see how impact changed over time
  - Export to PDF/PNG for presentations

#### API Endpoints Used:
```
POST   /api/v1/impact/analyze/{asset_id}
GET    /api/v1/impact/visualization/{asset_id}
GET    /api/v1/impact/history/{asset_id}
```

#### Example D3.js Integration:
```javascript
import * as d3 from 'd3';
import { useEffect, useRef } from 'react';

const ImpactGraph = ({ assetId }) => {
  const svgRef = useRef();

  useEffect(() => {
    // Fetch visualization data
    fetch(`/api/v1/impact/visualization/${assetId}`)
      .then(res => res.json())
      .then(data => {
        const { nodes, edges } = data;

        // Create D3 force simulation
        const simulation = d3.forceSimulation(nodes)
          .force("link", d3.forceLink(edges).id(d => d.id))
          .force("charge", d3.forceManyBody().strength(-300))
          .force("center", d3.forceCenter(width / 2, height / 2));

        // Render graph...
      });
  }, [assetId]);

  return <svg ref={svgRef} width={800} height={600} />;
};
```

---

### 1.2 Data Lineage Diagram

**Component:** `LineageDiagram.jsx`
**Technology:** React Flow (reactflow.dev)
**Location:** `frontend/src/components/lineage/`

#### Features to Implement:
- **Interactive Lineage Graph**
  - Horizontal flow: sources → transformations → targets
  - Node types: TABLE, VIEW, FILE, API, STREAM, DASHBOARD, MODEL
  - Edge labels showing transformation types (SELECT, JOIN, AGGREGATE, etc.)
  - Minimap for navigation on large lineages
  - Auto-layout with Dagre algorithm

- **Lineage Explorer**
  - Search/filter by asset name, type, or environment
  - Toggle upstream/downstream views
  - Column-level lineage drill-down
  - Transformation logic viewer (SQL queries)

- **Lineage Registration Form**
  - Manual lineage creation UI
  - SQL query parser with syntax highlighting
  - Bulk import from CSV/JSON
  - Verification workflow for stale lineage

#### API Endpoints Used:
```
POST   /api/v1/lineage/register
POST   /api/v1/lineage/parse-sql
GET    /api/v1/lineage/path/{asset_id}
GET    /api/v1/lineage/nodes
GET    /api/v1/lineage/edges
```

#### React Flow Example:
```javascript
import ReactFlow, { Background, Controls } from 'reactflow';

const LineageDiagram = ({ assetId }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
    fetch(`/api/v1/lineage/path/${assetId}?direction=both`)
      .then(res => res.json())
      .then(data => {
        // Transform API data to React Flow format
        const flowNodes = data.nodes.map(n => ({
          id: n.node_id.toString(),
          data: { label: n.node_name, type: n.node_type },
          position: { x: 0, y: 0 }, // Auto-layout will position
          type: 'custom'
        }));

        setNodes(flowNodes);
        setEdges(data.edges);
      });
  }, [assetId]);

  return (
    <ReactFlow nodes={nodes} edges={edges}>
      <Background />
      <Controls />
    </ReactFlow>
  );
};
```

---

### 1.3 Schema Registry UI

**Component:** `SchemaRegistry.jsx`
**Location:** `frontend/src/components/schemas/`

#### Features to Implement:
- **Schema Browser**
  - List all subjects with version counts
  - Filter by schema format (Avro, JSON Schema, Protobuf)
  - Search by subject name or content

- **Version History Viewer**
  - Timeline showing all versions of a schema
  - Diff tool comparing adjacent versions (added/removed/modified fields)
  - Deprecation warnings and compatibility badges

- **Schema Registration Form**
  - Monaco Editor for schema editing with JSON Schema validation
  - Format selector with examples
  - Compatibility mode dropdown with explanations
  - Preview validation results before registration

- **Schema Validation Tester**
  - Paste sample data to validate against schema
  - Live validation feedback with error highlighting
  - Example data generator from schema

#### API Endpoints Used:
```
POST   /api/v1/schemas/register
GET    /api/v1/schemas/subjects
GET    /api/v1/schemas/compare/{subject}
POST   /api/v1/schemas/validate/{subject}
```

---

### 1.4 Data Quality Dashboards

**Component:** `QualityDashboard.jsx`
**Location:** `frontend/src/components/quality/`

#### Features to Implement:
- **Quality Score Cards**
  - Overall quality score with letter grade (A-F)
  - Score breakdown by 6 dimensions (COMPLETENESS, ACCURACY, etc.)
  - Trend charts showing score over time
  - Asset comparison heatmap

- **Rule Management UI**
  - Create rules from pre-built templates
  - Custom SQL rule editor with syntax highlighting
  - Rule scheduling configuration
  - Enable/disable rules

- **Quality Check History**
  - Timeline of all check runs
  - Pass/fail indicators with details
  - Anomaly detection alerts
  - Drill-down to failing records

- **Alerting Configuration**
  - Configure Slack/Email/PagerDuty channels
  - Threshold settings for alerts
  - Alert history and acknowledgment

#### API Endpoints Used:
```
POST   /api/v1/quality/rules
POST   /api/v1/quality/rules/{rule_id}/execute
GET    /api/v1/quality/assets/{asset_id}/score
GET    /api/v1/quality/rules/{rule_id}/anomalies
```

#### Quality Score Visualization:
```javascript
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';

const QualityScoreCard = ({ assetId }) => {
  const [score, setScore] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/quality/assets/${assetId}/score`)
      .then(res => res.json())
      .then(data => setScore(data));
  }, [assetId]);

  return (
    <div>
      <CircularProgressbar
        value={score?.overall_score || 0}
        text={`${score?.overall_score}%`}
        styles={buildStyles({
          pathColor: score?.overall_score > 80 ? 'green' : 'orange',
          textColor: '#333'
        })}
      />
      <p>Grade: {score?.grade}</p>
    </div>
  );
};
```

---

### 1.5 SLA Monitoring Dashboard

**Component:** `SLADashboard.jsx`
**Location:** `frontend/src/components/sla/`

#### Features to Implement:
- **Real-time SLA Status**
  - Metric cards showing current vs target values
  - Green/yellow/red status indicators
  - Gauge charts for availability/performance metrics
  - Last measured timestamp

- **Violation Timeline**
  - Chronological list of SLA breaches
  - Severity indicators (CRITICAL, HIGH, MEDIUM, LOW)
  - Resolution status and MTTR
  - Root cause and remediation notes

- **Compliance Trends**
  - Line charts showing compliance % over time
  - Comparison across multiple metrics
  - Violation frequency heatmap
  - Export to reports

- **Metric Collection UI**
  - Manual metric entry form
  - Prometheus/CloudWatch integration setup
  - Test connection buttons
  - Collection history log

#### API Endpoints Used:
```
GET    /api/v1/sla/status
GET    /api/v1/sla/violations
GET    /api/v1/sla/metrics/{metric_id}/trend
POST   /api/v1/sla/metrics/define
```

---

### 1.6 Event Catalog Browser

**Component:** `EventCatalog.jsx`
**Location:** `frontend/src/components/events/`

#### Features to Implement:
- **Event Search & Browse**
  - Searchable catalog of all events
  - Filter by producer, format, status (active/deprecated)
  - Event cards showing consumer count, version, description

- **Event Version Viewer**
  - Version history timeline
  - Schema diff between versions
  - Deprecation warnings
  - Migration guide generator

- **Producer/Consumer Map**
  - Visual diagram showing event flow
  - Producer asset → Event → Consumer assets
  - Click to navigate to asset details

- **Breaking Change Checker**
  - Paste new schema to check compatibility
  - List of breaking changes and warnings
  - Recommendation (safe to update vs new major version)

- **Event Registration Form**
  - Event name and description
  - Schema editor with format selector
  - Producer asset picker
  - Compatibility mode selector

#### API Endpoints Used:
```
GET    /api/v1/events/catalog
GET    /api/v1/events/{event_name}/versions
POST   /api/v1/events/{event_name}/check-breaking-changes
GET    /api/v1/events/{event_name}/consumers
```

---

### 1.7 Policy Enforcement UI

**Component:** `PolicyManager.jsx`
**Location:** `frontend/src/components/policies/`

#### Features to Implement:
- **Policy Configuration Dashboard**
  - List all policies with enable/disable toggles
  - Policy type badges (NAMING, DOCUMENTATION, CLASSIFICATION, OWNER)
  - Blocking vs warning indicators
  - Edit/delete policy actions

- **Policy Validation Tester**
  - Enter asset data to test against policies
  - Real-time validation feedback
  - Violation details with fix suggestions

- **CI/CD Integration Guide**
  - GitHub Actions YAML download
  - GitLab CI YAML download
  - Setup instructions with copy-paste snippets
  - Example repository links

- **Validation History**
  - Timeline of policy checks
  - Pass/fail statistics
  - Pipeline context (branch, commit, author)
  - Blocked deployment alerts

#### API Endpoints Used:
```
POST   /api/v1/policies/create
POST   /api/v1/policies/validate
GET    /api/v1/policies/integrations/github-actions
GET    /api/v1/policies/validations
```

---

## Frontend Implementation Checklist

### Phase 3A: Core Visualizations (Week 1-2)
- [ ] Setup React Flow for lineage diagrams
- [ ] Setup D3.js for impact analysis graphs
- [ ] Create shared components: NodeCard, EdgeLabel, GraphControls
- [ ] Implement zoom/pan/filter utilities
- [ ] Add loading states and error handling

### Phase 3B: Dashboards (Week 2-3)
- [ ] Quality score dashboard with charts (react-chartjs-2)
- [ ] SLA monitoring dashboard with gauges
- [ ] Event catalog browser with search
- [ ] Policy management interface

### Phase 3C: Forms & Editors (Week 3-4)
- [ ] Schema registration form with Monaco Editor
- [ ] Lineage registration form with SQL parser
- [ ] Quality rule builder with template picker
- [ ] Policy configuration wizard

### Phase 3D: Integration & Polish (Week 4)
- [ ] Connect all components to API endpoints
- [ ] Add real-time updates (WebSocket or polling)
- [ ] Implement export features (PDF, PNG, CSV)
- [ ] Responsive design for mobile/tablet
- [ ] Accessibility improvements (ARIA labels, keyboard navigation)

---

## 🔌 Track 2: External System Integrations

**Priority:** MEDIUM
**Estimated Effort:** 2-3 weeks

### 2.1 Data Quality Integration - Great Expectations

**Integration:** Great Expectations (ge.io)
**Purpose:** Import existing data quality suites

#### Implementation Plan:
```python
# app/services/integrations/great_expectations.py

class GreatExpectationsImporter:
    """Import Great Expectations suites into quality engine"""

    def import_expectation_suite(self, suite_json: Dict) -> List[int]:
        """
        Convert GE expectations to quality rules

        GE Expectation → Quality Rule Mapping:
        - expect_column_values_to_not_be_null → null_check template
        - expect_column_values_to_be_unique → unique_check template
        - expect_column_values_to_be_between → range_check template
        - expect_column_values_to_match_regex → format_check template
        """
        rules = []
        for expectation in suite_json['expectations']:
            rule = self._convert_expectation(expectation)
            rules.append(self.quality_engine.create_rule(**rule))
        return rules
```

#### API Endpoints to Add:
```
POST   /api/v1/quality/import/great-expectations
GET    /api/v1/quality/export/great-expectations
```

---

### 2.2 SLA Monitoring Integration - Prometheus

**Integration:** Prometheus (prometheus.io)
**Purpose:** Automated metric collection

#### Implementation Status:
- ✅ Basic Prometheus collection implemented in `sla_monitor.py:collect_from_prometheus()`
- ⏳ Need to add PromQL query builder UI
- ⏳ Need to add metric discovery from Prometheus

#### Enhancement Plan:
```python
# app/services/integrations/prometheus.py

class PrometheusIntegration:
    def discover_metrics(self, prometheus_url: str) -> List[str]:
        """Query Prometheus metadata API to list available metrics"""
        response = requests.get(f"{prometheus_url}/api/v1/label/__name__/values")
        return response.json()['data']

    def suggest_queries(self, metric_name: str, sla_type: str) -> List[str]:
        """Suggest PromQL queries based on SLA metric type"""
        templates = {
            'AVAILABILITY': f'avg_over_time({metric_name}[5m])',
            'PERFORMANCE': f'histogram_quantile(0.95, {metric_name})',
            'RELIABILITY': f'rate({metric_name}[5m])'
        }
        return templates.get(sla_type, [])
```

---

### 2.3 SLA Monitoring Integration - AWS CloudWatch

**Integration:** AWS CloudWatch
**Purpose:** Cloud infrastructure metric collection

#### Implementation Status:
- ✅ Basic CloudWatch collection implemented in `sla_monitor.py:collect_from_cloudwatch()`
- ⏳ Need to add AWS credential management UI
- ⏳ Need to add namespace/metric discovery

#### Enhancement Plan:
```python
# app/services/integrations/cloudwatch.py

import boto3

class CloudWatchIntegration:
    def __init__(self, aws_region: str, credentials: Dict):
        self.client = boto3.client(
            'cloudwatch',
            region_name=aws_region,
            aws_access_key_id=credentials.get('access_key'),
            aws_secret_access_key=credentials.get('secret_key')
        )

    def list_namespaces(self) -> List[str]:
        """List available CloudWatch namespaces"""
        paginator = self.client.get_paginator('list_metrics')
        namespaces = set()
        for page in paginator.paginate():
            for metric in page['Metrics']:
                namespaces.add(metric['Namespace'])
        return sorted(namespaces)

    def list_metrics(self, namespace: str) -> List[Dict]:
        """List metrics in a namespace with dimensions"""
        response = self.client.list_metrics(Namespace=namespace)
        return response['Metrics']
```

---

### 2.4 Alerting Integration - Slack

**Integration:** Slack (slack.com)
**Purpose:** Real-time alerts for quality failures and SLA violations

#### Implementation Plan:
```python
# app/services/integrations/slack.py

import requests

class SlackNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_quality_alert(self, rule_name: str, asset_name: str,
                          failure_details: Dict):
        """Send quality check failure to Slack"""
        message = {
            "text": f"🚨 Quality Check Failed",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Quality Rule Failed:* {rule_name}\n*Asset:* {asset_name}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Result:* {failure_details['result_value']}"},
                        {"type": "mrkdwn", "text": f"*Threshold:* {failure_details['threshold']}"}
                    ]
                }
            ]
        }
        requests.post(self.webhook_url, json=message)

    def send_sla_violation(self, metric_name: str, violation: Dict):
        """Send SLA violation to Slack"""
        severity_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        # Similar message structure...
```

#### API Endpoints to Add:
```
POST   /api/v1/integrations/slack/configure
POST   /api/v1/integrations/slack/test
GET    /api/v1/integrations/slack/channels
```

---

### 2.5 Lineage Integration - dbt

**Integration:** dbt (getdbt.com)
**Purpose:** Import dbt model lineage automatically

#### Implementation Plan:
```python
# app/services/integrations/dbt.py

class DBTLineageImporter:
    def import_manifest(self, manifest_json: Dict) -> Dict:
        """
        Import lineage from dbt manifest.json

        dbt generates manifest.json with:
        - nodes: all models, seeds, snapshots
        - parent_map: upstream dependencies
        - child_map: downstream dependencies
        """
        nodes_created = 0
        edges_created = 0

        for node_id, node_data in manifest_json['nodes'].items():
            # Create lineage node for each dbt model
            if node_data['resource_type'] == 'model':
                lineage_node = self.lineage_tracker.create_node(
                    node_name=node_data['name'],
                    node_type='TABLE',
                    schema_definition=node_data['columns'],
                    description=node_data.get('description')
                )
                nodes_created += 1

        # Create edges from parent_map
        for node_id, parents in manifest_json['parent_map'].items():
            for parent_id in parents:
                edge = self.lineage_tracker.create_edge(
                    source=parent_id,
                    target=node_id,
                    transformation_type='SELECT',
                    transformation_logic=manifest_json['nodes'][node_id]['raw_sql']
                )
                edges_created += 1

        return {
            'nodes_created': nodes_created,
            'edges_created': edges_created
        }
```

#### API Endpoints to Add:
```
POST   /api/v1/lineage/import/dbt
GET    /api/v1/lineage/export/dbt
```

---

### 2.6 Lineage Integration - Apache Airflow

**Integration:** Apache Airflow
**Purpose:** Import DAG lineage

#### Implementation Plan:
```python
# app/services/integrations/airflow.py

class AirflowLineageImporter:
    def import_dag(self, dag_definition: Dict) -> Dict:
        """
        Import Airflow DAG as lineage

        DAG structure:
        - tasks: individual operations
        - dependencies: task >> task relationships
        """
        nodes = []
        edges = []

        for task_id, task_data in dag_definition['tasks'].items():
            # Map Airflow operators to lineage node types
            node_type_mapping = {
                'PostgresOperator': 'TABLE',
                'PythonOperator': 'SCRIPT',
                'BashOperator': 'SCRIPT',
                'S3ToRedshiftOperator': 'FILE'
            }

            node = self.lineage_tracker.create_node(
                node_name=task_id,
                node_type=node_type_mapping.get(task_data['operator'], 'CUSTOM'),
                description=task_data.get('doc')
            )
            nodes.append(node)

        # Create edges from dependencies
        for task_id, dependencies in dag_definition['dependencies'].items():
            for upstream_task in dependencies:
                edge = self.lineage_tracker.create_edge(
                    source=upstream_task,
                    target=task_id,
                    transformation_type='TRANSFORM'
                )
                edges.append(edge)

        return {'nodes': len(nodes), 'edges': len(edges)}
```

---

## Integration Implementation Checklist

### Phase 3E: Data Quality Integrations (Week 5)
- [ ] Great Expectations importer
- [ ] Slack alerting for quality failures
- [ ] Email alerting (SMTP configuration)
- [ ] PagerDuty integration for critical failures

### Phase 3F: SLA Monitoring Integrations (Week 6)
- [ ] Prometheus metric discovery UI
- [ ] CloudWatch namespace browser
- [ ] Datadog integration (optional)
- [ ] Grafana dashboard exporter

### Phase 3G: Lineage Integrations (Week 7)
- [ ] dbt manifest importer
- [ ] Airflow DAG parser
- [ ] Apache Atlas connector (optional)
- [ ] Collibra integration (optional)

---

## 🧪 Track 3: Comprehensive Testing

**Priority:** HIGH
**Estimated Effort:** 2 weeks

### 3.1 Backend Unit Tests

**Status:** Partially implemented, needs expansion
**Target Coverage:** >80%

#### Test Files to Create:

```
tests/
├── unit/
│   ├── test_impact_analyzer.py       ⏳ TO DO
│   ├── test_lineage_tracker.py       ⏳ TO DO
│   ├── test_schema_registry.py       ⏳ TO DO
│   ├── test_quality_engine.py        ⏳ TO DO
│   ├── test_policy_enforcer.py       ⏳ TO DO
│   ├── test_sla_monitor.py           ⏳ TO DO
│   └── test_event_manager.py         ⏳ TO DO
```

#### Example Test Structure:
```python
# tests/unit/test_quality_engine.py

import pytest
from app.services.quality_engine import QualityEngine
from app import models_advanced

@pytest.fixture
def quality_engine(db_session):
    return QualityEngine(db_session)

class TestQualityEngine:
    def test_create_rule_from_template(self, quality_engine):
        """Test creating rule from null_check template"""
        rule = quality_engine.create_rule_from_template(
            template_name="null_check",
            asset_id=1,
            table_name="customers",
            column_name="email",
            threshold=0.01
        )
        assert rule['dimension'] == 'COMPLETENESS'
        assert 'IS NULL' in rule['sql_query']

    def test_execute_rule_pass(self, quality_engine, mock_db):
        """Test rule execution with passing result"""
        # Mock database query result
        mock_db.execute.return_value = [(5,)]  # 5 nulls

        result = quality_engine.execute_rule(rule_id=1)
        assert result['passed'] == True
        assert result['result_value'] == 5

    def test_calculate_quality_score(self, quality_engine):
        """Test quality score calculation"""
        score = quality_engine.get_asset_quality_score(asset_id=1)
        assert 0 <= score['overall_score'] <= 100
        assert score['grade'] in ['A', 'B', 'C', 'D', 'F']

    def test_detect_anomalies(self, quality_engine):
        """Test anomaly detection with z-score"""
        anomalies = quality_engine.detect_anomalies(
            rule_id=1,
            lookback_days=30,
            std_threshold=2.0
        )
        assert isinstance(anomalies, list)
        for anomaly in anomalies:
            assert abs(anomaly['z_score']) > 2.0
```

---

### 3.2 Integration Tests

**Purpose:** Test component interactions and API endpoints

#### Test Files to Create:

```
tests/
├── integration/
│   ├── test_impact_api.py            ⏳ TO DO
│   ├── test_lineage_api.py           ⏳ TO DO
│   ├── test_schemas_api.py           ⏳ TO DO
│   ├── test_quality_api.py           ⏳ TO DO
│   ├── test_policies_api.py          ⏳ TO DO
│   ├── test_sla_api.py               ⏳ TO DO
│   └── test_events_api.py            ⏳ TO DO
```

#### Example Integration Test:
```python
# tests/integration/test_quality_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestQualityAPI:
    def test_create_rule_from_template(self, db_session):
        """Test POST /api/v1/quality/rules/from-template"""
        response = client.post("/api/v1/quality/rules/from-template", json={
            "template_name": "null_check",
            "asset_id": 1,
            "parameters": {
                "table_name": "customers",
                "column_name": "email"
            },
            "threshold_value": 0.01
        })
        assert response.status_code == 200
        data = response.json()
        assert data['dimension'] == 'COMPLETENESS'
        assert data['rule_id'] is not None

    def test_execute_rule(self, db_session, sample_rule):
        """Test POST /api/v1/quality/rules/{rule_id}/execute"""
        response = client.post(f"/api/v1/quality/rules/{sample_rule.rule_id}/execute")
        assert response.status_code == 200
        data = response.json()
        assert 'passed' in data
        assert 'result_value' in data

    def test_get_quality_score(self, db_session, sample_asset):
        """Test GET /api/v1/quality/assets/{asset_id}/score"""
        response = client.get(f"/api/v1/quality/assets/{sample_asset.asset_id}/score")
        assert response.status_code == 200
        data = response.json()
        assert 0 <= data['overall_score'] <= 100
        assert data['grade'] in ['A', 'B', 'C', 'D', 'F']
```

---

### 3.3 End-to-End Tests

**Purpose:** Full workflow testing with real data

#### Test Scenarios to Implement:

1. **Impact Analysis E2E**
   - Create assets A, B, C with lineage A→B→C
   - Analyze impact of deprecating A
   - Verify downstream_count = 2
   - Verify recommendations include migration steps

2. **Lineage Tracking E2E**
   - Parse SQL with JOIN
   - Verify nodes created for both tables
   - Trace lineage path from source to target
   - Verify transformation type = JOIN

3. **Schema Evolution E2E**
   - Register schema v1
   - Register schema v2 with breaking change
   - Verify compatibility check fails
   - Register schema v2 with non-breaking change
   - Verify compatibility check passes

4. **Quality Monitoring E2E**
   - Create quality rule
   - Execute rule (failing)
   - Verify violation recorded
   - Execute rule (passing)
   - Verify quality score improves

5. **Policy Enforcement E2E**
   - Create naming convention policy
   - Validate asset with correct name (passes)
   - Validate asset with incorrect name (fails)
   - Verify blocking prevents deployment

6. **SLA Monitoring E2E**
   - Define SLA metric (target: 200ms)
   - Collect metric (value: 150ms) - passes
   - Collect metric (value: 250ms) - fails
   - Verify violation created
   - Resolve violation
   - Verify MTTR calculated

---

### 3.4 Performance Tests

**Purpose:** Ensure system performs at scale

#### Tests to Implement:

```python
# tests/performance/test_graph_performance.py

import pytest
import time

class TestGraphPerformance:
    def test_impact_analysis_1000_nodes(self, large_graph):
        """Test impact analysis on 1000-node graph completes in <5s"""
        start = time.time()

        result = impact_analyzer.analyze_impact(
            asset_id=500,  # Middle node
            change_type="deprecation",
            analysis_depth=10
        )

        elapsed = time.time() - start
        assert elapsed < 5.0  # Must complete in <5 seconds
        assert result['downstream_dependencies']['count'] > 0

    def test_lineage_traversal_depth_10(self, deep_lineage):
        """Test lineage traversal 10 levels deep"""
        start = time.time()

        path = lineage_tracker.get_lineage_path(
            asset_id=1,
            direction="downstream",
            max_depth=10
        )

        elapsed = time.time() - start
        assert elapsed < 3.0
        assert len(path['nodes']) > 0
```

---

## Testing Implementation Checklist

### Phase 3H: Unit Tests (Week 8)
- [ ] Impact analyzer unit tests
- [ ] Lineage tracker unit tests
- [ ] Schema registry unit tests
- [ ] Quality engine unit tests
- [ ] Policy enforcer unit tests
- [ ] SLA monitor unit tests
- [ ] Event manager unit tests

### Phase 3I: Integration Tests (Week 9)
- [ ] All API endpoint tests
- [ ] Database transaction tests
- [ ] Error handling tests
- [ ] Pagination tests

### Phase 3J: E2E & Performance (Week 9)
- [ ] E2E workflow tests
- [ ] Performance benchmarks
- [ ] Load testing with 1000+ assets
- [ ] Concurrent user simulation

---

## 🚀 Track 4: Production Readiness

**Priority:** MEDIUM
**Estimated Effort:** 1-2 weeks

### 4.1 Docker Containerization

#### Dockerfile for Backend:
```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

#### Dockerfile for Frontend:
```dockerfile
# frontend/Dockerfile

FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY src/ src/
COPY public/ public/

# Build production bundle
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose:
```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/governance
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=governance
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

### 4.2 Kubernetes Deployment

#### Deployment YAML:
```yaml
# k8s/backend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: governance-portal-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: governance-backend
  template:
    metadata:
      labels:
        app: governance-backend
    spec:
      containers:
      - name: backend
        image: governance-portal-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

### 4.3 CI/CD Pipeline

#### GitHub Actions Workflow:
```yaml
# .github/workflows/deploy.yml

name: Deploy Governance Portal

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker images
        run: |
          docker build -t governance-backend:${{ github.sha }} backend/
          docker build -t governance-frontend:${{ github.sha }} frontend/

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push governance-backend:${{ github.sha }}
          docker push governance-frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/governance-backend backend=governance-backend:${{ github.sha }}
          kubectl rollout status deployment/governance-backend
```

---

### 4.4 Documentation

#### Documentation to Create:

1. **API Documentation** ✅ (Auto-generated via FastAPI)
   - Swagger UI at `/api/docs`
   - ReDoc at `/api/redoc`

2. **Architecture Documentation** ⏳ TO DO
   - System architecture diagram
   - Database schema diagram
   - Component interaction flowcharts
   - Deployment architecture

3. **User Guides** ⏳ TO DO
   - Getting started guide
   - Feature tutorials for each Phase 2 capability
   - Best practices guide
   - Troubleshooting guide

4. **Developer Guides** ⏳ TO DO
   - Local development setup
   - Contributing guidelines
   - Code style guide
   - Testing guidelines

5. **Deployment Guide** ⏳ TO DO
   - Docker deployment
   - Kubernetes deployment
   - AWS/GCP/Azure deployment
   - Database migration guide

---

## Production Readiness Checklist

### Phase 3K: Containerization (Week 10)
- [ ] Create Dockerfiles for backend and frontend
- [ ] Create docker-compose.yml for local development
- [ ] Test containerized deployment locally
- [ ] Optimize image sizes

### Phase 3L: Orchestration (Week 10-11)
- [ ] Create Kubernetes manifests
- [ ] Setup Helm charts (optional)
- [ ] Configure health checks and probes
- [ ] Setup autoscaling

### Phase 3M: CI/CD (Week 11)
- [ ] GitHub Actions workflow for tests
- [ ] Docker image build and push
- [ ] Automated deployment to staging
- [ ] Manual approval for production

### Phase 3N: Documentation (Week 11-12)
- [ ] Architecture documentation
- [ ] User guides for all features
- [ ] Developer setup guide
- [ ] Deployment guide

---

## 📊 Phase 3 Success Metrics

### Frontend Metrics:
- [ ] All 7 feature visualizations implemented
- [ ] <3 second page load time
- [ ] >90% mobile responsive coverage
- [ ] WCAG 2.1 AA accessibility compliance

### Integration Metrics:
- [ ] At least 3 external integrations working (GE, Prometheus, Slack)
- [ ] <5 second import time for dbt manifests with 100 models
- [ ] Alert delivery within 30 seconds of rule failure

### Testing Metrics:
- [ ] >80% code coverage
- [ ] All critical paths covered by E2E tests
- [ ] Performance tests pass for 1000+ asset graphs
- [ ] Zero P0 bugs in production

### Production Metrics:
- [ ] <5 minute deployment time
- [ ] 99.9% uptime SLA
- [ ] <1 second API response time (p95)
- [ ] Complete documentation for all features

---

## 📅 Estimated Timeline

```
Week 1-2:   Frontend Core Visualizations (Impact, Lineage, Schema)
Week 2-3:   Frontend Dashboards (Quality, SLA, Events, Policy)
Week 3-4:   Frontend Forms & Editors
Week 4:     Integration & Polish
Week 5:     Data Quality Integrations
Week 6:     SLA Monitoring Integrations
Week 7:     Lineage Integrations
Week 8:     Unit Tests
Week 9:     Integration & E2E Tests
Week 10:    Docker & Kubernetes
Week 11:    CI/CD Pipeline
Week 12:    Documentation & Launch Prep

Total: 12 weeks (3 months)
```

---

## 🎯 Phase 3 Deliverables

### Must Have (MVP):
1. ✅ Impact analysis graph visualization
2. ✅ Lineage diagram with React Flow
3. ✅ Quality score dashboard
4. ✅ SLA monitoring dashboard
5. ✅ Slack alerting integration
6. ✅ Unit test coverage >80%
7. ✅ Docker deployment
8. ✅ Basic user documentation

### Should Have:
1. Schema registry UI with diff viewer
2. Event catalog browser
3. Policy management interface
4. Prometheus integration
5. Great Expectations importer
6. E2E tests for all workflows
7. Kubernetes deployment
8. CI/CD pipeline

### Nice to Have:
1. Real-time updates via WebSocket
2. Advanced export features (PDF reports)
3. dbt lineage importer
4. Airflow DAG parser
5. Mobile app (React Native)
6. Multi-tenancy support
7. RBAC (Role-Based Access Control)
8. Audit logging

---

## 🚦 Getting Started Tomorrow

### Recommended First Tasks:

1. **Setup Frontend Environment**
   ```bash
   cd frontend
   npm install react-flow-renderer d3 recharts monaco-editor
   npm install @mui/icons-material
   ```

2. **Create Component Structure**
   ```bash
   mkdir -p src/components/{impact,lineage,schemas,quality,sla,events,policies}
   mkdir -p src/services
   mkdir -p src/hooks
   ```

3. **Start with Impact Analysis Visualization**
   - Create `ImpactAnalysisGraph.jsx`
   - Fetch data from `/api/v1/impact/visualization/{asset_id}`
   - Render with D3.js or React Flow
   - Add zoom/pan controls

4. **Add API Service Layer**
   ```javascript
   // src/services/api.js
   const API_BASE = 'http://localhost:8000/api/v1';

   export const impactAPI = {
     analyze: (assetId, request) =>
       fetch(`${API_BASE}/impact/analyze/${assetId}`, {
         method: 'POST',
         body: JSON.stringify(request)
       }).then(res => res.json()),

     getVisualization: (assetId) =>
       fetch(`${API_BASE}/impact/visualization/${assetId}`)
         .then(res => res.json())
   };
   ```

---

**Document Status:** Draft - Ready for review
**Next Update:** After Phase 3A completion
**Questions/Feedback:** Add as GitHub issues or discussion comments
