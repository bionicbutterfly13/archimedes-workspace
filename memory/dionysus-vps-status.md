# Dionysus VPS Stack Status

**Updated:** 2026-01-30 05:55 UTC

## ✅ Issue 1: dionysus-api Unhealthy - FIXED

### Root Causes (Multiple)
1. **NEO4J_URI incorrect**: Was `bolt://localhost:7687`, changed to `bolt://neo4j:7687`
2. **Race condition on startup**: `start_journal_scheduler()` and `warmup()` both tried to initialize Graphiti simultaneously, causing a deadlock
3. **RelatioNarrativeService None**: Import failed (spacy unavailable) but code tried to instantiate it anyway

### Fixes Applied
1. Changed `NEO4J_URI=bolt://neo4j:7687` in `~/dionysus-api/.env`
2. Added 30-second startup delay in `api/services/journal_service.py`:
   ```python
   async def start_journal_scheduler():
       # Delay first update to allow other startup tasks (warmup, etc.) to complete
       await asyncio.sleep(30)  # Wait 30 seconds before first update
       ...
   ```
3. Fixed `api/main.py` line 66:
   ```python
   relatio_svc = RelatioNarrativeService() if RelatioNarrativeService else None
   ```

### Current Status
```
dionysus-api    Up X minutes (healthy)
```

Health endpoint: `http://localhost:8000/health` returns:
```json
{
  "status": "healthy",
  "service": "dionysus-core",
  "meta_tot_thresholds": {...}
}
```

## ✅ Issue 2: Graphiti Embedding Dimension Mismatch - NOT REPRODUCED

### Investigation
- Checked all embeddings in Neo4j: All `name_embedding` fields are **1536 dimensions**
- Config values:
  - `EMBEDDINGS_PROVIDER=openai`
  - `OPENAI_EMBED_MODEL=text-embedding-3-small`
  - `EMBEDDING_DIM=1536`
- `text-embedding-3-small` produces 1536 dimensions by default ✓

### Testing
- **Search endpoint**: ✅ Working (`/api/graphiti/search`)
- **Ingest endpoint**: ✅ Working (`/api/graphiti/ingest`)

### Conclusion
The dimension mismatch error was either:
1. A transient issue that resolved itself
2. Caused by a stale Graphiti client that was using different embedding settings
3. The container restart (with proper Neo4j connectivity) reinitialized everything correctly

If the error reoccurs, the fix would be:
```bash
# Option A: Reset Neo4j vector indexes (if dimensions changed)
docker exec neo4j cypher-shell -u neo4j -p Mmsm2280 \
  "DROP INDEX entity_name_embedding IF EXISTS"

# Option B: If old vectors have wrong dimensions, clear them
docker exec neo4j cypher-shell -u neo4j -p Mmsm2280 \
  "MATCH (n:Entity) REMOVE n.name_embedding"
```

## Container Overview
```
NAMES           STATUS          PORTS
dionysus-api    Up (healthy)    0.0.0.0:8000->8000/tcp
dionysus-docs   Up (healthy)    0.0.0.0:3000->3000/tcp
graphiti        Up (healthy)    0.0.0.0:8001->8001/tcp
n8n             Up              127.0.0.1:5678->5678/tcp
neo4j           Up              127.0.0.1:7474->7474/tcp, 127.0.0.1:7687->7687/tcp
ollama          Up              127.0.0.1:11434->11434/tcp
```

## Files Modified on VPS
- `~/dionysus-api/.env` - Changed NEO4J_URI
- `~/dionysus-api/api/services/journal_service.py` - Added startup delay
- `~/dionysus-api/api/main.py` - Fixed RelatioNarrativeService conditional
