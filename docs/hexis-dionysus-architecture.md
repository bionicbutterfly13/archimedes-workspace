# Hexis + Dionysus 3.0 Memory Architecture
## Comprehensive Technical Reference

**Version**: 1.0
**Date**: 2026-01-30
**Purpose**: Document for researchers on the unified memory system architecture

---

## System Overview

The memory architecture consists of two primary systems working in concert:

1. **Hexis**: PostgreSQL-native cognitive architecture ("Database as Brain")
2. **Dionysus 3.0**: Python services layer with Neo4j/Graphiti knowledge graph

Together they implement a biologically-inspired cognitive system with:
- **AutoschemaKG**: Self-organizing knowledge graph
- **Nemori**: Stream-based episodic memory ("The River")
- **Graphiti**: Temporal knowledge graph for semantic memory
- **MemEvolve**: Vector-backed entity/fact extraction
- **Attractor Basin Architecture**: Hopfield network-based memory routing

---

## 1. Memory Type Hierarchy

### 1.1 Core Memory Types (Hexis)

```sql
CREATE TYPE memory_type AS ENUM (
    'episodic',    -- Events, conversations, experiences (timestamped)
    'semantic',    -- Facts, knowledge, information
    'procedural',  -- How-to, processes, methods
    'strategic',   -- Plans, approaches, patterns
    'worldview',   -- Beliefs, values, perspectives
    'goal'         -- Objectives with priority tracking
);
```

### 1.2 Memory Status Lifecycle

```sql
CREATE TYPE memory_status AS ENUM (
    'active',      -- Currently valid and retrievable
    'archived',    -- Preserved but deprioritized
    'invalidated'  -- Superseded or contradicted
);
```

### 1.3 Memory Table Schema

```sql
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    type memory_type NOT NULL,
    status memory_status DEFAULT 'active',
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,  -- pgvector
    importance DOUBLE PRECISION DEFAULT 0.5,
    source_attribution JSONB NOT NULL DEFAULT '{}',
    trust_level DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    decay_rate DOUBLE PRECISION DEFAULT 0.01,
    metadata JSONB NOT NULL DEFAULT '{}'
);
```

---

## 2. Episodic Memory System

### 2.1 Episodes as Containers

Episodes are time-bounded containers that group related memories:

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
```

### 2.2 Auto-Assignment Trigger

Memories automatically assign to episodes based on temporal proximity:

```sql
CREATE OR REPLACE FUNCTION assign_to_episode()
RETURNS trigger AS $$
DECLARE
    current_episode_id UUID;
BEGIN
    -- Close any open episode
    UPDATE episodes
    SET ended_at = CURRENT_TIMESTAMP
    WHERE ended_at IS NULL;
    
    -- Create new episode for each memory (1:1 mapping)
    INSERT INTO episodes (started_at, ended_at, metadata)
    VALUES (NEW.created_at, NEW.created_at, 
            jsonb_build_object('episode_type', 'message'))
    RETURNING id INTO current_episode_id;
    
    PERFORM link_memory_to_episode_graph(NEW.id, current_episode_id, 1);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 2.3 Nemori: The River (Dionysus)

Nemori implements hierarchical episodic memory as a flowing river:

```
Source Events → Tributaries (Episodes) → Main River (Narrative)
```

**Key Components:**

```python
class DevelopmentEvent:
    """Atomic unit of experience"""
    id: UUID
    content: str
    timestamp: datetime
    emotional_valence: float
    arousal: float
    metadata: dict

class DevelopmentEpisode:
    """Aggregated events forming a coherent narrative unit"""
    id: UUID
    title: str
    summary: str
    narrative: str
    archetype: str  # narrative pattern
    events: List[DevelopmentEvent]
```

---

## 3. Semantic Memory & Knowledge Graph

### 3.1 Graphiti Integration

Graphiti provides temporal knowledge graph capabilities:

```python
class GraphitiService:
    async def persist_fact(
        self,
        content: str,
        confidence: float,
        valid_at: datetime,
        source_episode_id: UUID
    ) -> UUID:
        """Store semantic fact with bi-temporal tracking"""
        
    async def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities for graph linking"""
```

### 3.2 Nemori Bridge

Connects episodic (Nemori) and semantic (Graphiti) systems:

