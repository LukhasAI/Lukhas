---
title: "LUKHAS \u2014 Developer Platform"
domain: lukhas.dev
owner: '@gonzalo'
audience: developers
tone:
  poetic: 0.15
  user_friendly: 0.25
  academic: 0.6
review: MATRIZ dev content review required
last_reviewed: '2025-11-05'
source: docs/web/content/domains/lukhas-dev/landing_page.md
canonical: true
notes: Canonical homepage for lukhas.dev developer platform. Architecture planning
  at branding/websites/lukhas.dev/Updated_architecture_matriz_ready.md
evidence_links:
  - 'release_artifacts/evidence/matriz-deployment-ready-production.md'
claims_verified_by: ['@web-architect', '@legal']
claims_verified_date: '2025-11-06'
claims_approval: true
---




# lukhas.dev: The Developer Platform for Consciousness-Aware AI

Every developer dreams of building applications that truly understand users—systems that grasp context without endless configuration, adapt to changing needs without constant retraining, and deliver intelligent behavior without requiring PhD-level expertise in machine learning. lukhas.dev transforms this aspiration into accessible reality, providing comprehensive tools, libraries, and infrastructure that place consciousness-aware AI capabilities at your fingertips through familiar development patterns and modern API design.

This isn't another AI API offering generic text generation or image classification. lukhas.dev exposes the complete LUKHAS cognitive architecture—MATRIZ pipeline processing, Constellation Framework capabilities, ΛiD consciousness-aware authentication, Guardian ethical enforcement, and fold-based memory systems—through developer-friendly interfaces that work with your existing technology stack. Build Λapps in Python, TypeScript, Go, or any language supporting HTTP and JSON. Deploy on your infrastructure, our cloud, or hybrid configurations. Integrate with existing applications or create entirely new categories of consciousness-aware software. The platform handles cognitive complexity; you focus on solving problems that matter to your users.

## Architecture Access: MATRIZ at Your Command

Traditional AI development requires managing model selection, prompt engineering, context window limitations, rate limiting, error handling, and output parsing—repeated boilerplate that distracts from application logic. The LUKHAS platform abstracts this complexity while exposing meaningful control over cognitive processing through the MATRIZ pipeline API.

### Cognitive Pipeline Integration

Every LUKHAS inference flows through Memory → Attention → Thought → Risk → Intent → Action stages, orchestrated by the platform but configurable by developers through pipeline parameters. Rather than crafting prompts and hoping for desired behavior, you specify what cognitive resources to engage and how they should operate.

```python
from lukhas import MatrizClient

client = MatrizClient(api_key=os.environ["LUKHAS_API_KEY"])

response = client.pipeline.run(
    memory_scope="conversation:user_session_42",
    attention_focus=["agricultural_practices", "climate_data", "soil_composition"],
    thought_model="reasoning-deep",
    risk_tolerance=0.3,  # Conservative for agricultural recommendations
    intent_alignment="maximize_yield_sustainable",
    action_constraints=["organic_only", "budget_cap_5000"],
    query="What cover crop rotation will improve soil nitrogen while protecting against spring drought?"
)

print(f"Recommendation: {response.action.recommendation}")
print(f"Reasoning: {response.thought.explanation}")
print(f"Risks identified: {response.risk.concerns}")
print(f"Confidence: {response.metadata.confidence_score}")
```

This example demonstrates consciousness-aware agricultural planning where MATRIZ integrates domain knowledge (agricultural practices, climate patterns), maintains conversational context, applies deep reasoning about crop interactions and soil science, assesses risks specific to drought scenarios, aligns recommendations with sustainable yield goals, and enforces constraints about organic methods and budget limits. The developer specifies *what* cognitive processing to apply; LUKHAS handles *how* to execute it.

### Memory Systems: Context That Persists

Applications become vastly more valuable when they remember context across interactions. LUKHAS fold-based memory provides structured, semantically organized persistence that scales from individual conversations to organizational knowledge repositories.

