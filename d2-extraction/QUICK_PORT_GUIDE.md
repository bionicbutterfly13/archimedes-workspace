# Quick Port Guide: D2 → D3

## Directory Structure for D3

```
/Volumes/Asylum/dev/dionysus3-core/
├── src/
│   ├── cognitive_tools/           # Phase 1
│   │   ├── __init__.py
│   │   ├── tools.py               # The 4 cognitive tools
│   │   ├── orchestrator.py        # ResearchValidatedCognitiveOrchestrator
│   │   └── prompts.py             # Research-validated prompts
│   │
│   ├── meta_coordinator/          # Phase 1
│   │   ├── __init__.py
│   │   ├── coordinator.py         # CognitiveMetaCoordinator
│   │   ├── agent_interface.py     # AgentCognitiveInterface
│   │   └── models.py              # CognitiveContext, CognitiveDecision
│   │
│   ├── meta_learning/             # Phase 2
│   │   ├── __init__.py
│   │   ├── episodic_learner.py    # MetaCognitiveEpisodicLearner
│   │   ├── emo_optimizer.py       # CognitiveEMOOptimizer
│   │   ├── memory.py              # EpisodicCognitiveMemory
│   │   └── ai_mri.py              # AI-MRI integration
│   │
│   ├── consciousness/             # Phase 3
│   │   ├── __init__.py
│   │   ├── detector.py            # ConsciousnessDetector
│   │   ├── pipeline.py            # ConsciousnessPipeline
│   │   └── patterns.py            # Pattern recognition
│   │
│   └── models/                    # Phase 3
│       ├── __init__.py
│       ├── journey.py             # Autobiographical models
│       └── consciousness.py       # ConsciousnessReading, etc.
```

---

## Phase 1: Core Cognitive Tools

### Step 1: Copy the enums and dataclasses

```python
# src/cognitive_tools/models.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class CognitiveToolCall:
    """Represents a cognitive tool function call"""
    name: str
    parameters: Dict[str, Any]
    context: Optional[str] = None

@dataclass 
class CognitiveToolResponse:
    """Response from executing a cognitive tool"""
    content: str
    success: bool = True
    metadata: Dict[str, Any] = None
    reasoning_trace: Optional[str] = None
```

### Step 2: Copy the tool prompts

```python
# src/cognitive_tools/prompts.py

UNDERSTAND_QUESTION_PROMPT = """You are a mathematical reasoning assistant designed to analyze 
and break down complex mathematical problems into structured steps...
[Full prompt from cognitive_tools_implementation.py]
"""

RECALL_RELATED_PROMPT = """You are a retrieval assistant whose purpose is to help solve 
new mathematical problems by providing solved examples of analogous problems...
[Full prompt from cognitive_tools_implementation.py]
"""

EXAMINE_ANSWER_PROMPT = """You are an expert mathematical assistant tasked with 
**verifying and improving** solutions...
[Full prompt from cognitive_tools_implementation.py]
"""

BACKTRACKING_PROMPT = """You are a careful problem-solving assistant with the ability 
to backtrack from flawed logic...
[Full prompt from cognitive_tools_implementation.py]
"""
```

### Step 3: Copy the ReasoningMode enum

```python
# src/meta_coordinator/models.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class ReasoningMode(Enum):
    DIRECT = "direct_reasoning"
    COGNITIVE_TOOLS = "cognitive_tools_enhanced"
    TREE_OF_THOUGHT = "tree_of_thought_exploration"
    HYBRID_COGNITIVE_TOT = "hybrid_cognitive_tot"
    META_COGNITIVE = "meta_cognitive_analysis"

@dataclass
class CognitiveContext:
    task_complexity: float
    domain_type: str
    agent_expertise: float
    previous_success_rate: float
    time_constraints: Optional[float] = None
    error_tolerance: float = 0.1
    requires_creativity: bool = False
    requires_verification: bool = True

@dataclass
class CognitiveDecision:
    recommended_mode: ReasoningMode
    confidence: float
    reasoning: str
    fallback_modes: List[ReasoningMode]
    expected_performance_gain: float
    estimated_processing_time: float
```

---

## Phase 2: Meta-Learning

### Step 1: Copy the EMO enums

```python
# src/meta_learning/models.py

from enum import Enum

class MemoryController(Enum):
    FIFO_EM = "fifo_episodic_memory"
    LRU_EM = "lru_episodic_memory"
    CLOCK_EM = "clock_episodic_memory"

class AggregationFunction(Enum):
    MEAN = "mean"
    SUM = "sum"
    TRANSFORMER = "transformer"

class CognitiveToolUsagePattern(Enum):
    SEQUENTIAL_DECOMPOSITION = "sequential_decomposition"
    VALIDATION_FOCUSED = "validation_focused"
    CREATIVE_EXPLORATION = "creative_exploration"
    DIRECT_SOLVE_VERIFY = "direct_solve_verify"
    ITERATIVE_REFINEMENT = "iterative_refinement"
```