```
                   ┌─────────────────────────────────────┐
                   │         Integration Layer           │
                   │         (Nemori Bridge)             │
                   └─────────────────────────────────────┘
                              │           │
              ┌───────────────┘           └───────────────┐
              ▼                                           ▼
    ┌─────────────────────┐                 ┌─────────────────────┐
    │   Episodic System   │                 │   Semantic System   │
    │      (Nemori)       │                 │     (MemEvolve)     │
    │                     │                 │                     │
    │ DevelopmentEvent ───┼─── Promote ────►│ TrajectoryData      │
    │ DevelopmentEpisode  │                 │ Entity              │
    │                     │                 │ Fact                │
    └─────────────────────┘                 └─────────────────────┘
```

**Promotion Flow:**
```python
# Episode → Trajectory promotion
adapter = get_memevolve_adapter()
await adapter.ingest_trajectory(
    query=episode.title,
    observation=episode.summary,
    thought=episode.narrative,
    action=episode.archetype
)

# Fact persistence
graphiti = await get_graphiti_service()
await graphiti.persist_fact(
    content=fact_content,
    confidence=prediction_confidence,
    valid_at=timestamp,
    source_episode_id=episode.id
)
```

---

## 4. Procedural Memory

### 4.1 Storage Format

```python
async def create_procedural_memory(
    content: str,
    steps: dict,  # {"steps": [...], "prerequisites": [...]}
    importance: float = 0.6
) -> UUID:
    """Store how-to knowledge with structured steps"""
```

### 4.2 Retrieval

```python
async def get_procedures(
    query: str,
    context: str = None,
    limit: int = 5
) -> List[Memory]:
    """Retrieve relevant procedural memories"""
```

---

## 5. Attractor Basin Architecture

### 5.1 Hopfield Network Foundation

Attractor basins use Hopfield network mathematics for memory routing:

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
        
    def recall(self, probe: np.ndarray, max_iterations: int = 100):
        """Run network dynamics until convergence to attractor"""
        state = probe.copy()
        for _ in range(max_iterations):
            # Asynchronous update
            new_state = np.sign(self.weights @ state + self.biases)
            if np.array_equal(new_state, state):
                break
            state = new_state
        return state
```

### 5.2 Memory Basin Router

Routes memories through specialized attractor basins:

```python
class MemoryBasinRouter:
    """Routes memory content through specialized attractor basins"""
    
    BASINS = {
        'episodic': 'autobiographical',
        'semantic': 'knowledge',
        'procedural': 'skills',
        'strategic': 'planning',
        'worldview': 'beliefs',
        'goal': 'intentions'
    }
    
    async def route_memory(
        self,
        content: str,
        memory_type: MemoryType
    ) -> AttractorBasinState:
        """
        Classify and route memory to appropriate basin.
        
        Returns basin state including:
        - basin_id: Which attractor captured the memory
        - attractor_strength: How strongly it resonates
        - resonance_score: Similarity to basin prototype
        """
```

### 5.3 Context Packaging with Attractors

Working memory cells have attractor properties:

```python
@dataclass
class WorkingMemoryCell:
    content: str
    priority: int
    resonance_score: float = 0.0      # Semantic similarity
    attractor_strength: float = 1.0   # Persistence strength (decays)
    basin_id: Optional[str] = None    # Associated attractor basin
    
    def access(self):
        """Reinforce attractor strength on access"""
        self.attractor_strength = min(1.0, self.attractor_strength + 0.1)
        
    def decay(self, rate: float = 0.1):
        """Apply decay to attractor strength"""
        self.attractor_strength = max(0.0, self.attractor_strength - rate)
