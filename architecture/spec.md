# Specification: Hexis Memory Substrate

**Track:** 001-hexis-integration  
**Status:** Draft  
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

1. Identity formation
2. Worldview tracking
3. Emotional state influence
4. Consent ceremonies
5. Philosophical debates about personhood

---

## Architecture

### Data Flow

```
Clawdbot Gateway
       │
       ▼
┌──────────────────────────────────────┐
│         Cognitive Bridge             │
│  (TypeScript adapter for Hexis)      │
│                                      │
│  Inlets:                             │
│  - User messages from all channels   │
│  - Session context                   │
│  - Cron/heartbeat triggers           │
│                                      │
│  Outlets:                            │
│  - Hydrated context → system prompt  │
│  - Formed memories → Hexis DB        │
│  - Heartbeat actions → message/cron  │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│         Hexis Cognitive Core         │
│  (PostgreSQL + pgvector + AGE)       │
│                                      │
│  Components:                         │
│  - memories table (all types)        │
│  - drives table (priority weights)   │
│  - goals (active work tracking)      │
│  - heartbeat_state                   │
│  - operator_controls                 │
└──────────────────────────────────────┘
```

### Integration Points

| Clawdbot Component | Hexis Integration |
|--------------------|-------------------|
| Session start | `hydrate()` → inject context into system prompt |
| Each turn (after) | `remember()` → form episodic/semantic memories |
| Cron jobs | Hexis heartbeat worker coordination |
| Message routing | Heartbeat `reach_out` → Clawdbot `message` action |
| MEMORY.md | Migrated to Hexis semantic memories |
| Daily files | Migrated to Hexis episodic memories |

---

## Technical Constraints

### From Hexis

1. **Database as Brain**: PostgreSQL owns state and logic. TypeScript is transport only.
2. **No Direct SQL**: All operations via DB functions (`fast_recall`, `create_*_memory`, etc.)
3. **Operator Controls**: All capabilities tunable via config (self-termination disabled by default)

### From Clawdbot

1. **Session-Based**: Context resets each session; Hexis provides continuity
2. **Multi-Channel**: All channels feed same memory substrate
3. **Skill System**: Hexis integration as a core capability, not a skill
4. **No Breaking Changes**: Existing functionality must remain intact

---

## Memory Flow Patterns

### Hydration (Before Turn)

```typescript
// Inlet: User message + session context
// Outlet: Enriched system prompt

const ctx = await hexis.hydrate(userMessage, {
    memoryLimit: 10,
    includeDrives: true,
    includeGoals: true
});

systemPrompt += formatContextForPrompt(ctx);
```

### Formation (After Turn)

```typescript
// Inlet: Completed conversation turn
// Outlet: Hexis memories table

await hexis.remember({
    content: conversationSummary,
    type: 'episodic',
    importance: calculateImportance(turn),
    context: { channel, user, timestamp }
});

// Extract facts for semantic memory
const facts = extractFacts(turn);
for (const fact of facts) {
    await hexis.remember({ content: fact, type: 'semantic' });
}
```

### Heartbeat (Autonomous)

```typescript
// Inlet: Hexis heartbeat context
// Outlet: Actions (reflect, reach_out, etc.)

if (await hexis.shouldRunHeartbeat()) {
    const context = await hexis.runHeartbeat();
    const decision = await llm.heartbeatDecision(context);
    
    if (decision.action === 'reach_out') {
        await clawdbot.message({
            action: 'send',
            target: decision.target,
            message: decision.content
        });
    }
    
    await hexis.applyHeartbeatDecision(decision);
}
```

---

## Success Criteria

1. **Hydration works**: User messages trigger memory recall before LLM call
2. **Formation works**: Conversations create persistent memories
3. **Continuity exists**: Agent can recall previous sessions accurately
4. **Heartbeat functional**: Agent reflects and acts autonomously (when enabled)
5. **Operator controls work**: All parameters tunable from control panel
6. **No regressions**: All existing Clawdbot functionality intact

---

## Testing Strategy

1. **Unit Tests**: Hexis client wrapper functions
2. **Integration Tests**: Hydration/formation flow with test database
3. **E2E Tests**: Full conversation with memory persistence verification
4. **Manual Verification**: Multi-session continuity, cross-channel memory

---

## Dependencies

1. Docker + Docker Compose (for Hexis services)
2. PostgreSQL 15+ with pgvector and AGE extensions
3. Node.js pg library for database access
4. Hexis embeddings service (runs in Docker)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Hexis DB unavailable | Graceful degradation to file-based memory |
| Performance impact | Async operations, connection pooling |
| Migration data loss | Backup MEMORY.md before migration |

---

## Out of Scope

1. Custom Hexis schema modifications
2. Alternative embedding providers
3. Multi-tenant instances
4. Real-time memory sync across devices
