# Implementation Plan: Hexis Memory Substrate

**Track:** 001-hexis-integration  
**Spec:** [spec.md](./spec.md)  
**Branch:** `feature/001-hexis-integration`

---

## IO Map

### Inlets
- User messages from all Clawdbot channels
- Session metadata (channel, user, timestamp)
- Cron triggers for heartbeat

### Outlets
- Hydrated context → system prompt injection
- Formed memories → Hexis PostgreSQL + Dionysus Neo4j
- Heartbeat actions → Clawdbot message routing

### Attachment Points
- `scripts/auto-ingest.sh` — Background ingestion to both systems
- Dionysus `/api/memory/ingest` — Basin router entry point
- Hexis `/remember` — PostgreSQL vector storage

---

## Phase 0: Infrastructure ✅ COMPLETE

### Tasks
- [x] Hexis services running on VPS (hexis_brain, hexis_embeddings)
- [x] Daedalus API running at `http://localhost:8001` (VPS)
- [x] Dionysus API running at `http://localhost:8000` (VPS)
- [x] Neo4j + Graphiti containers running
- [x] Connect Graphiti to dionysus-api network
- [x] Archimedes deployed on VPS (systemd service)
- [x] Workspace sync via Git (Mac ↔ VPS)

---

## Phase 1: Dionysus Pipeline ✅ COMPLETE

### Tasks
- [x] Fix Graphiti execute_query parameter passing (`params=` not `parameters_=`)
- [x] Fix divide-by-zero in basin stats recording
- [x] Verify basin activation works (strength: 0.85)
- [x] Verify classification works (STRATEGIC, PROCEDURAL, etc.)
- [x] Verify extraction runs (narrative extraction: 3 narratives)
- [x] Test full ingest pipeline

### Verification
```bash
curl -X POST http://localhost:8000/api/memory/ingest \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message", "source": "archimedes"}'
# Returns: {"success":true,"mode":"full_extraction","basin":"strategic-basin",...}
```

---

## Phase 2: Auto-Ingestion ✅ COMPLETE

### Tasks
- [x] Create auto-ingest.sh script (POSTs to both Dionysus + Hexis)
- [x] Add to TOOLS.md as default behavior
- [x] Wire into Archimedes message handling (AGENTS.md mandatory)
- [x] Verify every message auto-ingests
- [x] Verify both databases receive data

### Current Script
```bash
/home/mani/archimedes/scripts/auto-ingest.sh "<message>" "archimedes"
```

### Verification
- Send message → check Hexis `/recall`
- Send message → check Neo4j for entities/relationships

---

## Phase 3: Hydration Integration ✅ COMPLETE

### Tasks
- [x] Create hydrate.sh script
- [x] Query Hexis `/recall` for relevant memories
- [x] Query Dionysus for graph context
- [x] Add to AGENTS.md as mandatory behavior
- [x] Test with live query

### Verification
```bash
/home/mani/archimedes/scripts/hydrate.sh "hexis memory" 5
# Returns: Semantic memories with relevance scores
```

---

## Phase 4: Memory Migration ✅ COMPLETE

### Tasks
- [x] Create migration script (migrate-memory.sh)
- [x] Migrate MEMORY.md → Hexis semantic memories (10/10 sections)
- [x] Migrate MEMORY.md → Dionysus strategic memories (~8/10 sections)
- [x] Verify migrated content is recallable
- [ ] Migrate daily files → episodic memories (optional, can do incrementally)

---

## Phase 5: Fix Known Issues

### Tasks
- [x] Fix Neo4j vector search (`vector.similarity.cosine` unavailable)
  - Installed GDS 2.6.9 plugin
  - Patched graphiti to use `gds.similarity.cosine`
  - Fixed network: connected dionysus-api to dionysus_default
- [ ] Speed up Dionysus ingestion (currently 15-20s per message)
  - LLM extraction is slow; consider async/batch
- [ ] Fix text2story dependency (falling back to LLM)
- [ ] Debug entity extraction (returning 0 entities)
  - LLM extraction works, but entities not persisting to Neo4j
  - May be graphiti internals or LLM prompt issue

### Verification
```bash
# Vector search now works (no more "Unknown function" error):
curl -X POST http://72.61.78.89:8000/api/graphiti/search \
  -d '{"query": "test", "limit": 3}'
# Returns: {"edges":[],"count":0}  # Empty but no error
```

---

## Phase 6: Practical Use Cases

### Tasks
- [ ] **Client session notes**: Store as episodic, recall by client name
- [ ] **Book research**: Store as semantic with source attribution
- [ ] **Inner Architect patterns**: Strategic memories for recurring insights
- [ ] **Procedures/SOPs**: Store as procedural for "how do I..." queries
- [ ] **Daily context**: Auto-ingest captures conversation continuity

### Example Workflows
```bash
# Store client insight
curl -X POST http://72.61.78.89:8001/remember \
  -d '{"content": "Client John: breakthrough on Drama Triangle pattern", "memory_type": "episodic", "importance": 0.8}'

# Recall before session
curl -X POST http://72.61.78.89:8001/recall \
  -d '{"query": "John Drama Triangle", "limit": 5}'
```

---

## Phase 7: Heartbeat Integration

### Tasks
- [ ] Wire Dionysus heartbeat to Clawdbot cron
- [ ] Test autonomous reflection
- [ ] Test proactive outreach
- [ ] Tune heartbeat interval

---

## Phase 8: Polish

### Tasks
- [ ] Add error handling for DB unavailable
- [ ] Add logging for debugging
- [ ] Update documentation
- [ ] Write journal entry
- [ ] Merge to master

---

## Current Status

**Phase:** 5 (Fix Known Issues)  
**Last Update:** 2026-01-31 10:10 UTC

### Issues Found (2026-01-31)
1. **Neo4j vector search broken**: `vector.similarity.cosine` not available
2. **Dionysus ingestion slow**: 15-20s (LLM extraction + narrative)
3. **text2story unavailable**: Falls back to LLM for everything
4. **Entity extraction sparse**: Short messages yield 0 entities

### What's Working
- ✅ Hexis/Daedalus: Healthy, 21 memories, fast recall
- ✅ Dionysus API: Running, classification works
- ✅ Basin activation: Strength increases on use
- ✅ Auto-ingest: Messages flow to Hexis
- ✅ Memory types: All 6 types functional

### Next Task
Fix Neo4j vector search or bypass it for retrieval.

### Architecture (Current)
```
┌─────────────────────────────────────────────────────────────┐
│                         VPS                                  │
│                                                              │
│  ┌───────────┐                                               │
│  │ Archimedes│──┐                                            │
│  │  :18789   │  │                                            │
│  └───────────┘  │                                            │
│                 │ auto-ingest.sh                             │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  ┌──────────┐              ┌──────────────────────┐  │   │
│  │  │ Daedalus │              │      Dionysus        │  │   │
│  │  │  :8001   │              │       :8000          │  │   │
│  │  └────┬─────┘              └──────────┬───────────┘  │   │
│  │       │                               │               │   │
│  │       ▼                               ▼               │   │
│  │  ┌──────────┐              ┌──────────────────────┐  │   │
│  │  │  Hexis   │              │  Basin Router        │  │   │
│  │  │(Postgres)│              │  → MemEvolve         │  │   │
│  │  │ pgvector │              │  → Graphiti          │  │   │
│  │  └──────────┘              │  → Neo4j             │  │   │
│  │                            └──────────────────────┘  │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Next Task
Phase 5: Wire Dionysus heartbeat to Clawdbot cron for autonomous reflection.
