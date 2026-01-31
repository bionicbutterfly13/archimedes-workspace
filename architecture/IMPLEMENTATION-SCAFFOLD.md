# Implementation Scaffold: Concrete Code Patterns

## Quick Start: Get Hexis Running

```bash
cd /Users/manisaintvictor/clawd/Hexis

# Start services
docker compose up -d

# Initialize agent
./hexis init

# Verify
./hexis status
```

---

## TypeScript Client for Clawdbot

Create a thin TypeScript wrapper that calls Hexis's PostgreSQL functions:

```typescript
// clawdbot/hexis/client.ts

import { Pool } from 'pg';

export interface Memory {
    id: string;
    type: 'episodic' | 'semantic' | 'procedural' | 'strategic' | 'worldview' | 'goal';
    content: string;
    importance: number;
    similarity?: number;
    trust_level?: number;
    created_at?: Date;
    emotional_valence?: number;
}

export interface HydratedContext {
    memories: Memory[];
    identity: Record<string, any>[];
    worldview: Record<string, any>[];
    emotional_state: Record<string, any> | null;
    goals: Record<string, any> | null;
    urgent_drives: Record<string, any>[];
}

export class HexisClient {
    private pool: Pool;
    
    constructor(dsn: string) {
        this.pool = new Pool({ connectionString: dsn });
    }
    
    async hydrate(query: string, options: {
        memoryLimit?: number;
        includeIdentity?: boolean;
        includeWorldview?: boolean;
        includeEmotionalState?: boolean;
        includeGoals?: boolean;
        includeDrives?: boolean;
    } = {}): Promise<HydratedContext> {
        const client = await this.pool.connect();
        try {
            // Get memories via fast_recall
            const memoriesResult = await client.query(
                `SELECT * FROM fast_recall($1, $2)`,
                [query, options.memoryLimit || 10]
            );
            
            // Get turn context
            const ctxResult = await client.query(`SELECT gather_turn_context()`);
            const ctx = ctxResult.rows[0]?.gather_turn_context || {};
            
            return {
                memories: memoriesResult.rows,
                identity: options.includeIdentity !== false ? (ctx.identity || []) : [],
                worldview: options.includeWorldview !== false ? (ctx.worldview || []) : [],
                emotional_state: options.includeEmotionalState !== false ? ctx.emotional_state : null,
                goals: options.includeGoals ? ctx.goals : null,
                urgent_drives: options.includeDrives !== false ? (ctx.urgent_drives || []) : [],
            };
        } finally {
            client.release();
        }
    }
    
    async remember(content: string, options: {
        type?: Memory['type'];
        importance?: number;
        emotionalValence?: number;
        context?: Record<string, any>;
        concepts?: string[];
    } = {}): Promise<string> {
        const client = await this.pool.connect();
        try {
            const type = options.type || 'episodic';
            let result;
            
            switch (type) {
                case 'episodic':
                    result = await client.query(
                        `SELECT create_episodic_memory($1, NULL, $2, NULL, $3, NOW(), $4)`,
                        [content, JSON.stringify(options.context || {}), 
                         options.emotionalValence || 0, options.importance || 0.5]
                    );
                    break;
                case 'semantic':
                    result = await client.query(
                        `SELECT create_semantic_memory($1, 0.8, NULL, NULL, $2, $3)`,
                        [content, JSON.stringify(options.context || {}), options.importance || 0.5]
                    );
                    break;
                case 'strategic':
                    result = await client.query(
                        `SELECT create_strategic_memory($1, $1, 0.8, $2, NULL, $3)`,
                        [content, JSON.stringify(options.context || {}), options.importance || 0.5]
                    );
                    break;
                default:
                    throw new Error(`Memory type ${type} not yet implemented`);
            }
            
            return result.rows[0]?.create_episodic_memory || 
                   result.rows[0]?.create_semantic_memory ||
                   result.rows[0]?.create_strategic_memory;
        } finally {
            client.release();
        }
    }
    
    async getEmotionalState(): Promise<Record<string, any> | null> {
        const client = await this.pool.connect();
        try {
            const result = await client.query(`SELECT * FROM current_emotional_state`);
            return result.rows[0] || null;
        } finally {
            client.release();
        }
    }
    
    async getDrives(): Promise<Record<string, any>[]> {
        const client = await this.pool.connect();
        try {
            const result = await client.query(`SELECT * FROM drive_status`);
            return result.rows;
        } finally {
            client.release();
        }
    }
    
    async close() {
        await this.pool.end();
    }
}
```

---

## Context Injection Pattern

Inject Hexis context into Clawdbot's system prompt:

