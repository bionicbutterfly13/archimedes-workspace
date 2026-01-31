# Session Summary: HBD Funnel & Dionysus Integration
**Date:** 2026-01-30 (late night session)
**Context:** Extended working session on Inner Architect sales funnel

---

## Key Decisions Made

### Pricing
- **HBD (Hidden Block Decoder):** $97 (up from earlier $47 tests)
- **Upsell:** $279 (Phase 2+3 bundle)
- **Target:** Affluent buyers who can spend $97 easily, $279 without sweating

### Funnel Structure
1. **FB Ad** → proven "stop replaying conversations" hook
2. **Opt-in Page** → 24-40% conversion rate (WINNING)
3. **Thank-You Page** → HBD offer at $97
4. **Upsell Page** → $279 (Phase 2+3 + Obstacle Matrix)
5. **Email Day 3** → Second shot at HBD for non-buyers

### Previous Performance
- Opt-in page: 24-40% CVR (excellent)
- Old HBD page at $47: ~1 sale/day (before it was broken trying to optimize without control)
- Email open rates: fantastic (until the 33x email mishap)

---

## HBD Offer Stack (Final)

### Core Product
1. **Your Beautiful Loop** (10-min whiteboard video) ✅ COMPLETE
2. **Your Selective Mind** (10-min whiteboard video) ✅ COMPLETE  
3. **MOSAEIC Method** (mini-course) ✅ COMPLETE
4. **IA Blueprint Stack** (9 one-page micro-blueprints)

### Bonuses
1. Pattern Recognition Protocol (PDF) ✅ EXISTS
2. Inner Aspect Guide (PDF) ✅ EXISTS
3. Weekend Guide to Roles & Rules (IFS mini-course) ✅ EXISTS

### What Dr. Mani Has Ready
- Beautiful Loop video
- Selective Self video
- MOSAEIC mini course recordings
- Inner Aspect Guide
- Pattern Recognition Protocol
- Weekend Guide to Roles & Rules (IFS)
- 14-video "Creating a Life Beyond Beliefs" course (for upsell)
- GPT-written stack copy (needs polish)

---

## Sales Page Draft

**Location:** `/Users/manisaintvictor/archimedes/projects/hbd-sales-page-v1.md`

**Structure:**
- Thank-you page format (post opt-in)
- Video-led with timestamp hooks
- "This works even if..." fascinations (5 strongest)
- Clean $97 pricing, no scarcity/desperation
- 30-day guarantee
- Includes VSL script outline for Dr. Mani to record

**Next steps:**
1. Dr. Mani reviews copy
2. Dr. Mani records 9-min VSL following timestamp outline
3. Build $279 upsell page

---

## Dionysus Integration Status

### VPS Stack (72.61.78.89)
| Service | Port | Status |
|---------|------|--------|
| dionysus-api | 8000 | 🔴 Unhealthy (stuck on startup) |
| graphiti | 8001 | 🟡 Running but embedding dimension mismatch |
| neo4j | 7687 | 🟢 Running |
| n8n | 5678 | 🟢 Running |
| ollama | 11434 | 🟢 Running |

### Issues Found
1. **dionysus-api:** NEO4J_URI=bolt://localhost:7687 should be bolt://neo4j:7687 (Docker networking)
2. **graphiti:** Vector dimension mismatch - old embeddings incompatible with current config

### SSH Access
```bash
ssh -i ~/.ssh/mani_vps mani@72.61.78.89
```

### Relevant Codebases
- `/Volumes/Asylum/dev/dionysus3-core` — current Dionysus (VPS deployment)
- `/Volumes/Asylum/dev/Dionysus-2.0` — older version with metalearning
- `/Users/manisaintvictor/archimedes/Hexis` — Hexis memory system

---

## Winning Ad/Opt-in Copy (PROVEN)

**Hook:** "Stop replaying conversations in your head for hours"

**Target Audience:**
- High-achievers who speak their truth but crash emotionally after
- Overthinkers who replay conversations
- Analytical empaths
- Doctors, therapists, educators, professionals
- Tried therapy/coaching, nothing stuck

**Key Mechanism:** Memory reconsolidation (not mindset, not willpower)

**What converts:**
- Viscerally specific pain ("replaying conversations for hours")
- Identity preservation ("without losing your sharpness or your voice")
- Quick win (3-step checklist)
- Professional peer proof (MDs, DDSs in testimonials)

---

## Files Created This Session

1. `/Users/manisaintvictor/archimedes/projects/hbd-sales-page-v1.md` — full sales page draft
2. This session summary

---

## Tomorrow's Tasks

1. Dr. Mani: Review HBD sales page draft
2. Dr. Mani: Record 9-min VSL
3. Archimedes: Fix dionysus-api NEO4J_URI and restart
4. Archimedes: Debug Graphiti embedding dimension issue
5. Build $279 upsell page once HBD page is finalized
