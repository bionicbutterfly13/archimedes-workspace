#!/usr/bin/env python3
"""
Ingest the Analytical Empath Framework into Graphiti/Neo4j.

This script converts the framework markdown into structured episodes
for temporal knowledge graph storage.

Usage:
    export OPENAI_API_KEY="your-key"
    python ingest_framework.py

Requirements:
    pip install graphiti-core neo4j
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import Optional

# Check for API key early
if not os.environ.get("OPENAI_API_KEY"):
    print("⚠️  OPENAI_API_KEY not set. Graphiti requires this for embeddings.")
    print("   Set it with: export OPENAI_API_KEY='your-key'")
    print("   Continuing with schema creation only...")
    EMBEDDINGS_AVAILABLE = False
else:
    EMBEDDINGS_AVAILABLE = True

try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    GRAPHITI_AVAILABLE = True
except ImportError:
    print("⚠️  graphiti-core not installed. Install with: pip install graphiti-core")
    GRAPHITI_AVAILABLE = False

from neo4j import GraphDatabase

# Configuration
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

# Framework data structured for ingestion
FRAMEWORK_EPISODES = [
    {
        "name": "Framework Overview",
        "episode_type": "text",
        "content": """
The Analytical Empath Execution Framework addresses the insight-embodiment gap in high-performing 
individuals with exceptional analytical capacity but compromised execution architecture. This isn't 
a character flaw—it's a structural reality where multiple neurological systems create compounding 
barriers to action. Traditional self-help fails because it assumes individuals can self-regulate 
at the exact moment their biological capacity for regulation is offline. The solution is Externalized 
Decision Structures—scaffolding that extends the mind into the environment.
""",
        "source_description": "Framework Executive Summary",
    },
    {
        "name": "Triple-Bind Siege",
        "episode_type": "text", 
        "content": """
The Triple-Bind Siege is a multiplicative trap where intelligence becomes weaponized against embodiment.

Bind 1 - Insight without Execution: There's a structural gap between knowing and doing. The person sees 
the answer but can't reach it.

Bind 2 - Intellectualization as Fortress: Analytical sophistication is deployed to AVOID the discomfort 
of dysfunction. This defense mechanism perpetuates the problem.

Bind 3 - Shame Spiral Impairs Recovery: Each failure weakens the ACC and prefrontal systems needed to 
break the cycle. Being smarter means being MORE trapped, not less.

Key insight: These binds MULTIPLY, not add. High insight means clear visibility of failure. 
Intellectualization builds theories instead of acting. Shame weakens escape circuits.
""",
        "source_description": "Part I: Problem Architecture - Section 1",
    },
    {
        "name": "Empathic Override",
        "episode_type": "text",
        "content": """
The Empathic Override explains why the analytical empath specifically freezes.

The mechanism: The Mirror Neuron System becomes hyperactive, absorbing others' emotions, expectations, 
and needs as HIGH PRIORITY signals. This consumes bandwidth. Meanwhile, the Interoceptive System 
(internal body signals, task signals) becomes functionally OFFLINE, creating an interoceptive blackout.
The person becomes "pilotless in their own skin" and enters a FREEZE state.

This is NOT laziness. This is NOT resistance. The nervous system has already prioritized external 
emotional signals over internal task signals. Asking for willpower is asking the pilot to fly a 
plane they're not in.

Clinical grounding: The anterior insula is shared between interoception and empathy. When mirroring 
dominates, self-signal is suppressed. The individual becomes attuned to everyone else but out-of-body.
""",
        "source_description": "Part I: Problem Architecture - Section 2",
    },
    {
        "name": "ACC Atrophy Loop", 
        "episode_type": "text",
        "content": """
The ACC Atrophy Loop explains why "trying harder" becomes neurologically impossible.

The cycle: High Drive (Intention) → ACC engages with effort → Execution Gap (structural) → 
Task incomplete → ACC doesn't get completion signal → ACC atrophies → "Try harder" now requires 
MORE activation from a WEAKER structure → guaranteed failure.

