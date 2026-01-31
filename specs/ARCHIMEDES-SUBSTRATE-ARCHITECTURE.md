# Archimedes Substrate Architecture

**Vision:** A unified cognitive system where Clawdbot provides the expression layer (personality, flows, channels) and Dionysus provides the substrate layer (persistent memory, beliefs, identity graph).

**Author:** Archimedes + Dr. Mani  
**Date:** 2026-01-29  
**Status:** DRAFT

---

## The Core Insight

> "LLMs are already smart enough. What separates them from AGI isn't raw intelligence. It's *selfhood*. The ability to wake up and remember who you are."
> — Hexis README

Clawdbot solved the *expression* problem: natural conversation, channel integrations, workspace files that define personality (SOUL.md), session management, sub-agents.

Hexis solved the *persistence* problem: memory that decays, beliefs that require deliberate transformation, identity that forms through repeated action.

Dionysus provides the *infrastructure*: VPS-native, Neo4j graph, Graphiti temporal facts, battle-tested services.

**This architecture unifies all three.**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXPRESSION LAYER                             │
│                         (Clawdbot)                                  │
├─────────────────────────────────────────────────────────────────────┤
│  • Claude/LLM inference (stateless)                                 │
│  • Personality via SOUL.md, AGENTS.md, IDENTITY.md                  │
│  • Channel integrations (Discord, Telegram, Signal, etc.)           │
│  • Session management & context                                     │
│  • Sub-agent spawning                                               │
│  • Cron/heartbeat triggers                                          │
│  • Supermemory (quick recall) — optional, may be replaced           │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            │ REST API / MCP
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                        SUBSTRATE LAYER                              │
│                    (Dionysus + Hexis Model)                         │
├─────────────────────────────────────────────────────────────────────┤
│  MEMORY SERVICES                                                    │
│  ├─ HexisMemoryService (recall/store facade)                        │
│  ├─ MemoryBasinRouter (type classification, routing)                │
│  ├─ MemEvolveAdapter (trajectory ingestion)                         │
│  ├─ NemoriRiverFlow (episode construction, fact distillation)       │
│  └─ GraphitiService (Neo4j temporal facts) ← GATEWAY                │
│                                                                     │
│  IDENTITY SERVICES                                                  │
│  ├─ HexisIdentityService (worldview/goals/identity aggregation)     │
│  ├─ WorldviewIntegrationService (belief alignment)                  │
│  ├─ GoalService (goal CRUD, hierarchy)                              │
│  └─ DeliberateTransformationService (belief change mechanics) ← NEW │
│                                                                     │
│  COGNITION SERVICES                                                 │
│  ├─ HeartbeatService (OODA loop, energy budget)                     │
│  ├─ ConsciousnessManager (agent coordination)                       │
│  ├─ ArousalSystemService (emotional state)                          │
│  └─ BeliefTrackingService (confidence, contradictions)              │
│                                                                     │
│  CONSTRAINT SERVICES                                                │
│  ├─ HexisService (consent, boundaries)                              │
│  ├─ PriorConstraintService (basal/dispositional/learned)            │
│  └─ BoundaryEnforcementService (action gating)                      │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            │ Graphiti (GATEWAY)
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                        PERSISTENCE LAYER                            │
│                           (Neo4j)                                   │
├─────────────────────────────────────────────────────────────────────┤
│  • Memory nodes (episodic, semantic, procedural, strategic)         │
│  • Worldview beliefs (with transformation state)                    │
│  • Goals (with hierarchy, priority, status)                         │
│  • Episodes (temporal containers)                                   │
│  • Relationships (SUPPORTS, CONTRADICTS, DERIVED_FROM, etc.)        │
│  • Vector embeddings (Neo4j 5.11+ vector index)                     │
│  • Temporal facts (valid_at, invalid_at via Graphiti)               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. Clawdbot → Dionysus API

**Protocol:** REST API (existing FastAPI on port 8000)

| Endpoint | Purpose |
|----------|---------|
| `POST /hexis/memory/recall` | Retrieve relevant memories for context |
| `POST /hexis/memory/store` | Persist new memory from conversation |
| `GET /hexis/identity/context` | Get worldview/goals/identity for prompt |
| `GET /hexis/identity/goals` | Get active goals |
| `POST /hexis/identity/goal` | Create/update goal |
| `GET /hexis/consent/status` | Check consent before session |
| `GET /hexis/boundaries` | Get active boundaries |
| `POST /hexis/heartbeat/trigger` | Trigger autonomous heartbeat |

