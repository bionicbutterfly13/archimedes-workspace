#!/bin/bash
# Migrate MEMORY.md to databases
# Phase 4 of Hexis integration

MEMORY_FILE="/home/mani/archimedes/MEMORY.md"
HEXIS_URL="http://localhost:8001"
DIONYSUS_URL="http://localhost:8000"

echo "=== Migrating MEMORY.md ==="
echo ""

# Parse sections and ingest each
python3 << 'PYTHON'
import re
import json
import urllib.request
import sys

HEXIS_URL = "http://localhost:8001"
DIONYSUS_URL = "http://localhost:8000"

with open("/home/mani/archimedes/MEMORY.md", "r") as f:
    content = f.read()

# Split by ## headers
sections = re.split(r'\n## ', content)

count = 0
for section in sections[1:]:  # Skip first empty section
    lines = section.strip().split('\n')
    title = lines[0].strip()
    body = '\n'.join(lines[1:]).strip()
    
    if not body:
        continue
    
    # Prepare the full text
    full_text = f"## {title}\n{body}"
    
    # Truncate if too long
    if len(full_text) > 2000:
        full_text = full_text[:2000] + "..."
    
    print(f"Migrating: {title[:50]}...")
    
    # Ingest to Hexis (semantic memory)
    try:
        hexis_data = json.dumps({
            "content": full_text,
            "memory_type": "semantic",
            "importance": 0.8,
            "metadata": {"source": "MEMORY.md", "section": title}
        }).encode()
        req = urllib.request.Request(
            f"{HEXIS_URL}/remember",
            data=hexis_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ Hexis")
    except Exception as e:
        print(f"  ❌ Hexis: {e}")
    
    # Ingest to Dionysus (strategic memory for long-term knowledge)
    try:
        dionysus_data = json.dumps({
            "content": full_text,
            "source": "MEMORY.md",
            "memory_type": "strategic",
            "importance": 0.8,
            "auto_ingested": False
        }).encode()
        req = urllib.request.Request(
            f"{DIONYSUS_URL}/api/memory/ingest",
            data=dionysus_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=30)
        print(f"  ✅ Dionysus")
    except Exception as e:
        print(f"  ❌ Dionysus: {e}")
    
    count += 1

print(f"\n=== Migrated {count} sections ===")
PYTHON
