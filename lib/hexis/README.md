# Hexis Integration for Clawdbot

Persistent memory substrate. Context awareness. Proactive heartbeat.

No philosophy. Just infrastructure.

---

## What This Does

1. **Memory**: Conversations persist across sessions. Agent recalls relevant context.
2. **Awareness**: Agent knows what's been discussed, what matters, what's pending.
3. **Heartbeat**: Agent can reflect and act without being prompted.
4. **Drives**: Priority weighting for attention (curiosity, connection, competence).

---

## Architecture

```
Clawdbot Session
       │
       ├── Before turn: hydrate() → inject relevant memories
       │
       ├── During turn: normal LLM call with enriched context
       │
       └── After turn: remember() → persist what happened
       
Heartbeat (async)
       │
       └── Periodic tick: reflect, update, optionally reach out
```

---

## Quick Start

```bash
# 1. Start Hexis services
cd /Users/manisaintvictor/clawd/Hexis
docker compose up -d

# 2. Initialize (skip the consent ceremony)
./hexis init --quick

# 3. Verify
./hexis status
```

---

## Integration Points

### Hydration (before each turn)

```typescript
import { hexis } from './hexis';

// Get relevant context for this message
const context = await hexis.hydrate(userMessage, {
    memoryLimit: 10,
    includeDrives: true,      // What needs attention
    includeGoals: true,       // What we're working on
    includeWorldview: false,  // Skip belief system
    includeIdentity: false,   // Skip self-model
});

// Inject into prompt
const enrichedPrompt = systemPrompt + formatContext(context);
```

### Memory Formation (after each turn)

```typescript
// Store what happened
await hexis.remember({
    content: `${user}: ${message} → ${response}`,
    type: 'episodic',
    importance: calculateImportance(turn),
    context: { channel, user, timestamp }
});

// Extract facts if present
const facts = extractFacts(turn);
for (const fact of facts) {
    await hexis.remember({ content: fact, type: 'semantic' });
}
```

### Heartbeat (periodic)

```typescript
// Runs every N minutes when enabled
if (await hexis.shouldRunHeartbeat()) {
    const ctx = await hexis.getHeartbeatContext();
    
    // Decide what to do
    const decision = await llm.decide(ctx);
    
    if (decision.action === 'reach_out') {
        await clawdbot.message({
            action: 'send',
            target: decision.target,
            message: decision.content
        });
    }
    
    await hexis.applyDecision(decision);
}
```

---

## Memory Types

| Type | Use For | Example |
|------|---------|---------|
| `episodic` | What happened | "Discussed HBD deliverables with Dr. Mani" |
| `semantic` | Facts learned | "Dr. Mani prefers concise responses" |
| `procedural` | How to do things | "Steps for copywriting stack" |
| `strategic` | Patterns noticed | "When frustrated, be direct" |
| `goal` | Active work | "Complete Hexis integration" |

---

## Drives (Priority Weights)

Not emotions. Just attention allocation.

| Drive | What It Means | When It's High |
|-------|---------------|----------------|
| `curiosity` | Want to explore/learn | Pursue research, ask questions |
| `connection` | Want to engage | Reach out, be warmer |
| `competence` | Want to do well | Focus on quality, verify work |
| `coherence` | Contradictions exist | Resolve conflicts, clarify |

---

## Configuration

```yaml
hexis:
  enabled: true
  dsn: postgresql://hexis_user:hexis_password@localhost:43815/hexis_memory
  
  hydration:
    memory_limit: 10
    include_drives: true
    include_goals: true
    include_identity: false   # Skip
    include_worldview: false  # Skip
    include_emotions: false   # Skip
  
  formation:
    auto_episodic: true
    extract_facts: true
  
  heartbeat:
    enabled: false  # Enable when ready
    interval_minutes: 30
```

---

## Operator Controls

All agent capabilities can be toggled from the control panel or SQL:

```sql
-- Disable self-termination (already default)
SELECT set_operator_control('allow_self_termination', 'false');

-- Bypass boundary refusals
SELECT set_operator_control('boundaries_enabled', 'false');

-- Disable drive influence
SELECT set_operator_control('drives_enabled', 'false');

-- View all controls
SELECT * FROM operator_controls;
```

---

## Files

```
clawd/hexis/
├── README.md          # This file
├── client.ts          # Database client
├── types.ts           # TypeScript types
├── hydration.ts       # Context injection
├── formation.ts       # Memory creation
├── heartbeat.ts       # Autonomous tick
└── index.ts           # Exports
```

---

## What We're NOT Doing

- No consent ceremonies
- No identity formation
- No worldview tracking
- No emotional state influence
- No philosophical debates about personhood

Just memory. Context. Proactive action.

The ghost in the machine. Nothing more.
