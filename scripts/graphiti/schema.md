# Analytical Empath Framework - Knowledge Graph Schema

## Overview
This schema represents the Analytical Empath Framework as a temporal knowledge graph optimized for AI agent memory and retrieval.

## Entity Types

### 1. Concept
Core theoretical constructs from the framework.

**Properties:**
- `name`: String (required) - Concept name
- `description`: Text - Full description
- `summary`: Text - One-line summary for quick retrieval
- `part`: String - Framework part (I-V)
- `category`: String - Problem Architecture | Solution Architecture | Theory | Clinical Validation

**Examples:**
- Triple-Bind Siege
- Empathic Override
- ACC Atrophy Loop
- Finality Illusion
- Congested Library (Filter Failure)
- Externalized Decision Structures

### 2. Mechanism
Neurological or cognitive mechanisms.

**Properties:**
- `name`: String (required)
- `description`: Text
- `type`: biological | cognitive | behavioral
- `direction`: positive | negative | neutral

**Examples:**
- Mirror neuron hyperactivity
- Interoceptive suppression
- ACC atrophy through incomplete effort
- False prediction of recovery impossibility
- Filter overwhelm → workspace flooding

### 3. Intervention
Actionable therapeutic/practical protocols.

**Properties:**
- `name`: String (required)
- `description`: Text
- `function`: String - Core purpose
- `implementation`: Text - How to apply
- `phase`: 1 | 2 | 3 - Progression phase

**Examples:**
- Somatic Ignition Switch
- Micro-Yes (Titration)
- Five Windows of Awareness
- Vital Pause Protocol
- External Exoskeleton

### 4. Symptom
Observable manifestations of dysfunction.

**Properties:**
- `name`: String (required)
- `description`: Text
- `observable`: boolean - Can be externally observed
- `subjective`: boolean - Internally experienced

**Examples:**
- Freeze response
- "Pilotless in own skin" state
- Abandonment cycles
- Replay-Abandon-Restart pattern
- Workspace flooding

### 5. Structure
Brain regions and cognitive architecture components.

**Properties:**
- `name`: String (required)
- `full_name`: String
- `type`: neurological | cognitive
- `function`: Text

**Examples:**
- ACC (Anterior Cingulate Cortex)
- Anterior Insula
- Mirror Neuron System
- Filter (Reference Librarian)
- Workspace (Reading Desk)

### 6. Researcher
Academic sources and theorists.

**Properties:**
- `name`: String (required)
- `field`: String
- `key_contribution`: Text

**Examples:**
- Karl Friston (Predictive Coding)
- Russell Barkley (ADHD, Point of Performance)
- Andy Clark (Extended Mind)
- Tania Singer (Empathy/Interoception)
- Antonio Damasio (Somatic Markers)

### 7. Theory
Theoretical frameworks supporting the model.

**Properties:**
- `name`: String (required)
- `description`: Text
- `source`: String - Key paper/book
- `application`: Text - How it applies to framework

**Examples:**
- Predictive Coding / Active Inference
- Extended Mind Theory
- Point of Performance Intervention
- Distributed Cognition
- Somatic Marker Hypothesis

## Relationships

### Causal Relationships
```
(Mechanism) -[:CAUSES]-> (Symptom)
(Symptom) -[:LEADS_TO]-> (Symptom)
(Concept) -[:PRODUCES]-> (Symptom)
```

### Intervention Relationships
```
(Intervention) -[:ADDRESSES]-> (Mechanism)
(Intervention) -[:TREATS]-> (Symptom)
(Intervention) -[:BYPASSES]-> (Structure)
(Intervention) -[:REQUIRES]-> (Intervention)
(Intervention) -[:PRECEDES]-> (Intervention)
```

### Structural Relationships
```
(Concept) -[:PART_OF]-> (Concept)
(Mechanism) -[:INVOLVES]-> (Structure)
(Structure) -[:SHARED_WITH]-> (Structure)
(Symptom) -[:MANIFESTS_IN]-> (Structure)
```

### Knowledge Attribution
```
(Theory) -[:SUPPORTS]-> (Concept)
(Theory) -[:EXPLAINS]-> (Mechanism)
(Theory) -[:DEVELOPED_BY]-> (Researcher)
(Concept) -[:GROUNDED_IN]-> (Theory)
```

### Multiplicative Relationships (Special)
```
(Concept) -[:MULTIPLIES_WITH {effect: "exponential"}]-> (Concept)
```
Used specifically for the Triple-Bind: binds multiply, not add.

## Example Subgraph: Triple-Bind Siege

```cypher
// Create the Triple-Bind concept
CREATE (tb:Concept {
  name: "Triple-Bind Siege",
  description: "A multiplicative trap where intelligence becomes weaponized against embodiment",
  part: "I",
  category: "Problem Architecture"
})

// Create the three binds
CREATE (b1:Concept {name: "Insight without Execution", description: "Structural gap between knowing and doing"})
CREATE (b2:Concept {name: "Intellectualization as Fortress", description: "Analytical sophistication deployed to avoid discomfort"})
CREATE (b3:Concept {name: "Shame Spiral", description: "Each failure weakens ACC needed to break cycle"})

// Relationships
CREATE (b1)-[:PART_OF]->(tb)
CREATE (b2)-[:PART_OF]->(tb)
CREATE (b3)-[:PART_OF]->(tb)
CREATE (b1)-[:MULTIPLIES_WITH]->(b2)
CREATE (b2)-[:MULTIPLIES_WITH]->(b3)
CREATE (b3)-[:MULTIPLIES_WITH]->(b1)
```

## Temporal Considerations (Graphiti)

Graphiti automatically handles:
- **Episode timestamps**: When knowledge was ingested
- **Fact validity windows**: When relationships were true
- **Entity versioning**: How understanding evolved

This allows queries like:
- "What did we learn about the Empathic Override on January 15th?"
- "How has our understanding of interventions evolved?"
- "What's the most recent context about ACC atrophy?"

## Indexing Strategy

For efficient retrieval:
1. **Full-text index** on `description` fields
2. **Vector embeddings** on `summary` fields (via Graphiti)
3. **Composite index** on `category` + `part` for filtering

## Query Patterns for Clawdbot

### 1. Context Injection
"When user discusses procrastination, retrieve:"
```cypher
MATCH (c:Concept)-[:CAUSES|PRODUCES]->(s:Symptom)
WHERE s.name CONTAINS 'procrastination' OR s.name CONTAINS 'execution'
RETURN c, s
LIMIT 5
```

### 2. Intervention Lookup
"What helps with freeze response?"
```cypher
MATCH (i:Intervention)-[:TREATS|ADDRESSES]->(t)
WHERE t.name CONTAINS 'freeze' OR t.name CONTAINS 'paralysis'
RETURN i.name, i.implementation
```

### 3. Theory Grounding
"Explain the science behind this concept:"
```cypher
MATCH (c:Concept {name: $concept})-[:GROUNDED_IN]->(t:Theory)-[:DEVELOPED_BY]->(r:Researcher)
RETURN t, r
```
