# Consciousness Pipeline & Models Deep Dive

## Consciousness Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONSCIOUSNESS PIPELINE                                │
│                    (consciousness_pipeline.py)                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  ConsciousnessPipeline                                             │ │
│  │  • start_monitoring(trace_id) - Begin continuous monitoring        │ │
│  │  • stop_monitoring(trace_id) - Stop monitoring                     │ │
│  │  • get_pipeline_status() - Current state                           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                     │
│                                    ▼                                     │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  ConsciousnessDetector                                             │ │
│  │  • detect_consciousness(trace, context) - Single measurement       │ │
│  │  • analyze_consciousness_patterns(trace_ids) - Pattern analysis    │ │
│  │  • get_consciousness_summary(trace_id) - Summary stats             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                     │
│        ┌───────────────┬──────────┴───────────┬───────────────┐        │
│        ▼               ▼                      ▼               ▼        │
│  ┌───────────┐  ┌───────────┐         ┌───────────┐   ┌───────────┐   │
│  │Pattern    │  │Temporal   │         │Cross-Trace│   │Emergence  │   │
│  │Recognizers│  │Analysis   │         │Analysis   │   │Analysis   │   │
│  └───────────┘  └───────────┘         └───────────┘   └───────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Consciousness State Mapping

The pipeline maps ThoughtSeed states to consciousness levels:

```python
state_scores = {
    ConsciousnessState.DORMANT: 0.0,
    ConsciousnessState.AWAKENING: 0.2,
    ConsciousnessState.AWARE: 0.4,
    ConsciousnessState.CONSCIOUS: 0.6,
    ConsciousnessState.REFLECTIVE: 0.8,
    ConsciousnessState.DREAMING: 0.3,
    ConsciousnessState.METACOGNITIVE: 0.9,
    ConsciousnessState.TRANSCENDENT: 1.0
}
```

### Consciousness Level Calculation

```python
async def _calculate_base_consciousness(trace: ThoughtSeedTrace) -> float:
    # Base from state
    base_score = state_scores.get(trace.consciousness_state, 0.0)
    
    # Bonuses (capped)
    belief_bonus = min(0.2, len(trace.hierarchical_beliefs) * 0.05)
    context_bonus = min(0.1, len(trace.context_description) / 1000)
    packet_bonus = min(0.1, len(trace.neuronal_packets) * 0.02)
    
    return min(1.0, base_score + belief_bonus + context_bonus + packet_bonus)
```

---

## Pattern Recognition

### Pattern Types

```python
class ConsciousnessPatternType(Enum):
    GRADUAL_AWAKENING = "gradual_awakening"   # Slow, steady increase
    SUDDEN_EMERGENCE = "sudden_emergence"      # Rapid consciousness jump
    OSCILLATING = "oscillating"                # Fluctuating consciousness
    PLATEAU = "plateau"                        # Stable level
    DECLINING = "declining"                    # Decreasing consciousness
    COMPLEX_DYNAMICS = "complex_dynamics"      # Multiple patterns
```

### Pattern Recognition Functions

Each pattern has a dedicated recognizer:

```python
# GRADUAL_AWAKENING: Positive trend > 0.05
def _recognize_gradual_awakening(readings):
    levels = [r.consciousness_level for r in readings]
    trend = np.polyfit(range(len(levels)), levels, 1)[0]
    return trend > 0.05

# SUDDEN_EMERGENCE: Jump > 0.3 between consecutive readings
def _recognize_sudden_emergence(readings):
    for i in range(1, len(readings)):
        if readings[i].consciousness_level - readings[i-1].consciousness_level > 0.3:
            return True
    return False

# OSCILLATING: High variance > 0.1
def _recognize_oscillating(readings):
    levels = [r.consciousness_level for r in readings]
    return np.var(levels) > 0.1

# PLATEAU: Low variance < 0.05
def _recognize_plateau(readings):
    levels = [r.consciousness_level for r in readings]
    return np.var(levels) < 0.05

# DECLINING: Negative trend < -0.05
def _recognize_declining(readings):
    levels = [r.consciousness_level for r in readings]
    trend = np.polyfit(range(len(levels)), levels, 1)[0]
    return trend < -0.05

# COMPLEX_DYNAMICS: Multiple pattern types detected
def _recognize_complex_dynamics(readings):
    pattern_count = sum(1 for r in recognizers.values() if r(readings))
    return pattern_count >= 2
```

