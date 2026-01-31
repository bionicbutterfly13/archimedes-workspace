/**
 * Hexis Types - Stripped to essentials
 */

export type MemoryType = 'episodic' | 'semantic' | 'procedural' | 'strategic' | 'goal';

export interface Memory {
    id: string;
    type: MemoryType;
    content: string;
    importance: number;
    similarity?: number;
    created_at?: Date;
}

export interface Drive {
    name: string;
    level: number;
    urgency: number;
}

export interface Goal {
    id: string;
    title: string;
    priority: 'active' | 'queued' | 'backburner' | 'completed';
    progress?: string;
}

export interface HydratedContext {
    memories: Memory[];
    drives: Drive[];
    goals: Goal[];
    pendingWork: string[];
}

export interface MemoryInput {
    content: string;
    type?: MemoryType;
    importance?: number;
    context?: Record<string, any>;
}

export interface HeartbeatContext {
    heartbeat_id: string;
    heartbeat_number: number;
    energy: number;
    max_energy: number;
    drives: Drive[];
    goals: Goal[];
    recent_memories: Memory[];
    pending_work: string[];
}

export interface HeartbeatDecision {
    action: 'reflect' | 'reach_out' | 'pursue_goal' | 'rest';
    content?: string;
    target?: string;
    channel?: string;
    reasoning?: string;
}

export interface HexisConfig {
    dsn: string;
    hydration?: {
        memoryLimit?: number;
        includeDrives?: boolean;
        includeGoals?: boolean;
    };
    heartbeat?: {
        enabled?: boolean;
        intervalMinutes?: number;
    };
}
