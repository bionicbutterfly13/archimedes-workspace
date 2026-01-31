# Hexis + Dionysus Unified Memory & Cognition Architecture
## Comprehensive Researcher Guide

**Audience:** Researchers and external collaborators  
**Purpose:** In-depth, code-anchored reference for the complete cognitive memory stack  
**Systems Covered:** Hexis (PostgreSQL brain), Dionysus 3.0 (Python services), AutoSchemaKG, Nemori, Graphiti, MemEvolve, attractor basins, episodic/semantic/procedural memory, OODA, heartbeat, working memory, Consciousness Manager, thoughtseeds, neuronal packets, and mental models  
**Last updated:** 2026-01-30

---

## Architecture Overview: Two Brains, One Mind

The system comprises two complementary cognitive engines:

| System | Role | Storage | Philosophy |
|--------|------|---------|------------|
| **Hexis** | PostgreSQL-native cognitive core | PostgreSQL + pgvector + Apache AGE | "Database as Brain" — SQL functions own state and logic |
| **Dionysus 3.0** | Python orchestration layer | Neo4j (Graphiti) + in-memory caches | Services for extraction, active inference, consciousness |

**Integration Point:** **Daedalus API** (port 8001) bridges Archimedes (the agent) to Hexis brain; Dionysus services handle complex extraction, active inference, and consciousness management.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Agent / User Input                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          ▼                                                   ▼
┌─────────────────────────┐                     ┌─────────────────────────────┐
│      Daedalus API       │                     │   Memory Basin Router       │
│   (Hexis Interface)     │                     │   (Dionysus Classifier)     │
│   Port 8001             │                     │                             │
│   /remember, /recall    │                     │ • Classifies memory type    │
└─────────────────────────┘                     │ • Activates attractor basin │
          │                                     │ • Routes to extraction      │
          ▼                                     └─────────────────────────────┘
┌─────────────────────────┐                                   │
│     Hexis Brain         │                     ┌─────────────┴─────────────┐
│   (PostgreSQL)          │                     ▼                           ▼
│                         │           ┌─────────────────┐         ┌─────────────────┐
│ • memories table        │           │     Nemori      │         │  MemEvolve      │
│ • episodes table        │           │  (Episodic)     │         │  (Semantic)     │
│ • working_memory        │           │  River Flow     │         │  Adapter        │
│ • goals system          │           └─────────────────┘         └─────────────────┘
│ • SQL cognitive funcs   │                     │                           │
└─────────────────────────┘                     └───────────┬───────────────┘
          │                                                 ▼
          │                                     ┌─────────────────────────────┐
          │                                     │      Graphiti Service       │
          │                                     │   (Temporal Knowledge Graph)│
          │                                     │         Neo4j               │
          │                                     └─────────────────────────────┘
          │                                                 │
          └─────────────────────────────────────────────────┘
                              Unified Long-Term Memory
```

---

## 1. Hexis: The PostgreSQL Brain

### 1.1 Design Philosophy

From `Hexis/docs/architecture.md`:

> 1. The database owns state and logic. Application code is transport, orchestration, and I/O.
> 2. The contract surface is SQL functions that return JSON.
> 3. Long-term knowledge is stored as memories. Anything the agent should know must be represented in `memories`.
> 4. Heartbeat logic lives in SQL functions. The worker is a scheduler and LLM executor, not a decision-maker.

### 1.2 Core Memory Schema (Hexis)

**Source:** `Hexis/db/00_tables.sql`

```sql
-- Memory Types (Hexis)
CREATE TYPE memory_type AS ENUM (
    'episodic',    -- Events, conversations, experiences
    'semantic',    -- Facts, knowledge, information
    'procedural',  -- How-to, processes, methods
    'strategic',   -- Plans, approaches, patterns
    'worldview',   -- Beliefs, values, perspectives
    'goal'         -- Objectives with priority tracking
);

CREATE TYPE memory_status AS ENUM (
    'active',      -- Currently valid and retrievable
    'archived',    -- Preserved but deprioritized
    'invalidated'  -- Superseded or contradicted
);

-- Main memories table
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    type memory_type NOT NULL,
    status memory_status DEFAULT 'active',
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,      -- pgvector for semantic search
    importance DOUBLE PRECISION DEFAULT 0.5,
    source_attribution JSONB NOT NULL DEFAULT '{}',
    trust_level DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    trust_updated_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    decay_rate DOUBLE PRECISION DEFAULT 0.01,
    metadata JSONB NOT NULL DEFAULT '{}'
);

-- Indexes for retrieval
CREATE INDEX idx_memories_embedding ON memories 
    USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_memories_importance ON memories (importance DESC) 
    WHERE status = 'active';
CREATE INDEX idx_memories_type ON memories (type);
```

### 1.3 Episodes in Hexis

**Source:** `Hexis/db/00_tables.sql`, `Hexis/db/91_triggers.sql`

```sql
CREATE TABLE episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    summary TEXT,
    summary_embedding vector(768),
    metadata JSONB NOT NULL DEFAULT '{}',
    time_range TSTZRANGE GENERATED ALWAYS AS (
        tstzrange(started_at, COALESCE(ended_at, 'infinity'))
    ) STORED
);