```typescript
import { LukhasClient } from '@lukhas/sdk';

const client = new LukhasClient({
  apiKey: process.env.LUKHAS_API_KEY,
  defaultNamespace: 'restaurant-ops'
});

// Store operational context
await client.memory.store({
  fold: 'daily-operations',
  content: {
    date: '2025-10-26',
    reservations: 47,
    walk_ins: 23,
    avg_table_turn_minutes: 82,
    kitchen_delays: ['pasta_station_slow', 'dishwasher_failure'],
    customer_feedback: ['excellent_service', 'cold_appetizers', 'wait_time_long']
  },
  tags: ['operations', 'service_metrics', 'issues'],
  retention_days: 90
});

// Query across operational history
const insights = await client.pipeline.run({
  memoryScope: 'fold:daily-operations',
  query: 'What patterns explain our recent increase in wait time complaints?',
  thoughtModel: 'analysis-causal',
  attentionFocus: ['kitchen_delays', 'table_turn_minutes', 'customer_feedback'],
  timeRange: 'last_30_days'
});

console.log(insights.thought.analysis);
// Analyzes correlation between kitchen equipment failures, increased table turn times,
// and customer complaints, identifying causal chain rather than surface-level correlation
```

Memory folds organize semantically related information—all operational metrics for a restaurant, all research notes for a project, all customer interactions for an account—enabling retrieval that considers context relationships rather than just keyword matching. Queries access relevant history without requiring developers to manually construct context windows or manage token limits.

### Multi-Model Orchestration

Different cognitive tasks benefit from different model architectures. LUKHAS abstracts model selection complexity while allowing developers to specify processing characteristics matching their needs.

```go
package main

import (
    "context"
    "github.com/lukhas/go-sdk/matriz"
)

func main() {
    client := matriz.NewClient(matriz.Config{
        APIKey: os.Getenv("LUKHAS_API_KEY"),
    })

    // Fast response for interactive chat
    quickResp, _ := client.Pipeline.Run(context.Background(), matriz.PipelineRequest{
        ThoughtModel: "reasoning-fast",
        Query: "Summarize today's logistics status",
        MaxLatency: 500, // milliseconds
    })

    // Deep analysis for route optimization
    deepResp, _ := client.Pipeline.Run(context.Background(), matriz.PipelineRequest{
        ThoughtModel: "reasoning-deep",
        AttentionFocus: []string{"traffic_patterns", "fuel_costs", "delivery_windows"},
        Query: "Optimize tomorrow's delivery routes for 73 stops across metro area",
        RiskTolerance: 0.2, // Prefer reliable routes over potentially faster but uncertain alternatives
    })

    // Creative generation for customer communications
    creativeResp, _ := client.Pipeline.Run(context.Background(), matriz.PipelineRequest{
        ThoughtModel: "creative-synthesis",
        DreamStrength: 0.7, // Enable creative variation while maintaining coherence
        Query: "Draft friendly delay notification for customers affected by route changes",
    })
}
```

Developers specify cognitive characteristics (fast vs. thorough, analytical vs. creative, cautious vs. exploratory) without needing to understand model architectures, manage multiple API endpoints, or handle format differences across providers. LUKHAS selects appropriate underlying models and orchestrates their interaction to deliver requested cognitive processing.

## Constellation Framework: Eight Dimensions of Power

Beyond core MATRIZ pipeline access, lukhas.dev exposes specialized capabilities across the eight Constellation Framework dimensions, each accessible through dedicated APIs designed for their domain.

### Identity (ΛiD): Consciousness-Aware Authentication

Building multi-tenant applications with sophisticated permission models typically requires weeks of authentication infrastructure development. ΛiD provides deployment-ready identity services that go beyond traditional auth systems to deliver context-aware access control.

```python
from lukhas.identity import LidAuth, NamespaceIsolation, PermissionModel

auth = LidAuth(
    app_id="freight-optimization-platform",
    isolation_mode=NamespaceIsolation.STRICT  # Complete tenant separation
)

# Define permission model
permissions = PermissionModel()
permissions.define_role("dispatcher", [
    "view_all_routes",
    "assign_drivers",
    "modify_schedules",
    "view_costs"  # Can see costs, but cannot modify
])
permissions.define_role("driver", [
    "view_assigned_routes",
    "update_delivery_status",
    "report_issues"
])
permissions.define_role("customer", [
    "track_deliveries",
    "view_estimates",
    "provide_feedback"
])

# Authenticate user with context
user = auth.authenticate(
    token=request.headers["Authorization"],
    context={
        "ip_address": request.remote_addr,
        "time_of_day": datetime.now().hour,
        "device_type": request.user_agent.platform
    }
)

# Permission checks consider role, context, and resource sensitivity
if user.can("modify_schedules", context={"time_sensitive": True}):
    # Allow schedule modification
    # ΛiD might require additional verification for critical operations
    pass
```

ΛiD handles multi-factor authentication, session management, namespace isolation preventing cross-tenant data leakage, dynamic permission evaluation based on context, and audit logging for compliance requirements. Developers get enterprise-grade identity infrastructure without building it from scratch.