Key insight: The anterior cingulate cortex (willpower center) only strengthens through successful 
completion of difficult tasks. If structural gaps prevent completion, capacity atrophies despite 
high drive.

Implication: Shame-based motivation backfires catastrophically. Each failed attempt weakens the system.
""",
        "source_description": "Part I: Problem Architecture - Section 3",
    },
    {
        "name": "Finality Illusion",
        "episode_type": "text",
        "content": """
The Finality Illusion is the false prediction that triggers abandonment.

Mechanism: The brain caught in a mental replay loop generates a sensory error—it incorrectly signals 
that recovery within the current context is physiologically impossible.

Result: Abandonment feels like the only LOGICAL path to relief.

The Replay-Abandon-Restart Cycle:
1. Mental loop begins → brain predicts recovery impossible
2. Abandonment offers immediate relief (dopamine hit of "fresh start")
3. Underlying mechanism untouched
4. Next project triggers same collapse
5. Pattern reinforces: "I can't finish things"

Intervention point: Restore external recovery signal BEFORE false prediction "locks in."
""",
        "source_description": "Part I: Problem Architecture - Section 4",
    },
    {
        "name": "Congested Library (Filter Failure)",
        "episode_type": "text",
        "content": """
The Congested Library explains why sophisticated insight fails to produce concrete steps.

