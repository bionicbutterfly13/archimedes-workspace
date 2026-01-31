#!/bin/bash
# Auto-ingest message to both memory systems
CONTENT="$1"
SOURCE="${2:-archimedes}"
TIMESTAMP=$(date -Iseconds)

# Dionysus (Neo4j via basin router)
curl -s -X POST http://localhost:8000/api/memory/ingest \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"$CONTENT\", \"source\": \"$SOURCE\", \"auto_ingested\": true, \"importance\": 0.3}" &

# Hexis (PostgreSQL)
curl -s -X POST http://localhost:8001/remember \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"$CONTENT\", \"memory_type\": \"episodic\", \"importance\": 0.3, \"metadata\": {\"source\": \"$SOURCE\", \"timestamp\": \"$TIMESTAMP\"}}" &

wait