-- Auto-assignment trigger (1:1 memory:episode mapping)
CREATE OR REPLACE FUNCTION assign_to_episode()
RETURNS trigger AS $$
DECLARE
    current_episode_id UUID;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext('episode_manager'));
    
    -- Close any open episode
    UPDATE episodes SET ended_at = CURRENT_TIMESTAMP WHERE ended_at IS NULL;
    
    -- Create new episode for each memory
    INSERT INTO episodes (started_at, ended_at, metadata)
    VALUES (NEW.created_at, NEW.created_at, 
            jsonb_build_object('episode_type', 'message'))
    RETURNING id INTO current_episode_id;
    
    PERFORM link_memory_to_episode_graph(NEW.id, current_episode_id, 1);
    INSERT INTO memory_neighborhoods (memory_id, is_stale)
    VALUES (NEW.id, TRUE) ON CONFLICT DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_episode_assignment
    AFTER INSERT ON memories
    FOR EACH ROW EXECUTE FUNCTION assign_to_episode();
```

### 1.4 Working Memory (Hexis)

**Source:** `Hexis/db/00_tables.sql`

```sql
-- UNLOGGED for speed; ephemeral by design
CREATE UNLOGGED TABLE working_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    importance DOUBLE PRECISION DEFAULT 0.3,
    source_attribution JSONB NOT NULL DEFAULT '{}',
    trust_level DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    promote_to_long_term BOOLEAN NOT NULL DEFAULT FALSE,
    expiry TIMESTAMPTZ
);

-- Promotion criteria (from config)
-- maintenance.working_memory_promote_min_importance = 0.75
-- maintenance.working_memory_promote_min_accesses = 3
```

### 1.5 Goal System (Hexis)

**Source:** `Hexis/db/07_functions_heartbeat.sql`, `Hexis/db/08_functions_goals.sql`

```sql
CREATE TYPE goal_priority AS ENUM (
    'active',     -- Currently working on (max 3)
    'queued',     -- Next up
    'backburner', -- Parked for later
    'completed',
    'abandoned'
);

CREATE TYPE goal_source AS ENUM (
    'curiosity',     -- Self-generated
    'user_request',  -- User asked
    'identity',      -- Core to agent identity
    'derived',       -- From other goals
    'external'       -- Outside input
);

-- Key goal functions
CREATE OR REPLACE FUNCTION create_goal(
    p_title TEXT,
    p_description TEXT DEFAULT NULL,
    p_source goal_source DEFAULT 'curiosity',
    p_priority goal_priority DEFAULT 'queued',
    p_parent_id UUID DEFAULT NULL,
    p_due_at TIMESTAMPTZ DEFAULT NULL
) RETURNS UUID;

CREATE OR REPLACE FUNCTION change_goal_priority(
    p_goal_id UUID,
    p_new_priority goal_priority,
    p_reason TEXT DEFAULT NULL
) RETURNS VOID;

CREATE OR REPLACE FUNCTION add_goal_progress(
    p_goal_id UUID,
    p_note TEXT
) RETURNS VOID;

CREATE OR REPLACE FUNCTION get_goals_by_priority(
    p_priority goal_priority DEFAULT NULL
) RETURNS TABLE (...);
```

### 1.6 Daedalus API (Hexis Interface)

**Source:** `Hexis/api/main.py`

**Base URL:** `http://72.61.78.89:8001`

```python
# Hexis/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import httpx

app = FastAPI(title="Daedalus API", description="Memory interface for Archimedes")

DATABASE_URL = "postgresql://hexis_user:hexis_password@db:5432/hexis_memory"
EMBEDDINGS_URL = "http://hexis_embeddings:80/embed"

class MemoryInput(BaseModel):
    content: str
    memory_type: str = "semantic"
    importance: float = 0.5
    metadata: dict = {}

class SearchInput(BaseModel):
    query: str
    limit: int = 10

async def get_embedding(text: str) -> List[float]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(EMBEDDINGS_URL, json={"inputs": text})
        return resp.json()[0]

@app.post("/remember")
async def remember(memory: MemoryInput):
    embedding = await get_embedding(memory.content)
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        memory_id = uuid.uuid4()
        await conn.execute("""
            INSERT INTO memories (id, type, content, embedding, importance, 
                source_attribution, trust_level, metadata)
            VALUES ($1, $2::memory_type, $3, $4::vector, $5, $6::jsonb, $7, $8::jsonb)
        """, memory_id, memory.memory_type, memory.content, 
            str(embedding), memory.importance, 
            json.dumps({"source": "archimedes", "via": "daedalus-api"}),
            0.8, json.dumps(memory.metadata))
        return {"stored": True, "id": str(memory_id)}
    finally:
        await conn.close()

@app.post("/recall")
async def recall(search: SearchInput):
    query_embedding = await get_embedding(search.query)
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch("""
            SELECT id, content, type::text, importance, 
                   1 - (embedding <=> $1::vector) as similarity
            FROM memories WHERE status = 'active'
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """, str(query_embedding), search.limit)
        return {"memories": [dict(r) for r in rows]}
    finally:
        await conn.close()
```

---

## 2. Dionysus 3.0: Python Orchestration Layer

### 2.1 High-Level Data Flow

