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

## Phase 4: Memory Migration

### Tasks
- [ ] Backup MEMORY.md and daily files
- [ ] Create migration script
- [ ] Migrate MEMORY.md → Hexis semantic memories
- [ ] Migrate daily files → Hexis episodic memories
- [ ] Verify migrated content is recallable
- [ ] Update AGENTS.md to reflect new memory system

---

## Phase 5: Heartbeat Integration

### Tasks
- [ ] Wire Dionysus heartbeat to Clawdbot cron
- [ ] Test autonomous reflection
- [ ] Test proactive outreach
- [ ] Tune heartbeat interval

---

## Phase 6: Polish

### Tasks
- [ ] Add error handling for DB unavailable
- [ ] Add logging for debugging
- [ ] Update documentation
- [ ] Write journal entry
- [ ] Merge to master

---

## Current Status

**Phase:** 3 (Hydration Integration) — Complete ✅  
**Last Update:** 2026-01-31 09:52 UTC

### Next Phase
Phase 4: Migration — move MEMORY.md content to databases

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
Phase 4: Migrate MEMORY.md and daily files to databases for persistent recall.
