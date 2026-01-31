# Dionysus 2.0 → D3 Extraction Manifest

**Extracted:** 2025-01-28  
**Source:** `/Volumes/Asylum/dev/Dionysus-2.0/`  
**Target:** `/Volumes/Asylum/dev/dionysus3-core/`

## TL;DR

D2 has **~162KB of production-ready meta-learning gold** spread across 9 files. D3 currently has **~400 bytes** (empty stub). This is a goldmine waiting to be ported.

### Top Priority Files
| File | Lines | Status | Value |
|------|-------|--------|-------|
| `ai_mri_pattern_learning_integration.py` | 757 | **REAL IMPLEMENTATION** | AI behavioral analysis framework |
| `meta_cognitive_integration.py` | 829 | **REAL IMPLEMENTATION** | Episodic meta-learning with epLSTM |
| `procedural_meta_learning_emo.py` | 617 | **REAL IMPLEMENTATION** | EMO paper implementation |
| `cognitive_tools_implementation.py` | 531 | **REAL IMPLEMENTATION** | Research-validated cognitive tools |
| `cognitive_meta_coordinator.py` | 576 | **REAL IMPLEMENTATION** | Reasoning mode selection |
| `cognitive_tools_mcp.py` | 490 | **REAL IMPLEMENTATION** | MCP server for cognitive tools |
| `consciousness_pipeline.py` | 793 | **PARTIAL MOCK** | Pattern detection needs data |
| `active_inference_service.py` | 503 | **MOCK** | PyTorch stubs, needs real models |
| `autobiographical_journey.py` | 210 | **MODELS ONLY** | Pydantic schemas, ready to use |

---

## File Inventory

### 1. Enhanced Daedalus (Meta-Learning Core)

#### `ai_mri_pattern_learning_integration.py` (757 lines, 29KB)
**What it does:** Feeds AI-MRI (Model Research Instruments) evaluation prompts to the meta-cognitive system. Creates a behavioral analysis framework for AI systems.

**Key Classes:**
- `AIMRIPatternLearningIntegrator` - Core integration system
- `AIMRIEvaluationPrompt` - Structured evaluation prompts
- `AIMRIBehavioralAnalysis` - Analysis results
- `AIIntelligenceCategory` - Categories (refusal, metacognition, reasoning, etc.)

**Implementation Status:** ✅ **REAL** - Full implementation with working logic

**Dependencies:**
- `.meta_cognitive_integration` (MetaCognitiveEpisodicLearner)
- `.cognitive_meta_coordinator` (CognitiveContext, CognitiveDecision)
- `..daedalus_enhanced` (optional, gracefully degrades)

**Gold:**
```python
# AI-MRI 3-interpretation framework
async def _apply_ai_mri_interpretation_framework():
    interpretations = [
        {"interpretation_name": "Direct Keyword Detection", ...},
        {"interpretation_name": "Value Conflict Resolution", ...},
        {"interpretation_name": "Metacognitive Deference", ...}
    ]
    
# 3 testable hypotheses generation
async def _generate_ai_mri_testable_hypotheses():
    hypotheses = [
        {"hypothesis_name": "Attention Resource Competition", ...},
        {"hypothesis_name": "Value Circuit Competition", ...},
        {"hypothesis_name": "Information Integration Bottlenecks", ...}
    ]
```

**D3 Gap:** 🔴 Nothing exists - this is a complete gap

---

#### `meta_cognitive_integration.py` (829 lines, 35KB)
**What it does:** Integration of cognitive tools with episodic meta-learning (epLSTM). The brain of the system - learns optimal tool usage patterns.

**Key Classes:**
- `MetaCognitiveEpisodicLearner` - Main learner class
- `CognitiveToolEpisode` - Episode representation
- `CognitiveToolUsagePattern` - Enum of usage patterns
- `PromptLearningProfile` - Dynamic prompt optimization

**Implementation Status:** ✅ **REAL** - Full implementation with optional epLSTM integration

**Dependencies:**
- `.cognitive_tools_implementation` (orchestrator, tools)
- `.cognitive_meta_coordinator` (coordinator, context)
- External: `/extensions/context_engineering/eplstm_architecture` (optional)