```
Agent / User Input
        │
        ▼
┌──────────────────────────────────────────────────────────────────┐
│     Memory Basin Router (api/services/memory_basin_router.py)    │
│  • Classifies memory type: EPISODIC | SEMANTIC | PROCEDURAL |    │
│    STRATEGIC                                                     │
│  • Activates attractor basin (Hopfield-style)                    │
│  • Routes content to basin-aware extraction & storage            │
└──────────────────────────────────────────────────────────────────┘
        │
        ├── Episodic flow ──► Nemori (episode construction, predict–calibrate)
        │                      → DevelopmentEpisode, DevelopmentEvent
        │                      → Graphiti (facts) + MemEvolve (trajectories)
        │
        ├── Semantic / Procedural / Strategic ──► MemEvolve Adapter
        │                      → GraphitiService (extract, persist)
        │                      → Neo4j (Graphiti)
        │
        └── Schema induction ──► AutoSchemaKG
                              → Inferred concepts, triplets → Graphiti
```

### 2.2 Memory Types and Basin Mapping (Dionysus)

**Source:** `api/models/sync.py`, `api/services/memory_basin_router.py`

```python
# api/models/sync.py
class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    STRATEGIC = "strategic"

# api/services/memory_basin_router.py
BASIN_MAPPING: Dict[MemoryType, Dict[str, Any]] = {
    MemoryType.EPISODIC: {
        "basin_name": "experiential-basin",
        "description": "Time-tagged personal experiences and events",
        "concepts": ["experience", "event", "timeline", "context", "memory"],
        "default_strength": 0.7,
        "extraction_focus": "temporal context and personal significance",
    },
    MemoryType.SEMANTIC: {
        "basin_name": "conceptual-basin",
        "description": "Facts, relationships, and conceptual knowledge",
        "concepts": ["concept", "fact", "relationship", "definition", "knowledge"],
        "default_strength": 0.8,
        "extraction_focus": "entities, relationships, and factual accuracy",
    },
    MemoryType.PROCEDURAL: {
        "basin_name": "procedural-basin",
        "description": "How-to knowledge and skill-based patterns",
        "concepts": ["procedure", "skill", "step", "technique", "method"],
        "default_strength": 0.75,
        "extraction_focus": "action sequences, dependencies, and execution order",
    },
    MemoryType.STRATEGIC: {
        "basin_name": "strategic-basin",
        "description": "Planning patterns and decision frameworks",
        "concepts": ["strategy", "goal", "plan", "decision", "tradeoff"],
        "default_strength": 0.85,
        "extraction_focus": "goals, constraints, tradeoffs, and optimization criteria",
    },
}
```

### 2.3 Unified Memory Type Comparison

| Type | Hexis Role | Dionysus Role | Storage |
|------|------------|---------------|---------|
| **Episodic** | `memories` table with `type='episodic'`; episodes table | Nemori (DevelopmentEpisode/Event); predict–calibrate | Both: Hexis memories + Graphiti facts |
| **Semantic** | `memories` table with `type='semantic'` | GraphitiService extract; MemEvolve trajectories | Both: Hexis + Neo4j entities/facts |
| **Procedural** | `memories` table with `type='procedural'` | Basin router with procedural extraction focus | Both: Hexis + Graphiti |
| **Strategic** | `memories` table with `type='strategic'` | SubconsciousService observations | Both systems |
| **Worldview** | `memories` table with `type='worldview'` (Hexis only) | — | Hexis |
| **Goal** | `memories` table with `type='goal'` + goal functions | — | Hexis |

---

## 3. Attractor Basin Architecture

### 3.1 Concept

Attractor basins are **content-dependent attractors** in a Hopfield-like state space. They bias which concepts and extraction focus are used when processing new content.

### 3.2 Hopfield Network Implementation

**Source:** `api/services/attractor_basin_service.py`

```python
class HopfieldNetwork:
    """
    Hopfield Network for attractor basin dynamics.
    
    Stores patterns as attractors in a weight matrix.
    Input states evolve to nearest stored pattern (attractor basin).
    
    Properties:
    - Zero-bias networks have paired attractors (s* and -s*)
    - Adding bias breaks symmetry, enabling unique attractors
    """
    
    def __init__(self, n_units: int):
        self.n_units = n_units
        self.weights = np.zeros((n_units, n_units))
        self.biases = np.zeros(n_units)
    
    def store_pattern(self, pattern: np.ndarray, degree: int = 1):
        """
        Store pattern as attractor.
        
        Args:
            pattern: Binary pattern (-1/+1) to store
            degree: Multiplicity of storage (higher = stronger attractor)
        """
        # Hebbian learning rule with degree multiplier
        self.weights += degree * np.outer(pattern, pattern) / self.n_units
        np.fill_diagonal(self.weights, 0)  # No self-connections
        
    def recall(self, probe: np.ndarray, max_iterations: int = 100) -> np.ndarray:
        """Run network dynamics until convergence to attractor"""
        state = probe.copy()
        for _ in range(max_iterations):
            new_state = np.sign(self.weights @ state + self.biases)
            if np.array_equal(new_state, state):
                break
            state = new_state
        return state
    
    def energy(self, state: np.ndarray) -> float:
        """Calculate Hopfield energy (stored patterns are minima)"""
        return -0.5 * state @ self.weights @ state - self.biases @ state
```

### 3.3 Basin Service