```

---

## 6. Heartbeat & OODA Loop

### 6.1 Heartbeat Architecture

The heartbeat is the autonomous cognitive cycle:

```sql
CREATE TYPE heartbeat_action AS ENUM (
    'observe',           -- Gather context
    'review_goals',      -- Check active goals
    'remember',          -- Store to long-term memory
    'recall',            -- Retrieve from memory
    'connect',           -- Create graph relationships
    'reprioritize',      -- Adjust goal priorities
    'reflect',           -- Internal reflection
    'contemplate',       -- Deliberate on beliefs
    'meditate',          -- Quiet reflection
    'study',             -- Structured learning
    'debate_internally', -- Internal dialectic
    'maintain',          -- Update beliefs, prune
    'mark_turning_point',-- Flag significant moment
    'begin_chapter',     -- Start narrative chapter
    'close_chapter',     -- End narrative chapter
    'synthesize',        -- Generate artifact/conclusion
    'reach_out_user',    -- Contact user
    'pause_heartbeat',   -- Temporary pause
    'rest'               -- Bank remaining energy
);
```

### 6.2 OODA Loop Implementation

The cognitive cycle follows OODA (Observe-Orient-Decide-Act):

```python
async def run_heartbeat():
    """Execute one heartbeat cycle"""
    
    # OBSERVE: Gather context
    context = await gather_turn_context()
    # Returns: identity, worldview, emotional_state, goals, drives
    
    # ORIENT: Process through active inference
    prediction_error = await calculate_surprisal(context)
    
    # DECIDE: Select actions based on free energy minimization
    actions = await select_heartbeat_actions(
        context=context,
        prediction_error=prediction_error,
        energy_budget=current_energy
    )
    
    # ACT: Execute selected actions
    results = await execute_heartbeat_actions_batch(
        heartbeat_id=heartbeat_id,
        actions=actions
    )
    
    return results
```

### 6.3 Energy Budget System

Actions have costs that constrain the heartbeat:

```python
HEARTBEAT_COSTS = {
    'observe': 0,          # Always free
    'review_goals': 0,     # Always free
    'remember': 0,         # Always free
    'recall': 1,
    'connect': 1,
    'reprioritize': 1,
    'reflect': 2,
    'contemplate': 1,
    'meditate': 1,
    'study': 2,
    'debate_internally': 2,
    'maintain': 2,
    'synthesize': 3,
    'reach_out_user': 5,
    'reach_out_public': 7,
    'rest': 0
}
```

---

## 7. Working Memory

### 7.1 Schema

```sql
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
```

### 7.2 Promotion Rules

Working memory promotes to long-term based on:

```python
PROMOTION_CRITERIA = {
    'min_importance': 0.75,  # High importance
    'min_accesses': 3,       # Frequently accessed
}
```

---

## 8. Consciousness Manager & Thoughtseeds

### 8.1 Thoughtseed Hierarchy

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
Layer 6: Dominant Thoughtseed           # Current consciousness
    ↓
Layer 7: Meta-cognition                 # Higher-order control
    ↓
Layer 8: Agent-Level Integration        # Global goals/policies
```

### 8.2 Neuronal Packet Model

```python
class PacketDynamics(BaseModel):
    """
    Neuronal Packet (50-200ms population spike) as atomic cognitive unit.
    """
    id: UUID
    state: Literal['unmanifested', 'manifested', 'activated']
    alpha_core: float      # Core attractor activation
    alpha_sub: List[float] # Subordinate attractor activations
    binding_energy: float  # Energy barrier for state transition
    knowledge: dict        # Encapsulated knowledge
    created_at: datetime
```

### 8.3 Active Inference & Free Energy

```python
async def calculate_surprisal(context: dict) -> float:
    """
    Calculate prediction error (surprisal) for active inference.
    
    Based on Free Energy Principle:
    F = Complexity + Accuracy
    F = D_KL[q(s)||p(s)] - E_q[log p(o|s)]
    """
    # Complexity: KL divergence from prior
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
```

### 8.4 Global Workspace Broadcasting

Winner-take-all selection for consciousness:

```python
async def select_dominant_thoughtseed(
    active_pool: List[ThoughtSeed],
    consciousness_state: str,
    arousal: float
) -> ThoughtSeed:
    """
    Select dominant thoughtseed via free energy minimization.
    
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

---

## 9. MoSAEIC Protocol

### 9.1 Overview

**M**indful **o**bservation of **S**enses, **A**ctions, **E**motions, **I**mpulses, **C**ognitions

A 5-phase therapeutic protocol for belief reconsolidation:

```
Phase 1: Interrupt      → Detect maladaptive pattern
Phase 2: Data Capture   → 5-window observation
Phase 3: Prediction Error → Generate cognitive dissonance
Phase 4: Rewrite        → Update belief during reconsolidation window
Phase 5: Verification   → Track new belief activation
```

### 9.2 Five-Window Data Model

| Window | Content | Neural Substrate |
|--------|---------|------------------|
| **Senses** | Physical sensations, body state | Insula, somatosensory cortex |
| **Actions** | Executed behaviors | Motor cortex, basal ganglia |
| **Emotions** | Feelings, affective tone | Amygdala, vmPFC |
| **Impulses** | Urges, action tendencies | OFC, anterior cingulate |
| **Cognitions** | Thoughts, interpretations | Lateral/medial PFC |

### 9.3 Reconsolidation Window

```python
RECONSOLIDATION_WINDOW_HOURS = 4  # Protein-synthesis dependent plasticity