The Five-Layer Cognitive Architecture:
1. Strategist - High-level optimization, learning (Failure: over-optimizes, never executes)
2. Narrator - Weaves experience into coherent history (Failure: floods workspace with "relevant" backstory)
3. Filter (Reference Librarian) - Gates what reaches immediate workspace (Failure: overwhelmed, everything feels relevant)
4. Workspace (Reading Desk) - Immediate action context (Failure: flooded with meta-patterns, can't isolate next step)
5. Execution - Embodied action (Failure: decoupled from intention—structurally severed)

The bottleneck is the Filter. When attractor basins (memory resonance patterns) are overwhelmed, 
the reading desk becomes too cluttered for action.
""",
        "source_description": "Part I: Problem Architecture - Section 5",
    },
    {
        "name": "Externalized Decision Structures",
        "episode_type": "text",
        "content": """
Externalized Decision Structures (The Exoskeleton) are external scaffolding that extends the mind 
into the environment.

Five Core Functions:
1. Internal Governor Offload - Bypass reliance on willpower during dysregulation by placing decision 
   pathways outside the self
2. False Prediction Correction - Prevent abandonment cycles via visible recovery pathway that restores 
   signal early
3. Synaptic Bridge - Connect intention to action when internal wiring fails through external cue at 
   point of performance
4. Vital Pause Framework - Enable observation without intellectualization through externalized 
   categorization of experience
5. Identity-Action Synchronization - Maintain self-concept under load; architecture holds intention 
   when internal system dysregulates

Key distinction: These are SCAFFOLDING (temporary, capacity-building) not REPLACEMENT. Successful 
completion strengthens ACC, building internal capacity over time.
""",
        "source_description": "Part II: Solution Architecture - Section 1",
    },
    {
        "name": "Somatic Ignition Switch",
        "episode_type": "text",
        "content": """
The Somatic Ignition Switch is a body-based bypass for analytical paralysis.

Core insight: A frozen analytical system needs ACTIVATION, not sedation. Traditional relaxation 
techniques sedate a system that needs to move.

Four Components:
1. Safe Up-Regulation - Activation protocols, not calming techniques. Generate neural energy without 
   threat response.
2. Rhythmic Grounding - Sensory rhythms bypass analytical loop. Bottom-up process (body → brain) 
   creates movement while mind buffers.
3. Micro-Yes (Titration) - Tiny physical movement BEFORE mind can argue. Secure body consent, bypass 
   threat-detection.
4. Somatic Anchor - Physical cue at exact moment action required. Interrupt mental replay, provide 
   traction.

Why it works: The "micro-yes" is a low-cost motor action that generates confirming sensory feedback, 
reducing prediction error without requiring full cognitive commitment.
""",
        "source_description": "Part II: Solution Architecture - Section 2",
    },
    {
        "name": "Five Windows of Awareness",
        "episode_type": "text",
        "content": """
The Five Windows of Awareness (Vital Pause Protocol) is a real-time observation framework preventing 
the intellectualization trap.

The Five Windows:
1. Sensations — Physical body signals
2. Actions — Current behavior
3. Emotions — Core feeling state
4. Impulses — Sudden urges
5. Thoughts — Internal dialogue

Three-Step Training Progression:
Phase 1 - Detection: Notice attention drift → Build metacognitive awareness
Phase 2 - Identification: Which of 5 windows is pulling? → Prevent global flooding
Phase 3 - Vital Pause: Observe without defensive action → Break stimulus → reaction chain

Key insight: Identifying WHICH domain (sensation vs. thought vs. impulse) prevents analyzing the 
whole system at once. Scalpel, not floodlight.
""",
        "source_description": "Part II: Solution Architecture - Section 3",
    },
    {
        "name": "Three-Phase Progression",
        "episode_type": "text",
        "content": """
The Three-Phase Progression moves from fragile to fortified stability.

Phase 1 - Predictive Self-Mapping: 
Focus: Locate where internal signals break down
Outcome: Map personal execution gaps

Phase 2 - Repatterning:
Focus: Design external recovery pathways
Outcome: Install scaffolding at failure points

Phase 3 - Stabilization:
Focus: Architecture becomes permanent extension
Outcome: Identity-action synchronization achieved

End state: External exoskeleton maintains coherence under load. Self-concept no longer shattered 
by execution failures.
""",
        "source_description": "Part II: Solution Architecture - Section 4",
    },
    {
        "name": "Theoretical Foundations",
        "episode_type": "text",
        "content": """
The framework is grounded in several theoretical foundations:

1. Predictive Coding / Active Inference (Karl Friston, Montgomery 2024):
   - Traditional view: ADHD = broken attention filter
   - Predictive coding view: ADHD = different prediction weighting
   - External structures provide environmental predictability that stabilizes chaotic internal predictions

2. Extended Mind Theory (Clark & Chalmers 1998):
   - External objects can be genuine constituents of cognitive processes
   - For this population, extended cognition is an architectural REQUIREMENT, not a metaphor

3. Point of Performance Intervention (Russell Barkley):
   - ADHD interventions fail when placed upstream of the action moment
   - The exoskeleton operates at the point of performance—not planning, not intention, but the 
     exact moment action is required

4. Distributed Cognition (Hutchins, Kirsh, Annie Murphy Paul):
   - Cognition is distributed across brain, body, and environment
   - Epistemic actions simplify cognitive tasks
   - Cognitive offloading reduces working memory load
""",
        "source_description": "Part III: Theoretical Foundation",
    },
    {
        "name": "Key Researchers",
        "episode_type": "text",
        "content": """
Key researchers whose work informs the Analytical Empath Framework:

- Tania Singer: Empathy, interoception, neural overlap between self and other
- A.D. Craig: Interoceptive awareness and the insula as integration hub
- Karl Friston: Predictive coding, active inference, free energy principle
- Russell Barkley: ADHD clinical research, point-of-performance interventions
- Andy Clark: Extended mind, supersizing cognition, scaffolded thought
- David Kirsh: Epistemic actions, cognitive offloading, thinking with external representations
- Antonio Damasio: Somatic marker hypothesis, emotions in decision-making
""",
        "source_description": "Research Sources",
    },
]


def create_neo4j_constraints(driver):
    """Create Neo4j constraints and indexes for the schema."""
    constraints = [
        "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT mechanism_name IF NOT EXISTS FOR (m:Mechanism) REQUIRE m.name IS UNIQUE",
        "CREATE CONSTRAINT intervention_name IF NOT EXISTS FOR (i:Intervention) REQUIRE i.name IS UNIQUE",
        "CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT structure_name IF NOT EXISTS FOR (s:Structure) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT researcher_name IF NOT EXISTS FOR (r:Researcher) REQUIRE r.name IS UNIQUE",
        "CREATE CONSTRAINT theory_name IF NOT EXISTS FOR (t:Theory) REQUIRE t.name IS UNIQUE",
    ]
    
    indexes = [
        "CREATE INDEX concept_category IF NOT EXISTS FOR (c:Concept) ON (c.category)",
        "CREATE INDEX concept_part IF NOT EXISTS FOR (c:Concept) ON (c.part)",
        "CREATE FULLTEXT INDEX concept_description IF NOT EXISTS FOR (c:Concept) ON EACH [c.description]",
    ]
    
    with driver.session() as session:
        for constraint in constraints:
            try:
                session.run(constraint)
                print(f"✓ Created constraint")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  Constraint already exists")
                else:
                    print(f"  Warning: {e}")
        
        for index in indexes:
            try:
                session.run(index)
                print(f"✓ Created index")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  Index already exists")
                else:
                    print(f"  Warning: {e}")


def create_base_nodes(driver):
    """Create the core framework nodes directly in Neo4j."""
    
    nodes = [
        # Core Concepts
        ("Concept", {
            "name": "Analytical Empath",
            "description": "Individual with high insight + empathic sensitivity + execution dysfunction",
            "category": "Core Definition"
        }),
        ("Concept", {
            "name": "Triple-Bind Siege", 
            "description": "Multiplicative trap where intelligence becomes weaponized against embodiment",
            "category": "Problem Architecture",
            "part": "I"
        }),
        ("Concept", {
            "name": "Empathic Override",
            "description": "Hyperactive mirroring consumes bandwidth, suppressing interoception",
            "category": "Problem Architecture",
            "part": "I"
        }),
        ("Concept", {
            "name": "ACC Atrophy Loop",
            "description": "Willpower center weakens through repeated incomplete efforts",
            "category": "Problem Architecture", 
            "part": "I"
        }),
        ("Concept", {
            "name": "Finality Illusion",
            "description": "False prediction that recovery is physiologically impossible",
            "category": "Problem Architecture",
            "part": "I"
        }),
        ("Concept", {
            "name": "Congested Library",
            "description": "Filter failure flooding workspace with archive material",
            "category": "Problem Architecture",
            "part": "I"
        }),
        
        # Interventions
        ("Intervention", {
            "name": "External Exoskeleton",
            "description": "Architecture extending mind into environment",
            "function": "Scaffold cognition externally when internal systems dysregulate",
            "phase": 2
        }),
        ("Intervention", {
            "name": "Somatic Ignition Switch",
            "description": "Body-based activation bypassing analytical paralysis",
            "function": "Use body to bypass frozen mind",
            "phase": 1
        }),
        ("Intervention", {
            "name": "Micro-Yes",
            "description": "Small physical movement securing body consent before mind argues",
            "function": "Titrated commitment bypassing threat detection",
            "phase": 1
        }),
        ("Intervention", {
            "name": "Five Windows of Awareness",
            "description": "Sensations, Actions, Emotions, Impulses, Thoughts observation framework",
            "function": "Categorical observation preventing global flooding",
            "phase": 2
        }),
        ("Intervention", {
            "name": "Vital Pause",
            "description": "Observing internal state without defensive action",
            "function": "Break stimulus-reaction chain",
            "phase": 2
        }),
        
        # Brain Structures
        ("Structure", {
            "name": "ACC",
            "full_name": "Anterior Cingulate Cortex",
            "type": "neurological",
            "function": "Willpower, effort allocation, completion signaling"
        }),
        ("Structure", {
            "name": "Anterior Insula",
            "full_name": "Anterior Insular Cortex",
            "type": "neurological", 
            "function": "Shared substrate for interoception and empathy"
        }),
        ("Structure", {
            "name": "Mirror Neuron System",
            "type": "neurological",
            "function": "Simulating others' emotional and motor states"
        }),
        
        # Cognitive Architecture
        ("Structure", {
            "name": "Filter",
            "full_name": "Reference Librarian",
            "type": "cognitive",
            "function": "Gates what reaches immediate workspace"
        }),
        ("Structure", {
            "name": "Workspace",
            "full_name": "Reading Desk",
            "type": "cognitive",
            "function": "Immediate action context"
        }),
        
        # Theories
        ("Theory", {
            "name": "Predictive Coding",
            "description": "Brain as prediction machine, behavior driven by minimizing prediction error",
            "source": "Karl Friston"
        }),
        ("Theory", {
            "name": "Extended Mind",
            "description": "External objects can be genuine constituents of cognitive processes",
            "source": "Clark & Chalmers 1998"
        }),
        ("Theory", {
            "name": "Point of Performance",
            "description": "Interventions must occur at exact moment of action, not upstream",
            "source": "Russell Barkley"
        }),
        
        # Researchers
        ("Researcher", {
            "name": "Karl Friston",
            "field": "Computational Neuroscience",
            "key_contribution": "Predictive coding, active inference, free energy principle"
        }),
        ("Researcher", {
            "name": "Russell Barkley",
            "field": "Clinical Psychology",
            "key_contribution": "ADHD research, point-of-performance interventions"
        }),
        ("Researcher", {
            "name": "Andy Clark",
            "field": "Philosophy of Mind",
            "key_contribution": "Extended mind thesis, scaffolded cognition"
        }),
        ("Researcher", {
            "name": "Tania Singer",
            "field": "Social Neuroscience",
            "key_contribution": "Empathy, interoception, neural overlap"
        }),
        
        # Symptoms
        ("Symptom", {
            "name": "Freeze Response",
            "description": "Inability to initiate action despite intention",
            "observable": True
        }),
        ("Symptom", {
            "name": "Interoceptive Blackout",
            "description": "State of being pilotless in own skin",
            "subjective": True
        }),
        ("Symptom", {
            "name": "Replay-Abandon-Restart",
            "description": "Cycle of quitting for fresh start dopamine without resolving mechanism",
            "observable": True
        }),
    ]
    
    with driver.session() as session:
        for label, props in nodes:
            # Create node with MERGE to avoid duplicates
            props_str = ", ".join([f"{k}: ${k}" for k in props.keys()])
            query = f"MERGE (n:{label} {{{props_str}}})"
            session.run(query, **props)
        print(f"✓ Created {len(nodes)} base nodes")


def create_relationships(driver):
    """Create relationships between nodes."""
    
    relationships = [
        # Triple-Bind causes symptoms
        ("Concept", "Triple-Bind Siege", "CAUSES", "Symptom", "Freeze Response"),
        ("Concept", "Empathic Override", "CAUSES", "Symptom", "Interoceptive Blackout"),
        ("Concept", "Finality Illusion", "CAUSES", "Symptom", "Replay-Abandon-Restart"),
        
        # Structures involved in mechanisms
        ("Concept", "Empathic Override", "INVOLVES", "Structure", "Mirror Neuron System"),
        ("Concept", "Empathic Override", "INVOLVES", "Structure", "Anterior Insula"),
        ("Concept", "ACC Atrophy Loop", "INVOLVES", "Structure", "ACC"),
        ("Concept", "Congested Library", "INVOLVES", "Structure", "Filter"),
        ("Concept", "Congested Library", "INVOLVES", "Structure", "Workspace"),
        
        # Interventions address problems
        ("Intervention", "External Exoskeleton", "ADDRESSES", "Concept", "Triple-Bind Siege"),
        ("Intervention", "Somatic Ignition Switch", "ADDRESSES", "Concept", "Empathic Override"),
        ("Intervention", "Somatic Ignition Switch", "BYPASSES", "Structure", "ACC"),
        ("Intervention", "Micro-Yes", "BYPASSES", "Concept", "Finality Illusion"),
        ("Intervention", "Five Windows of Awareness", "ADDRESSES", "Concept", "Congested Library"),
        ("Intervention", "Vital Pause", "ADDRESSES", "Symptom", "Freeze Response"),
        
        # Theory supports concepts
        ("Theory", "Predictive Coding", "SUPPORTS", "Concept", "ACC Atrophy Loop"),
        ("Theory", "Predictive Coding", "SUPPORTS", "Concept", "Finality Illusion"),
        ("Theory", "Extended Mind", "SUPPORTS", "Intervention", "External Exoskeleton"),
        ("Theory", "Point of Performance", "SUPPORTS", "Intervention", "Somatic Ignition Switch"),
        
        # Researchers developed theories
        ("Researcher", "Karl Friston", "DEVELOPED", "Theory", "Predictive Coding"),
        ("Researcher", "Andy Clark", "DEVELOPED", "Theory", "Extended Mind"),
        ("Researcher", "Russell Barkley", "DEVELOPED", "Theory", "Point of Performance"),
    ]
    
    with driver.session() as session:
        for from_label, from_name, rel_type, to_label, to_name in relationships:
            query = f"""
            MATCH (a:{from_label} {{name: $from_name}})
            MATCH (b:{to_label} {{name: $to_name}})
            MERGE (a)-[r:{rel_type}]->(b)
            """
            session.run(query, from_name=from_name, to_name=to_name)
        print(f"✓ Created {len(relationships)} relationships")


async def ingest_via_graphiti(episodes):
    """Ingest episodes using Graphiti for temporal tracking and embeddings."""
    if not GRAPHITI_AVAILABLE:
        print("⚠️  Skipping Graphiti ingestion (not installed)")
        return
    
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping Graphiti ingestion (no OPENAI_API_KEY)")
        return
    
    print("\n📊 Ingesting episodes via Graphiti...")
    
    graphiti = Graphiti(
        NEO4J_URI,
        NEO4J_USER, 
        NEO4J_PASSWORD
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        
        for i, episode in enumerate(episodes):
            print(f"  Ingesting: {episode['name']}...")
            await graphiti.add_episode(
                name=episode['name'],
                episode_body=episode['content'].strip(),
                source=EpisodeType.text,
                source_description=episode['source_description'],
                group_id="analytical-empath-framework",
            )
        
        print(f"✓ Ingested {len(episodes)} episodes via Graphiti")
        
    finally:
        await graphiti.close()


def verify_graph(driver):
    """Print statistics about the created graph."""
    with driver.session() as session:
        # Count nodes by label
        result = session.run("""
            CALL db.labels() YIELD label
            CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {}) 
            YIELD value
            RETURN label, value.count as count
            ORDER BY count DESC
        """)
        
        # Fallback if APOC not installed
        try:
            counts = list(result)
        except:
            counts = []
            for label in ["Concept", "Intervention", "Structure", "Theory", "Researcher", "Symptom"]:
                r = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = r.single()["count"]
                if count > 0:
                    counts.append({"label": label, "count": count})
        
        print("\n📈 Graph Statistics:")
        if counts:
            for row in counts:
                if isinstance(row, dict):
                    print(f"   {row['label']}: {row['count']}")
                else:
                    print(f"   {row['label']}: {row['count']}")
        
        # Count relationships
        rel_result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC")
        print("\n   Relationships:")
        for row in rel_result:
            print(f"   {row['type']}: {row['count']}")


def main():
    print("🧠 Analytical Empath Framework → Neo4j/Graphiti Ingestion")
    print("=" * 60)
    
    # Connect to Neo4j
    print(f"\n📡 Connecting to Neo4j at {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        # Verify connection
        driver.verify_connectivity()
        print("✓ Connected to Neo4j")
        
        # Create schema
        print("\n📐 Creating schema constraints and indexes...")
        create_neo4j_constraints(driver)
        
        # Create base nodes
        print("\n🏗️  Creating base nodes...")
        create_base_nodes(driver)
        
        # Create relationships
        print("\n🔗 Creating relationships...")
        create_relationships(driver)
        
        # Ingest via Graphiti (if available)
        asyncio.run(ingest_via_graphiti(FRAMEWORK_EPISODES))
        
        # Verify
        verify_graph(driver)
        
        print("\n✅ Ingestion complete!")
        print("\n📋 Next steps:")
        print("   1. Visit http://localhost:7474 to explore the graph")
        print("   2. Set OPENAI_API_KEY and re-run for Graphiti embeddings")
        print("   3. Configure Clawdbot MCP to use Graphiti server")
        
    finally:
        driver.close()


if __name__ == "__main__":
    main()