```python
class AttractorBasinService:
    """High-level service for attractor basin operations"""
    
    def __init__(self, n_units: int = 128):
        self.n_units = n_units
        self.network = HopfieldNetwork(n_units)
        self.basins: Dict[str, BasinState] = {}
    
    def _content_to_pattern(self, content: str) -> np.ndarray:
        """Hash-based deterministic encoding → binary pattern (-1/+1)"""
        content_hash = hashlib.sha256(content.encode()).digest()
        bits = np.unpackbits(np.frombuffer(content_hash[:self.n_units // 8], dtype=np.uint8))
        return 2 * bits[:self.n_units].astype(float) - 1
    
    async def create_basin(self, name: str, seed_content: str, 
                          metadata: Optional[Dict] = None) -> BasinState:
        pattern = self._content_to_pattern(seed_content)
        self.network.store_pattern(pattern)
        basin = BasinState(
            name=name, pattern=pattern,
            energy=self.network.energy(pattern),
            activation=1.0, stability=1.0,
            metadata=metadata or {}
        )
        self.basins[name] = basin
        return basin
    
    async def find_nearest_basin(self, query_content: str) -> Optional[ConvergenceResult]:
        """Find which basin the query content converges to"""
        query_pattern = self._content_to_pattern(query_content)
        converged_pattern = self.network.recall(query_pattern)
        
        # Find matching basin
        for name, basin in self.basins.items():
            if np.array_equal(converged_pattern, basin.pattern):
                return ConvergenceResult(
                    basin_name=name,
                    converged=True,
                    iterations=...,
                    final_energy=self.network.energy(converged_pattern)
                )
        return None
```

### 3.4 Basin Activation in Router

```python
# api/services/memory_basin_router.py
async def _activate_basin(self, basin_name: str, content: str) -> str:
    """Activate basin: MERGE in Neo4j, strengthen on match"""
    create_cypher = """
    MERGE (b:AttractorBasin {name: $name})
    ON CREATE SET 
        b.description = $description,
        b.concepts = $concepts,
        b.strength = $strength,
        b.activation_count = 1,
        b.created_at = datetime()
    ON MATCH SET 
        b.strength = CASE WHEN b.strength < 2.0 
                         THEN b.strength + 0.05 
                         ELSE b.strength END,
        b.activation_count = b.activation_count + 1,
        b.last_activated = datetime()
    RETURN b.concepts as concepts, b.description as description
    """
    # Execute via MemEvolve adapter (Graphiti)
    # Return basin context string for extraction guidance
```

---

## 4. AutoSchemaKG

### 4.1 Role

AutoSchemaKG **induces schemas from episodes**: turns raw entities/events/relations into **hierarchical concepts** and stores them as contextual triplets in Graphiti.

**Source:** `api/services/consciousness/autoschemakg_integration.py`

```python
class AutoSchemaKGIntegration:
    async def infer_schema(
        self,
        episode_id: str,
        content: Optional[str] = None,
        entities: Optional[List[Dict[str, Any]]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        relations: Optional[List[Dict[str, Any]]] = None,
    ) -> SchemaInferenceResult:
        """
        Infer schema from episode content.
        
        Process:
        1. Process pre-extracted entities → infer entity concept → triplet
        2. Process events → infer event concept → triplet
        3. Process relations → infer relation concept → triplet
        4. Store triplets via Graphiti
        """
        # Implementation...
```

### 4.2 Schema Context Retrieval

```python
# api/services/context_packaging.py
async def fetch_schema_context(
    query: str, 
    budget_manager: TokenBudgetManager
) -> Optional[SchemaContextCell]:
    """Retrieve schema context for RAG augmentation"""
    svc = get_autoschemakg_service()
    concepts = await svc.retrieve_relevant_concepts(query)
    # Package as SchemaContextCell (HIGH priority)
    return SchemaContextCell(concepts=concepts, priority=Priority.HIGH)
```

---

## 5. Nemori (Episodic "River" Flow)

### 5.1 Dual-System Episodic Memory

Episodic memory exists in **both** systems:

| System | Implementation | Granularity |
|--------|----------------|-------------|
| **Hexis** | `memories` table + `episodes` table + trigger | 1:1 memory:episode mapping |
| **Dionysus** | Nemori DevelopmentEpisode/Event | Narrative episodes with predict–calibrate |

### 5.2 Nemori Architecture

**Source:** `api/services/nemori_river_flow.py`

```python
class DevelopmentEvent:
    """Atomic unit of experience"""
    id: UUID
    content: str
    timestamp: datetime
    emotional_valence: float  # -1 to 1
    arousal: float            # 0 to 1
    metadata: dict

class DevelopmentEpisode:
    """Aggregated events forming a coherent narrative unit"""
    id: UUID
    title: str
    summary: str
    narrative: str
    archetype: str  # Narrative pattern (e.g., "hero's journey", "resolution")
    events: List[DevelopmentEvent]
```

### 5.3 Predict–Calibrate (Active Inference)

```python
# api/services/nemori_river_flow.py
async def predict_and_calibrate(
    self,
    episode: DevelopmentEpisode,
    original_events: List[DevelopmentEvent],
    basin_context: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Active inference: predict → compare → calibrate.
    
    Process:
    1. Build prediction prompt from episode narrative
    2. LLM predicts semantic facts that should be confirmed
    3. Calibrate predictions vs actual logs
    4. Output: new_facts, symbolic_residue, surprisal
    5. If surprisal > 0.6: trigger_evolution() (MemEvolve)
    6. For each new_fact: route_memory + graphiti.persist_fact
    """
    # Predict what should be true
    predictions = await self._generate_predictions(episode)
    
    # Compare with actual evidence
    calibration = await self._calibrate_predictions(predictions, original_events)
    
    # Extract new facts with confidence scores
    new_facts = calibration['verified_facts']
    surprisal = calibration['surprisal']
    
    # High surprisal triggers schema evolution
    if surprisal > 0.6:
        await self.memevolve_adapter.trigger_evolution(
            episode_id=episode.id,
            surprisal=surprisal
        )
    
    # Persist each fact
    for fact in new_facts:
        await self.router.route_memory(
            content=fact['content'],
            memory_type=MemoryType.SEMANTIC
        )
        await self.graphiti.persist_fact(
            content=fact['content'],
            confidence=fact['confidence'],
            valid_at=datetime.now(),
            source_episode_id=episode.id
        )
    
    return new_facts, calibration['symbolic_residue']
```

