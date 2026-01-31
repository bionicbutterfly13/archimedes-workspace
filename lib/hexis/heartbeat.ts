/**
 * Heartbeat - Autonomous periodic reflection and action
 * 
 * The ghost wakes up, looks around, decides what to do.
 */

import { HexisClient } from './client';
import { HeartbeatContext, HeartbeatDecision } from './types';

export interface HeartbeatHandler {
    /**
     * Called when heartbeat decides to reach out
     */
    onReachOut?: (target: string, message: string, channel?: string) => Promise<void>;
    
    /**
     * Called when heartbeat decides to reflect (optional logging)
     */
    onReflect?: (content: string) => void;
    
    /**
     * Called when heartbeat decides to pursue a goal
     */
    onPursueGoal?: (goalId: string, goalTitle: string) => Promise<void>;
}

/**
 * Run a single heartbeat tick
 * 
 * Returns true if heartbeat ran, false if skipped
 */
export async function runHeartbeatTick(
    hexis: HexisClient,
    decider: (ctx: HeartbeatContext) => Promise<HeartbeatDecision>,
    handler: HeartbeatHandler
): Promise<boolean> {
    // Check if we should run
    if (!await hexis.shouldRunHeartbeat()) {
        return false;
    }

    // Get context
    const ctx = await hexis.getHeartbeatContext();
    if (!ctx) {
        return false;
    }

    // Get decision from LLM (or other decider)
    const decision = await decider(ctx);

    // Execute decision
    await executeDecision(hexis, ctx, decision, handler);

    // Record decision
    await hexis.applyHeartbeatDecision(ctx.heartbeat_id, decision);

    return true;
}

/**
 * Execute a heartbeat decision
 */
async function executeDecision(
    hexis: HexisClient,
    ctx: HeartbeatContext,
    decision: HeartbeatDecision,
    handler: HeartbeatHandler
): Promise<void> {
    switch (decision.action) {
        case 'reach_out':
            if (decision.target && decision.content && handler.onReachOut) {
                await handler.onReachOut(decision.target, decision.content, decision.channel);
            }
            // Satisfy connection drive
            await hexis.satisfyDrive('connection', 0.3);
            break;

        case 'reflect':
            if (decision.content) {
                // Store reflection as strategic memory
                await hexis.remember({
                    content: decision.content,
                    type: 'strategic',
                    importance: 0.5,
                    context: {
                        source: 'heartbeat_reflection',
                        heartbeat: ctx.heartbeat_number,
                    }
                });
                handler.onReflect?.(decision.content);
            }
            // Satisfy coherence drive
            await hexis.satisfyDrive('coherence', 0.2);
            break;

        case 'pursue_goal':
            if (decision.content && handler.onPursueGoal) {
                // Find the goal
                const goals = ctx.goals.filter(g => 
                    g.title.toLowerCase().includes(decision.content!.toLowerCase())
                );
                if (goals.length > 0) {
                    await handler.onPursueGoal(goals[0].id, goals[0].title);
                }
            }
            // Satisfy competence drive
            await hexis.satisfyDrive('competence', 0.2);
            break;

        case 'rest':
            // Just rest, satisfy rest drive
            await hexis.satisfyDrive('rest', 0.4);
            break;
    }
}

/**
 * Format heartbeat context for LLM decision
 */
export function formatHeartbeatPrompt(ctx: HeartbeatContext): string {
    const parts: string[] = [];

    parts.push(`Heartbeat #${ctx.heartbeat_number}`);
    parts.push(`Energy: ${ctx.energy}/${ctx.max_energy}`);
    parts.push('');

    // Drives
    if (ctx.drives.length > 0) {
        parts.push('## Current Drives');
        for (const d of ctx.drives) {
            const urgencyLabel = d.urgency > 0.8 ? ' [HIGH]' : d.urgency > 0.6 ? ' [medium]' : '';
            parts.push(`- ${d.name}: ${(d.level * 100).toFixed(0)}%${urgencyLabel}`);
        }
        parts.push('');
    }

    // Active goals
    if (ctx.goals.length > 0) {
        parts.push('## Active Goals');
        for (const g of ctx.goals) {
            parts.push(`- ${g.title}`);
        }
        parts.push('');
    }

    // Pending work
    if (ctx.pending_work.length > 0) {
        parts.push('## Pending Work');
        for (const item of ctx.pending_work) {
            parts.push(`- ${item}`);
        }
        parts.push('');
    }

    // Recent memories
    if (ctx.recent_memories.length > 0) {
        parts.push('## Recent Activity');
        for (const m of ctx.recent_memories.slice(0, 3)) {
            parts.push(`- ${m.content}`);
        }
        parts.push('');
    }

    parts.push('## Available Actions');
    parts.push('- reflect: Think about something, store insight');
    parts.push('- reach_out: Send a message to someone');
    parts.push('- pursue_goal: Work on an active goal');
    parts.push('- rest: Do nothing, recharge');

    return parts.join('\n');
}

/**
 * Simple decision logic (no LLM required)
 * 
 * Use this for basic automated heartbeat behavior.
 */
export function simpleDecider(ctx: HeartbeatContext): HeartbeatDecision {
    // If very low energy, rest
    if (ctx.energy < 10) {
        return { action: 'rest', reasoning: 'Low energy, need to recharge' };
    }

    // Find most urgent drive
    const urgent = ctx.drives.filter(d => d.urgency > 0.8);
    
    if (urgent.length === 0) {
        // Nothing urgent, just reflect
        return { 
            action: 'reflect', 
            content: `Heartbeat ${ctx.heartbeat_number}: All systems nominal.`,
            reasoning: 'No urgent drives' 
        };
    }

    // Handle based on most urgent drive
    const mostUrgent = urgent.reduce((a, b) => a.urgency > b.urgency ? a : b);

    switch (mostUrgent.name) {
        case 'curiosity':
            // If we have goals, work on one
            if (ctx.goals.length > 0) {
                return {
                    action: 'pursue_goal',
                    content: ctx.goals[0].title,
                    reasoning: `High curiosity, pursuing goal: ${ctx.goals[0].title}`
                };
            }
            return {
                action: 'reflect',
                content: 'Curiosity is high but no clear direction. Waiting for input.',
                reasoning: 'High curiosity but no goals'
            };

        case 'connection':
            // Would reach out, but need a target
            // In practice, this would check for users to contact
            return {
                action: 'reflect',
                content: 'Connection drive is high. Ready to engage when opportunity arises.',
                reasoning: 'High connection drive'
            };

        case 'coherence':
            return {
                action: 'reflect',
                content: 'Taking a moment to organize thoughts and ensure consistency.',
                reasoning: 'High coherence drive'
            };

        case 'rest':
            return { action: 'rest', reasoning: 'Rest drive is high' };

        default:
            return { action: 'rest', reasoning: 'Default action' };
    }
}