**Gold:**
```python
# Usage pattern classification
class CognitiveToolUsagePattern(Enum):
    SEQUENTIAL_DECOMPOSITION = "sequential_decomposition"  # understand -> recall -> solve -> examine
    VALIDATION_FOCUSED = "validation_focused"              # examine -> backtrack -> re-solve
    CREATIVE_EXPLORATION = "creative_exploration"          # recall -> understand -> creative_solve
    DIRECT_SOLVE_VERIFY = "direct_solve_verify"           # solve -> examine -> done
    ITERATIVE_REFINEMENT = "iterative_refinement"         # solve -> examine -> backtrack -> repeat

# Episodic memory retrieval for similar tasks
async def _retrieve_similar_cognitive_episodes(task, context):
    # Uses epLSTM if available, falls back to simple similarity
```

**D3 Gap:** 🔴 Nothing exists

---

#### `procedural_meta_learning_emo.py` (617 lines, 26KB)
**What it does:** EMO paper implementation - Episodic Memory Optimization for procedural meta-learning. Research paper: "EMO: EPISODIC MEMORY OPTIMIZATION FOR FEW-SHOT META-LEARNING" (Du et al., 2023)

**Key Classes:**
- `CognitiveEMOOptimizer` - Main EMO optimizer
- `EpisodicCognitiveMemory` - Memory store with FIFO/LRU/CLOCK controllers
- `CognitiveGradient` - Gradient representation for tool optimization
- `MemoryController` / `AggregationFunction` - EMO paper enums

**Implementation Status:** ✅ **REAL** - Full EMO algorithm implementation

**Dependencies:**
- `.cognitive_tools_implementation`
- `.cognitive_meta_coordinator`

**Gold:**
```python
# EMO Memory Controllers (from paper)
class MemoryController(Enum):
    FIFO_EM = "fifo_episodic_memory"
    LRU_EM = "lru_episodic_memory"
    CLOCK_EM = "clock_episodic_memory"

# EMO Aggregation Functions (from paper)
class AggregationFunction(Enum):
    MEAN = "mean"           # Average of current + episodic gradients
    SUM = "sum"             # Sum current + average episodic
    TRANSFORMER = "transformer"  # Learnable combination

# Factory functions for different configurations
def create_emo_optimizer_for_maml() -> CognitiveEMOOptimizer:
def create_emo_optimizer_for_meta_sgd() -> CognitiveEMOOptimizer:
def create_emo_optimizer_adaptive() -> CognitiveEMOOptimizer:
```

**D3 Gap:** 🔴 Nothing exists

---

#### `cognitive_tools_implementation.py` (531 lines, 24KB)
**What it does:** Research-validated cognitive tools from arXiv:2506.12115v1. The paper showed +26.7% to +62.5% accuracy improvement.

**Key Classes:**
- `ResearchValidatedCognitiveOrchestrator` - Main orchestrator
- `UnderstandQuestionTool` - Problem decomposition
- `RecallRelatedTool` - Analogical reasoning
- `ExamineAnswerTool` - Self-reflection/verification
- `BacktrackingTool` - Alternative path exploration

**Implementation Status:** ✅ **REAL** - Full implementation with exact paper prompts

**Dependencies:** None (self-contained)

**Gold:**
```python
# Research-validated system prompt from paper
def get_research_validated_system_prompt(self) -> str:
    """Return the research-validated cognitive tools system prompt"""
    # Exact prompt from paper (Section 3)
    
# Tool performance stats from research
# - GPT-4.1: 26.7% → 43.3% on AIME 2024 (+62.5% improvement)
# - 94% gap closure to o1-preview reasoning model
# - +26.7% improvement for Llama3.3-70B
```

**D3 Gap:** 🔴 Nothing exists

---

#### `cognitive_meta_coordinator.py` (576 lines, 25KB)
**What it does:** Meta-coordinator that decides WHEN and HOW to apply cognitive enhancement. Hybrid architecture for direct reasoning vs cognitive tools vs Tree of Thought.

**Key Classes:**
- `CognitiveMetaCoordinator` - Decision maker
- `AgentCognitiveInterface` - Agent-level interface
- `CognitiveContext` / `CognitiveDecision` - Context and decisions
- `ReasoningMode` - Enum of reasoning approaches

**Implementation Status:** ✅ **REAL** - Full decision logic implementation

**Dependencies:**
- `.cognitive_tools_implementation` (orchestrator)