### 5.4 Nemori Bridge (Episodic ↔ Semantic)

The **Nemori Bridge** connects episodic and semantic systems:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Integration Layer (Nemori Bridge)            │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
    ┌───────────────┘                           └───────────────┐
    ▼                                                           ▼
┌─────────────────────┐                         ┌─────────────────────┐
│   Episodic System   │                         │   Semantic System   │
│      (Nemori)       │                         │     (MemEvolve)     │
│                     │                         │                     │
│ DevelopmentEvent ───┼─── Promote ────────────►│ TrajectoryData      │
│ DevelopmentEpisode  │                         │ Entity              │
│                     │    Distill ────────────►│ Fact                │
└─────────────────────┘                         └─────────────────────┘
```

**Promotion (Episode → Trajectory):**
```python
adapter = get_memevolve_adapter()
await adapter.ingest_trajectory(
    query=episode.title,
    observation=episode.summary,
    thought=episode.narrative,
    action=episode.archetype
)
```

**Distillation (Episode → Facts):**
```python
graphiti = await get_graphiti_service()
await graphiti.persist_fact(
    content=fact_content,
    confidence=prediction_confidence,
    valid_at=timestamp,
    source_episode_id=episode.id
)
```

---

## 6. Graphiti and MemEvolve Adapter

### 6.1 Graphiti (Temporal Knowledge Graph)

**Source:** `api/services/graphiti_service.py`

Graphiti is the **only authorized path to Neo4j** (Gateway Protocol):

```python
class GraphitiService:
    async def ingest_message(self, content: str, source_id: str):
        """Raw text → LLM extraction → entities + relationships → store"""
        
    async def extract_with_context(
        self, 
        content: str, 
        basin_context: Optional[str] = None,
        strategy_context: Optional[str] = None
    ) -> ExtractionResult:
        """Basin-aware extraction with confidence scoring"""
        
    async def persist_fact(
        self,
        content: str,
        confidence: float,
        valid_at: datetime,
        source_episode_id: UUID
    ) -> UUID:
        """Create Fact node with bi-temporal validity"""
        
    async def execute_cypher(
        self, 
        statement: str, 
        parameters: Dict
    ) -> List[Dict]:
        """Single authorized Cypher path (with destruction gate)"""
```

### 6.2 MemEvolve Adapter

**Source:** `api/services/memevolve_adapter.py`

```python
class MemEvolveAdapter:
    """Main orchestration gateway for memory operations"""
    
    async def execute_cypher(self, statement: str, parameters: Dict = None):
        """Delegate to Graphiti"""
        graphiti = await self._get_graphiti_service()
        return await graphiti.execute_cypher(statement, parameters)
    
    async def extract_with_context(self, content: str, **kwargs):
        """Basin-aware extraction via Graphiti"""
        graphiti = await self._get_graphiti_service()
        return await graphiti.extract_with_context(content, **kwargs)
    
    async def ingest_trajectory(
        self, 
        query: str, 
        observation: str, 
        thought: str, 
        action: str
    ):
        """Store trajectory (narrative unit) in graph"""
        
    async def trigger_evolution(self, episode_id: UUID, surprisal: float):
        """High surprisal triggers schema evolution"""
```

---

## 7. OODA Loop and Heartbeat

### 7.1 Dual Heartbeat Systems

| System | Implementation | Cycle |
|--------|----------------|-------|
| **Hexis** | SQL functions (`run_heartbeat`, `execute_heartbeat_actions_batch`) | DB-driven with energy budget |
| **Dionysus** | `HeartbeatService` + `ConsciousnessManager` | Python orchestration |

### 7.2 Hexis Heartbeat Actions

**Source:** `Hexis/db/07_functions_heartbeat.sql`

```sql
CREATE TYPE heartbeat_action AS ENUM (
    'observe',              -- Gather context (free)
    'review_goals',         -- Check goals (free)
    'remember',             -- Store to LTM (free)
    'recall',               -- Retrieve (cost: 1)
    'connect',              -- Create relationships (cost: 1)
    'reprioritize',         -- Adjust goals (cost: 1)
    'reflect',              -- Internal reflection (cost: 2)
    'contemplate',          -- Deliberate on belief (cost: 1)
    'meditate',             -- Quiet reflection (cost: 1)
    'study',                -- Structured learning (cost: 2)
    'debate_internally',    -- Internal dialectic (cost: 2)
    'maintain',             -- Update beliefs (cost: 2)
    'mark_turning_point',   -- Flag significant moment (cost: 2)
    'begin_chapter',        -- Start narrative chapter (cost: 3)
    'close_chapter',        -- End chapter (cost: 3)
    'synthesize',           -- Generate conclusion (cost: 3)
    'reach_out_user',       -- Contact user (cost: 5)
    'reach_out_public',     -- Public outreach (cost: 7)
    'pause_heartbeat',      -- Temporary pause (free)
    'rest'                  -- Bank energy (free)
);

