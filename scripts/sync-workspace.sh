#!/bin/bash
# Auto-sync workspace from GitHub
cd /home/mani/archimedes

# Pull latest (fast-forward only to avoid conflicts)
git pull --ff-only origin main 2>&1

# If there are local changes, commit and push them
if [[ -n $(git status --porcelain) ]]; then
    git add -A
    git commit -m "Auto-sync from VPS $(date +%Y-%m-%d-%H%M)"
    git push origin main 2>&1
fi
