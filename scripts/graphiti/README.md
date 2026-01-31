# Graphiti Memory Infrastructure for Archimedes

## Overview
This directory contains scripts for ingesting the Analytical Empath Framework into a Neo4j-based temporal knowledge graph using Graphiti.

## Setup Status
- **Neo4j**: Running at `bolt://localhost:7687` (via Graphiti docker-compose)
- **Web UI**: http://localhost:7474
- **Credentials**: neo4j / password

## Architecture

### Why Graphiti over Raw Neo4j?
Graphiti provides:
1. **Temporal awareness** - Tracks when knowledge was added/changed
2. **Episode-based ingestion** - Natural for conversational AI
3. **Semantic search** - Built-in vector embeddings for retrieval
4. **MCP Server** - Direct integration path for Clawdbot

### Schema Design

The Analytical Empath Framework will be ingested as **episodes** with the following entity types:

#### Core Concepts (Nodes)
| Entity Type | Description | Examples |
|-------------|-------------|----------|
| `Concept` | Core theoretical constructs | Triple-Bind Siege, Empathic Override, ACC Atrophy Loop |
| `Mechanism` | How things work | Mirror neuron suppression, False prediction, Filter failure |
| `Intervention` | Actionable protocols | Somatic Ignition Switch, Vital Pause, External Exoskeleton |
| `Symptom` | Observable manifestations | Freeze response, Abandonment cycles, Workspace flooding |
| `Structure` | Brain/cognitive regions | ACC, Anterior insula, Prefrontal cortex |
| `Researcher` | Academic sources | Karl Friston, Russell Barkley, Andy Clark |
| `Theory` | Theoretical frameworks | Predictive Coding, Extended Mind, Point of Performance |

#### Relationships (Edges)
| Relationship | Description |
|--------------|-------------|
| `CAUSES` | A mechanism causes a symptom |
| `ADDRESSES` | An intervention addresses a mechanism/symptom |
| `PART_OF` | Concept is part of larger framework |
| `SUPPORTS` | Theory supports the framework |
| `AUTHORED_BY` | Research attributed to researcher |
| `REQUIRES` | Intervention requires another intervention |
| `MULTIPLIES_WITH` | Binds multiply with each other |

## Files

- `schema.md` - Detailed schema documentation
- `ingest_framework.py` - Python script to ingest framework via Graphiti
- `verify_graph.py` - Script to verify ingestion

## Usage

### Option 1: Via Graphiti MCP Server (Recommended for Clawdbot)
```bash
cd /Volumes/Asylum/repos/graphiti/mcp_server
# Configure for Neo4j backend
cp config/config-docker-neo4j.yaml config.yaml
# Start MCP server
docker compose -f docker/docker-compose-neo4j.yml up
```

### Option 2: Direct Python Script
```bash
cd /Users/manisaintvictor/clawd/scripts/graphiti
pip install graphiti-core neo4j
python ingest_framework.py
```

## Next Steps for Clawdbot Integration

1. **Add Graphiti MCP to Clawdbot's MCP config**
2. **Create ingestion skill** for continuous learning
3. **Build retrieval patterns** for context injection
4. **Test temporal queries** (e.g., "what did we discuss last week?")

## Dependencies
- Neo4j 5.26+
- Python 3.10+
- graphiti-core
- OpenAI API key (for embeddings)