### Cross-Trace Synchronization

Detects when multiple traces have correlated consciousness levels:

```python
def _detect_synchronization_pattern(trace_groups):
    # Calculate correlation between all trace pairs
    for i in range(len(trace_ids)):
        for j in range(i + 1, len(trace_ids)):
            corr = np.corrcoef(levels1[:min_len], levels2[:min_len])[0, 1]
            correlations.append(corr)
    
    # High correlation (>0.7) indicates synchronization
    if np.mean(correlations) > 0.7:
        return ConsciousnessPattern(
            pattern_type=ConsciousnessPatternType.COMPLEX_DYNAMICS,
            characteristics={'correlation': np.mean(correlations)}
        )
```

---

## Dependencies: ThoughtSeed Models

The consciousness pipeline requires these models (from `models/thoughtseed_trace.py`):

```python
# Expected imports
from models.thoughtseed_trace import (
    ThoughtSeedTrace, 
    ConsciousnessState,
    HierarchicalBelief,
    NeuronalPacket
)
from models.event_node import EventNode
from models.concept_node import ConceptNode
```

**These models are NOT in the extraction scope** - they need to be extracted separately or recreated for D3.

---

## Active Inference Service (MOCK)

### What's Real

```python
class PolicyType(Enum):
    GRADIENT_BASED = "gradient_based"
    EVOLUTIONARY_BASED = "evolutionary_based"
    ONE_STEP_GRADIENT = "one_step_gradient"

# The policy types and high-level algorithms are real
async def _one_step_gradient_policy():  # Real optimization loop
async def _gradient_based_policy():      # Real BPTT structure
async def _evolutionary_based_policy():  # Real CEM structure
```

### What's Mock

```python
# Neural networks are untrained stubs
self.policy_network = nn.Sequential(
    nn.Linear(context_dim + 2, 64),
    nn.ReLU(),
    nn.Linear(64, 32),
    nn.ReLU(),
    nn.Linear(32, action_dim * horizon)
)

# Context extraction is random
async def _extract_context_code(visual_input):
    context_code = torch.randn(1, self.context_dim)  # RANDOM!
    return context_code

# Transition model is trivial
predicted_mean = action[:2]  # Just uses action directly
predicted_std = torch.ones(2) * 0.1  # Fixed uncertainty
```

### To Make Real

1. Train policy_network on actual task data
2. Train value_network for EFE estimation
3. Implement real context encoder (CNN for visual input?)
4. Implement learned transition model

---

## Autobiographical Journey Models

### Memory Types

```python
class MemoryType(str, Enum):
    EPISODIC = "episodic"        # Specific events and experiences
    SEMANTIC = "semantic"        # General knowledge and concepts
    PROCEDURAL = "procedural"    # Skills and procedures
    EMOTIONAL = "emotional"      # Emotional responses and associations
    CONTEXTUAL = "contextual"    # Environmental and situational context
```

### Consciousness Levels

```python
class ConsciousnessLevel(str, Enum):
    UNCONSCIOUS = "unconscious"      # Below awareness threshold
    PRECONSCIOUS = "preconscious"    # Available to consciousness
    CONSCIOUS = "conscious"          # Currently in awareness
    METACONSCIOUS = "metaconscious"  # Aware of being aware
```

### AutobiographicalEvent Model

