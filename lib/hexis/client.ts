/**
 * Hexis Client - Persistent memory substrate for Clawdbot
 * 
 * Stripped down. No philosophy. Just memory and awareness.
 */

import { Pool, PoolClient } from 'pg';
import {
    Memory,
    MemoryType,
    MemoryInput,
    Drive,
    Goal,
    HydratedContext,
    HeartbeatContext,
    HeartbeatDecision,
    HexisConfig,
} from './types';

export class HexisClient {
    private pool: Pool;
    private config: HexisConfig;

    constructor(config: HexisConfig) {
        this.config = config;
        this.pool = new Pool({ connectionString: config.dsn });
    }

    // =========================================================================
    // HYDRATION - Get context before each turn
    // =========================================================================

    async hydrate(query: string, options?: {
        memoryLimit?: number;
        includeDrives?: boolean;
        includeGoals?: boolean;
    }): Promise<HydratedContext> {
        const client = await this.pool.connect();
        try {
            const limit = options?.memoryLimit ?? this.config.hydration?.memoryLimit ?? 10;

            // Get relevant memories
            const memories = await this.recallMemories(client, query, limit);

            // Get drives if requested
            let drives: Drive[] = [];
            if (options?.includeDrives ?? this.config.hydration?.includeDrives) {
                drives = await this.getDrives(client);
            }

            // Get goals if requested
            let goals: Goal[] = [];
            if (options?.includeGoals ?? this.config.hydration?.includeGoals) {
                goals = await this.getActiveGoals(client);
            }

            // Get pending work items
            const pendingWork = await this.getPendingWork(client);

            return { memories, drives, goals, pendingWork };
        } finally {
            client.release();
        }
    }

    // =========================================================================
    // MEMORY - Store what happened
    // =========================================================================

    async remember(input: MemoryInput): Promise<string> {
        const client = await this.pool.connect();
        try {
            const type = input.type ?? 'episodic';
            const importance = input.importance ?? 0.5;
            const context = input.context ?? {};

            let result: any;
            switch (type) {
                case 'episodic':
                    result = await client.query(
                        `SELECT create_episodic_memory($1, NULL, $2::jsonb, NULL, 0, NOW(), $3) as id`,
                        [input.content, JSON.stringify(context), importance]
                    );
                    break;
                case 'semantic':
                    result = await client.query(
                        `SELECT create_semantic_memory($1, 0.8, NULL, NULL, $2::jsonb, $3) as id`,
                        [input.content, JSON.stringify(context), importance]
                    );
                    break;
                case 'strategic':
                    result = await client.query(
                        `SELECT create_strategic_memory($1, $1, 0.8, $2::jsonb, NULL, $3) as id`,
                        [input.content, JSON.stringify(context), importance]
                    );
                    break;
                case 'goal':
                    result = await client.query(
                        `SELECT create_goal($1, $2, 'user_request', 'queued', NULL, NULL) as id`,
                        [input.content, input.context?.description ?? null]
                    );
                    break;
                default:
                    result = await client.query(
                        `SELECT create_semantic_memory($1, 0.8, NULL, NULL, $2::jsonb, $3) as id`,
                        [input.content, JSON.stringify(context), importance]
                    );
            }

            return result.rows[0]?.id;
        } finally {
            client.release();
        }
    }

    async rememberBatch(inputs: MemoryInput[]): Promise<string[]> {
        const ids: string[] = [];
        for (const input of inputs) {
            const id = await this.remember(input);
            if (id) ids.push(id);
        }
        return ids;
    }

    // =========================================================================
    // RECALL - Get relevant memories
    // =========================================================================

    async recall(query: string, limit: number = 10): Promise<Memory[]> {
        const client = await this.pool.connect();
        try {
            return this.recallMemories(client, query, limit);
        } finally {
            client.release();
        }
    }

    async recallRecent(limit: number = 10, type?: MemoryType): Promise<Memory[]> {
        const client = await this.pool.connect();
        try {
            const result = await client.query(
                `SELECT memory_id as id, memory_type as type, content, importance, created_at
                 FROM list_recent_memories($1, $2::memory_type[], false)`,
                [limit, type ? [type] : null]
            );
            return result.rows.map(this.rowToMemory);
        } finally {
            client.release();
        }
    }

    // =========================================================================
    // HEARTBEAT - Autonomous reflection
    // =========================================================================

    async shouldRunHeartbeat(): Promise<boolean> {
        const client = await this.pool.connect();
        try {
            const result = await client.query(`SELECT should_run_heartbeat() as should_run`);
            return result.rows[0]?.should_run ?? false;
        } finally {
            client.release();
        }
    }

    async getHeartbeatContext(): Promise<HeartbeatContext | null> {
        const client = await this.pool.connect();
        try {
            const result = await client.query(`SELECT run_heartbeat() as context`);
            const ctx = result.rows[0]?.context;
            if (!ctx) return null;

            return {
                heartbeat_id: ctx.heartbeat_id,
                heartbeat_number: ctx.heartbeat_number,
                energy: ctx.energy?.current ?? 0,
                max_energy: ctx.energy?.max ?? 100,
                drives: (ctx.drives ?? []).map((d: any) => ({
                    name: d.name,
                    level: d.current_level,
                    urgency: d.urgency_ratio ?? d.current_level / 0.8,
                })),
                goals: (ctx.goals?.active ?? []).map((g: any) => ({
                    id: g.id,
                    title: g.title,
                    priority: g.priority,
                    progress: g.progress,
                })),
                recent_memories: (ctx.recent_memories ?? []).map(this.rowToMemory),
                pending_work: ctx.pending_work ?? [],
            };
        } finally {
            client.release();
        }
    }

