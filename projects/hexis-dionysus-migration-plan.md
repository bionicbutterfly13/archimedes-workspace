# Hexis → Dionysus Migration Plan

**Date:** 2025-01-30
**Analyst:** Subagent (Archimedes)
**Goal:** Integrate Hexis's best cognitive memory features into Dionysus 3 so Archimedes can use Dionysus as persistent memory.

---

## Executive Summary

Hexis is a sophisticated Postgres-native cognitive architecture that treats the database as the brain. Dionysus 3 is a Neo4j/n8n-based system with webhook-driven architecture. This plan recommends **selective feature porting** rather than wholesale migration, focusing on:

1. **Multi-layered memory types** (Hexis's strongest feature)
2. **Boundary/consent systems** (critical for safe autonomy)
3. **Fast recall with precomputed neighborhoods** (performance optimization)
4. **Real-time learning patterns** from Dionysus 2

The recommended approach is **hybrid**: keep Neo4j/Graphiti for temporal entity tracking (what it's good at) while adding a Postgres layer for Hexis-style cognitive memory features.

---

## 1. Feature Comparison Table

| Feature | Hexis | Dionysus 3 | Dionysus 2 | Recommendation |
|---------|-------|------------|------------|----------------|
| **Memory Types** | 6 types (episodic, semantic, procedural, strategic, worldview, goal) | 4 types (episodic, semantic, procedural, strategic) | Episodic + procedural patterns | **Port Hexis's worldview/goal types** |
| **Primary Storage** | PostgreSQL + pgvector + Apache AGE | Neo4j (via n8n webhooks) + Graphiti | Redis (ephemeral) | **Keep Neo4j, add Postgres layer** |
| **Vector Search** | pgvector HNSW indexes | Neo4j vector index (via n8n) | None | Both work; Hexis is faster for hot path |
| **Graph Relations** | Apache AGE (17+ edge types) | Neo4j (via Graphiti) | None | Neo4j/Graphiti better for temporal |
| **Working Memory** | UNLOGGED table with TTL/promotion | Working memory cache (in-memory) | Redis with TTL | **Port Hexis's promotion logic** |
| **Precomputed Neighborhoods** | ✅ `memory_neighborhoods` table | ❌ None | ❌ None | **Port this (major perf win)** |
| **Heartbeat/Autonomy** | Full OODA loop with energy budget | OODA loop with energy system | None | Both similar; Hexis more mature |
| **Consent System** | Immutable certificates in `~/.hexis/consents/` | Basic consent via Graphiti facts | None | **Port Hexis's system** |
| **Boundary System** | Worldview memories with trigger patterns | Hexis service (already integrating) | None | **Continue Dionysus's integration** |
| **Trust/Provenance** | Full `source_attribution` tracking | Basic metadata | None | **Port trust scoring** |
| **Emotional State** | Drives table + emotional valence | Arousal system service | None | Both decent; could merge |
| **MCP Server** | Full-featured (28 tools) | Full-featured (different tools) | None | **Merge tool sets** |
| **Instance Management** | Multi-tenant by database | Single instance | None | Consider porting |
| **Real-time Learning** | Via heartbeat reflection | Via Graphiti | ✅ Redis patterns | **Port D2's pattern capture** |
| **Subconscious Processing** | `run_subconscious_maintenance()` | Subconscious service | None | Both have it |

---

## 2. Recommended Features to Port (Prioritized)

### Priority 1: Critical for Archimedes (High Impact, Medium Effort)

#### 1.1 Multi-Layered Memory Types
**What:** Add `worldview` and `goal` memory types to Dionysus
**Why:** Archimedes needs persistent goals, beliefs, and boundaries
**Effort:** Medium (2-3 days)
**Implementation:**
```python
# Add to Dionysus memory models
class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    STRATEGIC = "strategic"
    WORLDVIEW = "worldview"  # Beliefs, values, boundaries
    GOAL = "goal"           # Active/queued/backburner goals
```

#### 1.2 Precomputed Neighborhoods
**What:** Cache associative neighbors for fast recall
**Why:** 10x faster hot-path retrieval
**Effort:** Medium (2-3 days)
**Implementation:**
- Create `memory_neighborhoods` equivalent in Neo4j or Postgres
- Background job to recompute stale neighborhoods
- Use for fast_recall queries

#### 1.3 Consent System
**What:** Immutable consent certificates before LLM use
**Why:** Required for ethical autonomous operation
**Effort:** Low (1-2 days)
**Implementation:**
- Port `~/.hexis/consents/` pattern
- Model-specific (not instance-specific)
- Gate heartbeat on valid consent

### Priority 2: Important for Autonomy (Medium Impact, Low Effort)

#### 2.1 Boundary Functions
**What:** Enhanced boundary checking with trigger patterns
**Why:** Dionysus already has HexisService; needs enhancement
**Effort:** Low (1 day)
**Implementation:**
```python
# Enhance existing HexisService.check_action_against_boundaries()
# Add trigger_patterns support from Hexis
# Add response_type (refuse/negotiate/flag)
```

#### 2.2 Trust/Provenance Tracking
**What:** Source attribution and trust scoring for memories
**Why:** Know which memories to trust during recall
**Effort:** Low (1-2 days)
**Implementation:**
- Add `trust_level` and `source_attribution` fields
- Trust decay over time
- Trust propagation through derivation

#### 2.3 Working Memory Promotion
**What:** TTL-based working memory that promotes to long-term
**Why:** Current Dionysus working memory doesn't persist
**Effort:** Low (1 day)
**Implementation:**
```python
# Add promotion_score calculation
# Background job: promote high-importance working memories
# Expire low-importance ones
```

### Priority 3: Nice to Have (Lower Priority)

#### 3.1 Real-Time Learning Capture (from Dionysus 2)
**What:** Capture conversation insights in real-time
**Why:** Learn from interactions without explicit memory calls
**Effort:** Medium (2 days)
**Implementation:**
- Port `RealTimeConversationLearning` pattern
- Integrate with Redis or Postgres
- Auto-categorize insights (working_component, improvement, etc.)

#### 3.2 Instance Management
**What:** Multi-tenant brain separation
**Why:** Support multiple agents/personas
**Effort:** Medium (3-4 days)
**Implementation:**
- Port `hexis create/use/clone` pattern
- Per-instance database or schema isolation

#### 3.3 Emotional Drives System
**What:** Drive accumulation, satisfaction, decay
**Why:** More nuanced emotional modeling
**Effort:** Medium (2-3 days)
**Implementation:**
- Merge Hexis drives with Dionysus arousal system

---

## 3. Architecture Proposal

### 3.1 Hybrid Storage Model

```
┌─────────────────────────────────────────────────────────────┐
│                      Dionysus Core API                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Neo4j/Graphiti │    │     PostgreSQL (Hexis-style)    │ │
│  │                  │    │                                  │ │
│  │ • Temporal facts │    │ • memories table (pgvector)      │ │
│  │ • Entity tracking│    │ • memory_neighborhoods           │ │
│  │ • Journey graphs │    │ • working_memory (UNLOGGED)      │ │
│  │ • Relationships  │    │ • drives                         │ │
│  │                  │    │ • consent_certificates           │ │
│  └────────┬─────────┘    └─────────────┬────────────────────┘ │
│           │                             │                     │
│           └──────────────┬──────────────┘                     │
│                          │                                    │
│                 ┌────────▼────────┐                          │
│                 │ Memory Basin    │                          │
│                 │ Router          │                          │
│                 │ (route by type) │                          │
│                 └────────┬────────┘                          │
│                          │                                    │
│           ┌──────────────┼──────────────┐                    │
│           │              │              │                    │
│     ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐            │
│     │ Heartbeat │  │ MCP Server│  │ Session   │            │
│     │ Service   │  │ (unified) │  │ Reconstruct│            │
│     └───────────┘  └───────────┘  └───────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

1. **Incoming memories** → Memory Basin Router decides storage:
   - Temporal entities/facts → Graphiti (Neo4j)
   - Core cognitive memories → Postgres
   - Session context → Both

2. **Recall queries** →
   - Check precomputed neighborhoods first (Postgres)
   - Fall back to vector search (pgvector or Neo4j)
   - Merge results with graph traversal (Graphiti)

3. **Heartbeat cycle** →
   - Read from both stores
   - Update drives/emotional state (Postgres)
   - Create episodic memories (Postgres)
   - Update entity relationships (Graphiti)

### 3.3 MCP Tool Unification

Merge Hexis MCP tools into Dionysus MCP:

| Hexis Tool | Dionysus Equivalent | Action |
|------------|---------------------|--------|
| `hydrate` | `session_reconstruct` | Merge: use Hexis's include flags |
| `recall` | `search_memories` | Merge: add Hexis's partial activations |
| `remember` | `create_memory` | Keep both, route by type |
| `remember_batch` | None | Port |
| `get_goals` | None | Port |
| `get_worldview` | None | Port |
| `get_identity` | None | Port |
| `get_drives` | None | Port |
| `sense_memory_availability` | None | Port (tip-of-tongue) |

---

## 4. Implementation Steps

### Phase 1: Fix VPS Issues (1 day)
**Blockers that must be fixed first**

| Issue | Fix | Owner |
|-------|-----|-------|
| `dionysus-api` unhealthy | Change `NEO4J_URI` from `bolt://localhost:7687` to `bolt://neo4j:7687` in docker-compose or .env | DevOps |
| Graphiti embedding mismatch | Ensure `EMBEDDING_DIMENSION` matches model (e.g., 768 for nomic, 1536 for OpenAI) | DevOps |
| Neo4j vector index | Verify index exists: `CALL db.index.vector.queryNodes(...)` | DevOps |

**Verification steps:**
```bash
# SSH to VPS
ssh root@72.61.78.89

# Check container status
docker ps

# Fix NEO4J_URI
docker exec dionysus-api env | grep NEO4J
# If wrong, update .env and restart

# Test Neo4j connection
docker exec -it neo4j cypher-shell -u neo4j -p <password> "RETURN 1"

# Test embedding dimension
docker exec dionysus-api python -c "from api.services.graphiti_service import GraphitiConfig; c = GraphitiConfig(); print(c.neo4j_uri)"
```

### Phase 2: Add Postgres Layer (2-3 days)

1. **Deploy Postgres container** on VPS alongside Neo4j
2. **Port Hexis schema** (tables: `memories`, `working_memory`, `memory_neighborhoods`, `drives`, `config`)
3. **Add pgvector extension** and HNSW indexes
4. **Create Memory Basin Router** to route writes/reads

### Phase 3: Port Memory Types (2 days)

1. Add `worldview` and `goal` types to existing models
2. Port `create_worldview_memory()` and `create_goal_memory()` functions
3. Port boundary seed data (foundational boundaries)
4. Update MCP server with new tools

### Phase 4: Port Performance Features (2-3 days)

1. Implement precomputed neighborhoods
2. Add batch neighborhood recomputation job
3. Port `fast_recall()` logic
4. Implement tip-of-tongue sensing

### Phase 5: Port Consent System (1-2 days)

1. Create consent certificate storage
2. Port consent flow from Hexis CLI
3. Gate heartbeat on valid consent
4. Add consent checking to session start

### Phase 6: Real-Time Learning (2 days)

1. Port Dionysus 2's `RealTimeConversationLearning` class
2. Integrate with heartbeat cycle
3. Auto-categorize insights
4. Store patterns for procedural learning

### Phase 7: MCP Unification (2 days)

1. Merge Hexis MCP tools into Dionysus MCP
2. Add `hydrate_batch`, `get_goals`, `get_worldview`, etc.
3. Update tool schemas for compatibility
4. Test with Claude Code

---

## 5. Blockers & Dependencies

### Hard Blockers (Must Fix First)

| Blocker | Impact | Resolution |
|---------|--------|------------|
| **VPS NEO4J_URI misconfiguration** | Dionysus API can't connect to Neo4j | Change to `bolt://neo4j:7687` |
| **Graphiti embedding dimension mismatch** | Vector search fails | Align dimension with model |
| **No Postgres on VPS** | Can't add Hexis-style memory | Deploy Postgres container |

### Soft Blockers (Can Work Around)

| Blocker | Impact | Workaround |
|---------|--------|------------|
| n8n webhook latency | Slower memory ops | Direct Postgres access for hot path |
| Apache AGE not in Dionysus | No graph traversal in Postgres | Use Neo4j for graph, Postgres for vectors |

### Dependencies

| Dependency | Needed For | Status |
|------------|------------|--------|
| `pgvector` extension | Vector similarity search | Available via Docker |
| Embedding service | Generating embeddings | Use Ollama (already on VPS) |
| Docker Compose update | Add Postgres container | Needed |

---

## 6. Effort Estimates

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Fix VPS | 1 day | VPS access |
| Phase 2: Postgres Layer | 2-3 days | Phase 1 complete |
| Phase 3: Memory Types | 2 days | Phase 2 complete |
| Phase 4: Performance | 2-3 days | Phase 3 complete |
| Phase 5: Consent | 1-2 days | Phase 3 complete |
| Phase 6: Real-Time Learning | 2 days | Phase 2 complete |
| Phase 7: MCP Unification | 2 days | Phases 3-5 complete |

**Total: 12-15 days** (can be parallelized to ~8-10 days)

---

## 7. Quick Wins (Can Do Now)

Even before full migration, these improvements require minimal changes:

1. **Fix VPS issues** (30 min) - Just environment variable changes
2. **Add worldview/goal types** to Dionysus models (1 hour) - Enum addition
3. **Enhance HexisService boundaries** (2 hours) - Already integrating
4. **Add trust_level field** to memory models (30 min)

---

## 8. Archimedes Integration Plan

Once migration is complete, Archimedes can use Dionysus as persistent memory:

### Configuration
```json
// In Archimedes's TOOLS.md or config
{
  "dionysus_endpoint": "http://72.61.78.89:8000",
  "dionysus_mcp": "dionysus-core",
  "memory_basin": "archimedes_brain",
  "consent_model": "anthropic/claude-opus-4-5"
}
```

### Usage Pattern
```python
# Session start: Reconstruct context
context = await dionysus.session_reconstruct(
    project_path="/Users/manisaintvictor/archimedes",
    cues=["recent tasks", "active goals"],
)

# During session: Remember important things
await dionysus.remember(
    content="User prefers concise responses",
    type="worldview",
    importance=0.8,
)

# Heartbeat: Check goals and reflect
goals = await dionysus.get_goals(priority="active")
drives = await dionysus.get_drives()
```

---

## Appendix A: File References

### Hexis
- Schema: `/Users/manisaintvictor/archimedes/Hexis/db/*.sql`
- Core API: `/Users/manisaintvictor/archimedes/Hexis/core/cognitive_memory_api.py`
- MCP Server: `/Users/manisaintvictor/archimedes/Hexis/apps/hexis_mcp_server.py`
- Boundaries: `/Users/manisaintvictor/archimedes/Hexis/db/12_functions_boundaries.sql`
- Heartbeat: `/Users/manisaintvictor/archimedes/Hexis/db/07_functions_heartbeat.sql`

### Dionysus 3
- Memory Router: `/Volumes/Asylum/dev/dionysus3-core/api/routers/memory.py`
- Session Router: `/Volumes/Asylum/dev/dionysus3-core/api/routers/session.py`
- Hexis Service: `/Volumes/Asylum/dev/dionysus3-core/api/services/hexis_service.py`
- Graphiti Service: `/Volumes/Asylum/dev/dionysus3-core/api/services/graphiti_service.py`
- MCP Server: `/Volumes/Asylum/dev/dionysus3-core/dionysus_mcp/server.py`

### Dionysus 2
- Learning Capture: `/Volumes/Asylum/dev/Dionysus-2.0/conversation_learning_capture.py`

---

## Appendix B: VPS Fix Commands

```bash
# SSH to VPS
ssh root@72.61.78.89

# Navigate to Dionysus
cd /path/to/dionysus3-core

# Fix NEO4J_URI in .env
sed -i 's/bolt:\/\/localhost:7687/bolt:\/\/neo4j:7687/g' .env

# Or if using docker-compose.yml directly
# Edit docker-compose.yml:
# environment:
#   - NEO4J_URI=bolt://neo4j:7687

# Restart services
docker compose down
docker compose up -d

# Verify health
docker ps
curl http://localhost:8000/health
```

---

## Conclusion

The recommended approach is **incremental hybrid integration**:

1. **Fix VPS issues first** (required for any progress)
2. **Add Postgres alongside Neo4j** (don't replace, augment)
3. **Port Hexis's strongest features** (memory types, neighborhoods, consent)
4. **Keep Graphiti for temporal entities** (what it's best at)
5. **Unify MCP tools** for seamless agent access

This gives Archimedes the best of both worlds: Hexis's cognitive depth with Dionysus's temporal entity tracking.