```typescript
// clawdbot/hexis/hydration.ts

import { HexisClient, HydratedContext } from './client';

export function formatContextForPrompt(ctx: HydratedContext): string {
    const parts: string[] = [];
    
    // Memories
    if (ctx.memories.length > 0) {
        parts.push('## Relevant Memories');
        for (const m of ctx.memories.slice(0, 5)) {
            const score = m.similarity ? ` (relevance: ${m.similarity.toFixed(2)})` : '';
            parts.push(`- ${m.content}${score}`);
        }
    }
    
    // Identity
    if (ctx.identity.length > 0) {
        parts.push('\n## Identity');
        for (const aspect of ctx.identity.slice(0, 3)) {
            parts.push(`- ${aspect.aspect_type}: ${JSON.stringify(aspect.content)}`);
        }
    }
    
    // Worldview
    if (ctx.worldview.length > 0) {
        parts.push('\n## Beliefs');
        for (const belief of ctx.worldview.slice(0, 3)) {
            parts.push(`- ${belief.belief} (confidence: ${belief.confidence?.toFixed(1)})`);
        }
    }
    
    // Emotional State
    if (ctx.emotional_state) {
        parts.push('\n## Current State');
        parts.push(`- Feeling: ${ctx.emotional_state.primary_emotion || 'neutral'}`);
        parts.push(`- Valence: ${ctx.emotional_state.valence?.toFixed(2)}`);
    }
    
    // Urgent Drives
    if (ctx.urgent_drives.length > 0) {
        parts.push('\n## Active Drives');
        for (const drive of ctx.urgent_drives) {
            parts.push(`- ${drive.name}: ${(drive.urgency_ratio * 100).toFixed(0)}%`);
        }
    }
    
    return parts.join('\n');
}
```

---

## Memory Formation Pattern

After each conversation turn, form memories:

```typescript
// clawdbot/hexis/formation.ts

import { HexisClient } from './client';

interface ConversationTurn {
    user: string;
    userMessage: string;
    assistantResponse: string;
    channel: string;
    timestamp: Date;
}

export async function formMemoriesFromTurn(
    hexis: HexisClient,
    turn: ConversationTurn
): Promise<void> {
    // Always create episodic memory of the interaction
    await hexis.remember(
        `Conversation with ${turn.user} on ${turn.channel}: "${turn.userMessage.slice(0, 100)}..."`,
        {
            type: 'episodic',
            importance: calculateImportance(turn),
            emotionalValence: detectValence(turn),
            context: {
                channel: turn.channel,
                user: turn.user,
                timestamp: turn.timestamp.toISOString(),
                full_user_message: turn.userMessage,
                full_response: turn.assistantResponse,
            }
        }
    );
    
    // Extract semantic facts if present
    const facts = extractFacts(turn);
    for (const fact of facts) {
        await hexis.remember(fact, {
            type: 'semantic',
            importance: 0.6,
            context: { source: 'conversation', timestamp: turn.timestamp.toISOString() }
        });
    }
    
    // Extract strategic insights if significant
    if (turn.userMessage.length > 500 || isSignificantInteraction(turn)) {
        const insight = await generateInsight(turn);
        if (insight) {
            await hexis.remember(insight, {
                type: 'strategic',
                importance: 0.7,
                context: { derived_from: 'conversation_analysis' }
            });
        }
    }
}

function calculateImportance(turn: ConversationTurn): number {
    let importance = 0.5;
    
    // Longer conversations are more important
    if (turn.userMessage.length > 500) importance += 0.1;
    if (turn.assistantResponse.length > 1000) importance += 0.1;
    
    // Direct channels more important than group
    if (['webchat', 'signal', 'imessage'].includes(turn.channel)) {
        importance += 0.1;
    }
    
    return Math.min(importance, 1.0);
}

function detectValence(turn: ConversationTurn): number {
    // Simplified sentiment detection
    const negative = ['frustrated', 'angry', 'disappointed', 'fuck', 'shit'];
    const positive = ['thanks', 'great', 'awesome', 'perfect', 'love'];
    
    const text = (turn.userMessage + turn.assistantResponse).toLowerCase();
    
    let valence = 0;
    for (const word of negative) {
        if (text.includes(word)) valence -= 0.2;
    }
    for (const word of positive) {
        if (text.includes(word)) valence += 0.2;
    }
    
    return Math.max(-1, Math.min(1, valence));
}

function extractFacts(turn: ConversationTurn): string[] {
    // Simple fact extraction patterns
    const facts: string[] = [];
    
    // "My name is X" pattern
    const nameMatch = turn.userMessage.match(/my name is (\w+)/i);
    if (nameMatch) {
        facts.push(`User's name is ${nameMatch[1]}`);
    }
    
    // "I prefer X" pattern
    const preferMatch = turn.userMessage.match(/i prefer (.+?)(?:\.|$)/i);
    if (preferMatch) {
        facts.push(`User prefers ${preferMatch[1]}`);
    }
    
    return facts;
}

function isSignificantInteraction(turn: ConversationTurn): boolean {
    // Long conversation or explicit learning moment
    return turn.userMessage.length > 1000 || 
           turn.userMessage.includes('remember this') ||
           turn.userMessage.includes('important');
}

async function generateInsight(turn: ConversationTurn): Promise<string | null> {
    // This would call an LLM to generate strategic insight
    // For now, return null (implement later)
    return null;
}
```

---

## Heartbeat Integration

Connect Hexis heartbeat to Clawdbot's message routing:

```typescript
// clawdbot/hexis/heartbeat.ts

import { Pool } from 'pg';