async def check_window_status(intervention_id: UUID) -> dict:
    """Check if reconsolidation window is still open"""
    intervention = await get_intervention(intervention_id)
    window_end = intervention.window_opened_at + timedelta(hours=4)
    
    return {
        'is_open': datetime.now() < window_end,
        'time_remaining': max(0, (window_end - datetime.now()).seconds),
        'requires_reactivation': datetime.now() >= window_end
    }
```

---

## 10. Mental Models

### 10.1 Model Structure

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
    
    If prediction_error > threshold:
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

## 11. Goal System

### 11.1 Goal Priorities

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
```

### 11.2 Goal Functions

```sql
-- Create a goal
SELECT create_goal(
    'Learn about quantum computing',
    'Understand basic principles',
    'curiosity'::goal_source,
    'queued'::goal_priority,
    NULL,  -- parent_id
    NULL   -- due_at
);

-- Change priority
SELECT change_goal_priority(
    goal_id,
    'active'::goal_priority,
    'User expressed interest'
);

-- Add progress
SELECT add_goal_progress(
    goal_id,
    'Completed chapter 1 of textbook'
);
```

---

## 12. API Reference

### 12.1 Daedalus API (Hexis Interface)

**Base URL**: `http://72.61.78.89:8001`

#### Store Memory
```http
POST /remember
Content-Type: application/json

{
    "content": "User prefers morning meetings",
    "memory_type": "semantic",
    "importance": 0.8,
    "metadata": {}
}

Response:
{
    "stored": true,
    "id": "uuid..."
}
```

#### Recall Memories
```http
POST /recall
Content-Type: application/json

{
    "query": "meeting preferences",
    "limit": 10
}

Response:
{
    "memories": [
        {
            "id": "uuid...",
            "content": "User prefers morning meetings",
            "type": "semantic",
            "importance": 0.8,
            "similarity": 0.85
        }
    ]
}
```

### 12.2 Dionysus API (Knowledge Graph)

**Base URL**: `http://72.61.78.89:8000`

#### Ingest Trajectory
```http
POST /api/graphiti/ingest
Content-Type: application/json

{
    "content": "Discussion about project roadmap",
    "source": "archimedes",
    "metadata": {
        "episode_type": "planning"
    }
}
```

#### Search Knowledge Graph
```http
POST /api/graphiti/search
Content-Type: application/json

{
    "query": "project roadmap",
    "limit": 5
}
```

---

## 13. Configuration

### 13.1 Key Config Values

```sql
-- Heartbeat settings
heartbeat.heartbeat_interval_minutes = 60
heartbeat.max_energy = 20
heartbeat.base_regeneration = 10

-- Memory settings
memory.recall_min_trust_level = 0
maintenance.working_memory_promote_min_importance = 0.75
maintenance.working_memory_promote_min_accesses = 3

-- Subconscious (disabled by default)
maintenance.subconscious_enabled = false

-- Safety
operator.allow_self_termination = false
```

### 13.2 VPS Services

| Service | Port | Description |
|---------|------|-------------|
| Daedalus API | 8001 | Memory interface for Archimedes |
| Dionysus API | 8000 | Graphiti knowledge graph |
| SilverBullet | 3000 | Documentation/notes |
| Hexis Brain | 43815 (internal) | PostgreSQL database |
| Embeddings | 80 (internal) | Text embedding service |

---

## References

1. Kavi et al. (2025) - "From Neuronal Packets to Thoughtseeds"
2. Friston, K. - Free Energy Principle and Active Inference
3. Hopfield, J. - Neural Networks and Physical Systems with Emergent Collective Computational Abilities
4. Graphiti Documentation - Temporal Knowledge Graphs
5. Hexis Philosophy Document - `/docs/PHILOSOPHY.md`

---

*Last updated: 2026-01-30*