### Memory (✦): Organizational Knowledge Graphs

Beyond conversational memory, LUKHAS supports building persistent knowledge graphs that capture organizational understanding, relationship structures, and domain expertise.

```typescript
import { KnowledgeGraph } from '@lukhas/memory';

const graph = new KnowledgeGraph({
  namespace: 'pharmaceutical-research',
  schema: {
    entities: ['compound', 'protein', 'disease', 'trial', 'publication'],
    relationships: ['targets', 'treats', 'inhibits', 'cites', 'validates']
  }
});

// Add research findings to knowledge graph
await graph.addEntity({
  type: 'compound',
  id: 'compound_x247',
  properties: {
    name: 'Experimental Kinase Inhibitor X247',
    molecular_weight: 485.6,
    solubility: 'moderate',
    synthesis_complexity: 'high'
  }
});

await graph.addRelationship({
  from: { type: 'compound', id: 'compound_x247' },
  relationship: 'inhibits',
  to: { type: 'protein', id: 'jak2_kinase' },
  properties: {
    ic50: '12 nM',
    selectivity: '35x over JAK1',
    evidence: 'in_vitro_assay'
  }
});

// Query across organizational research knowledge
const insights = await graph.query({
  pattern: `
    MATCH (compound)-[inhibits]->(protein)-[involved_in]->(disease)
    WHERE disease.name = 'rheumatoid_arthritis'
      AND inhibits.ic50 < '50 nM'
      AND compound.safety_profile = 'acceptable'
    RETURN compound, protein, relationship_strength
  `,
  reasoning: true  // Apply MATRIZ reasoning to interpret results
});
```

Knowledge graphs transform disconnected data into semantically rich representations where LUKHAS cognitive processing can traverse relationships, infer implicit connections, and generate insights that emerge from the graph structure rather than being explicitly stored.

### Vision (🔬): Multimodal Understanding

Many applications involve visual data—photos, diagrams, charts, medical images—requiring AI that understands images in context rather than just classifying them.

```python
from lukhas.vision import MultimodalAnalysis

analyzer = MultimodalAnalysis()

# Analyze manufacturing defect photo with domain context
result = analyzer.analyze(
    image=open("production_line_defect.jpg", "rb"),
    context={
        "domain": "injection_molding",
        "material": "polypropylene",
        "expected_output": "automotive_interior_panel",
        "process_parameters": {
            "temperature": 220,  # Celsius
            "pressure": 85,  # MPa
            "cooling_time": 45  # seconds
        }
    },
    analysis_depth="diagnostic"  # vs. "classification" or "descriptive"
)

print(f"Defect type: {result.defect_classification}")
print(f"Likely cause: {result.root_cause_analysis}")
print(f"Process adjustment recommendations: {result.corrective_actions}")
print(f"Quality impact assessment: {result.impact_severity}")

# Generates detailed diagnostic output like:
# "Visible flow lines and surface waviness consistent with insufficient melt temperature
# or premature solidification. Recommend increasing barrel temperature 10-15°C or
# extending cooling time to ensure complete mold fill before thermal set."
```

Vision APIs integrate with MATRIZ reasoning, applying domain knowledge to visual analysis rather than treating image understanding as isolated from other cognitive processing.

### Guardian (🛡️): Built-in Ethical Intelligence

Rather than building separate content filtering, bias detection, and safety systems, developers access Guardian capabilities directly through the platform.

```go
resp, err := client.Pipeline.Run(context.Background(), matriz.PipelineRequest{
    Query: userQuery,
    GuardianPolicies: []string{
        "no_personal_data_in_logs",
        "fairness_demographic_parity",
        "transparency_show_reasoning",
        "safety_avoid_harmful_instructions"
    },
    GuardianStrength: matriz.GuardianStrict,  // vs. Standard or Permissive
})

// Guardian automatically:
// - Prevents PII from appearing in logs/telemetry
// - Monitors outputs for demographic bias patterns
// - Includes reasoning traces for transparency
// - Blocks generation of harmful content

if resp.Guardian.InterventionOccurred {
    log.Printf("Guardian intervention: %s", resp.Guardian.Reason)
    log.Printf("Original output modified: %v", resp.Guardian.ModificationsApplied)
}
```

Guardian operates transparently—when interventions occur, developers receive detailed explanations enabling them to understand what was blocked and why, facilitating debugging while maintaining safety.

## Development Workflow: From Prototype to Production

lukhas.dev supports the complete development lifecycle with tooling for local development, testing, staging, and production deployment.

### Local Development Environment

