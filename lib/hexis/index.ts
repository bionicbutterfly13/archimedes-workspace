/**
 * Hexis Integration for Clawdbot
 * 
 * Persistent memory substrate. Context awareness. Proactive heartbeat.
 */

// Client
export { HexisClient, getHexis, initHexis } from './client';

// Types
export type {
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

// Hydration
export {
    formatContextForPrompt,
    formatContextAsXml,
    formatContextCompact,
} from './hydration';

// Memory Formation
export {
    formMemoriesFromTurn,
    calculateImportance,
    ConversationTurn,
} from './formation';

// Heartbeat
export {
    runHeartbeatTick,
    formatHeartbeatPrompt,
    simpleDecider,
    HeartbeatHandler,
} from './heartbeat';