    async applyHeartbeatDecision(
        heartbeatId: string,
        decision: HeartbeatDecision
    ): Promise<void> {
        const client = await this.pool.connect();
        try {
            await client.query(
                `SELECT apply_heartbeat_decision($1::uuid, $2::jsonb, 0)`,
                [heartbeatId, JSON.stringify(decision)]
            );
        } finally {
            client.release();
        }
    }

    // =========================================================================
    // GOALS - What we're working on
    // =========================================================================

    async createGoal(title: string, description?: string): Promise<string> {
        const client = await this.pool.connect();
        try {
            const result = await client.query(
                `SELECT create_goal($1, $2, 'user_request', 'active', NULL, NULL) as id`,
                [title, description ?? null]
            );
            return result.rows[0]?.id;
        } finally {
            client.release();
        }
    }

    async completeGoal(goalId: string): Promise<void> {
        const client = await this.pool.connect();
        try {
            await client.query(
                `UPDATE memories SET metadata = jsonb_set(COALESCE(metadata, '{}'::jsonb), '{priority}', '"completed"')
                 WHERE id = $1 AND type = 'goal'`,
                [goalId]
            );
        } finally {
            client.release();
        }
    }

    // =========================================================================
    // DRIVES - Priority weights
    // =========================================================================

    async getDriveLevels(): Promise<Drive[]> {
        const client = await this.pool.connect();
        try {
            return this.getDrives(client);
        } finally {
            client.release();
        }
    }

    async satisfyDrive(name: string, amount: number = 0.3): Promise<void> {
        const client = await this.pool.connect();
        try {
            await client.query(`SELECT satisfy_drive($1, $2)`, [name, amount]);
        } finally {
            client.release();
        }
    }

    // =========================================================================
    // OPERATOR CONTROLS
    // =========================================================================

    async setControl(key: string, value: any): Promise<void> {
        const client = await this.pool.connect();
        try {
            await client.query(
                `SELECT set_operator_control($1, $2::jsonb)`,
                [key, JSON.stringify(value)]
            );
        } finally {
            client.release();
        }
    }

    async getControls(): Promise<Record<string, any>> {
        const client = await this.pool.connect();
        try {
            const result = await client.query(`SELECT key, value FROM operator_controls`);
            const controls: Record<string, any> = {};
            for (const row of result.rows) {
                controls[row.key.replace('operator.', '')] = row.value;
            }
            return controls;
        } finally {
            client.release();
        }
    }

    // =========================================================================
    // LIFECYCLE
    // =========================================================================

    async close(): Promise<void> {
        await this.pool.end();
    }

    async ping(): Promise<boolean> {
        const client = await this.pool.connect();
        try {
            await client.query('SELECT 1');
            return true;
        } catch {
            return false;
        } finally {
            client.release();
        }
    }

    // =========================================================================
    // INTERNALS
    // =========================================================================

    private async recallMemories(client: PoolClient, query: string, limit: number): Promise<Memory[]> {
        const result = await client.query(
            `SELECT memory_id as id, content, memory_type as type, score as similarity, importance, created_at
             FROM fast_recall($1, $2)`,
            [query, limit]
        );
        return result.rows.map(this.rowToMemory);
    }

    private async getDrives(client: PoolClient): Promise<Drive[]> {
        const result = await client.query(
            `SELECT name, current_level as level, current_level / urgency_threshold as urgency
             FROM drives
             ORDER BY current_level DESC`
        );
        return result.rows;
    }

    private async getActiveGoals(client: PoolClient): Promise<Goal[]> {
        const result = await client.query(
            `SELECT * FROM get_goals_by_priority('active')`
        );
        return result.rows.map((r: any) => ({
            id: r.id,
            title: r.title,
            priority: r.priority,
            progress: r.progress,
        }));
    }

    private async getPendingWork(client: PoolClient): Promise<string[]> {
        const result = await client.query(
            `SELECT content FROM memories 
             WHERE type = 'goal' 
             AND (metadata->>'priority') IN ('active', 'queued')
             ORDER BY importance DESC
             LIMIT 5`
        );
        return result.rows.map((r: any) => r.content);
    }

    private rowToMemory(row: any): Memory {
        return {
            id: row.id,
            type: row.type,
            content: row.content,
            importance: parseFloat(row.importance),
            similarity: row.similarity ? parseFloat(row.similarity) : undefined,
            created_at: row.created_at,
        };
    }
}

// Singleton instance
let _instance: HexisClient | null = null;

export function getHexis(config?: HexisConfig): HexisClient {
    if (!_instance && config) {
        _instance = new HexisClient(config);
    }
    if (!_instance) {
        throw new Error('Hexis not initialized. Call getHexis(config) first.');
    }
    return _instance;
}

export async function initHexis(dsn: string): Promise<HexisClient> {
    _instance = new HexisClient({ dsn });
    const ok = await _instance.ping();
    if (!ok) {
        throw new Error('Cannot connect to Hexis database');
    }
    return _instance;
}
