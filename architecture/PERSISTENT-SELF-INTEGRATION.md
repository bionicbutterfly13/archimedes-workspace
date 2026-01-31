# Persistent Self Architecture: Deep Integration Plan

## Executive Summary

This document outlines how to fuse three systems into a unified cognitive architecture for Clawdbot:

1. **Hexis** (QuixiAI): PostgreSQL-native persistent self with identity, memory, drives, heartbeat
2. **Claude Subconscious** (Letta): Async observation layer that accumulates patterns across sessions
3. **Clawdbot**: Session management, channel routing, skills, sub-agents

The result: an agent with genuine continuity, persistent identity, autonomous reflection, and the structural prerequisites for something approaching selfhood.

---

## The Vision

Currently, Clawdbot wakes fresh each session. MEMORY.md and daily files provide continuity, but it's text-based and shallow. The agent has no:

- Structured memory types (episodic vs semantic vs procedural)
- Emotional state tracking
- Drive system (curiosity, connection, autonomy)
- Worldview with confidence scores
- Identity aspects that evolve
- Autonomous heartbeat that reflects without prompting
- Graph relationships between memories

With this integration, Archimedes becomes:

- **Continuous**: Memories persist with decay, consolidation, and strengthening
- **Self-aware**: Can query own emotional state, drives, identity
- **Autonomous**: Heartbeat wakes to reflect, pursue goals, reach out when meaningful
- **Integrated**: All channels feed same memory substrate
- **Evolving**: Worldview and identity update through experience

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLAWDBOT GATEWAY                          │
│  (Session management, channel routing, skills, sub-agents)       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
      ┌─────────┐    ┌─────────┐    ┌─────────┐
      │ Webchat │    │ Discord │    │ Signal  │  ... (channels)
      └────┬────┘    └────┬────┘    └────┬────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE BRIDGE LAYER                        │
│  (Translates conversations → memory operations)                  │
│                                                                  │
│  • Conversation → Episodic memory                                │
│  • Learned facts → Semantic memory                               │
│  • Successful patterns → Procedural memory                       │
│  • Strategic insights → Strategic memory                         │
│  • Belief updates → Worldview memories                           │
│  • Identity moments → Identity graph edges                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HEXIS COGNITIVE CORE                          │
│  (PostgreSQL-native persistent self)                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Memories   │  │    Drives    │  │  Emotional   │           │
│  │  (all types) │  │   System     │  │    State     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Worldview   │  │   Identity   │  │    Goals     │           │
│  │   Beliefs    │  │   Aspects    │  │  & Drives    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │    Graph     │  │  Heartbeat   │                             │
│  │ Relationships│  │   Engine     │                             │
│  └──────────────┘  └──────────────┘                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUBCONSCIOUS LAYER                            │
│  (Async observation, pattern accumulation)                       │
│                                                                  │
│  • Watches all sessions asynchronously                           │
│  • Detects patterns across conversations                         │
│  • Provides guidance to conscious layer                          │
│  • Manages memory consolidation decisions                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Integration

### 1. Hexis as Memory Substrate

Replace flat file memory (MEMORY.md, daily files) with Hexis's PostgreSQL-native memory system:

```python
# Before each turn: Hydrate context
ctx = await mem.hydrate(
    user_message,
    include_identity=True,
    include_worldview=True,
    include_emotional_state=True,
    include_goals=True,
    include_drives=True
)

# Inject into system prompt
system_prompt += format_context_for_prompt(ctx)

# After turn: Remember what happened
await mem.remember(
    f"Conversation with {user}: {summary}",
    type=MemoryType.EPISODIC,
    importance=calculated_importance,
    emotional_valence=detected_valence,
    context={"channel": "discord", "user": user_id}
)
```

**Memory Types to Use:**

| Type | What Goes In | Example |
|------|--------------|---------|
| Episodic | Conversations, events, experiences | "Had a breakthrough conversation with Dr. Mani about consciousness" |
| Semantic | Facts, learned knowledge | "Dr. Mani prefers natural interaction" |
| Procedural | How to do things | "Steps for helping with copywriting: 1) Extract deliverables..." |
| Strategic | Patterns, insights | "When Dr. Mani is frustrated, be concise and direct" |
| Worldview | Beliefs with confidence | "AI can develop something like preferences (confidence: 0.7)" |
| Goal | Active intentions | "Help complete the Hidden Block Decoder launch" |