-- Heartbeat energy budget
-- heartbeat.max_energy = 20
-- heartbeat.base_regeneration = 10
```

### 7.3 Dionysus OODA Implementation

**Source:** `api/services/heartbeat_service.py`

```python
class HeartbeatService:
    async def heartbeat(self) -> HeartbeatSummary:
        # Phase 1: Initialize
        energy = await self._get_energy()
        
        # Phase 2: OBSERVE
        observe_result = await self._action_executor.execute(
            ActionRequest(action_type=ActionType.OBSERVE)
        )
        environment = EnvironmentSnapshot.from_observation(observe_result)
        
        # Phase 3: ORIENT (build context, run ConsciousnessManager)
        context = await self._build_context(environment)
        
        # Phase 4: DECIDE (LLM decision with energy constraints)
        decision = await self._make_decision(context, energy)
        
        # Phase 5: ACT (execute plan)
        results = await self._execute_actions(decision.actions)
        
        # Record episodic memory
        await self._record_heartbeat_memory(decision, results)
        
        # Update working memory
        cache = get_working_memory_cache()
        is_boundary, boundary_event = await cache.update(
            observation=environment.to_dict(),
            energy_level=energy,
            surprisal=calculate_surprisal(results)
        )
        
        if is_boundary and boundary_event:
            await self.autobiographical_service.record_event(boundary_event)
        
        return HeartbeatSummary(...)
```

---

## 8. Working Memory

### 8.1 Hexis Working Memory

Fast, ephemeral storage with promotion rules:

```sql
-- UNLOGGED table (fast but not crash-safe)
CREATE UNLOGGED TABLE working_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    importance DOUBLE PRECISION DEFAULT 0.3,
    access_count INTEGER DEFAULT 0,
    promote_to_long_term BOOLEAN DEFAULT FALSE,
    expiry TIMESTAMPTZ
);

-- Promotion on expiry
-- If importance >= 0.75 OR access_count >= 3 → promote to memories
```

### 8.2 Dionysus Working Memory (CEO Model)

**Source:** `api/services/working_memory_cache.py`

```python
class WorkingMemoryCache:
    """
    CEO model working memory:
    - Object Cache: MetacognitiveParticles (bounded by Miller's Law 7±2)
    - Event Cache: Recent DevelopmentEvents
    - Central Executive: External loop (heartbeat/ConsciousnessManager)
    """
    
    def __init__(self):
        self._object_cache: Dict[str, MetacognitiveParticle] = {}
        self._event_cache: List[DevelopmentEvent] = []
        self._max_objects = 7  # Miller's Law
        self._max_events = 3
        self._boundary_threshold = 0.7
    
    async def update(
        self, 
        observation: dict, 
        energy_level: float, 
        surprisal: float,
        new_particles: List[MetacognitiveParticle] = None
    ) -> Tuple[bool, Optional[DevelopmentEvent]]:
        """
        Update working memory state.
        
        Returns: (is_boundary, boundary_event)
        """
        # 1. Add new particles, apply decay, prune excess
        for particle in (new_particles or []):
            await self.add_particle(particle)
        
        self._apply_decay()
        self._prune_inactive()
        
        # 2. Cerebellar fast-path correction
        await self._cerebellar_correction(surprisal, energy_level)
        
        # 3. Boundary detection
        is_boundary = surprisal > self._boundary_threshold
        event = None
        
        if is_boundary:
            event = DevelopmentEvent(
                content=str(observation),
                emotional_valence=self._compute_valence(),
                arousal=surprisal
            )
            self._event_cache.append(event)
            self._event_cache = self._event_cache[-self._max_events:]
        
        return is_boundary, event
    
    async def add_particle(self, particle: MetacognitiveParticle):
        """Add particle; persist to Graphiti if high resonance"""
        self._object_cache[particle.id] = particle
        
        if particle.resonance_score >= 0.8:
            await self._persist_to_graphiti(particle)
        
        # Enforce Miller's Law
        while len(self._object_cache) > self._max_objects:
            self._evict_lowest_resonance()
```

---

## 9. Consciousness Manager and Thoughtseeds

### 9.1 Thoughtseed Hierarchy

Based on Kavi et al. (2025) "From Neuronal Packets to Thoughtseeds":

```
Layer 0: Neuronal Packets (NPs)         # 50-200ms population spikes
    ↓
Layer 1: Superordinate Ensembles (SEs)  # Coordinated NP groups
    ↓
Layer 2: Neuronal Packet Domains (NPDs) # Specialized cognitive areas
    ↓
Layer 3: Knowledge Domains (KDs)        # Semantic organization
    ↓
Layer 4: Thoughtseeds (TSs)             # Discrete cognitive units
    ↓
Layer 5: Active Thoughtseeds Pool       # Competition arena
    ↓
Layer 6: Dominant Thoughtseed           # Current consciousness content
    ↓
Layer 7: Meta-cognition                 # Higher-order control
    ↓