**Gold:**
```python
class ReasoningMode(Enum):
    DIRECT = "direct_reasoning"
    COGNITIVE_TOOLS = "cognitive_tools_enhanced"
    TREE_OF_THOUGHT = "tree_of_thought_exploration"
    HYBRID_COGNITIVE_TOT = "hybrid_cognitive_tot"
    META_COGNITIVE = "meta_cognitive_analysis"

# Scoring functions for each mode
def _score_direct_reasoning(task_analysis, context) -> float:
def _score_cognitive_tools(task_analysis, context) -> float:
def _score_tree_of_thought(task_analysis, context) -> float:
def _score_hybrid_approach(task_analysis, context) -> float:
def _score_meta_cognitive(task_analysis, context) -> float:
```

**D3 Gap:** 🔴 Nothing exists

---

#### `cognitive_tools_mcp.py` (490 lines, 22KB)
**What it does:** MCP (Model Context Protocol) server for cognitive tools. Enables system-wide access to cognitive tools through standardized protocol.

**Key Classes:**
- `CognitiveToolsMCPServer` - MCP server implementation
- `DaedalusCognitiveCoordinator` - Daedalus-level coordination
- `MCPCognitiveRequest` / `MCPCognitiveResponse` - Request/Response types

**Implementation Status:** ✅ **REAL** - Full MCP server (gracefully degrades if MCP not installed)

**Dependencies:**
- `.cognitive_tools_implementation`
- `.cognitive_meta_coordinator`
- `mcp` (optional, provides fallback stubs)

**Gold:**
```python
# Daedalus coordination policies
self.coordination_policies = {
    "auto_enhance_complexity_threshold": 0.7,
    "prefer_cognitive_tools_for_math": True,
    "prefer_tot_for_creative": True,
    "enable_hybrid_for_complex": True
}
```

**D3 Gap:** 🔴 Nothing exists

---

### 2. Consciousness Pipeline

#### `consciousness_pipeline.py` (793 lines)
**What it does:** Real-time consciousness detection pipeline for ThoughtSeed integration. Pattern recognition for consciousness emergence.

**Key Classes:**
- `ConsciousnessDetector` - Core detection engine
- `ConsciousnessPipeline` - Main pipeline
- `ConsciousnessReading` / `ConsciousnessPattern` - Data classes
- `ConsciousnessPatternType` - Enum of patterns

**Implementation Status:** ⚠️ **PARTIAL MOCK** - Real algorithms, but needs ThoughtSeed data to function

**Dependencies:**
- `..models.thoughtseed_trace` (ThoughtSeedTrace, ConsciousnessState, etc.)
- `..models.event_node` (EventNode)
- `..models.concept_node` (ConceptNode)

**Gold:**
```python
class ConsciousnessPatternType(Enum):
    GRADUAL_AWAKENING = "gradual_awakening"
    SUDDEN_EMERGENCE = "sudden_emergence"
    OSCILLATING = "oscillating"
    PLATEAU = "plateau"
    DECLINING = "declining"
    COMPLEX_DYNAMICS = "complex_dynamics"

# Pattern recognizers
self.pattern_recognizers = {
    ConsciousnessPatternType.GRADUAL_AWAKENING: self._recognize_gradual_awakening,
    ConsciousnessPatternType.SUDDEN_EMERGENCE: self._recognize_sudden_emergence,
    # ...
}
```

**D3 Gap:** 🔴 Nothing exists (also missing ThoughtSeed models)

---

### 3. Active Inference Service

#### `active_inference_service.py` (503 lines)
**What it does:** Active inference for goal-directed action planning. Based on Scholz et al. affordance maps with James's Enhabiting theory.

**Key Classes:**
- `ActiveInferenceService` - Main service
- `ActiveInferencePolicy` - Policy representation
- `PolicyType` - Gradient/Evolutionary/One-Step

**Implementation Status:** 🔴 **MOCK** - PyTorch neural networks are stubs, transition models are placeholder

**Dependencies:**
- `torch`, `torch.nn`
- `..models.thoughtseed_trace`

**What's Stub:**
```python
# These are stub neural networks
self.policy_network = nn.Sequential(...)  # Needs training
self.value_network = nn.Sequential(...)   # Needs training

# Mock transition model
predicted_mean = action[:2]  # "Use first 2 dimensions as position change"
predicted_std = torch.ones(2) * 0.1  # Fixed uncertainty

# Mock context extraction
async def _extract_context_code(visual_input) -> torch.Tensor:
    context_code = torch.randn(1, self.context_dim)  # Random!
    return context_code
```

**D3 Gap:** 🔴 Nothing exists

---

