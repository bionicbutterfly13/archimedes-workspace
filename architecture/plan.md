# Implementation Plan: Hexis Cognitive Core Integration

**Track:** 001-hexis-integration  
**Spec:** [spec.md](./spec.md)  
**Status:** Phase 0 (Setup)

---

## Integration (IO Map)

### Attachment Points

| File/Component | Integration |
|----------------|-------------|
| Clawdbot gateway session handler | Calls `hexis.hydrate()` before LLM |
| Clawdbot post-response handler | Calls `hexis.remember()` after turn |
| Clawdbot cron system | Coordinates with Hexis heartbeat worker |
| Clawdbot message tool | Receives heartbeat `reach_out` actions |

### Inputs

- User messages from all channels (Signal, Discord, webchat, etc.)
- Session metadata (channel, user, timestamp)
- Cron triggers for heartbeat coordination

### Outputs

- Hydrated context injected into system prompt
- Memories persisted to Hexis PostgreSQL
- Heartbeat actions routed to Clawdbot message system

---

## Phase 0: Infrastructure Setup

### Tasks

- [ ] Verify Docker Desktop installed and running
- [ ] Clone Hexis repo (done: `/Users/manisaintvictor/clawd/Hexis`)
- [ ] Start Hexis services: `docker compose up -d`
- [ ] Run Hexis init: `./hexis init`
- [ ] Verify status: `./hexis status`
- [ ] Test basic chat: `./hexis chat --no-extended-tools`

### Verification

```bash
cd /Users/manisaintvictor/clawd/Hexis
docker compose ps  # All services healthy
./hexis status     # Agent configured, heartbeat ready
```

---

## Phase 1: TypeScript Client

### Tasks

- [ ] Create `/Users/manisaintvictor/clawd/hexis/` directory structure
- [ ] Implement `client.ts`: Connection pool, basic operations
- [ ] Implement `types.ts`: TypeScript types matching Hexis schema
- [ ] Implement `hydration.ts`: Context formatting for prompts
- [ ] Implement `formation.ts`: Memory creation from conversations
- [ ] Add unit tests for client functions

### Files to Create

```
clawd/hexis/
├── client.ts          # Pool management, DB function calls
├── types.ts           # Memory, HydratedContext, etc.
├── hydration.ts       # formatContextForPrompt()
├── formation.ts       # formMemoriesFromTurn()
├── index.ts           # Public exports
└── __tests__/
    ├── client.test.ts
    └── hydration.test.ts
```

### Verification

```typescript
// Manual test in Node REPL
import { HexisClient } from './hexis';
const client = new HexisClient(process.env.HEXIS_DSN);
const ctx = await client.hydrate('test query');
console.log(ctx.memories.length);
await client.close();
```

---

## Phase 2: Hydration Integration

### Tasks

- [ ] Identify Clawdbot session handler entry point
- [ ] Add hydration call before LLM invocation
- [ ] Format and inject context into system prompt
- [ ] Add configuration for hydration settings
- [ ] Test with live conversation

### Integration Pattern

```typescript
// In session handler (pseudocode)
async function handleUserMessage(session, message) {
    // NEW: Hydrate from Hexis
    const ctx = await hexis.hydrate(message.text, config.hexis.hydration);
    const contextBlock = formatContextForPrompt(ctx);
    
    // Inject into system prompt
    const enrichedSystemPrompt = systemPrompt + '\n\n' + contextBlock;
    
    // Existing LLM call
    const response = await llm.complete(enrichedSystemPrompt, message.text);
    
    return response;
}
```

### Verification

- [ ] Send message mentioning something from previous session
- [ ] Verify hydrated context appears in system prompt
- [ ] Verify agent recalls relevant memories

---

## Phase 3: Memory Formation

### Tasks

- [ ] Identify post-response handler entry point
- [ ] Implement episodic memory formation after each turn
- [ ] Implement semantic fact extraction
- [ ] Add importance/valence calculation
- [ ] Test memory persistence across sessions

### Integration Pattern

