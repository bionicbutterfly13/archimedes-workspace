#!/usr/bin/env python3
"""
dionysus_wake.py - Wake-up module for Archimedes (Clawdbot) to hydrate context from Dionysus

Following Conductor best practices:
1. Load constraints, workflow, best-practices
2. Reconstruct session context from episodic memory  
3. Return structured context for injection

Usage:
    python dionysus_wake.py [project_path] [cue1] [cue2] ...
    
    # Or as module:
    from dionysus_wake import wake_up
    context = wake_up(cues=["HDB offer", "neuroadaptive scaffolding"])

Author: Mani Saint-Victor, MD
"""

import json
import os
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Configuration
DIONYSUS_API = os.environ.get("DIONYSUS_API", "http://72.61.78.89:8000")
DEFAULT_PROJECT_PATH = "/Volumes/Asylum/dev/dionysus3-core"
AGENTS_DIR = Path.home() / ".claude" / "agents"
SKILLS_DIR = Path("/Volumes/Asylum/dev/dionysus3-core/skills_library")


@dataclass
class WakeUpContext:
    """Structured wake-up context from Dionysus."""
    
    # Status
    success: bool = False
    api_healthy: bool = False
    conductor_loaded: bool = False
    
    # Conductor files
    constraints_path: Optional[str] = None
    workflow_path: Optional[str] = None
    best_practices_path: Optional[str] = None
    
    # Agent roster
    agent_count: int = 0
    agent_categories: list = field(default_factory=list)
    
    # Skills
    skills: list = field(default_factory=list)
    
    # Session reconstruction
    coherence_score: float = 0.0
    fragment_count: int = 0
    reconstruction_time_ms: float = 0.0
    compact_context: str = ""
    episodic_memories: list = field(default_factory=list)
    key_entities: list = field(default_factory=list)
    recent_decisions: list = field(default_factory=list)
    
    # Warnings
    warnings: list = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert context to markdown for injection."""
        lines = [
            "# Dionysus Wake-Up Context",
            "",
            f"**Status:** {'✓ Connected' if self.api_healthy else '✗ Offline'}",
            f"**Conductor:** {'✓ Loaded' if self.conductor_loaded else '✗ Not loaded'}",
            f"**Agents:** {self.agent_count} specialized agents available",
            f"**Skills:** {', '.join(self.skills) if self.skills else 'None'}",
            "",
        ]
        
        if self.compact_context:
            lines.append("## Session Context")
            lines.append(self.compact_context)
            lines.append("")
        
        if self.episodic_memories:
            lines.append("## Recent Episodic Memories")
            for mem in self.episodic_memories[:5]:
                content = mem.get("content", "")[:100]
                lines.append(f"- {content}...")
            lines.append("")
        
        if self.key_entities:
            lines.append("## Key Entities")
            for ent in self.key_entities[:10]:
                name = ent.get("name", "Unknown")
                summary = ent.get("summary", "")[:80]
                lines.append(f"- **{name}**: {summary}")
            lines.append("")
        
        if self.warnings:
            lines.append("## Warnings")
            for warn in self.warnings:
                lines.append(f"- ⚠ {warn}")
            lines.append("")
        
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Convert context to JSON."""
        return json.dumps({
            "success": self.success,
            "api_healthy": self.api_healthy,
            "conductor_loaded": self.conductor_loaded,
            "agent_count": self.agent_count,
            "skills": self.skills,
            "coherence_score": self.coherence_score,
            "fragment_count": self.fragment_count,
            "compact_context": self.compact_context,
            "episodic_memories": self.episodic_memories,
            "key_entities": self.key_entities,
            "warnings": self.warnings,
        }, indent=2)