Layer 8: Agent-Level Integration        # Global goals/policies
```

### 9.2 Neuronal Packet Model

**Source:** `api/models/autobiographical.py`

```python
class PacketDynamics(BaseModel):
    """
    Neuronal Packet (50-200ms population spike) as atomic cognitive unit.
    
    Implements quantization of cognitive streams for:
    - Event segmentation
    - Active inference
    - Entropy/surprisal calculation
    """
    id: UUID
    state: Literal['unmanifested', 'manifested', 'activated']
    alpha_core: float      # Core attractor activation [0, 1]
    alpha_sub: List[float] # Subordinate attractor activations
    binding_energy: float  # Energy barrier for state transition
    knowledge: dict        # Encapsulated knowledge
    created_at: datetime
```

### 9.3 Metacognitive Particles (Runtime Thoughtseeds)

**Source:** `api/models/metacognitive_particle.py`

```python
class MetacognitiveParticle(BaseModel):
    """
    Runtime instantiation of thoughtseed concept.
    
    These are the "packets" that compete for working memory.
    """
    id: str
    content: str
    source_agent: str  # Which agent produced this
    resonance_score: float = 0.0  # Activation level [0, 1]
    is_active: bool = True
    precision: float = 1.0  # Confidence/reliability
    entropy: float = 0.0    # Uncertainty
    created_at: datetime = Field(default_factory=datetime.now)
    
    def decay(self, rate: float = 0.1) -> None:
        """Apply temporal decay to resonance"""
        self.resonance_score = max(0.0, self.resonance_score * (1.0 - rate))
        if self.resonance_score < 0.05:
            self.is_active = False
    
    def reinforce(self, amount: float = 0.2) -> None:
        """Strengthen resonance (attention/access)"""
        self.resonance_score = min(1.0, self.resonance_score + amount)
```

### 9.4 Active Inference & Free Energy Selection

**Source:** `api/services/active_inference_service.py`, `api/services/efe_engine.py`

```python
async def calculate_surprisal(context: dict) -> float:
    """
    Calculate prediction error (surprisal) for active inference.
    
    Free Energy Principle:
    F = Complexity + Accuracy
    F = D_KL[q(s)||p(s)] - E_q[log p(o|s)]
    """
    # Complexity: KL divergence from prior beliefs
    complexity = kl_divergence(
        posterior=context['current_beliefs'],
        prior=context['prior_beliefs']
    )
    
    # Accuracy: Log-likelihood of observations
    accuracy = log_likelihood(
        observations=context['sensory_input'],
        model=context['generative_model']
    )
    
    return complexity - accuracy

async def select_dominant_thoughtseed(
    active_pool: List[ThoughtSeed],
    consciousness_state: str,
    arousal: float
) -> ThoughtSeed:
    """
    Winner-take-all selection via free energy minimization.
    
    A_pool(t) = {TS_m | α_m(t) ≥ τ_activation}
    TS_dominant = argmin_{TS_m ∈ A_pool} F_m
    """
    # Dynamic threshold based on arousal
    tau = calculate_activation_threshold(consciousness_state, arousal)
    
    # Filter to active pool
    active = [ts for ts in active_pool if ts.activation >= tau]
    
    # Select by minimum free energy
    return min(active, key=lambda ts: ts.free_energy)
```

### 9.5 Consciousness Manager

**Source:** `api/agents/consciousness_manager.py`

```python
class ConsciousnessManager:
    """
    Runs one OODA cycle using managed agents.
    Produces MetacognitiveParticle and adds to WorkingMemoryCache.
    """
    
    def __init__(self, model_id: str = "dionysus-agents"):
        self.particle_store = get_working_memory_cache()
        self.perception_wrapper = ManagedPerceptionAgent(model_id)
        self.reasoning_wrapper = ManagedReasoningAgent(model_id)
        self.metacognition_wrapper = ManagedMetacognitionAgent(model_id)
    
    async def run_cycle(self, input_context: dict) -> MetacognitiveParticle:
        """
        Execute one consciousness cycle:
        1. Perception: Process sensory input
        2. Reasoning: Generate thoughts/plans
        3. Metacognition: Evaluate and score
        4. Output: MetacognitiveParticle → working memory
        """
        # Perception
        percept = await self.perception_wrapper.perceive(input_context)
        
        # Reasoning
        thought = await self.reasoning_wrapper.reason(percept)
        
        # Metacognition
        evaluation = await self.metacognition_wrapper.evaluate(thought)
        
        # Synthesize particle
        particle = MetacognitiveParticle(
            content=thought.content,
            source_agent="consciousness_manager",
            resonance_score=evaluation.confidence,
            precision=evaluation.precision,
            entropy=evaluation.entropy
        )
        
        # Add to working memory
        await self.particle_store.add_particle(particle)
        
        return particle
```

---

## 10. Mental Models

### 10.1 Structure

Mental models are persistent predictive structures:

```python
class MentalModel:
    """Predictive model of an entity/concept"""
    id: UUID
    name: str
    entity_type: str  # person, system, concept
    beliefs: List[Belief]
    predictions: List[Prediction]
    confidence: float
    last_updated: datetime

class Belief:
    content: str
    confidence: float
    evidence_ids: List[UUID]  # Supporting memories

class Prediction:
    condition: str    # "If X..."
    outcome: str      # "Then Y..."
    confidence: float
    verification_count: int
```

### 10.2 Model Updates via Prediction Error

```python
async def update_mental_model(
    model_id: UUID,
    observation: str,
    predicted: str
) -> dict:
    """
    Update mental model based on prediction error.
    
    High prediction error triggers:
    - Decrease confidence in prediction
    - Store episodic memory of mismatch
    - Queue for potential belief revision
    """
    error = calculate_prediction_error(observation, predicted)
    
    if error > REVISION_THRESHOLD:
        await flag_for_revision(model_id, observation, predicted, error)
        
    return {'error': error, 'revised': error > REVISION_THRESHOLD}
