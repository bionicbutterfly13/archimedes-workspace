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
- Formed memories → Hexis PostgreSQL
- Heartbeat actions → Clawdbot message routing

### Attachment Points
- `clawd/hexis/` — TypeScript integration module
- Clawdbot gateway session handler (hydration hook)
- Clawdbot post-response handler (formation hook)
- Clawdbot cron system (heartbeat coordination)

---

## Phase 0: Infrastructure

### Tasks
- [x] Clone Hexis repo
- [x] Create operator controls SQL
- [x] Create control panel UI
- [x] Create TypeScript client module
- [ ] Start Hexis services: `docker compose up -d`
- [ ] Initialize Hexis: `./hexis init --quick`
- [ ] Verify connection: `./hexis status`

### Verification
```bash
cd /Users/manisaintvictor/clawd/Hexis
docker compose ps  # All healthy
./hexis status     # Configured
```

---

## Phase 1: Client Verification

### Tasks
- [ ] Install pg dependency in clawd
- [ ] Test client connection to Hexis
- [ ] Test `hydrate()` returns memories
- [ ] Test `remember()` creates memories
- [ ] Test `recall()` retrieves by query

### Verification
```typescript
const hexis = await initHexis(DSN);
await hexis.remember({ content: 'Test memory', type: 'semantic' });
const ctx = await hexis.hydrate('test');
console.log(ctx.memories); // Should include test memory
```

---

## Phase 2: Hydration Integration

### Tasks
- [ ] Identify Clawdbot session handler entry point
- [ ] Add hydration call before LLM invocation
- [ ] Format and inject context into system prompt
- [ ] Test with live conversation
- [ ] Verify memories appear in context

### Verification
- Send message referencing something from MEMORY.md
- Confirm agent recalls it via Hexis (not just file read)

---

## Phase 3: Memory Formation

### Tasks
- [ ] Identify post-response handler in Clawdbot
- [ ] Add formation call after each turn
- [ ] Verify episodic memories created
- [ ] Verify fact extraction works
- [ ] Test cross-session recall

### Verification
```sql
SELECT * FROM memories ORDER BY created_at DESC LIMIT 5;
```

---

## Phase 4: Migration

### Tasks
- [ ] Backup MEMORY.md and daily files
- [ ] Create migration script
- [ ] Migrate MEMORY.md → semantic memories
- [ ] Migrate daily files → episodic memories
- [ ] Verify migrated content is recallable
- [ ] Update AGENTS.md to reflect new memory system

### Verification
- Query Hexis for known facts from MEMORY.md
- Confirm they're returned in hydration

---

## Phase 5: Heartbeat (Optional)

### Tasks
- [ ] Review Clawdbot cron system
- [ ] Wire heartbeat tick to cron
- [ ] Test autonomous reflection
- [ ] Test proactive outreach (if target available)
- [ ] Tune heartbeat interval

### Verification
- Enable heartbeat, wait for interval
- Check `heartbeat_log` for entries
- Confirm reflection memories created

---

## Phase 6: Polish

### Tasks
- [ ] Add error handling for DB unavailable
- [ ] Add logging for debugging
- [ ] Update documentation
- [ ] Write journal entry
- [ ] Merge to master

---

## Quality Gates

Before marking any task complete:
- [ ] Code works as expected
- [ ] No regressions
- [ ] Documentation updated if needed

---

## Commit Protocol

```bash
git add -A
git commit -m "feat(hexis): <description>

<details>

AUTHOR Mani Saint-Victor, MD"
```

---

## Current Status

**Phase:** 0 (Infrastructure) — Complete  
**Last Update:** 2026-01-31

### Completed
- [x] Hexis services running on VPS (hexis_brain, hexis_embeddings)
- [x] Daedalus API running at `http://localhost:8001` (VPS)
- [x] Auto-memory ingestion endpoint configured
- [x] Verified `/remember` endpoint works
- [x] **Archimedes deployed on VPS** (ws://100.66.39.11:18789)
- [x] Running as systemd user service (`archimedes.service`)
- [x] Bound to Tailscale for secure access
- [x] VPS Archimedes uses localhost:8001 for Daedalus (no network hop)

### VPS Archimedes Details
```
Gateway:    ws://100.66.39.11:18789
Control UI: http://100.66.39.11:18789
Auth Token: archimedes-vps-token-2026
Service:    systemctl --user status archimedes
```

### Architecture
```
┌─────────────────────────────────────────────┐
│                   VPS                        │
│  ┌───────────┐    ┌──────────┐   ┌───────┐  │
│  │ Archimedes│───▶│ Daedalus │──▶│ Hexis │  │
│  │  :18789   │    │  :8001   │   │(Postgres)│
│  └───────────┘    └──────────┘   └───────┘  │
└─────────────────────────────────────────────┘
         ▲
         │ Tailscale
         │
┌────────┴────────┐
│    Your Mac     │
└─────────────────┘
```

### Known Issues
- Dionysus `/api/memory/ingest` has parameter bugs
- Using Daedalus directly until Dionysus pipeline is fixed
- Mac Archimedes still has Discord; VPS does not yet

### Next Tasks
- [ ] Move Discord config to VPS Archimedes
- [ ] Set up workspace sync (Mac ↔ VPS)
- [ ] Wire Clawdbot TypeScript client to Hexis (Phase 1)
