/**
 * Memory Formation - Store what happened in conversations
 */

import { HexisClient } from './client';
import { MemoryType } from './types';

export interface ConversationTurn {
    user: string;
    userMessage: string;
    assistantResponse: string;
    channel: string;
    timestamp: Date;
}

/**
 * Form memories from a completed conversation turn
 */
export async function formMemoriesFromTurn(
    hexis: HexisClient,
    turn: ConversationTurn,
    options?: {
        alwaysStore?: boolean;
        extractFacts?: boolean;
        minImportance?: number;
    }
): Promise<string[]> {
    const ids: string[] = [];
    const importance = calculateImportance(turn);
    const minImportance = options?.minImportance ?? 0.3;

    // Skip low-importance turns unless forced
    if (importance < minImportance && !options?.alwaysStore) {
        return ids;
    }

    // Create episodic memory of the interaction
    const summary = summarizeTurn(turn);
    const id = await hexis.remember({
        content: summary,
        type: 'episodic',
        importance,
        context: {
            channel: turn.channel,
            user: turn.user,
            timestamp: turn.timestamp.toISOString(),
            message_length: turn.userMessage.length,
            response_length: turn.assistantResponse.length,
        }
    });
    if (id) ids.push(id);

    // Extract and store facts
    if (options?.extractFacts !== false) {
        const facts = extractFacts(turn);
        for (const fact of facts) {
            const factId = await hexis.remember({
                content: fact,
                type: 'semantic',
                importance: 0.6,
                context: {
                    source: 'conversation',
                    extracted_from: id,
                    timestamp: turn.timestamp.toISOString(),
                }
            });
            if (factId) ids.push(factId);
        }
    }

    // Extract action items / todos
    const todos = extractTodos(turn);
    for (const todo of todos) {
        const todoId = await hexis.createGoal(todo);
        if (todoId) ids.push(todoId);
    }

    return ids;
}

/**
 * Calculate importance of a conversation turn
 */
export function calculateImportance(turn: ConversationTurn): number {
    let importance = 0.4; // baseline

    // Length signals significance
    if (turn.userMessage.length > 500) importance += 0.1;
    if (turn.userMessage.length > 1000) importance += 0.1;
    if (turn.assistantResponse.length > 1000) importance += 0.1;

    // Direct channels more important
    if (['webchat', 'signal', 'imessage'].includes(turn.channel)) {
        importance += 0.1;
    }

    // Explicit importance markers
    const text = turn.userMessage.toLowerCase();
    if (text.includes('important') || text.includes('remember this')) {
        importance += 0.2;
    }
    if (text.includes('urgent') || text.includes('priority')) {
        importance += 0.15;
    }

    // Questions about past work
    if (text.includes('we discussed') || text.includes('last time') || text.includes('remember when')) {
        importance += 0.1;
    }

    return Math.min(importance, 1.0);
}

/**
 * Create a brief summary of the turn
 */
function summarizeTurn(turn: ConversationTurn): string {
    // Truncate long messages
    const maxLen = 200;
    let userPart = turn.userMessage;
    if (userPart.length > maxLen) {
        userPart = userPart.slice(0, maxLen) + '...';
    }

    // Extract topic if possible
    const topic = extractTopic(turn.userMessage);
    if (topic) {
        return `${turn.channel}: Discussed ${topic} with ${turn.user}`;
    }

    return `${turn.channel}: ${turn.user} asked about "${userPart}"`;
}

/**
 * Extract factual statements from the conversation
 */
function extractFacts(turn: ConversationTurn): string[] {
    const facts: string[] = [];
    const text = turn.userMessage;

    // "My name is X"
    const nameMatch = text.match(/my name is (\w+)/i);
    if (nameMatch) {
        facts.push(`User's name is ${nameMatch[1]}`);
    }

    // "I prefer X"
    const preferMatch = text.match(/i prefer (.+?)(?:\.|,|$)/i);
    if (preferMatch) {
        facts.push(`${turn.user} prefers ${preferMatch[1].trim()}`);
    }

    // "I'm working on X"
    const workingMatch = text.match(/(?:i'm|i am) working on (.+?)(?:\.|,|$)/i);
    if (workingMatch) {
        facts.push(`${turn.user} is working on ${workingMatch[1].trim()}`);
    }

    // "I like X" / "I don't like X"
    const likeMatch = text.match(/i (don't |do not )?like (.+?)(?:\.|,|$)/i);
    if (likeMatch) {
        const negation = likeMatch[1] ? "doesn't" : "";
        facts.push(`${turn.user} ${negation} likes ${likeMatch[2].trim()}`);
    }

    // "Remember that X"
    const rememberMatch = text.match(/remember (?:that |this: )?(.+?)(?:\.|$)/i);
    if (rememberMatch && !rememberMatch[1].match(/^(when|what|how|why)/i)) {
        facts.push(rememberMatch[1].trim());
    }

    return facts;
}

/**
 * Extract todos/action items from the conversation
 */
function extractTodos(turn: ConversationTurn): string[] {
    const todos: string[] = [];
    const text = turn.userMessage + ' ' + turn.assistantResponse;

    // "TODO: X" or "To do: X"
    const todoMatches = text.matchAll(/(?:todo|to do|action item)[:\s]+(.+?)(?:\.|,|$)/gi);
    for (const match of todoMatches) {
        todos.push(match[1].trim());
    }

    // "Need to X"
    const needMatches = text.matchAll(/(?:we |i )?need to (.+?)(?:\.|,|$)/gi);
    for (const match of needMatches) {
        const item = match[1].trim();
        if (item.length > 10 && item.length < 100) {
            todos.push(item);
        }
    }

    // "Don't forget to X"
    const forgetMatches = text.matchAll(/don't forget (?:to )?(.+?)(?:\.|,|$)/gi);
    for (const match of forgetMatches) {
        todos.push(match[1].trim());
    }

    return todos.slice(0, 3); // Max 3 todos per turn
}

/**
 * Try to extract the main topic from a message
 */
function extractTopic(text: string): string | null {
    // Look for "about X" patterns
    const aboutMatch = text.match(/(?:tell me |help (?:me )?with |working on |need help with )(.+?)(?:\.|,|\?|$)/i);
    if (aboutMatch) {
        const topic = aboutMatch[1].trim();
        if (topic.length > 3 && topic.length < 50) {
            return topic;
        }
    }

    // Look for question patterns
    const questionMatch = text.match(/(?:what|how|why|when|where|can you) (?:is |are |do |does |can |should )?(.+?)(?:\?|$)/i);
    if (questionMatch) {
        const topic = questionMatch[1].trim();
        if (topic.length > 3 && topic.length < 50) {
            return topic;
        }
    }

    return null;
}