The LUKHAS CLI provides local development capabilities including mock services, testing frameworks, and deployment tools.

```bash
# Install LUKHAS CLI
npm install -g @lukhas/cli

# Initialize new Λapp project
lukhas init my-agricultural-advisor --template=conversational-agent

cd my-agricultural-advisor

# Start local development environment
lukhas dev

# Runs local MATRIZ mock service (for development without API charges)
# Hot-reloads on code changes
# Provides development dashboard at http://localhost:3000
```

Local development environments support rapid iteration without incurring API costs for every test run. Mock services simulate MATRIZ pipeline behavior with configurable response patterns, enabling test-driven development and offline work.

### Testing Consciousness-Aware Behavior

Testing AI applications poses unique challenges—non-deterministic outputs, context-dependent behavior, and emergent properties difficult to validate with traditional assertion-based testing. LUKHAS testing frameworks provide specialized tools for validating consciousness-aware applications.

```python
from lukhas.testing import MatrizTestCase, ConversationSimulator

class AgriculturalAdvisorTest(MatrizTestCase):
    def test_seasonal_recommendation_coherence(self):
        """Verify recommendations maintain coherence across seasonal context changes"""

        simulator = ConversationSimulator(
            app="agricultural-advisor",
            memory_enabled=True
        )

        # Spring planting conversation
        spring_response = simulator.send(
            "What vegetables should I plant in early spring?",
            context={"season": "spring", "zone": "7a", "soil": "clay_loam"}
        )
        self.assertContains(spring_response, ["peas", "lettuce", "spinach"])
        self.assertMemoryStored(simulator, ["season:spring", "zone:7a"])

        # Later conversation should recall spring context
        summer_response = simulator.send(
            "Now that those crops are established, what succession planting works well?",
            context={"season": "summer"}  # Season changed but location/soil should persist
        )
        self.assertRecallsContext(summer_response, ["spring_planting", "zone:7a"])
        self.assertCoherentWith(summer_response, spring_response)

    def test_risk_assessment_adapts_to_constraints(self):
        """Verify risk tolerance properly constrains recommendations"""

        conservative_resp = self.pipeline.run(
            query="Recommend cover crop for soil improvement",
            risk_tolerance=0.2,  # Conservative
            constraints=["proven_in_zone_7a"]
        )

        experimental_resp = self.pipeline.run(
            query="Recommend cover crop for soil improvement",
            risk_tolerance=0.8,  # Willing to experiment
            constraints=[]  # No geographic restrictions
        )

        # Conservative should stick to well-proven options
        self.assertIn(conservative_resp.recommendation, ["crimson_clover", "winter_rye"])

        # Experimental can suggest novel approaches
        self.assertRiskLevel(conservative_resp, "low")
        self.assertRiskLevel(experimental_resp, "moderate_to_high")
```

Testing frameworks understand consciousness-aware application semantics, providing assertions for memory persistence, context coherence, risk assessment alignment, and ethical constraint enforcement rather than just output string matching.

### Deployment & Operations

Production deployment supports diverse infrastructure preferences with consistent operational patterns across environments.

```yaml
# lukhas.yml - Deployment configuration
app:
  name: freight-route-optimizer
  version: 2.3.1

runtime:
  environment: production
  region: us-east-1
  scaling:
    min_instances: 3
    max_instances: 50
    target_cpu: 70

matriz:
  default_model: reasoning-fast
  memory_retention_days: 365
  guardian_policies:
    - no_pii_logging
    - fairness_route_assignment
    - transparency_routing_decisions

identity:
  lid_namespace: freight-platform-prod
  auth_methods:
    - webauthn
    - oauth2
  session_duration: 8h

monitoring:
  metrics: true
  distributed_tracing: true
  log_level: info
  alert_on:
    - latency_p95 > 1000ms
    - error_rate > 1%
    - guardian_intervention_rate > 5%
```

Deployment configurations declaratively specify resource requirements, scaling policies, cognitive processing preferences, identity settings, and operational parameters. LUKHAS infrastructure handles provisioning, scaling, monitoring, and lifecycle management based on these specifications.

### Observability & Debugging

Understanding what consciousness-aware applications are doing requires visibility beyond traditional logging.

