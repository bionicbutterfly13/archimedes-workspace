# Cognitive Tools Deep Dive

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DAEDALUS COGNITIVE COORDINATOR                        │
│                    (cognitive_tools_mcp.py)                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     MCP Server Layer                               │ │
│  │  • CognitiveToolsMCPServer - System-wide cognitive tool access     │ │
│  │  • DaedalusCognitiveCoordinator - Daedalus-level coordination      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   META-COGNITIVE COORDINATOR                             │
│                   (cognitive_meta_coordinator.py)                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  CognitiveMetaCoordinator                                          │ │
│  │  • decide_reasoning_approach() - Which mode to use?                │ │
│  │  • _score_direct_reasoning()                                       │ │
│  │  • _score_cognitive_tools()                                        │ │
│  │  • _score_tree_of_thought()                                        │ │
│  │  • _score_hybrid_approach()                                        │ │
│  │  • _score_meta_cognitive()                                         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AgentCognitiveInterface                                           │ │
│  │  • enhance_reasoning() - Apply cognitive enhancement               │ │
│  │  • _execute_cognitive_tools_reasoning()                            │ │
│  │  • _execute_tree_of_thought_reasoning()                            │ │
│  │  • _execute_hybrid_reasoning()                                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  COGNITIVE TOOLS ORCHESTRATOR                            │
│                  (cognitive_tools_implementation.py)                     │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  ResearchValidatedCognitiveOrchestrator                            │ │
│  │  • get_research_validated_system_prompt() - The magic prompt       │ │
│  │  • execute_cognitive_tool() - Run individual tools                 │ │
│  │  • enhance_agent_reasoning() - Full enhancement pipeline           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐              │
│  │understand_│ │recall_    │ │examine_   │ │backtrack- │              │
│  │question   │ │related    │ │answer     │ │ing        │              │
│  │+4-8%      │ │+6-10%     │ │critical   │ │+26.7%     │              │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

## The 4 Research-Validated Cognitive Tools

### 1. understand_question (Problem Decomposition)

**Research Basis:** Anderson et al., 1997 - Cognitive architecture principles

**What It Does:**
- Identifies core mathematical concepts
- Extracts and categorizes symbols, variables, functions
- Rephrases problem into step-by-step sequence
- Highlights applicable theorems/techniques
- **Does NOT provide the answer**

**The Prompt (from paper Appendix A.3):**
```python
prompt = f"""You are a mathematical reasoning assistant designed to analyze 
and break down complex mathematical problems into structured steps...

1. Identify the core mathematical concepts involved
2. Extract and categorize relevant symbols, variables, and functions
3. Rephrase the problem into a step-by-step sequence
4. Highlight any known theorems or techniques
5. DO NOT provide any answer to the question, only provide instructions

Question: {question}
"""
```

**Performance:** +4-8% accuracy improvement

---

### 2. recall_related (Analogical Reasoning)

**Research Basis:** Yasunaga et al., 2024 - Knowledge recall techniques

**What It Does:**
- Finds 2-3 similar problems from training
- Provides full problem statement for each
- Provides complete step-by-step solution
- Highlights final answers
- **Does NOT solve the current problem**

**The Prompt:**
```python
prompt = f"""You are a retrieval assistant whose purpose is to help solve 
new mathematical problems by providing solved examples of analogous problems.

Given a new math problem, your task is to:
1. Identify 2 or 3 **similar problems** that require comparable reasoning
2. For each similar problem:
   - Provide the **full problem statement**
   - Provide a **complete step-by-step solution**
   - Highlight the **final answer**

Do **not** solve the current problem.

Output Format:
Analogous Example 1:
Q: [Similar Problem 1]
A: [Step-by-step solution...]
Final Answer: ...
"""
```

**Performance:** +6-10% accuracy through pattern matching

---

### 3. examine_answer (Self-Reflection/Verification)

**Research Basis:** Shinn et al., 2023 - Metacognitive self-examination

**What It Does:**
- Verifies solution correctness
- Checks logical consistency
- Identifies miscalculations, incorrect assumptions
- Analyzes edge cases
- Tests numerical answers by plugging back
- Tests expressions by symbolic substitution

