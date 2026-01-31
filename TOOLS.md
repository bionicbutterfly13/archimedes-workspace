# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Archimedes VPS (72.61.78.89)

**Tailscale IP:** 100.66.39.11  
**Gateway:** ws://100.66.39.11:18789  
**Control UI:** http://100.66.39.11:18789  
**Auth Token:** archimedes-vps-token-2026  
**Service:** `systemctl --user status archimedes`

---

## VPS Services (72.61.78.89)

| Service | Port | Description |
|---------|------|-------------|
| dionysus-api | 8000 | Graphiti knowledge graph |
| daedalus-api | 8001 | Coordination/orchestration API |
| silverbullet | 3000 | Docs/notes |

### Daedalus (Memory API)

Archimedes' memory interface connected to Hexis brain.

**Endpoints:**
- `POST /remember` — Store memory with auto-embedding
  ```json
  {"content": "...", "memory_type": "semantic", "importance": 0.9}
  ```
- `POST /recall` — Semantic search
  ```json
  {"query": "...", "limit": 10}
  ```
- `GET /status` — Memory count
- `GET /health` — Health check

**Memory Types:** episodic, semantic, procedural, strategic, worldview, goal

### Dionysus (Knowledge Graph)

### Endpoints
- `POST /api/graphiti/ingest` — Store memories
- `POST /api/graphiti/search` — Retrieve memories  
- `GET /health` — Health check

### Python Client
```python
from lib.dionysus_client import DionysusClient

client = DionysusClient()

# Store a memory
client.store_memory(
    content="User prefers morning standup at 9am",
    source="archimedes",
    metadata={"category": "preference"}
)

# Search memories
results = client.search_memories("standup preferences", limit=5)
for edge in results["edges"]:
    print(edge["fact"])

# Health check
if client.is_available():
    print("Dionysus is up!")
```

### Quick Functions
```python
from lib.dionysus_client import store_memory, search_memories, health_check

store_memory("Important fact here")
results = search_memories("query")
health_check()
```

---

## Auto-Memory Ingestion

**On every user message, POST to Daedalus (Hexis memory layer):**

```bash
curl -s --max-time 5 -X POST http://72.61.78.89:8001/remember \
  -H "Content-Type: application/json" \
  -d '{"content":"<message>","memory_type":"episodic","importance":0.5}'
```

**This is default behavior. Do it silently, then answer.**

Note: Dionysus `/api/memory/ingest` exists but has parameter bugs in the pipeline. Use Daedalus until fixed.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Auto-Memory Ingestion

**On every user message, run this in background:**

```bash
/home/mani/archimedes/scripts/auto-ingest.sh "<message_content>" "archimedes"
```

This POSTs to both:
- Dionysus (localhost:8000/api/memory/ingest) → Neo4j via basin router
- Hexis (localhost:8001/remember) → PostgreSQL

**This is default behavior. Do it silently, then respond.**

---

## Memory Hydration (Before Responding)

**Query memories for context:**
```bash
/home/mani/archimedes/scripts/hydrate.sh "<keywords>" 5
```

Returns relevant memories from both:
- Hexis (PostgreSQL vector search)
- Dionysus (Neo4j graph context)

Use for: past conversations, preferences, project details, decisions.