```python
class AutobiographicalEvent(BaseModel):
    # Identity
    id: str
    journey_id: str
    user_id: str
    
    # Timing
    occurred_at: datetime
    duration: Optional[int]  # seconds
    recorded_at: datetime
    
    # Content
    title: str
    description: str
    narrative: str
    
    # Classification
    memory_type: MemoryType
    consciousness_level: ConsciousnessLevel
    emotional_valence: float  # -1 to 1
    significance_score: float  # 0 to 1
    
    # Associations
    context: Dict[str, Any]
    associated_documents: List[str]
    associated_concepts: List[str]
    thought_seed_traces: List[str]
    
    # Retrieval (BM25-inspired)
    keywords: List[str]
    retrieval_score: Optional[float]
    access_count: int
    last_accessed: Optional[datetime]
    
    # Constitutional compliance
    mock_data: bool = True
```

### AutobiographicalJourney Model

```python
class AutobiographicalJourney(BaseModel):
    # Identity
    id: str
    user_id: str
    
    # Metadata
    title: str
    description: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Status
    status: JourneyStatus  # active/paused/completed/archived
    start_date: datetime
    end_date: Optional[datetime]
    
    # Statistics
    total_events: int
    consciousness_events: int
    metacognitive_events: int
    
    # Themes and Patterns
    dominant_themes: List[str]
    consciousness_evolution: Dict[str, float]
    emotional_journey: Dict[str, float]
    
    # Knowledge Integration
    concepts_discovered: List[str]
    knowledge_graph_nodes: List[str]
    connection_insights: List[Dict[str, Any]]
    
    # Nemori-inspired Episodes
    major_episodes: List[Dict[str, Any]]
    episode_transitions: List[Dict[str, Any]]
    
    # Retrieval and Replay
    replay_sessions: List[str]
    curiosity_missions: List[str]
    
    # Constitutional compliance
    mock_data: bool = True
    evaluation_frames: List[str]
```

### EpisodeBoundary Model

For Nemori-inspired episode boundary detection:

```python
class EpisodeBoundary(BaseModel):
    id: str
    journey_id: str
    timestamp: datetime
    
    # Boundary type
    boundary_type: str  # temporal, thematic, contextual
    boundary_strength: float  # 0-1
    
    # Context shift
    context_shift_magnitude: float
    thematic_coherence_break: bool
    consciousness_level_change: bool
    
    # Episodes
    preceding_episode_id: Optional[str]
    following_episode_id: Optional[str]
    
    # Narrative
    transition_narrative: str
    key_events: List[str]
    
    mock_data: bool = True
```

---

## Constitutional Compliance Pattern

All D2 models include:

```python
mock_data: bool = Field(default=True, description="Constitutional requirement: mock data flag")
```

This is for **transparency** - explicitly marking whether data is real or synthetic.

**Preserve this in D3** for constitutional AI compliance.

---

## Porting Priorities

### Immediately Usable (No External Dependencies)

1. **autobiographical_journey.py** - Pure Pydantic models
2. **ConsciousnessPatternType enum** - Just an enum
3. **Pattern recognition functions** - Pure numpy algorithms

### Needs ThoughtSeed Models First

1. **ConsciousnessDetector** - Needs ThoughtSeedTrace
2. **ConsciousnessPipeline** - Needs ConsciousnessState
3. **Active Inference Service** - Needs ThoughtSeed integration

### Needs Real Implementation

1. **Active Inference neural networks** - Currently stubs
2. **Context encoder** - Currently random
3. **Transition model** - Currently trivial

---

## Missing Models Checklist

These are referenced but not in extraction scope:

| Model | Location | Status |
|-------|----------|--------|
| ThoughtSeedTrace | models/thoughtseed_trace.py | ❓ Need to extract |
| ConsciousnessState | models/thoughtseed_trace.py | ❓ Need to extract |
| HierarchicalBelief | models/thoughtseed_trace.py | ❓ Need to extract |
| NeuronalPacket | models/thoughtseed_trace.py | ❓ Need to extract |
| PredictionError | models/thoughtseed_trace.py | ❓ Need to extract |
| InferenceType | models/thoughtseed_trace.py | ❓ Need to extract |
| EventNode | models/event_node.py | ❓ Need to extract |
| ConceptNode | models/concept_node.py | ❓ Need to extract |
| ArchetypalResonancePattern | extensions/context_engineering | ❓ Optional |