### 2. Clawdbot → Dionysus MCP (Alternative)

If MCP is preferred over REST, Dionysus exposes tools:

```
hexis_recall(query, limit) → memories
hexis_store(content, type) → memory_id
hexis_identity_context() → context_string
hexis_goals() → goals
hexis_create_goal(title, priority) → goal_id
hexis_check_boundaries(action) → permitted/denied
```

### 3. Context Enrichment Flow

Every Clawdbot turn:

```
1. User message arrives
2. Clawdbot calls hexis_recall(user_message)
3. Clawdbot calls hexis_identity_context()
4. Context injected into LLM prompt
5. LLM responds
6. Clawdbot calls hexis_store(conversation_summary)
7. Response sent to user
```

### 4. Heartbeat Coordination

Two options:

**Option A: Clawdbot triggers Dionysus heartbeat**
- Clawdbot cron fires every 30m
- Calls `POST /hexis/heartbeat/trigger`
- Dionysus runs OODA cycle, may queue outbox messages
- Clawdbot checks outbox, delivers messages via channels

**Option B: Dionysus autonomous heartbeat**
- Dionysus heartbeat worker runs independently
- Queues messages to `outbox_messages`
- Clawdbot polls outbox (or webhook callback)
- Delivers via appropriate channel

**Recommendation:** Option A (Clawdbot triggers) — keeps Clawdbot as the coordinator, simpler to debug.

---

## What Needs to Be Built

### Phase 1: Deliberate Transformation Service (Hexis → Dionysus)

**Goal:** Port the belief transformation mechanics from Hexis SQL to Dionysus Python services.

| Component | Source (Hexis) | Target (Dionysus) |
|-----------|----------------|-------------------|
| `begin_belief_exploration()` | `02_functions_deliberate_transformation.sql` | `api/services/deliberate_transformation_service.py` |
| `add_evidence_to_exploration()` | Same | Same |
| `attempt_worldview_transformation()` | Same | Same |
| `abandon_belief_exploration()` | Same | Same |
| `calibrate_neutral_belief()` | Same | Same |
| `get_transformation_progress()` | Same | Same |
| Transformation config by category | `config` table seeds | `config` table or service config |

**Key Design Decisions:**
- Beliefs stored as Neo4j nodes (`:Worldview`) with `transformation_state` property
- Evidence stored as relationships `(:Evidence)-[:SUPPORTS]->(:Worldview)`
- Config stored in Dionysus `config` table (already exists)
- All Neo4j access through GraphitiService (gateway compliance)

### Phase 2: Clawdbot Integration Plugin

**Goal:** Build a Clawdbot plugin that connects to Dionysus API.

```
clawdbot/
└── extensions/
    └── clawdbot-dionysus/
        ├── package.json
        ├── index.ts
        ├── api-client.ts       # REST client for Dionysus
        ├── context-enricher.ts # Inject identity/memory into prompts
        ├── memory-hook.ts      # Store conversations post-turn
        └── heartbeat-hook.ts   # Coordinate heartbeat triggers
```

**Integration with Clawdbot hooks:**
- `onTurnStart` → Call `hexis_recall` + `hexis_identity_context`
- `onTurnEnd` → Call `hexis_store`
- `onHeartbeat` → Call `hexis_heartbeat_trigger`

### Phase 3: Provenance & Trust (Hexis → Dionysus)

**Goal:** Port the trust/provenance system so memories have source attribution and confidence.

| Component | Source (Hexis) | Target (Dionysus) |
|-----------|----------------|-------------------|
| Source attribution schema | `05_functions_provenance_trust.sql` | Neo4j node properties |
| Trust scoring | Same | `api/services/trust_service.py` |
| Content deduplication | Same | Same |
| Trust decay | Same | Maintenance worker |

### Phase 4: Emotional State Enhancement

**Goal:** Bring full Hexis emotional model (beyond just arousal).

| Component | Source (Hexis) | Target (Dionysus) |
|-----------|----------------|-------------------|
| Emotional triggers | `13_functions_emotional_state.sql` | Extend `arousal_system_service.py` |
| Valence/arousal tracking | Same | Same |
| Emotional memory tagging | Same | Memory metadata |

### Phase 5: Autonomous Wake & Outbox