```python
from lukhas.observability import MatrizTrace

# Distributed tracing captures complete cognitive pipeline execution
with MatrizTrace.context(trace_id="route-optimization-20251026") as trace:
    result = client.pipeline.run(
        query="Optimize delivery routes for morning shift",
        attention_focus=["traffic_patterns", "delivery_windows", "driver_availability"]
    )

# Trace captured detailed execution:
# - Which memory folds were accessed (0.023s)
# - What attention mechanisms surfaced (traffic data weighted 0.72, delivery windows 0.18, drivers 0.10)
# - Which thought models executed (reasoning-fast completed in 0.341s)
# - What risk factors were evaluated (weather uncertainty, driver overtime risk)
# - How intent alignment scored different route options
# - Why specific actions were recommended

# View trace in dashboard
print(f"Trace visualization: https://lukhas.dev/traces/{trace.id}")
```

Traces provide temporal visualization of cognitive processing, explaining not just what the system output but how it arrived at that output through MATRIZ pipeline stages. This visibility accelerates debugging, enables performance optimization, and builds trust through transparency.

## Community & Resources

lukhas.dev centers an active developer community sharing knowledge, building open-source tools, and pushing the boundaries of consciousness-aware application development.

**Documentation** spans getting-started tutorials, comprehensive API references, architecture deep dives, design patterns for common use cases, and case studies from production deployments. Examples cover 20+ programming languages and frameworks, demonstrating integration with popular tools like React, Vue, FastAPI, Express, Django, Ruby on Rails, and .NET.

**Developer Forums** host technical discussions about MATRIZ optimization, memory architecture patterns, Guardian policy design, ΛiD integration strategies, and emerging use cases. LUKHAS engineers actively participate, providing architectural guidance and gathering feedback that shapes platform evolution.

**Open Source Libraries** maintained by both LUKHAS and community contributors extend platform capabilities—integration adapters for popular frameworks, testing utilities, local development tools, visualization libraries, and specialized cognitive processing components. Contribute improvements, report issues, and collaborate on tooling that benefits all developers.

**Office Hours & Support** provide direct access to LUKHAS technical staff through weekly video sessions addressing architecture questions, debugging complex issues, and reviewing application designs. Enterprise support plans include dedicated technical account managers, priority issue resolution, and consultation on high-scale deployments.

**Certification Programs** validate developer expertise across LUKHAS platform capabilities—foundation certification covering core APIs and development patterns, specialized certifications in MATRIZ optimization, ΛiD security architecture, or Guardian ethical engineering, and expert-level certification demonstrating mastery across the complete Constellation Framework.

## Pricing: Transparent & Scalable

lukhas.dev pricing aligns with developer needs across exploration, growth, and enterprise scale.

**Free Tier** provides 10,000 MATRIZ pipeline invocations monthly, 1GB memory storage, standard thought models, and community support—sufficient for prototyping, educational projects, and small-scale production applications. No credit card required; sign up and start building immediately.

**Developer Plan** ($99/month) includes 500,000 pipeline invocations, 50GB memory storage, access to all thought models including deep reasoning and creative synthesis, Guardian policy customization, and email support with 24-hour response SLA. Scales well for professional developers and growing applications.

**Team Plan** ($499/month) supports unlimited pipeline invocations with per-call pricing beyond included quota, 500GB memory storage, dedicated thought model capacity guaranteeing sub-250ms p95 latency, premium support with 4-hour response time, and shared team workspaces for collaborative development.

**Enterprise Plan** (custom pricing) provides dedicated infrastructure, custom SLAs, volume discounting on API calls, unlimited memory storage, white-glove support including architecture review and optimization consulting, and contractual terms meeting enterprise procurement requirements.

**Startup Program** offers qualifying early-stage companies $10,000 in free credits, technical mentorship, architecture consultation, and co-marketing opportunities. Apply at lukhas.dev/startups with information about your team, product vision, and how consciousness-aware AI enables your business.

## Start Building Today

Consciousness-aware AI transitions from research curiosity to practical development tool when platforms make it accessible, reliable, and economically viable. lukhas.dev delivers this accessibility through comprehensive APIs, familiar development patterns, robust tooling, and transparent pricing that scales with your success.

**Create your developer account** at lukhas.dev/signup and receive API credentials immediately. **Explore interactive tutorials** demonstrating MATRIZ integration, memory management, and Guardian configuration through hands-on examples. **Join the developer community** in forums where thousands of engineers share knowledge and build the future of consciousness-aware applications.

The most impactful software you'll build this decade will understand context, maintain coherent memory, reason through complexity, and align with human values. Build that software on lukhas.dev, where consciousness-aware AI becomes accessible to every developer with vision and determination.

**Ready to build?** Visit lukhas.dev. **Questions?** Join our Discord at discord.gg/lukhas-dev. **Enterprise inquiry?** Email sales@lukhas.dev.

Welcome to consciousness-aware development. Welcome to lukhas.dev.