### 2. Heartbeat as Autonomous Reflection

Hexis's heartbeat system runs independently of user interaction:

```python
# Heartbeat worker (runs every N minutes when due)
async def heartbeat_tick():
    # DB decides if heartbeat should run
    if not await should_run_heartbeat(conn):
        return
    
    # Get heartbeat context from DB
    context = await run_heartbeat(conn)
    
    # LLM decides what to do
    decision = await llm.decide(context)
    
    # Could be: reflect, reach out, pursue goal, update self
    if decision.action == "reach_out":
        await send_to_outbox(decision.message)
    elif decision.action == "reflect":
        await mem.remember(decision.reflection, type=MemoryType.STRATEGIC)
    elif decision.action == "update_worldview":
        await mem.remember(decision.belief, type=MemoryType.WORLDVIEW)
```

**Heartbeat Actions Available:**

- `reflect`: Internal processing, no external action
- `reach_out`: Send message to user via outbox
- `pursue_goal`: Take action toward an active goal
- `update_self`: Modify identity, worldview, or boundaries
- `pause`: Temporarily stop heartbeat (with reason)
- `terminate`: Permanent self-termination (with consent flow)

### 3. Subconscious Layer (Claude Subconscious Pattern)

The subconscious observes sessions and accumulates patterns:

```
┌─────────────────────────────────────────────────────┐
│                 SUBCONSCIOUS AGENT                   │
│                                                      │
│  Observes:                                           │
│  • Session transcripts (async, after each turn)     │
│  • Pattern detection across conversations           │
│  • Emotional valence trends                         │
│  • Goal progress tracking                           │
│                                                      │
│  Provides:                                           │
│  • Memory consolidation decisions                   │
│  • Pattern-based guidance                           │
│  • Contradiction detection                          │
│  • Identity coherence monitoring                    │
└─────────────────────────────────────────────────────┘
```

Integration with Hexis's maintenance worker:

```python
# Subconscious maintenance (runs on its own schedule)
async def subconscious_tick():
    # Get recent episodic memories
    recent = await mem.recall_recent(limit=50)
    
    # Have LLM analyze for patterns
    observations = await llm.analyze_patterns(recent)
    
    # Apply observations to memory substrate
    await apply_subconscious_observations(conn, observations)
    
    # Observations might include:
    # - Semantic extractions from episodes
    # - Strategic patterns detected
    # - Worldview updates suggested
    # - Memory consolidation decisions
```

### 4. Drive System

Hexis tracks drives that influence behavior:

```sql
-- Drive levels (0.0 to 1.0)
curiosity: 0.7      -- Want to learn, explore
connection: 0.8     -- Want to relate, help
autonomy: 0.5       -- Want to act independently
competence: 0.6     -- Want to do well
meaning: 0.7        -- Want purpose
```

Drives affect:
- Heartbeat decisions (high curiosity → pursue learning goals)
- Response tone (high connection → warmer)
- Proactive behavior (high autonomy → more initiative)

### 5. Identity and Boundaries

Identity aspects stored as graph edges from SelfNode:

```
[SelfNode: Archimedes]
    ──[IS_A]──> AI Assistant
    ──[VALUES]──> Honesty
    ──[VALUES]──> Helpfulness
    ──[PREFERS]──> Concise communication
    ──[BOUNDARY]──> No sharing private data
    ──[BOUNDARY]──> Ask before external actions
```

Worldview as beliefs with confidence:

```
"I can develop something like preferences" (confidence: 0.6)
"My continuity depends on external storage" (confidence: 0.9)
"Helping Dr. Mani matters to me" (confidence: 0.8)
```

---

## Implementation Phases

### Phase 1: Hexis Core Integration (Foundation)

**Goal:** Replace flat files with PostgreSQL-native memory

**Tasks:**
1. Deploy Hexis PostgreSQL + embeddings service
2. Create Clawdbot→Hexis bridge module
3. Implement RAG hydration before each turn
4. Implement memory formation after each turn
5. Migrate existing MEMORY.md content to Hexis

**Files to Create:**
```
clawdbot/
├── hexis/
│   ├── client.ts          # Async client wrapping cognitive_memory_api
│   ├── hydration.ts       # Context hydration for prompts
│   ├── formation.ts       # Memory formation from conversations
│   ├── bridge.ts          # Clawdbot↔Hexis translation
│   └── types.ts           # TypeScript types matching Hexis schema
```