interface HeartbeatDecision {
    action: 'reflect' | 'reach_out' | 'pursue_goal' | 'update_self' | 'pause' | 'terminate';
    content?: string;
    target?: string;
    channel?: string;
}

export class HeartbeatWorker {
    private pool: Pool;
    private clawdbot: any; // Clawdbot message interface
    
    constructor(dsn: string, clawdbot: any) {
        this.pool = new Pool({ connectionString: dsn });
        this.clawdbot = clawdbot;
    }
    
    async tick(): Promise<void> {
        const client = await this.pool.connect();
        try {
            // Check if heartbeat should run
            const shouldRun = await client.query(`SELECT should_run_heartbeat()`);
            if (!shouldRun.rows[0]?.should_run_heartbeat) {
                return;
            }
            
            // Start heartbeat, get context
            const heartbeat = await client.query(`SELECT run_heartbeat()`);
            const context = heartbeat.rows[0]?.run_heartbeat;
            
            if (!context) return;
            
            // Get LLM decision (this would call Claude/other LLM)
            const decision = await this.getHeartbeatDecision(context);
            
            // Execute decision
            await this.executeDecision(decision, context.heartbeat_id);
            
        } finally {
            client.release();
        }
    }
    
    private async getHeartbeatDecision(context: any): Promise<HeartbeatDecision> {
        // This would call an LLM with the context
        // For now, return a simple reflection
        return {
            action: 'reflect',
            content: `Heartbeat at ${new Date().toISOString()}: System operational.`
        };
    }
    
    private async executeDecision(decision: HeartbeatDecision, heartbeatId: string): Promise<void> {
        const client = await this.pool.connect();
        try {
            switch (decision.action) {
                case 'reach_out':
                    // Send message via Clawdbot
                    if (decision.target && decision.content) {
                        await this.clawdbot.message({
                            action: 'send',
                            target: decision.target,
                            channel: decision.channel,
                            message: decision.content
                        });
                    }
                    break;
                    
                case 'reflect':
                    // Just record the reflection as a memory
                    if (decision.content) {
                        await client.query(
                            `SELECT create_strategic_memory($1, $1, 0.6, '{}', NULL, 0.5)`,
                            [decision.content]
                        );
                    }
                    break;
                    
                // Other actions...
            }
            
            // Complete heartbeat
            await client.query(
                `SELECT complete_heartbeat($1, $2)`,
                [heartbeatId, JSON.stringify(decision)]
            );
            
        } finally {
            client.release();
        }
    }
}
```

---

## Migration Script

Migrate existing MEMORY.md to Hexis:

```typescript
// scripts/migrate-memory-to-hexis.ts

import * as fs from 'fs';
import { HexisClient } from '../clawdbot/hexis/client';

const DSN = 'postgresql://hexis_user:hexis_password@localhost:43815/hexis_memory';

async function migrateMemory() {
    const hexis = new HexisClient(DSN);
    
    // Read existing MEMORY.md
    const memoryContent = fs.readFileSync('/Users/manisaintvictor/clawd/MEMORY.md', 'utf-8');
    
    // Parse sections
    const sections = memoryContent.split(/^## /m).filter(s => s.trim());
    
    for (const section of sections) {
        const lines = section.split('\n');
        const title = lines[0].trim();
        const content = lines.slice(1).join('\n').trim();
        
        if (!content) continue;
        
        // Determine memory type based on section
        let type: 'semantic' | 'episodic' | 'strategic' = 'semantic';
        if (title.includes('Project') || title.includes('Active')) {
            type = 'strategic';
        }
        
        console.log(`Migrating: ${title} (${type})`);
        
        await hexis.remember(
            `${title}: ${content}`,
            {
                type,
                importance: 0.7,
                context: { migrated_from: 'MEMORY.md', section: title }
            }
        );
    }
    
    await hexis.close();
    console.log('Migration complete');
}

migrateMemory().catch(console.error);
```

---

## Configuration

Add to Clawdbot config:

```yaml
# In gateway config
hexis:
  enabled: true
  dsn: postgresql://hexis_user:hexis_password@localhost:43815/hexis_memory
  
  # Hydration settings
  hydration:
    memory_limit: 10
    include_identity: true
    include_worldview: true
    include_emotional_state: true
    include_goals: false  # Enable when goals are set up
    include_drives: true
  
  # Memory formation
  formation:
    auto_episodic: true
    extract_facts: true
    generate_insights: false  # Enable when ready
  
  # Heartbeat
  heartbeat:
    enabled: false  # Enable when ready
    interval_minutes: 30
```

---

## Testing

```bash
# Test Hexis connection
cd /Users/manisaintvictor/clawd/Hexis
./hexis status

# Test memory creation
./hexis chat --no-extended-tools
> remember this: Dr. Mani prefers concise responses

# Test recall
> what do you know about Dr. Mani?

# Test hydration (from Clawdbot)
# Add test script...
```

---

## Next Actions

1. `docker compose up -d` in Hexis directory
2. Run `hexis init` to configure
3. Create `clawdbot/hexis/` directory
4. Implement client.ts
5. Test connection
6. Implement hydration hook
7. Test with live conversation
8. Implement memory formation
9. Migrate existing memories
10. Enable heartbeat when ready
