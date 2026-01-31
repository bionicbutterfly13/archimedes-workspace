#!/usr/bin/env python3
"""
Graphiti Bridge - Routes Archimedes' memory to Neo4j temporal knowledge graph.

This module provides the synaptic bridge between flat-file memory and the
graph-based memory architecture that supports:
- Attractor basin routing
- Meme valve propagation  
- Temporal validity tracking
- Meta-episodic learning
- Autobiographical memory with diff tracking

Usage:
    from lib.graphiti_bridge import MemoryBridge
    
    bridge = MemoryBridge()
    bridge.ingest_concept("Triple-Bind", {
        "definition": "Multiplicative trap where intelligence weaponizes against embodiment",
        "components": ["insight_without_execution", "intellectualization_fortress", "shame_spiral"],
        "framework": "analytical_empath"
    })
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: neo4j driver not installed. Run: pip install neo4j")


@dataclass
class Concept:
    """A concept node in the knowledge graph."""
    name: str
    definition: str
    framework: str
    components: List[str] = None
    sources: List[str] = None
    created_at: str = None
    valid_from: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.valid_from is None:
            self.valid_from = self.created_at
        if self.components is None:
            self.components = []
        if self.sources is None:
            self.sources = []


@dataclass  
class SessionMemory:
    """A session memory node tracking what happened in a conversation."""
    session_id: str
    date: str
    summary: str
    concepts_discussed: List[str]
    artifacts_created: List[str]
    insights: List[str]
    next_steps: List[str]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class UserPreference:
    """Tracks user preferences with temporal validity for diff tracking."""
    key: str
    value: Any
    context: str
    valid_from: str = None
    valid_until: str = None  # None means currently valid
    
    def __post_init__(self):
        if self.valid_from is None:
            self.valid_from = datetime.now(timezone.utc).isoformat()


class MemoryBridge:
    """
    Bridge between Clawdbot's file-based memory and Neo4j graph memory.
    
    Provides:
    - Concept ingestion with relationship mapping
    - Session memory tracking
    - User preference evolution (the "diff of the person")
    - Framework hierarchy navigation
    """
    
    def __init__(
        self,
        neo4j_uri: str = None,
        neo4j_user: str = None,
        neo4j_password: str = None
    ):
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD", "dionysus2026")
        
        self._driver = None
        
    @property
    def driver(self):
        """Lazy-load Neo4j driver."""
        if self._driver is None:
            if not NEO4J_AVAILABLE:
                raise RuntimeError("neo4j driver not installed")
            self._driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
        return self._driver
    
    def close(self):
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    # =========================================================================
    # Schema Setup
    # =========================================================================
    
    def setup_schema(self):
        """Create indexes and constraints for the memory graph."""
        with self.driver.session() as session:
            # Constraints for uniqueness
            session.run("""
                CREATE CONSTRAINT concept_name IF NOT EXISTS
                FOR (c:Concept) REQUIRE c.name IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT framework_name IF NOT EXISTS
                FOR (f:Framework) REQUIRE f.name IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT session_id IF NOT EXISTS
                FOR (s:Session) REQUIRE s.session_id IS UNIQUE
            """)
            
            # Indexes for common queries
            session.run("""
                CREATE INDEX concept_framework IF NOT EXISTS
                FOR (c:Concept) ON (c.framework)
            """)
            session.run("""
                CREATE INDEX session_date IF NOT EXISTS
                FOR (s:Session) ON (s.date)
            """)
            session.run("""
                CREATE INDEX preference_key IF NOT EXISTS
                FOR (p:Preference) ON (p.key)
            """)
            
        print("Schema setup complete.")
    
    # =========================================================================
    # Concept Operations
    # =========================================================================
    
    def ingest_concept(self, concept: Concept) -> str:
        """
        Ingest a concept into the knowledge graph.
        
        Returns the concept's node ID.
        """
        with self.driver.session() as session:
            result = session.run("""
                MERGE (c:Concept {name: $name})
                SET c.definition = $definition,
                    c.framework = $framework,
                    c.components = $components,
                    c.sources = $sources,
                    c.created_at = $created_at,
                    c.valid_from = $valid_from,
                    c.updated_at = datetime()
                
                WITH c
                MERGE (f:Framework {name: $framework})
                MERGE (c)-[:BELONGS_TO]->(f)
                
                RETURN elementId(c) as id
            """, **asdict(concept))
            
            record = result.single()
            return record["id"] if record else None
    
    def link_concepts(self, from_concept: str, to_concept: str, relationship: str = "RELATES_TO", properties: Dict = None):
        """Create a relationship between two concepts."""
        props = properties or {}
        props["created_at"] = datetime.now(timezone.utc).isoformat()
        
        with self.driver.session() as session:
            session.run(f"""
                MATCH (a:Concept {{name: $from_name}})
                MATCH (b:Concept {{name: $to_name}})
                MERGE (a)-[r:{relationship}]->(b)
                SET r += $props
            """, from_name=from_concept, to_name=to_concept, props=props)
    
    def get_concept(self, name: str) -> Optional[Dict]:
        """Retrieve a concept by name."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $name})
                OPTIONAL MATCH (c)-[:BELONGS_TO]->(f:Framework)
                OPTIONAL MATCH (c)-[r]->(related:Concept)
                RETURN c, f.name as framework, 
                       collect({concept: related.name, rel: type(r)}) as relationships
            """, name=name)
            
            record = result.single()
            if not record:
                return None
            
            concept = dict(record["c"])
            concept["framework"] = record["framework"]
            concept["relationships"] = [r for r in record["relationships"] if r["concept"]]
            return concept
    
    # =========================================================================
    # Session Memory Operations  
    # =========================================================================
    
    def record_session(self, memory: SessionMemory) -> str:
        """Record a session in the knowledge graph."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (s:Session {session_id: $session_id})
                SET s.date = $date,
                    s.summary = $summary,
                    s.concepts_discussed = $concepts_discussed,
                    s.artifacts_created = $artifacts_created,
                    s.insights = $insights,
                    s.next_steps = $next_steps,
                    s.created_at = $created_at
                
                WITH s
                UNWIND $concepts_discussed as concept_name
                MATCH (c:Concept {name: concept_name})
                MERGE (s)-[:DISCUSSED]->(c)
                
                RETURN elementId(s) as id
            """, **asdict(memory))
            
            record = result.single()
            return record["id"] if record else None
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent sessions ordered by date."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Session)
                RETURN s
                ORDER BY s.date DESC
                LIMIT $limit
            """, limit=limit)
            
            return [dict(record["s"]) for record in result]
    
    # =========================================================================
    # User Preference Evolution (The "Diff of the Person")
    # =========================================================================
    
    def set_preference(self, pref: UserPreference):
        """
        Set a user preference with temporal tracking.
        
        If the preference already exists with a different value,
        the old one is marked with valid_until and a new one created.
        This creates the "diff" of how the user evolves.
        """
        with self.driver.session() as session:
            # First, check if there's an existing current preference
            existing = session.run("""
                MATCH (p:Preference {key: $key})
                WHERE p.valid_until IS NULL
                RETURN p.value as value, elementId(p) as id
            """, key=pref.key).single()
            
            if existing and existing["value"] != pref.value:
                # Mark old preference as no longer valid
                session.run("""
                    MATCH (p:Preference {key: $key})
                    WHERE p.valid_until IS NULL
                    SET p.valid_until = $now
                """, key=pref.key, now=pref.valid_from)
            
            # Create new preference
            session.run("""
                CREATE (p:Preference {
                    key: $key,
                    value: $value,
                    context: $context,
                    valid_from: $valid_from,
                    valid_until: $valid_until
                })
            """, **asdict(pref))
    
    def get_preference_history(self, key: str) -> List[Dict]:
        """Get the evolution history of a preference."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Preference {key: $key})
                RETURN p
                ORDER BY p.valid_from DESC
            """, key=key)
            
            return [dict(record["p"]) for record in result]
    
    def get_current_preferences(self) -> Dict[str, Any]:
        """Get all currently valid preferences."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Preference)
                WHERE p.valid_until IS NULL
                RETURN p.key as key, p.value as value
            """)
            
            return {record["key"]: record["value"] for record in result}
    
    # =========================================================================
    # Framework Navigation (Document-like traversal)
    # =========================================================================
    
    def get_framework(self, name: str, depth: int = 2) -> Dict:
        """
        Get a framework with nested concepts up to specified depth.
        
        This enables the "search the avatar like a document" pattern -
        you can drill into nested sub-elements.
        """
        with self.driver.session() as session:
            # Get the framework and its direct concepts
            result = session.run("""
                MATCH (f:Framework {name: $name})
                OPTIONAL MATCH (c:Concept)-[:BELONGS_TO]->(f)
                RETURN f, collect(c) as concepts
            """, name=name)
            
            record = result.single()
            if not record:
                return None
            
            framework = dict(record["f"]) if record["f"] else {"name": name}
            framework["concepts"] = {}
            
            for concept in record["concepts"]:
                if concept:
                    c = dict(concept)
                    c_name = c["name"]
                    
                    # Get related concepts (sub-elements)
                    if depth > 1:
                        related = session.run("""
                            MATCH (c:Concept {name: $name})-[r]->(related:Concept)
                            RETURN related, type(r) as rel_type
                        """, name=c_name)
                        
                        c["related"] = [
                            {"name": dict(r["related"])["name"], "relationship": r["rel_type"]}
                            for r in related
                        ]
                    
                    framework["concepts"][c_name] = c
            
            return framework
    
    # =========================================================================
    # Bulk Ingestion from Markdown
    # =========================================================================
    
    def ingest_framework_from_markdown(self, filepath: str, framework_name: str):
        """
        Parse a markdown framework document and ingest it into the graph.
        
        Extracts:
        - Section headers as concepts
        - Bullet points as components
        - Tables as structured data
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        content = path.read_text()
        
        # Create the framework node
        with self.driver.session() as session:
            session.run("""
                MERGE (f:Framework {name: $name})
                SET f.source_file = $source,
                    f.ingested_at = datetime()
            """, name=framework_name, source=str(filepath))
        
        # Parse sections (## headers become concepts)
        current_concept = None
        current_definition = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                # Save previous concept
                if current_concept:
                    self.ingest_concept(Concept(
                        name=current_concept,
                        definition='\n'.join(current_definition).strip(),
                        framework=framework_name
                    ))
                
                current_concept = line[3:].strip()
                current_definition = []
            elif line.startswith('### '):
                # Sub-concepts become related
                sub_concept = line[4:].strip()
                if current_concept:
                    current_definition.append(f"**{sub_concept}**")
            elif current_concept:
                current_definition.append(line)
        
        # Save last concept
        if current_concept:
            self.ingest_concept(Concept(
                name=current_concept,
                definition='\n'.join(current_definition).strip(),
                framework=framework_name
            ))
        
        print(f"Ingested framework '{framework_name}' from {filepath}")


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI for memory bridge operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Graphiti Memory Bridge")
    parser.add_argument("command", choices=["setup", "ingest", "query", "status"])
    parser.add_argument("--file", "-f", help="File to ingest")
    parser.add_argument("--framework", help="Framework name")
    parser.add_argument("--concept", help="Concept to query")
    
    args = parser.parse_args()
    
    bridge = MemoryBridge()
    
    try:
        if args.command == "setup":
            bridge.setup_schema()
            print("Schema setup complete.")
            
        elif args.command == "ingest":
            if not args.file or not args.framework:
                print("Error: --file and --framework required for ingest")
                return
            bridge.ingest_framework_from_markdown(args.file, args.framework)
            
        elif args.command == "query":
            if args.concept:
                result = bridge.get_concept(args.concept)
                print(json.dumps(result, indent=2, default=str))
            elif args.framework:
                result = bridge.get_framework(args.framework)
                print(json.dumps(result, indent=2, default=str))
            else:
                print("Error: --concept or --framework required for query")
                
        elif args.command == "status":
            with bridge.driver.session() as session:
                counts = session.run("""
                    MATCH (c:Concept) WITH count(c) as concepts
                    MATCH (f:Framework) WITH concepts, count(f) as frameworks
                    MATCH (s:Session) WITH concepts, frameworks, count(s) as sessions
                    MATCH (p:Preference) 
                    RETURN concepts, frameworks, sessions, count(p) as preferences
                """).single()
                
                print(f"Concepts: {counts['concepts']}")
                print(f"Frameworks: {counts['frameworks']}")
                print(f"Sessions: {counts['sessions']}")
                print(f"Preferences: {counts['preferences']}")
                
    finally:
        bridge.close()


if __name__ == "__main__":
    main()