def http_get(url: str, timeout: float = 5.0) -> Optional[dict]:
    """Simple HTTP GET returning JSON."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def http_post(url: str, data: dict, timeout: float = 10.0) -> Optional[dict]:
    """Simple HTTP POST returning JSON."""
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def check_api_health() -> bool:
    """Check if Dionysus API is healthy."""
    result = http_get(f"{DIONYSUS_API}/health")
    if result:
        return result.get("status") == "healthy" or "healthy" in str(result)
    return False


def load_conductor_files(project_path: str) -> tuple:
    """Load Conductor protocol files."""
    project = Path(project_path)
    
    files = {
        "constraints": project / ".conductor" / "constraints.md",
        "workflow": project / "conductor" / "workflow.md",
        "best_practices": project / ".conductor" / "best-practices.md",
    }
    
    result = {}
    all_loaded = True
    
    for name, path in files.items():
        if path.exists():
            result[name] = str(path)
        else:
            result[name] = None
            all_loaded = False
    
    return all_loaded, result


def count_agents() -> tuple:
    """Count available agents and their categories."""
    if not AGENTS_DIR.exists():
        return 0, []
    
    categories = []
    count = 0
    
    for item in AGENTS_DIR.iterdir():
        if item.is_dir():
            categories.append(item.name)
            count += len(list(item.glob("*.md")))
        elif item.suffix == ".md" and item.name not in ["README.md", "CLAUDE.md", "CONTRIBUTING.md"]:
            count += 1
    
    return count, categories


def get_skills() -> list:
    """Get available skills."""
    if not SKILLS_DIR.exists():
        return []
    
    return [item.name for item in SKILLS_DIR.iterdir() if item.is_dir()]


def reconstruct_session(project_path: str, cues: list) -> dict:
    """Call session reconstruction endpoint."""
    result = http_post(
        f"{DIONYSUS_API}/api/session/reconstruct",
        {"project_path": project_path, "cues": cues},
        timeout=30.0,
    )
    return result or {"success": False, "error": "Request failed"}


def semantic_search(query: str, limit: int = 5) -> list:
    """Search semantic memory."""
    result = http_post(
        f"{DIONYSUS_API}/api/memory/semantic-search",
        {"query": query, "limit": limit},
        timeout=10.0,
    )
    if result:
        return result.get("results", [])
    return []


def wake_up(
    project_path: str = DEFAULT_PROJECT_PATH,
    cues: Optional[list] = None,
) -> WakeUpContext:
    """
    Execute the full wake-up protocol.
    
    Args:
        project_path: Path to the project for Conductor files
        cues: Optional retrieval cues for session reconstruction
        
    Returns:
        WakeUpContext with all hydrated context
    """
    ctx = WakeUpContext()
    cues = cues or []
    
    # 1. Check API health
    ctx.api_healthy = check_api_health()
    
    # 2. Load Conductor files
    ctx.conductor_loaded, conductor_files = load_conductor_files(project_path)
    ctx.constraints_path = conductor_files.get("constraints")
    ctx.workflow_path = conductor_files.get("workflow")
    ctx.best_practices_path = conductor_files.get("best_practices")
    
    if not ctx.conductor_loaded:
        ctx.warnings.append("Some Conductor files not found")
    
    # 3. Count agents
    ctx.agent_count, ctx.agent_categories = count_agents()
    
    # 4. Get skills
    ctx.skills = get_skills()
    
    # 5. Reconstruct session context (if API available)
    if ctx.api_healthy:
        result = reconstruct_session(project_path, cues)
        
        if result.get("success"):
            ctx.coherence_score = result.get("coherence_score", 0)
            ctx.fragment_count = result.get("fragment_count", 0)
            ctx.reconstruction_time_ms = result.get("reconstruction_time_ms", 0)
            ctx.compact_context = result.get("compact_context", "")
            ctx.episodic_memories = result.get("episodic_memories", [])
            ctx.key_entities = result.get("key_entities", [])
            ctx.recent_decisions = result.get("recent_decisions", [])
            ctx.warnings.extend(result.get("warnings", []))
        else:
            ctx.warnings.append(f"Session reconstruction failed: {result.get('error', 'unknown')}")
        
        # 6. Semantic search for cues (if any)
        if cues:
            for cue in cues[:3]:  # Limit to 3 cues
                memories = semantic_search(cue, limit=3)
                for mem in memories:
                    if mem not in ctx.episodic_memories:
                        ctx.episodic_memories.append(mem)
    else:
        ctx.warnings.append("Dionysus API not available - using local context only")
    
    ctx.success = ctx.conductor_loaded or ctx.api_healthy
    
    return ctx


def main():
    """CLI entry point."""
    # Parse args
    args = sys.argv[1:]
    project_path = args[0] if args else DEFAULT_PROJECT_PATH
    cues = args[1:] if len(args) > 1 else []
    
    # Run wake-up
    ctx = wake_up(project_path=project_path, cues=cues)
    
    # Output
    print(ctx.to_markdown())
    
    # Exit with appropriate code
    sys.exit(0 if ctx.success else 1)


if __name__ == "__main__":
    main()