```typescript
// In post-response handler (pseudocode)
async function afterResponse(session, turn) {
    // NEW: Form memories in Hexis
    await formMemoriesFromTurn(hexis, {
        user: session.user,
        userMessage: turn.userMessage,
        assistantResponse: turn.response,
        channel: session.channel,
        timestamp: new Date()
    });
}
```

### Verification

- [ ] Have conversation with memorable content
- [ ] Query Hexis DB: `SELECT * FROM memories ORDER BY created_at DESC LIMIT 5`
- [ ] Verify memory content matches conversation
- [ ] Start new session, verify memory is recalled

---

## Phase 4: Migration

### Tasks

- [ ] Create migration script for MEMORY.md → Hexis semantic memories
- [ ] Create migration script for daily files → Hexis episodic memories
- [ ] Backup existing files before migration
- [ ] Run migration
- [ ] Verify migrated content is recallable
- [ ] Update AGENTS.md to reflect new memory system

### Migration Script

```typescript
// scripts/migrate-to-hexis.ts
import { HexisClient } from '../hexis';
import * as fs from 'fs';

async function migrate() {
    const hexis = new HexisClient(process.env.HEXIS_DSN);
    
    // 1. Migrate MEMORY.md
    const memory = fs.readFileSync('MEMORY.md', 'utf-8');
    // Parse sections, create semantic memories
    
    // 2. Migrate daily files
    const dailyFiles = fs.readdirSync('memory/');
    for (const file of dailyFiles) {
        // Parse, create episodic memories with dates
    }
    
    await hexis.close();
}
```

### Verification

- [ ] Count memories before/after migration
- [ ] Query for known content from MEMORY.md
- [ ] Query for known content from daily files

---

## Phase 5: Heartbeat Integration (Optional)

### Tasks

- [ ] Review Clawdbot cron system for coordination
- [ ] Implement heartbeat worker bridge
- [ ] Connect heartbeat `reach_out` to Clawdbot message tool
- [ ] Add heartbeat configuration to gateway config
- [ ] Test autonomous reflection
- [ ] Test proactive outreach

### Integration Pattern

```typescript
// Heartbeat worker coordination
async function hexisHeartbeatTick() {
    if (!await hexis.shouldRunHeartbeat()) return;
    
    const context = await hexis.runHeartbeat();
    const decision = await llm.heartbeatDecision(context);
    
    switch (decision.action) {
        case 'reach_out':
            await clawdbot.message({
                action: 'send',
                target: decision.target,
                message: decision.content
            });
            break;
        case 'reflect':
            // Recorded in Hexis
            break;
    }
    
    await hexis.applyHeartbeatDecision(decision);
}
```

### Verification

- [ ] Enable heartbeat in Hexis config
- [ ] Wait for heartbeat interval
- [ ] Check `heartbeat_log` for entries
- [ ] Verify reflection memories created

---

## Phase 6: Polish and Documentation

### Tasks

- [ ] Add error handling and graceful degradation
- [ ] Add logging for debugging
- [ ] Update AGENTS.md with new memory patterns
- [ ] Update MEMORY.md header (now backed by Hexis)
- [ ] Write journal entry documenting the integration
- [ ] Create runbook for Hexis operations

---

## Quality Gates

Before marking any phase complete:

- [ ] All tests pass
- [ ] No regressions in existing functionality
- [ ] Documentation updated
- [ ] Verified manually with live conversation

---

## Configuration

Add to Clawdbot gateway config:

```yaml
hexis:
  enabled: true
  dsn: postgresql://hexis_user:hexis_password@localhost:43815/hexis_memory
  
  hydration:
    memory_limit: 10
    include_identity: true
    include_worldview: true
    include_emotional_state: true
    include_goals: false
    include_drives: true
  
  formation:
    auto_episodic: true
    extract_facts: true
  
  heartbeat:
    enabled: false  # Enable when ready
    coordinate_with_cron: true
```

---

## Notes

- Start with Phase 0-2 for immediate value (memory hydration)
- Phase 3 creates the feedback loop (formation)
- Phase 4 preserves existing knowledge
- Phase 5 is optional until heartbeat behavior is tuned
- Each phase can be merged independently