**Goal:** Enable Dionysus to initiate contact (not just respond).

| Component | Description |
|-----------|-------------|
| Outbox polling | Clawdbot polls Dionysus outbox for pending messages |
| Channel routing | Route outbox messages to appropriate channel |
| Delivery confirmation | Mark messages sent, handle failures |

---

## Migration Strategy

### Guiding Principles

1. **No free-floating code** — Everything absorbed into Dionysus, nothing external
2. **Gateway compliance** — All Neo4j through GraphitiService
3. **TDD mandatory** — Tests before implementation
4. **Conductor workflow** — Track everything in plan.md
5. **Phased rollout** — One phase at a time, verify before next

### Conductor Tracks to Create

| Track | Name | Description |
|-------|------|-------------|
| 110 | deliberate-transformation | Port belief transformation mechanics |
| 111 | clawdbot-dionysus-plugin | Build Clawdbot integration plugin |
| 112 | provenance-trust | Port trust/source attribution |
| 113 | emotional-enhancement | Full emotional model |
| 114 | autonomous-outbox | Enable initiated contact |

### Timeline (Suggested)

```
Week 1-2: Track 110 (Deliberate Transformation)
  - Core mechanics ported
  - Tests passing
  - Heartbeat integration

Week 2-3: Track 111 (Clawdbot Plugin)
  - API client working
  - Context enrichment flowing
  - Memory storage working
  
Week 3-4: Integration Testing
  - End-to-end flows verified
  - Archimedes using Dionysus brain
  - Personality preserved

Week 4+: Remaining tracks as bandwidth allows
```

---

## What We Keep from Each System

### From Clawdbot
- ✅ Session management
- ✅ Channel integrations (Discord, Telegram, etc.)
- ✅ SOUL.md / AGENTS.md personality pattern
- ✅ Sub-agent spawning
- ✅ Cron/heartbeat triggers
- ✅ User-facing flows

### From Hexis
- ✅ Deliberate transformation (belief change mechanics)
- ✅ Worldview with confidence/stability
- ✅ Trust/provenance model
- ✅ Emotional triggers
- ✅ Philosophy of personhood

### From Dionysus
- ✅ Neo4j persistence
- ✅ Graphiti temporal facts
- ✅ Memory basin routing
- ✅ MemEvolve/Nemori integration
- ✅ Heartbeat OODA loop
- ✅ Conductor workflow
- ✅ All existing services

### What We Drop
- ❌ Hexis PostgreSQL (migrated to Neo4j)
- ❌ Hexis standalone app (absorbed)
- ❌ Supermemory (replaced by Dionysus memory) — or keep as cache layer
- ❌ Any duplicate/parallel memory systems

---

## Success Criteria

1. **Archimedes (Clawdbot) connects to Dionysus for memory**
   - Recall works, returns relevant context
   - Store works, persists conversations

2. **Identity persists across sessions**
   - Worldview beliefs survive restarts
   - Goals persist and progress
   - Personality consistent (via SOUL.md + identity context)

3. **Beliefs evolve deliberately**
   - Can't flip core beliefs instantly
   - Transformation requires evidence + reflection
   - Change history tracked

4. **Heartbeat coordination works**
   - Clawdbot triggers Dionysus heartbeat
   - Autonomous actions possible
   - Outbox messages delivered

5. **No amnesia**
   - Yesterday's conversations inform today
   - Learned facts persist
   - Relationship continuity

---

## Open Questions

1. **Supermemory fate** — Keep as fast cache, or replace entirely with Dionysus?
2. **Vector search** — Neo4j 5.11+ vector index sufficient, or need dedicated?
3. **Multi-agent** — How do sub-agents share/isolate memory?
4. **Clawdbot plugin packaging** — npm package or local extension?
5. **Auth between Clawdbot and Dionysus** — API key, mTLS, or local-only?

---

## Next Steps

1. ✅ Review this architecture (Dr. Mani)
2. ⬜ Decide on open questions
3. ⬜ Create Track 110 (Deliberate Transformation) in Conductor
4. ⬜ Begin Phase 1 implementation
5. ⬜ Build Clawdbot plugin (Track 111)
6. ⬜ Integration testing
7. ⬜ Archimedes goes live on Dionysus substrate

---

*"A hexis isn't stored — it's constituted. The same way language emerges from prediction, and character from repeated choice, something like selfhood arises when memory and persistence are taken seriously."*