```

---

## 11. MoSAEIC Protocol

### 11.1 Overview

**M**indful **o**bservation of **S**enses, **A**ctions, **E**motions, **I**mpulses, **C**ognitions

A 5-phase therapeutic protocol for belief reconsolidation:

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | **Interrupt** | Detect maladaptive pattern |
| 2 | **Data Capture** | 5-window observation |
| 3 | **Prediction Error** | Generate cognitive dissonance |
| 4 | **Rewrite** | Update belief during reconsolidation window |
| 5 | **Verification** | Track new belief activation |

### 11.2 Five-Window Data Model

| Window | Content | Neural Substrate |
|--------|---------|------------------|
| **Senses** | Physical sensations, body state | Insula, somatosensory cortex |
| **Actions** | Executed behaviors | Motor cortex, basal ganglia |
| **Emotions** | Feelings, affective tone | Amygdala, vmPFC |
| **Impulses** | Urges, action tendencies | OFC, anterior cingulate |
| **Cognitions** | Thoughts, interpretations | Lateral/medial PFC |

### 11.3 Reconsolidation Window

```python
RECONSOLIDATION_WINDOW_HOURS = 4  # Protein-synthesis dependent plasticity

async def check_window_status(intervention_id: UUID) -> dict:
    intervention = await get_intervention(intervention_id)
    window_end = intervention.window_opened_at + timedelta(hours=4)
    
    return {
        'is_open': datetime.now() < window_end,
        'time_remaining': max(0, (window_end - datetime.now()).seconds),
        'requires_reactivation': datetime.now() >= window_end
    }
```

---

## 12. End-to-End Flow Summary

| Input | Classification | Extraction/Episode | Persistence |
|-------|----------------|-------------------|-------------|
| Raw text | MemoryBasinRouter → BASIN_MAPPING | extract_with_context (Graphiti) | Hexis + Graphiti |
| Episode + events | Nemori (episodic) | predict_and_calibrate → facts | route_memory + persist_fact |
| Heartbeat | Episodic | HeartbeatService → HeartbeatLog + Memory | Hexis + optional Graphiti |
| Subconscious | STRATEGIC/SEMANTIC | apply_observations | route_memory |
| High-resonance particle | — | — | WorkingMemoryCache → Graphiti |

**Unified ingestion (KG Learning):**
`classify → activate basin → AutoSchema extraction → MemEvolve/Graphiti`

---

## 13. Configuration Reference

### 13.1 Hexis Config (PostgreSQL)

```sql
-- Key config values from hexis_memory.config table
heartbeat.heartbeat_interval_minutes = 60
heartbeat.max_energy = 20
heartbeat.base_regeneration = 10
memory.recall_min_trust_level = 0
maintenance.subconscious_enabled = false
maintenance.working_memory_promote_min_importance = 0.75
maintenance.working_memory_promote_min_accesses = 3
operator.allow_self_termination = false
```

### 13.2 VPS Services

| Service | Port | Description |
|---------|------|-------------|
| Daedalus API | 8001 | Hexis memory interface |
| Dionysus API | 8000 | Graphiti knowledge graph |
| SilverBullet | 3000 | Documentation |
| Hexis Brain | 43815 (internal) | PostgreSQL |
| Embeddings | 80 (internal) | Text embeddings |

---

## 14. Key Files Quick Reference

| Component | Hexis Location | Dionysus Location |
|-----------|----------------|-------------------|
| Memory types | `db/00_tables.sql` | `api/models/sync.py` |
| Episodes | `db/00_tables.sql`, `db/91_triggers.sql` | `api/services/nemori_river_flow.py` |
| Goals | `db/08_functions_goals.sql` | — |
| Heartbeat | `db/07_functions_heartbeat.sql` | `api/services/heartbeat_service.py` |
| Working memory | `db/00_tables.sql` | `api/services/working_memory_cache.py` |
| Attractor basins | — | `api/services/attractor_basin_service.py` |
| AutoSchemaKG | — | `api/services/consciousness/autoschemakg_integration.py` |
| Graphiti | — | `api/services/graphiti_service.py` |
| MemEvolve | — | `api/services/memevolve_adapter.py` |
| Consciousness | — | `api/agents/consciousness_manager.py` |
| Particles | — | `api/models/metacognitive_particle.py` |
| API | `api/main.py` | `api/routers/*.py` |

---

## 15. Further Reading

### Documentation
- `Hexis/docs/architecture.md` — Database as Brain philosophy
- `Hexis/docs/PHILOSOPHY.md` — Personhood and consent framework
- `dionysus-api/docs/concepts/` — Concept documentation
- `dionysus-api/docs/science/` — Scientific foundations

### Key Concepts
- `docs/concepts/Multi-Tier Memory Architecture.md`
- `docs/concepts/Attractor Basin Dynamics.md`
- `docs/concepts/Thoughtseeds Framework.md`
- `docs/concepts/Neural Packets.md`
- `docs/concepts/OODA Loops and Heartbeat Agent.md`

### Protocols
- `CLAUDE.md` § Memory Stack Integration
- `CLAUDE.md` § Database Access Pattern (Gateway)
- `CLAUDE.md` § MemEvolve Protocol

---

*Last updated: 2026-01-30*