**The Prompt (abridged):**
```python
prompt = f"""You are an expert mathematical assistant tasked with 
**verifying and improving** solutions. Your role is **not to solve** 
but to critically analyze.

### **Verification Process:**
1. Understanding the Problem - Check interpretation
2. Verifying the Given Solution - Step by step
   2.a) Testing and Validation (Problem-Derived Checks)
3. Suggesting Improvements - Without solving
4. Providing a Judgment - Correct or incorrect?

### **Guidelines:**
- DO NOT provide the actual answer
- Focus only on verifying and critiquing
- Explicitly say whether the answer is correct or incorrect

Question: {question}
Current Reasoning Trace: {current_reasoning}
"""
```

**Performance:** Critical for error detection

---

### 4. backtracking (Alternative Path Exploration)

**Research Basis:** Related to Monte Carlo Tree Search (MCTS)

**What It Does:**
- Analyzes reasoning trace step by step
- Identifies first error, bad assumption, or confusion
- Proposes revised approach from that point
- Suggests better strategy if entire approach invalid

**The Prompt:**
```python
prompt = f"""You are a careful problem-solving assistant with the ability 
to backtrack from flawed logic.

Your task is to:
1. Analyze the reasoning and summarize it into different steps
2. Identify where the first error occurs (if any)
3. Propose how to revise from that point
4. If entire approach was invalid, suggest better strategy

Response format:
**Identified Issues:**
- Step X: Explain what is incorrect

**Backtrack Point:**
- Indicate the step where reasoning was still valid

**Revised Strategy (from backtrack point or new):**
- Present step-by-step strategy from this point

Be precise and critical. Always backtrack to the most recent correct step.
"""
```

**Performance:** +26.7% improvement (highest single tool impact!)

---

## Reasoning Mode Selection Logic

The meta-coordinator scores each reasoning mode and picks the best:

```python
mode_scores = {
    ReasoningMode.DIRECT: self._score_direct_reasoning(task_analysis, context),
    ReasoningMode.COGNITIVE_TOOLS: self._score_cognitive_tools(task_analysis, context),
    ReasoningMode.TREE_OF_THOUGHT: self._score_tree_of_thought(task_analysis, context),
    ReasoningMode.HYBRID_COGNITIVE_TOT: self._score_hybrid_approach(task_analysis, context),
    ReasoningMode.META_COGNITIVE: self._score_meta_cognitive(task_analysis, context)
}

recommended_mode = max(mode_scores, key=mode_scores.get)
```

### Scoring Rules:

**DIRECT (baseline):**
- +0.3 if complexity < 0.4
- +0.2 if expertise > 0.8
- +0.3 if time < 30 seconds
- +0.2 if math + logic complexity both < 0.4

**COGNITIVE_TOOLS:**
- +0.4 if complexity > 0.6 (threshold)
- +0.3 if mathematical or math complexity > 0.5 (research validated!)
- +0.2 if requires verification
- +0.2 if decomposition beneficial
- +0.2 if analogical reasoning valuable
- +0.1 if previous success > 0.7

**TREE_OF_THOUGHT:**
- +0.4 if requires creativity
- +0.3 if logical complexity > 0.7
- +0.3 if creative/strategic/planning domain
- +0.2 if error tolerance > 0.2
- +0.2 if time > 120 seconds

**HYBRID (Cognitive + ToT):**
- +0.3 if complexity > 0.8
- +0.4 if both mathematical AND creative
- +0.2 if complex verification needs
- +0.1 if high expertise

**META_COGNITIVE:**
- +0.4 if complexity > 0.9
- +0.3 if expertise < 0.5 (novel domain)
- +0.3 if previous success < 0.4 (failures)
- +0.2 if error tolerance < 0.1

---

## Performance Metrics From Research

From the paper (arXiv:2506.12115v1):

| Model | Baseline | With Cognitive Tools | Improvement |
|-------|----------|---------------------|-------------|
| GPT-4.1 (AIME 2024) | 26.7% | 43.3% | +62.5% |
| Llama3.3-70B | baseline | baseline + 26.7% | +26.7% |
| Gap to o1-preview | 100% | 6% | 94% closure |

---

## Porting Notes for D3

1. **No external dependencies** - cognitive_tools_implementation.py is self-contained
2. **Clean interfaces** - CognitiveToolCall, CognitiveToolResponse are simple dataclasses
3. **Easy testing** - Each tool has standalone execute() method
4. **LLM agnostic** - Prompts work with any model, orchestrator needs llm_interface
