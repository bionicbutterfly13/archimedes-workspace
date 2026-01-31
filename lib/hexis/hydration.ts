/**
 * Context Hydration - Inject relevant memories into prompts
 */

import { HydratedContext, Memory, Drive, Goal } from './types';

/**
 * Format hydrated context for injection into system prompt
 */
export function formatContextForPrompt(ctx: HydratedContext, options?: {
    maxMemories?: number;
    maxGoals?: number;
    showDrives?: boolean;
}): string {
    const parts: string[] = [];
    const maxMemories = options?.maxMemories ?? 5;
    const maxGoals = options?.maxGoals ?? 3;
    const showDrives = options?.showDrives ?? true;

    // Relevant memories
    if (ctx.memories.length > 0) {
        parts.push('## Relevant Context');
        for (const m of ctx.memories.slice(0, maxMemories)) {
            const score = m.similarity ? ` (${(m.similarity * 100).toFixed(0)}% match)` : '';
            parts.push(`- ${m.content}${score}`);
        }
    }

    // Active goals
    if (ctx.goals.length > 0) {
        parts.push('');
        parts.push('## Active Work');
        for (const g of ctx.goals.slice(0, maxGoals)) {
            const progress = g.progress ? ` [${g.progress}]` : '';
            parts.push(`- ${g.title}${progress}`);
        }
    }

    // Pending work
    if (ctx.pendingWork.length > 0) {
        parts.push('');
        parts.push('## Pending');
        for (const item of ctx.pendingWork.slice(0, 3)) {
            parts.push(`- ${item}`);
        }
    }

    // Drives (as attention hints)
    if (showDrives && ctx.drives.length > 0) {
        const urgent = ctx.drives.filter(d => d.urgency > 0.8);
        if (urgent.length > 0) {
            parts.push('');
            parts.push('## Attention');
            for (const d of urgent) {
                parts.push(`- High ${d.name} (${(d.level * 100).toFixed(0)}%)`);
            }
        }
    }

    return parts.join('\n');
}

/**
 * Format context as XML block (alternative format)
 */
export function formatContextAsXml(ctx: HydratedContext): string {
    const parts: string[] = ['<context>'];

    if (ctx.memories.length > 0) {
        parts.push('  <memories>');
        for (const m of ctx.memories.slice(0, 5)) {
            parts.push(`    <memory type="${m.type}">${escapeXml(m.content)}</memory>`);
        }
        parts.push('  </memories>');
    }

    if (ctx.goals.length > 0) {
        parts.push('  <goals>');
        for (const g of ctx.goals.slice(0, 3)) {
            parts.push(`    <goal priority="${g.priority}">${escapeXml(g.title)}</goal>`);
        }
        parts.push('  </goals>');
    }

    if (ctx.pendingWork.length > 0) {
        parts.push('  <pending>');
        for (const item of ctx.pendingWork.slice(0, 3)) {
            parts.push(`    <item>${escapeXml(item)}</item>`);
        }
        parts.push('  </pending>');
    }

    parts.push('</context>');
    return parts.join('\n');
}

/**
 * Create a compact one-line summary of context
 */
export function formatContextCompact(ctx: HydratedContext): string {
    const pieces: string[] = [];

    if (ctx.memories.length > 0) {
        pieces.push(`${ctx.memories.length} relevant memories`);
    }

    if (ctx.goals.length > 0) {
        pieces.push(`${ctx.goals.length} active goals`);
    }

    if (ctx.pendingWork.length > 0) {
        pieces.push(`${ctx.pendingWork.length} pending items`);
    }

    const urgent = ctx.drives.filter(d => d.urgency > 0.8);
    if (urgent.length > 0) {
        pieces.push(`high ${urgent.map(d => d.name).join(', ')}`);
    }

    return pieces.length > 0 ? `[Context: ${pieces.join(', ')}]` : '';
}

function escapeXml(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
