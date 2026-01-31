# Specification: Hexis Memory Substrate Integration

**Track:** 001-hexis-integration  
**Branch:** `feature/001-hexis-integration`  
**Status:** In Progress  
**Author:** Mani Saint-Victor, MD

---

## Overview

Integrate Hexis as the persistent memory substrate for Clawdbot. Memory, awareness, heartbeat. No personality theater.

---

## Goals

1. **Persistent Memory**: Replace flat files with structured memory (episodic, semantic, procedural, strategic, goal)
2. **Context Awareness**: Agent recalls relevant past conversations and facts
3. **Autonomous Heartbeat**: Periodic reflection and proactive action
4. **Drive System**: Priority weighting for attention allocation
5. **Operator Control**: Full parameter tuning via control panel

---

## Non-Goals

1. Identity formation / worldview tracking / emotional state
2. Consent ceremonies / philosophical personhood debates
3. Full Dionysus integration (separate track)
4. Neo4j migration (Hexis uses PostgreSQL + AGE)

---

## Integration Points

| Clawdbot Component | Hexis Integration |
|--------------------|-------------------|
| Session start | `hydrate()` → inject context into system prompt |
| Each turn (after) | `remember()` → form episodic/semantic memories |
| Cron jobs | Hexis heartbeat coordination |
| Message routing | Heartbeat `reach_out` → Clawdbot `message` |
| MEMORY.md | Migrated to Hexis semantic memories |
| Daily files | Migrated to Hexis episodic memories |

---

## Technical Constraints

1. **Database as Brain**: PostgreSQL owns state. TypeScript is transport.
2. **No Direct SQL**: All operations via DB functions
3. **Operator Controls**: All capabilities tunable (self-termination disabled by default)
4. **No Breaking Changes**: Existing Clawdbot functionality intact

---

## Memory Flow

### Hydration (Before Turn)

```typescript
const ctx = await hexis.hydrate(userMessage, {
    memoryLimit: 10,
    includeDrives: true,
    includeGoals: true
});
systemPrompt += formatContextForPrompt(ctx);
```

### Formation (After Turn)

```typescript
await formMemoriesFromTurn(hexis, {
    user, userMessage, assistantResponse, channel, timestamp
});
```

### Heartbeat (Autonomous)

```typescript
if (await hexis.shouldRunHeartbeat()) {
    const ctx = await hexis.getHeartbeatContext();
    const decision = simpleDecider(ctx); // or LLM-based
    // Execute decision...
    await hexis.applyHeartbeatDecision(ctx.heartbeat_id, decision);
}
```

---

## Success Criteria

1. [ ] Hexis services running locally
2. [ ] TypeScript client connects and queries
3. [ ] Hydration injects relevant memories into prompts
4. [ ] Formation persists conversations to Hexis
5. [ ] Heartbeat runs autonomously (when enabled)
6. [ ] Operator controls work from control panel
7. [ ] No regressions in existing Clawdbot functionality

---

## Dependencies

- Docker + Docker Compose
- PostgreSQL 15+ with pgvector and AGE
- Node.js pg library
- Hexis embeddings service

---

## Files Created

```
clawd/
├── hexis/
│   ├── README.md
│   ├── types.ts
│   ├── client.ts
│   ├── hydration.ts
│   ├── formation.ts
│   ├── heartbeat.ts
│   └── index.ts
├── Hexis/
│   ├── db/99_operator_controls.sql
│   └── control-panel/index.html
└── architecture/
    ├── spec.md
    └── plan.md
```