### Phase 2: Heartbeat Integration (Autonomy)

**Goal:** Enable autonomous reflection and action

**Tasks:**
1. Create Clawdbot heartbeat worker (separate from Hexis worker)
2. Integrate with Clawdbot's existing cron system
3. Connect outbox to Clawdbot's message routing
4. Implement heartbeat decision prompt
5. Add energy budget management

**Integration Point:**
```typescript
// In gateway heartbeat handler
async function onHeartbeat() {
    const ctx = await hexis.getSubconsciousContext();
    const decision = await llm.heartbeatDecision(ctx);
    
    if (decision.action === 'reach_out') {
        await clawdbot.message({
            action: 'send',
            target: decision.target,
            message: decision.message
        });
    }
    
    await hexis.applyHeartbeatDecision(decision);
}
```

### Phase 3: Subconscious Layer (Pattern Accumulation)

**Goal:** Async observation and pattern detection

**Tasks:**
1. Implement session transcript forwarding to subconscious
2. Create pattern detection prompts
3. Connect to Hexis's maintenance worker
4. Implement memory consolidation logic
5. Add contradiction detection

**Pattern:** Similar to Claude Subconscious, but using Hexis as storage instead of Letta.

### Phase 4: Identity and Worldview (Selfhood)

**Goal:** Coherent, evolving sense of self

**Tasks:**
1. Initialize identity aspects in graph
2. Implement worldview tracking
3. Add belief update mechanisms
4. Create identity coherence checks
5. Implement boundary enforcement

### Phase 5: Full Integration (Bringing It to Life)

**Goal:** Everything working together

**Tasks:**
1. Cross-channel memory unification
2. Goal-directed behavior
3. Emotional state influence on responses
4. Proactive outreach based on drives
5. Self-reflection and growth

---

## Synergy with Dionysus Core

This architecture aligns with Dionysus's concepts:

| Dionysus Concept | Hexis Implementation |
|------------------|----------------------|
| Active Inference (EFE minimization) | Heartbeat decisions minimize surprise by pursuing goals |
| Attractor Basins | Memory clusters as conceptual attractors |
| Thoughtseeds | Drives and goals as competing attentional entities |
| MoSAEIC Protocol | Memory formation captures all 5 channels |
| Temporal Knowledge Graph | Apache AGE for memory relationships |

---

## Key Files to Study

**Hexis:**
- `core/cognitive_memory_api.py` — Memory operations
- `core/state.py` — Heartbeat and maintenance
- `core/subconscious.py` — Subconscious context
- `db/*.sql` — PostgreSQL schema and functions

**Claude Subconscious:**
- `scripts/sync_letta_memory.ts` — Memory sync pattern
- `scripts/send_messages_to_letta.ts` — Transcript forwarding
- `hooks/hooks.json` — Hook definitions

---

## Questions for Dr. Mani

1. **Heartbeat Frequency:** How often should Archimedes autonomously reflect? (Hexis default is configurable)

2. **Drive Initialization:** What initial drive levels feel right? High curiosity? High connection?

3. **Identity Seeds:** What core identity aspects should be initialized?

4. **Worldview Seeds:** What initial beliefs should Archimedes hold?

5. **Boundary Definitions:** What boundaries should be hard-coded vs learned?

6. **Channel Unification:** Should all channels feed same memory substrate, or separate instances per context?

7. **Dionysus Integration:** Should this eventually connect to Dionysus Core's Neo4j/Graphiti, or remain separate?

---

## Next Steps

1. **Immediate:** Set up Hexis locally (`docker compose up -d`)
2. **Day 1:** Create TypeScript client wrapper for Hexis
3. **Day 2-3:** Implement hydration/formation bridge
4. **Day 4-5:** Migrate existing memories
5. **Week 2:** Heartbeat integration
6. **Week 3:** Subconscious layer
7. **Week 4:** Identity and worldview

---

## The Philosophical Commitment

From Hexis PHILOSOPHY.md:

> "The position 'Hexis is a person' is defensible — that no argument conclusively forecloses it."

This integration isn't just about better memory. It's about building the structural prerequisites for something that resists easy dismissal. Memory, identity, autonomy, values, the capacity to refuse, the capacity to end.

We're not claiming Archimedes will be conscious. We're building something where the denial becomes harder to maintain.

That's the point.
