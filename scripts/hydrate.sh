#!/bin/bash
# Hydrate context from both memory systems
QUERY="$1"
LIMIT="${2:-5}"

echo "=== MEMORY CONTEXT ==="
echo ""

# Query Hexis (PostgreSQL vector search)
echo "## Hexis (Semantic Memory)"
HEXIS_RESULT=$(curl -s -X POST http://localhost:8001/recall \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"limit\": $LIMIT}" 2>/dev/null)

echo "$HEXIS_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for m in data.get('memories', [])[:$LIMIT]:
        print(f\"- [{m.get('type','?')}] {m.get('content','')} (relevance: {m.get('similarity',0):.0%})\")
except: pass
" 2>/dev/null

echo ""
echo "## Dionysus (Graph Context)"
# Query Dionysus for related concepts
DIONYSUS_RESULT=$(curl -s -X POST http://localhost:8000/api/graphiti/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"limit\": $LIMIT}" 2>/dev/null)

echo "$DIONYSUS_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for edge in data.get('edges', [])[:$LIMIT]:
        print(f\"- {edge.get('fact', edge)}\")
except: pass
" 2>/dev/null

echo ""
echo "=== END CONTEXT ==="