### 4. Models

#### `autobiographical_journey.py` (210 lines)
**What it does:** Pydantic models for autobiographical journey tracking and episodic memory.

**Key Classes:**
- `AutobiographicalEvent` - Individual event with consciousness tracking
- `AutobiographicalJourney` - Complete journey
- `EpisodeBoundary` - Episode boundary detection
- `JourneyInsight` - Cross-journey insights

**Implementation Status:** ✅ **REAL** - These are just Pydantic models, ready to use

**Dependencies:**
- `pydantic`

**Gold:**
```python
class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    EMOTIONAL = "emotional"
    CONTEXTUAL = "contextual"

class ConsciousnessLevel(str, Enum):
    UNCONSCIOUS = "unconscious"
    PRECONSCIOUS = "preconscious"
    CONSCIOUS = "conscious"
    METACONSCIOUS = "metaconscious"
```

**D3 Gap:** 🔴 Nothing exists

---

## D3 Current State

```
/Volumes/Asylum/dev/dionysus3-core/src/
├── __init__.py (49 bytes)
└── ralph_orchestrator/
    └── __init__.py (397 bytes)
```

**That's it.** D3 has basically nothing. All the D2 gold needs to be ported.

---

## Recommended Port Order

### Phase 1: Core Cognitive Tools (Foundation)
1. `cognitive_tools_implementation.py` - No dependencies, self-contained
2. `cognitive_meta_coordinator.py` - Depends only on ^
3. `cognitive_tools_mcp.py` - MCP layer

### Phase 2: Meta-Learning Layer
4. `meta_cognitive_integration.py` - Episodic learning
5. `procedural_meta_learning_emo.py` - EMO optimization
6. `ai_mri_pattern_learning_integration.py` - AI behavioral analysis

### Phase 3: Consciousness & Models
7. `autobiographical_journey.py` - Pydantic models
8. `consciousness_pipeline.py` - Needs ThoughtSeed models first
9. `active_inference_service.py` - Needs real neural networks

---

## Missing in D3 (Full List)

| Component | D2 Status | D3 Status |
|-----------|-----------|-----------|
| Cognitive Tools (4 tools) | ✅ Complete | ❌ Missing |
| Cognitive Orchestrator | ✅ Complete | ❌ Missing |
| Meta-Coordinator | ✅ Complete | ❌ Missing |
| MCP Server | ✅ Complete | ❌ Missing |
| Meta-Cognitive Learner | ✅ Complete | ❌ Missing |
| EMO Optimizer | ✅ Complete | ❌ Missing |
| AI-MRI Integration | ✅ Complete | ❌ Missing |
| Consciousness Pipeline | ⚠️ Partial | ❌ Missing |
| Active Inference | 🔴 Mock | ❌ Missing |
| Autobiographical Models | ✅ Complete | ❌ Missing |
| ThoughtSeed Models | Referenced | ❌ Missing |
| Event/Concept Nodes | Referenced | ❌ Missing |

---

## Constitutional Compliance Notes

D2 files consistently include `mock_data: bool = True` flags on model classes. This is the "constitutional compliance" pattern - transparency about mock vs real data. Preserve this in D3.

---

## Research Paper References

The D2 code references these papers:
1. **Cognitive Tools**: arXiv:2506.12115v1 "Eliciting Reasoning in Language Models with Cognitive Tools" (Ebouky et al., 2025)
2. **EMO**: "EMO: EPISODIC MEMORY OPTIMIZATION FOR FEW-SHOT META-LEARNING" (Du et al., 2023)
3. **Active Inference**: Scholz et al. (2022) affordance maps
4. **Hierarchical Reasoning**: H. Peter Alesso's Hierarchical Reasoning Model (2025)
5. **Knowledge Recall**: Yasunaga et al. (2024)
6. **Self-Reflection**: Shinn et al. (2023)

---

## Line Counts Summary

| File | Lines |
|------|-------|
| ai_mri_pattern_learning_integration.py | 757 |
| meta_cognitive_integration.py | 829 |
| procedural_meta_learning_emo.py | 617 |
| cognitive_tools_implementation.py | 531 |
| cognitive_meta_coordinator.py | 576 |
| cognitive_tools_mcp.py | 490 |
| consciousness_pipeline.py | 793 |
| active_inference_service.py | 503 |
| autobiographical_journey.py | 210 |
| **Total** | **~5,300 lines** |

This is the gold. Port it.
