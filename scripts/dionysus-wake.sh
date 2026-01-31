#!/bin/bash
# dionysus-wake.sh - Wake-up script for Archimedes (Clawdbot) to hydrate context from Dionysus
#
# Usage: ./scripts/dionysus-wake.sh [project_path] [cues...]
#
# Following Conductor best practices:
# 1. Load constraints, workflow, best-practices
# 2. Reconstruct session context from episodic memory
# 3. Output compact context for injection
#
# Author: Mani Saint-Victor, MD

set -euo pipefail

# Configuration
DIONYSUS_API="${DIONYSUS_API:-http://72.61.78.89:8000}"
PROJECT_PATH="${1:-/Volumes/Asylum/dev/dionysus3-core}"
shift || true
CUES=("$@")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  DIONYSUS WAKE-UP PROTOCOL${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check API health
echo -e "${YELLOW}[1/5] Checking Dionysus API health...${NC}"
HEALTH=$(curl -s --connect-timeout 5 "${DIONYSUS_API}/health" 2>/dev/null || echo '{"status":"unreachable"}')
if echo "$HEALTH" | grep -q '"healthy"'; then
    echo -e "${GREEN}  ✓ API healthy${NC}"
else
    echo -e "${RED}  ✗ API unreachable at ${DIONYSUS_API}${NC}"
    echo -e "${YELLOW}  Continuing with local context only...${NC}"
fi

# Load Conductor files (if project path exists)
echo ""
echo -e "${YELLOW}[2/5] Loading Conductor protocol...${NC}"
if [[ -d "$PROJECT_PATH" ]]; then
    CONSTRAINTS_FILE="${PROJECT_PATH}/.conductor/constraints.md"
    WORKFLOW_FILE="${PROJECT_PATH}/conductor/workflow.md"
    BEST_PRACTICES_FILE="${PROJECT_PATH}/.conductor/best-practices.md"
    
    if [[ -f "$CONSTRAINTS_FILE" ]]; then
        echo -e "${GREEN}  ✓ constraints.md loaded${NC}"
    else
        echo -e "${YELLOW}  ⚠ constraints.md not found${NC}"
    fi
    
    if [[ -f "$WORKFLOW_FILE" ]]; then
        echo -e "${GREEN}  ✓ workflow.md loaded${NC}"
    else
        echo -e "${YELLOW}  ⚠ workflow.md not found${NC}"
    fi
    
    if [[ -f "$BEST_PRACTICES_FILE" ]]; then
        echo -e "${GREEN}  ✓ best-practices.md loaded${NC}"
    else
        echo -e "${YELLOW}  ⚠ best-practices.md not found${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Project path not found: ${PROJECT_PATH}${NC}"
fi

# Check agent roster
echo ""
echo -e "${YELLOW}[3/5] Checking agent roster...${NC}"
AGENTS_DIR="$HOME/.claude/agents"
if [[ -d "$AGENTS_DIR" ]]; then
    AGENT_COUNT=$(find "$AGENTS_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo -e "${GREEN}  ✓ ${AGENT_COUNT} specialized agents available at ~/.claude/agents/${NC}"
else
    echo -e "${YELLOW}  ⚠ Agent roster not found at ~/.claude/agents/${NC}"
fi

# Check skills library
SKILLS_DIR="/Volumes/Asylum/dev/dionysus3-core/skills_library"
if [[ -d "$SKILLS_DIR" ]]; then
    SKILLS=$(ls "$SKILLS_DIR" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
    echo -e "${GREEN}  ✓ Skills library: ${SKILLS}${NC}"
else
    echo -e "${YELLOW}  ⚠ Skills library not found${NC}"
fi

# Reconstruct session context
echo ""
echo -e "${YELLOW}[4/5] Reconstructing session context from episodic memory...${NC}"

# Build cues JSON array
CUES_JSON="[]"
if [[ ${#CUES[@]} -gt 0 ]]; then
    CUES_JSON=$(printf '%s\n' "${CUES[@]}" | jq -R . | jq -s .)
fi

# Call reconstruction endpoint
RECONSTRUCT_RESPONSE=$(curl -s --connect-timeout 10 -X POST "${DIONYSUS_API}/api/session/reconstruct" \
    -H "Content-Type: application/json" \
    -d "{\"project_path\": \"${PROJECT_PATH}\", \"cues\": ${CUES_JSON}}" 2>/dev/null || echo '{"success":false}')

if echo "$RECONSTRUCT_RESPONSE" | grep -q '"success":true'; then
    COHERENCE=$(echo "$RECONSTRUCT_RESPONSE" | jq -r '.coherence_score // 0')
    FRAGMENTS=$(echo "$RECONSTRUCT_RESPONSE" | jq -r '.fragment_count // 0')
    TIME_MS=$(echo "$RECONSTRUCT_RESPONSE" | jq -r '.reconstruction_time_ms // 0' | cut -d. -f1)
    
    echo -e "${GREEN}  ✓ Context reconstructed (coherence: ${COHERENCE}, fragments: ${FRAGMENTS}, ${TIME_MS}ms)${NC}"
    
    # Extract compact context
    COMPACT_CONTEXT=$(echo "$RECONSTRUCT_RESPONSE" | jq -r '.compact_context // ""')
    
    # Extract episodic memories if any
    EPISODIC_COUNT=$(echo "$RECONSTRUCT_RESPONSE" | jq -r '.episodic_memories | length // 0')
    if [[ "$EPISODIC_COUNT" -gt 0 ]]; then
        echo -e "${GREEN}  ✓ ${EPISODIC_COUNT} episodic memories retrieved${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Session reconstruction unavailable${NC}"
    COMPACT_CONTEXT=""
fi

# Output summary
echo ""
echo -e "${YELLOW}[5/5] Wake-up complete.${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Constraints, workflow, and best practices loaded.${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Output compact context if available
if [[ -n "$COMPACT_CONTEXT" ]]; then
    echo ""
    echo -e "${BLUE}--- COMPACT CONTEXT ---${NC}"
    echo "$COMPACT_CONTEXT"
    echo -e "${BLUE}--- END CONTEXT ---${NC}"
fi

# Output JSON for programmatic consumption
if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
    echo ""
    echo '{"wake_up":"complete","api_healthy":true,"conductor_loaded":true,"agents_available":'$AGENT_COUNT'}'
fi