### Step 2: Copy the EMO memory class

```python
# src/meta_learning/memory.py

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class CognitiveGradient:
    tool_name: str
    context_embedding: np.ndarray
    optimization_direction: np.ndarray
    performance_outcome: float
    usage_frequency: int
    timestamp: float
    task_similarity_threshold: float = 0.7

@dataclass
class EpisodicCognitiveMemory:
    cognitive_gradients: List[CognitiveGradient] = field(default_factory=list)
    max_capacity: int = 200
    k_neighbors: int = 5
    similarity_threshold: float = 0.7
    controller: MemoryController = MemoryController.LRU_EM
    access_history: List[int] = field(default_factory=list)
    clock_pointer: int = 0
    
    # Copy all methods from procedural_meta_learning_emo.py
```

---

## Phase 3: Consciousness & Models

### Step 1: Copy the Pydantic models

```python
# src/models/journey.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JourneyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

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

# Copy AutobiographicalEvent, AutobiographicalJourney, EpisodeBoundary, JourneyInsight
```

---

## Key Files to Copy Verbatim

These files are self-contained and can be copied with minimal changes:

1. **cognitive_tools_implementation.py** → Just update imports
2. **cognitive_meta_coordinator.py** → Just update imports
3. **procedural_meta_learning_emo.py** → Just update imports
4. **autobiographical_journey.py** → Copy directly

---

## Import Updates Needed

### D2 (Current)

```python
from .cognitive_tools_implementation import (
    ResearchValidatedCognitiveOrchestrator,
    CognitiveToolCall,
    CognitiveToolResponse
)
from .cognitive_meta_coordinator import (
    CognitiveContext,
    CognitiveDecision,
    ReasoningMode
)
```

### D3 (Target)

```python
from dionysus3_core.cognitive_tools import (
    ResearchValidatedCognitiveOrchestrator,
    CognitiveToolCall,
    CognitiveToolResponse
)
from dionysus3_core.meta_coordinator import (
    CognitiveContext,
    CognitiveDecision,
    ReasoningMode
)
```

---

## Testing After Port

### Quick Smoke Test

```python
# test_cognitive_tools.py

import asyncio
from dionysus3_core.cognitive_tools import ResearchValidatedCognitiveOrchestrator

async def test():
    orch = ResearchValidatedCognitiveOrchestrator()
    
    # Test understand_question
    result = await orch.execute_cognitive_tool(
        CognitiveToolCall("understand_question", {"question": "Solve x^2 + 5x + 6 = 0"})
    )
    assert result.success
    print("✅ understand_question works")
    
    # Test orchestrator
    enhanced = await orch.enhance_agent_reasoning(
        "test_agent",
        "What is 2+2?",
        {}
    )
    assert enhanced["cognitive_enhancement_applied"]
    print("✅ enhancement works")

asyncio.run(test())
```

### EMO Test

```python
# test_emo.py

import asyncio
from dionysus3_core.meta_learning import create_emo_optimizer_adaptive, CognitiveContext

async def test():
    optimizer = create_emo_optimizer_adaptive()
    
    context = CognitiveContext(
        task_complexity=0.7,
        domain_type="mathematical",
        agent_expertise=0.8,
        previous_success_rate=0.75
    )
    
    sequence, metrics = await optimizer.optimize_cognitive_tool_usage(
        context,
        ["understand_question", "recall_related"],
        0.75
    )
    
    print(f"Optimized sequence: {sequence}")
    print(f"Memory hits: {metrics['retrieval_statistics']['hit_rate']}")

asyncio.run(test())
```

---

## Common Gotchas

1. **numpy dependency** - EMO uses np.ndarray for embeddings
2. **asyncio** - All main methods are async
3. **Optional epLSTM** - Code gracefully degrades when not available
4. **MCP fallback** - cognitive_tools_mcp.py has stub classes if mcp not installed
5. **Constitutional compliance** - Keep `mock_data: bool = True` flags

---

## Total Effort Estimate

| Phase | Files | Lines | Effort |
|-------|-------|-------|--------|
| 1. Core Cognitive | 2 | ~1,100 | 2-4 hours |
| 2. Meta-Learning | 3 | ~2,200 | 4-8 hours |
| 3. Consciousness | 4 | ~2,000 | 4-8 hours |
| **Total** | **9** | **~5,300** | **10-20 hours** |

Most of the work is reorganizing imports and testing. The code itself is solid.
