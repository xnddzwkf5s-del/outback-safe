# Open Survival Wiki — Site Review Report
**Date:** 2026-07-22
**Reviewer:** AI Subagent (Site Review Protocol)
**Scope:** Full structural, content, and navigation review with focus on Australia Outback Travel Survival

---

## Executive Summary

The Open Survival Wiki is a **high-quality, content-rich survival resource** with exceptional depth in Australian outback 4WD survival. However, the site suffers from a **critical identity crisis**: it is branded as a generic "SHTF societal collapse" wiki, but its best, most complete, and most valuable content is specifically **Australian outback vehicle survival**. The generic collapse content (Tier 2 Stabilise, Tier 3 Thrive) is almost entirely placeholder stubs ("Content under development"), while the outback content is production-ready and outstanding.

**Overall Grade: Needs Work** (with specific areas of Strong and Critical Gap)

---

## 1. Structural Review

### 1.1 Navigation Bar
**Grade: Needs Work**

The top navigation bar shows:
- Immediate (1–7)
- Stabilise (8–90)
- Thrive (4–60 mo)
- Reference

**Problems:**
- **Outback Survival is buried.** The single most valuable section (01-immediate/09-outback) is subsection 9 of Tier 1. A user looking for outback 4WD survival must click: Immediate → scroll past 8 sections → find Outback 4WD Survival at the bottom.
- **No top-level Outback item.** Given the project's stated focus on "Australia Outback Travel Survival," this should be a primary navigation item, not a subsection.
- **Tier labels are confusing.** "Immediate (1–7)" means days 1–7, but this is not obvious to a first-time visitor. "Stabilise (8–90)" and "Thrive (4–60 mo)" are similarly opaque.
- **Reference is the only tier with substantial content** besides Tier 1, but it is last in the nav order.

**Recommendation:** Restructure navigation to reflect actual content value and user intent.

### 1.2 Tier Logic
**Grade: Adequate (conceptually) / Critical Gap (execution)**

The 4-tier time-criticality model is sound in theory:
- Tier 1: Immediate (days 1–7) — life-saving priorities
- Tier 2: Stabilise (days 8–90) — sustainable base
- Tier 3: Thrive (months 4–60) — long-term community
- Tier 4: Reference — deep technical knowledge

**Execution failure:** Tier 2 has 11 subsections, of which **10 are placeholder stubs** ("Content under development"). Only 08-medicine has real content. Tier 3 has 13 subsections, of which **12 are placeholder stubs**. Only 04-weapons has real content. Tier 4 has 9 subsections, of which **7 are placeholder stubs**. Only maps and communications have real content.

This means **~75% of the site's promised content does not exist.** The tier structure promises a comprehensive survival wiki but delivers a Tier 1 + Outback + Maps + Medicine + Weapons site.

### 1.3 Outback Section Prominence
**Grade: Critical Gap**

The Outback 4WD Survival section (12 pages, ~150KB of content) is:
- The most complete section in the entire wiki
- The most Australia-specific content
- The most practically useful for the stated project focus
- **Buried as subsection 09 of Tier 1**

**This is the single biggest structural problem.** The outback content should be promoted to a top-level section or the entire site should be rebranded around it.

### 1.4 Homepage Effectiveness
**Grade: Needs Work**

The homepage (`index.html`) currently:
- Describes the site as "surviving and rebuilding after a societal collapse, natural disaster, or other SHTF scenario"
- Lists the 4 tiers with equal weight
- Mentions "Content in Progress" as a living project
- Does NOT mention Australia, outback, 4WD, or vehicle survival anywhere
- Does NOT surface the best content (outback section, maps, snake bite)

**The homepage fails to communicate what the site actually is.** A first-time visitor would have no idea this is an Australia-focused outback survival resource.

### 1.5 Section Weighting
**Grade: Critical Gap**

Content accessibility is inversely proportional to quality:

| Section | Content Quality | Accessibility | Mismatch |
|---------|---------------|-------------|----------|
| Outback 4WD Survival | Excellent | 3 clicks deep | **Severe** |
| Maps (Reference) | Excellent | 2 clicks deep | Moderate |
| Medicine (Stabilise) | Excellent | 2 clicks deep | Moderate |
| Tier 1 General | Good | 1 click | Appropriate |
| Tier 2 (non-medicine) | Non-existent | 1 click | **Severe** |
| Tier 3 (non-weapons) | Non-existent | 1 click | **Severe** |
| Weapons (Thrive) | Good | 2 clicks deep | Moderate |

---

## 2. Content Review

### 2.1 Alignment with Project Focus
**Grade: Needs Work**

The project's stated focus is **Australia Outback Travel Survival**. The content alignment is mixed:

**Strongly aligned:**
- Outback 4WD Survival (12 pages) — vehicle breakdown, heat survival, navigation, emergency services, route planning, bush mechanics, vehicle recovery, water/food, what to carry
- Maps (10 pages) — Simpson Desert, Canning Stock Route, Cape York, Gibb River Road, Binns Track, Anne Beadell, other tracks, Australia overview, map resources
- Communications (2 pages) — 2m repeaters, UHF channels
- Medicine (7 pages) — snake bite, outback bush medicine, remote first aid, herbal database, by-ailment, preparation, safety
- Tier 1 general survival (partially aligned) — first aid, water, shelter, fire, signaling are universally applicable

**Misaligned or unnecessary:**
- Tier 2 Stabilise (10 of 11 sections are stubs) — water systems, food procurement, food preservation, tool making, shelter upgrade, hygiene, clothing, record keeping, security/defense, social structure
- Tier 3 Thrive (12 of 13 sections are stubs) — agriculture, animal husbandry, food production, advanced tools, construction, textiles, medicine advanced, energy, trade, education, long-term planning, open engineering
- Weapons (29 pages) — gunpowder, medieval weapons, fortification, firearms. This is the largest single content block after outback, but it is **completely misaligned** with outback travel survival. It belongs to a societal collapse scenario, not a vehicle breakdown scenario.
- Herbal database (30 plants) — many are Chinese/SEA species (ginseng, astragalus, schisandra, coptis, scutellaria, rehmannia, angelica, artemisia, andrographis, curcuma, morinda, moringa, psidium, carica, centella, tinospora, blumea, zingiber zerumbet). Only ~10 are Australian natives.

### 2.2 Orphan Pages
**Grade: Adequate**

No true orphan pages found. All content pages are reachable through navigation. However:
- The `images-needed.html` pages (3 pages) are marked `draft = true` in frontmatter but are still built and linked. They are internal working documents that should not be publicly accessible.
- The `2m-repeaters.html` page has a broken link: `href="../../../mechanics/realform-deploy.md"` — this is a raw markdown file link that will 404 in the built site.

### 2.3 Dead-End Pages
**Grade: Adequate**

Most content pages have "Related Pages" sections with cross-references. The outback section is particularly well-cross-referenced. However:
- Placeholder stub pages (Tier 2, Tier 3, most of Reference) are dead ends by definition — they have no content and no links to related content.
- Some herbal plant pages have no outbound links beyond the standard nav (they are leaf nodes).

### 2.4 Writing Quality Consistency
**Grade: Strong (for completed content) / Critical Gap (for stubs)**

The completed content is **exceptionally well-written**:
- Outback section: authoritative, practical, Australia-specific, with correct terminology (UHF channels, RFDS, PLB, PIB technique, gnamma holes, etc.)
- Maps: detailed, accurate, with real distances, fuel stops, permit requirements
- Snake bite: medically accurate, follows Australian Resuscitation Council guidelines, regionally specific
- Tier 1 general: solid, practical, well-structured

The stub content is **non-existent** — 29 placeholder pages with "Content under development."

### 2.5 Missing Content
**Critical gaps for an Australia Outback Travel Survival site:**

1. **No dedicated "Outback Survival" landing page** that unifies the outback content
2. **No trip planning checklist** as a standalone printable page
3. **No seasonal travel guide** (when to go where)
4. **No vehicle preparation checklist** as a standalone page (currently embedded in route-planning)
5. **No "First 24 Hours" outback-specific quick reference** (the 00-start-here page is generic)
6. **No Aboriginal land permit guide** as a standalone page
7. **No fuel/water cache planning** for major routes
8. **No recovery gear comparison** (Maxtrax vs. TRED vs. etc.)
9. **No satellite communicator comparison** (inReach vs. Zoleo vs. PLB)
10. **No outback-specific first aid kit contents** list

### 2.6 Unnecessary Content (Given AU-Only Focus)

**Recommend removal or de-emphasis:**
- **Weapons section (29 pages)** — gunpowder, medieval weapons, fortification, firearms. This is the largest misaligned content block. It serves a societal collapse scenario, not outback travel. If kept, it should be clearly labeled as "Long-Term Societal Collapse" and separated from the outback travel content.
- **Chinese/SEA herbal plants (20 of 30)** — ginseng, astragalus, schisandra, coptis, scutellaria, rehmannia, angelica, artemisia, andrographis, curcuma, morinda, moringa, psidium, carica, centella, tinospora, blumea, zingiber zerumbet, glycyrrhiza. These are not found in the Australian outback and dilute the AU focus.
- **Snow shelter** — irrelevant for outback Australia (except alpine regions, which are not the focus).
- **Drowning** — while possible in outback waterholes, it is not a primary outback survival skill.
- **Most Tier 2 and Tier 3 stubs** — either complete them or remove them. Empty sections damage credibility.

---

## 3. Navigation & Discovery

### 3.1 Click Depth Analysis
**Grade: Needs Work**

| Target Content | Clicks from Homepage | Assessment |
|---------------|----------------------|------------|
| Outback 4WD Survival index | 2 (Immediate → Outback) | Acceptable but should be 1 |
| Vehicle Breakdown: Stay or Go? | 3 (Immediate → Outback → Vehicle Breakdown) | Too deep for the most critical page |
| Snake Bite | 3 (Stabilise → Medicine → Snake Bite) | Acceptable for reference content |
| Simpson Desert map | 3 (Reference → Maps → Simpson Desert) | Acceptable for reference content |
| What to Carry | 3 (Immediate → Outback → What to Carry) | Too deep for pre-trip planning |
| Emergency Services | 3 (Immediate → Outback → Emergency Services) | Too deep for emergency reference |
| 2m Repeaters | 3 (Reference → Communications → 2m Repeaters) | Acceptable |
| Tier 2 Water Systems | 2 (Stabilise → Water Systems) | **Leads to empty stub** |
| Tier 3 Agriculture | 2 (Thrive → Agriculture) | **Leads to empty stub** |

**Problem:** The most critical outback pages (vehicle breakdown, emergency services, what to carry) require 3 clicks. Empty stub pages require only 2 clicks. This is backwards.

### 3.2 Redundant/Overlapping Content
**Grade: Adequate**

- **Snake bite** appears in both 01-immediate/09-outback/outback-first-aid (rapid version) and 02-stabilise/08-medicine/snake-bite (definitive reference). This is appropriate — one is for immediate action, one is for deep reference.
- **Heat illness** appears in both 01-immediate/09-outback/heat-survival (detailed) and 01-immediate/09-outback/outback-first-aid (summary). Appropriate.
- **Water** appears in 01-immediate/02-water (general) and 01-immediate/09-outback/water-food-outback (outback-specific). Appropriate.
- **Signaling** appears in 01-immediate/06-signaling (general) and 01-immediate/09-outback/vehicle-as-resource (vehicle-specific). Appropriate.

No problematic redundancy found.

### 3.3 Cross-References
**Grade: Strong**

The outback section has excellent cross-referencing:
- vehicle-breakdown ↔ heat-survival ↔ vehicle-as-resource ↔ emergency-services ↔ what-to-carry ↔ navigation-basics
- Maps pages link back to route-planning, vehicle-breakdown, what-to-carry
- Medicine pages link to outback-first-aid, heat-survival, emergency-services
- Tier 1 general pages link to relevant outback pages

The cross-reference network is one of the site's strengths.

### 3.4 Search Feature
**Grade: Critical Gap**

There is **no search functionality**. For a 181-page site, this is a significant usability gap. Users cannot search for "snake bite," "UHF channel," "Simpson Desert fuel," or "PIB technique."

Given the static HTML nature of the site, a client-side search (e.g., Lunr.js, Fuse.js, or a simple pre-built index) would be feasible and highly valuable.

### 3.5 Related Pages Sections
**Grade: Strong**

Most completed pages have "Related Pages" or "Cross-References" sections. This is excellent practice and should be maintained.

---

## 4. Content Inventory Analysis

### 4.1 Outback 4WD Survival (12 pages)
**Grade: Strong**

| Page | Quality | Notes |
|------|---------|-------|
| _index.md | Excellent | Good overview, key statistics table |
| vehicle-breakdown.md | Excellent | The core decision tree — stay or go |
| heat-survival.md | Excellent | Comprehensive heat illness management |
| vehicle-as-resource.md | Excellent | Creative use of vehicle components |
| what-to-carry.md | Excellent | Complete checklist with quantities |
| emergency-services.md | Excellent | Australian-specific contacts and procedures |
| navigation-basics.md | Excellent | Sun, stars, terrain — no GPS needed |
| route-planning.md | Excellent | Permits, comms, vehicle prep, convoy procedures |
| bush-mechanics.md | Excellent | Field repairs for common breakdowns |
| vehicle-recovery.md | Excellent | Bogged vehicle recovery techniques |
| water-food-outback.md | Excellent | Water sourcing, rationing, emergency food |
| outback-first-aid.md | Excellent | Snake bite, heat, bleeding, fractures |

**This is the crown jewel of the site.** 12 pages, all complete, all Australia-specific, all practically useful.

### 4.2 Maps (10 pages)
**Grade: Strong**

| Page | Quality | Notes |
|------|---------|-------|
| _index.md | Excellent | Good overview with track categorisation |
| australia-overview.md | Excellent | States, distances, datum, map series |
| map-resources.md | Excellent | Hema, Westprint, digital tools, GPS waypoints |
| simpson-desert.md | Excellent | French Line, Rig Road, WAA Line, Hay River |
| canning-stock-route.md | Excellent | 1,850 km, wells, fuel drops, permits |
| anne-beadell-highway.md | Excellent | 1,360 km, Coober Pedy to Laverton |
| cape-york.md | Excellent | Old Telegraph Track, creek crossings, crocs |
| gibb-river-road.md | Excellent | Kimberley, gorges, river crossings |
| binns-track.md | Excellent | 2,230 km, NT's longest route |
| other-tracks.md | Excellent | Birdsville, Oodnadatta, Strzelecki, Tanami, etc. |

**Outstanding reference material.** Real distances, real fuel stops, real permit requirements.

### 4.3 Communications (2 pages)
**Grade: Adequate**

| Page | Quality | Notes |
|------|---------|-------|
| _index.md | Good | Brief overview |
| 2m-repeaters.md | Good | Comprehensive repeater directory |

**Note:** The 2m-repeaters page has a broken link to `../../../mechanics/realform-deploy.md`.

### 4.4 Medicine (7 pages + 30 plant pages)
**Grade: Strong (AU content) / Needs Work (CN/SEA content)**

| Page | Quality | Notes |
|------|---------|-------|
| _index.md | Excellent | Outback-focused triage table |
| snake-bite.md | Excellent | Definitive Australian reference |
| outback-bush-medicine.md | Excellent | Curated AU plants with look-alike warnings |
| remote-first-aid-techniques.md | Excellent | Wound closure, splints, dental, childbirth |
| by-ailment.md | Good | Cross-reference index |
| preparation-methods.md | Good | Infusion, decoction, poultice, etc. |
| safety.md | Good | Plant ID, toxic look-alikes, dosage |
| herbal/_index.md | Good | Database overview |
| herbal/plants/* (30 pages) | Mixed | 10 AU natives excellent, 20 CN/SEA misaligned |

### 4.5 Weapons (29 pages)
**Grade: Good (quality) / Critical Gap (alignment)**

| Section | Pages | Quality | Alignment |
|---------|-------|---------|-----------|
| Gunpowder | 6 | Good | Misaligned |
| Black Powder | 1 | Good | Misaligned |
| Firearms | 5 | Good | Misaligned |
| Medieval | 6 | Good | Misaligned |
| Fortification | 6 | Good | Misaligned |

**This is well-written content for a societal collapse scenario, but it does not belong in an Australia Outback Travel Survival site.** A 4WD traveller broken down on the Canning Stock Route does not need to know how to manufacture black powder or build a moat.

### 4.6 Tier 1 General (49 pages)
**Grade: Strong**

First aid, water, shelter, fire, food, signaling, group management, security — all complete and well-written. Some content is generic (not AU-specific) but universally applicable.

### 4.7 Tier 2 Stabilise (11 sections, 10 stubs)
**Grade: Critical Gap**

Only 08-medicine has content. The other 10 sections are empty placeholders.

### 4.8 Tier 3 Thrive (13 sections, 12 stubs)
**Grade: Critical Gap**

Only 04-weapons has content. The other 12 sections are empty placeholders.

### 4.9 Tier 4 Reference (9 sections, 7 stubs)
**Grade: Critical Gap**

Only maps and communications have content. The other 7 sections are empty placeholders.

---

## 5. Specific Recommendations

### 5.1 Proposed New Navigation Structure

```
Open Survival Wiki — Australia Outback Travel Survival
├── 🚨 Outback Emergency (start here if broken down)
│   ├── Vehicle Breakdown: Stay or Go?
│   ├── Extreme Heat Survival
│   ├── Outback First Aid
│   ├── Emergency Services & PLB
│   └── Navigation Basics (no GPS)
├── 🚗 Trip Planning
│   ├── What to Carry (complete checklist)
│   ├── Route Planning & Preparation
│   ├── Vehicle Preparation Checklist
│   ├── Bush Mechanics (field repairs)
│   ├── Vehicle Recovery (bogged)
│   └── Water & Food in the Outback
├── 🗺️ Maps & Tracks
│   ├── Australia Overview
│   ├── Simpson Desert
│   ├── Canning Stock Route
│   ├── Cape York
│   ├── Gibb River Road
│   ├── Binns Track
│   ├── Anne Beadell Highway
│   ├── Other Tracks
│   └── Map Resources & Tools
├── 🏥 Medicine & First Aid
│   ├── Snake Bite (definitive)
│   ├── Outback Bush Medicine
│   ├── Remote First Aid Techniques
│   ├── Herbal Database (AU natives only)
│   ├── By Ailment
│   ├── Preparation Methods
│   └── Safety Guide
├── 📻 Communications
│   ├── UHF Channels & Emergency
│   ├── 2m Repeater Directory
│   └── Satellite Communicators
├── 🎒 General Survival (Tier 1)
│   ├── Start Here (first hour)
│   ├── First Aid
│   ├── Water
│   ├── Shelter
│   ├── Fire
│   ├── Food (Emergency)
│   ├── Signaling
│   ├── Group Management
│   └── Security
└── 📚 Reference Library
    ├── Weapons (long-term collapse only)
    ├── Chemistry
    ├── Botany
    ├── Engineering
    └── [other stubs — either complete or remove]
```

### 5.2 Content Reorganisation Priority

**P0 — Do immediately:**
1. **Rebrand homepage** to "Australia Outback Travel Survival" — remove SHTF/collapse framing
2. **Promote Outback 4WD Survival to top-level nav** — rename to "Outback Emergency" or "Outback Survival"
3. **Add "What to Carry" and "Vehicle Breakdown" to homepage quick links**
4. **Fix broken link** in 2m-repeaters.html (`../../../mechanics/realform-deploy.md`)
5. **Hide or remove `images-needed.html` pages** from public build (they are draft=true)

**P1 — Do within 1 week:**
6. **Remove or clearly separate CN/SEA herbal plants** — create an "Australian Natives Only" filter or move CN/SEA plants to a clearly labeled subsection
7. **Add search functionality** — client-side search index for 181 pages
8. **Create a "Quick Reference" printable card** — vehicle breakdown decision tree, emergency numbers, PIB steps
9. **Either complete or remove Tier 2 stubs** — 10 empty sections damage credibility
10. **Either complete or remove Tier 3 stubs** — 12 empty sections damage credibility

**P2 — Do within 1 month:**
11. **Add "Related Pages" to all map pages** linking to relevant outback survival pages
12. **Create seasonal travel guide** — when to attempt each major track
13. **Add vehicle preparation checklist** as standalone page
14. **Add satellite communicator comparison** (inReach vs. Zoleo vs. PLB)
15. **Consider removing or archiving Weapons section** — or clearly label as "Long-Term Societal Collapse Scenario"

### 5.3 Homepage Improvements

**Current homepage problems:**
- No mention of Australia or outback
- Equal weight to all 4 tiers (misleading — most are empty)
- No quick access to best content
- No emergency quick reference

**Proposed homepage structure:**

```markdown
# Australia Outback Travel Survival Wiki

Open-source survival knowledge for remote Australian 4WD travel.
When you're 300 km from the nearest town, this is what keeps you alive.

## 🚨 Broken Down Right Now?
- [Vehicle Breakdown: Stay or Go?](01-immediate/09-outback/vehicle-breakdown) — The critical decision
- [Extreme Heat Survival](01-immediate/09-outback/heat-survival) — 45°C+ kills in hours
- [Emergency Services](01-immediate/09-outback/emergency-services) — 000, PLB, UHF channels
- [Outback First Aid](01-immediate/09-outback/outback-first-aid) — Snake bite, heat stroke, bleeding

## 🚗 Planning a Trip?
- [What to Carry](01-immediate/09-outback/what-to-carry) — Complete checklist
- [Route Planning](01-immediate/09-outback/route-planning) — Permits, comms, fuel
- [Maps & Tracks](04-reference/maps/) — Simpson, Canning, Cape York, Gibb River
- [Vehicle Preparation](01-immediate/09-outback/route-planning#vehicle-preparation-checklist)

## 🏥 Medical Emergency?
- [Snake Bite](02-stabilise/08-medicine/snake-bite) — PIB technique, symptoms, hospital
- [Remote First Aid](02-stabilise/08-medicine/remote-first-aid-techniques) — Wounds, fractures, dental
- [Outback Bush Medicine](02-stabilise/08-medicine/outback-bush-medicine) — Plants that work

## 📚 Full Contents
- [Outback 4WD Survival](01-immediate/09-outback/) — All 12 pages
- [General Survival](01-immediate/) — First aid, water, shelter, fire
- [Medicine](02-stabilise/08-medicine/) — Snake bite, bush medicine, first aid
- [Maps](04-reference/maps/) — All major tracks
- [Communications](04-reference/communications/) — UHF, repeaters, satellite
```

### 5.4 What to Add

1. **Printable quick reference cards** (PDF or single-page HTML):
   - Vehicle breakdown decision tree
   - PIB snake bite steps
   - Emergency numbers and UHF channels
   - Water requirements calculator

2. **Seasonal travel calendar** — month-by-month guide to which tracks are open

3. **Fuel and water cache calculator** — input route, get required quantities

4. **Recovery gear comparison table** — Maxtrax, TRED, X-Bull, etc.

5. **Satellite communicator comparison** — inReach Mini 2, Zoleo, PLB, Iridium GO

6. **Aboriginal land permit guide** — state-by-state application process

7. **Outback-specific first aid kit contents** — what to buy, what to improvise

8. **"Last Resort" water procurement** — radiator water, AC condensate, dew collection (expand existing content)

### 5.5 What to Remove or Reorganise

**Remove entirely:**
- `images-needed.html` pages (internal working docs, draft=true)
- Broken link in 2m-repeaters.html

**Reorganise / de-emphasise:**
- **Weapons section (29 pages)** — move to a clearly labeled "Long-Term Societal Collapse" appendix or remove entirely. It is the largest misaligned content block.
- **CN/SEA herbal plants (20 pages)** — either remove or move to a clearly labeled "Non-Australian Reference" subsection. The AU-native plants (10 pages) should be the primary herbal database.
- **Snow shelter** — keep but de-emphasise (not outback-relevant)
- **Tier 2 stubs (10 sections)** — either complete with real content or remove from navigation
- **Tier 3 stubs (12 sections)** — either complete with real content or remove from navigation
- **Reference stubs (7 sections)** — either complete with real content or remove from navigation

---

## 6. Overall Grade Summary

| Area | Grade | Notes |
|------|-------|-------|
| **Outback 4WD Survival content** | **Strong** | Best-in-class, production-ready |
| **Maps & track references** | **Strong** | Detailed, accurate, comprehensive |
| **Medicine (AU-focused)** | **Strong** | Snake bite, bush medicine, remote first aid |
| **Tier 1 general survival** | **Strong** | Solid, practical, well-structured |
| **Cross-referencing** | **Strong** | Excellent internal linking |
| **Writing quality** | **Strong** | Authoritative, practical, Australia-specific |
| **Homepage** | **Needs Work** | Does not reflect actual site focus |
| **Navigation structure** | **Needs Work** | Best content is buried |
| **Search** | **Critical Gap** | No search for 181 pages |
| **Tier 2 content** | **Critical Gap** | 10 of 11 sections are empty stubs |
| **Tier 3 content** | **Critical Gap** | 12 of 13 sections are empty stubs |
| **Reference content** | **Critical Gap** | 7 of 9 sections are empty stubs |
| **AU focus alignment** | **Needs Work** | Weapons and CN/SEA herbs dilute focus |
| **Mobile experience** | **Adequate** | Responsive CSS present, but not tested |

---

## 7. Top 5 Priorities

### Priority 1: Rebrand and Restructure Around Outback Survival
**Impact:** Highest. Fixes the identity crisis.
**Effort:** Medium (homepage rewrite, nav restructure, tier page updates)
**Action:** Change homepage title, description, and quick links to focus on Australia Outback Travel Survival. Promote Outback 4WD Survival to top-level navigation. Remove or de-emphasise SHTF/collapse framing.

### Priority 2: Deal with Empty Stub Sections
**Impact:** High. 29 empty sections damage credibility and frustrate users.
**Effort:** Low-Medium (either write content or remove from nav)
**Action:** For each of the 29 placeholder stubs, decide: complete it with real content, or remove it from navigation and mark as "planned." Do not leave empty pages in the public nav.

### Priority 3: Add Search Functionality
**Impact:** High. Users cannot find content across 181 pages.
**Effort:** Medium (client-side search index)
**Action:** Implement a static site search (Lunr.js, Fuse.js, or Pagefind) with a pre-built index. Add search box to header.

### Priority 4: Align Content with AU-Only Focus
**Impact:** Medium-High. Removes dilution and confusion.
**Effort:** Low-Medium (reorganise existing content)
**Action:** Move or clearly label CN/SEA herbal plants. Move or clearly label Weapons section as "Long-Term Collapse." Ensure all primary content is Australia-specific.

### Priority 5: Fix Technical Issues
**Impact:** Medium. Broken links and draft pages reduce professionalism.
**Effort:** Low
**Action:** Fix broken link in 2m-repeaters.html. Remove images-needed.html pages from public build. Add 404 page. Verify all internal links resolve.

---

## 8. Final Assessment

The Open Survival Wiki is **two websites in one**:

1. **An outstanding Australia Outback Travel Survival resource** — 12 outback pages, 10 map pages, 7 medicine pages, 2 comms pages, and solid Tier 1 general survival. This is production-ready, best-in-class content that could save lives.

2. **A skeletal societal collapse wiki** — 29 empty placeholder stubs across Tier 2, Tier 3, and Reference, plus 29 weapons pages that belong to a different project entirely.

The site should **lean into its strength** (outback survival) and **either complete or remove its weakness** (empty collapse stubs). The current state — promising a comprehensive survival wiki but delivering mostly empty sections — undermines the exceptional outback content.

**Recommendation:** Rebrand as "Australia Outback Travel Survival Wiki," promote outback content to top-level navigation, add search, and either complete or remove the 29 empty stubs. The weapons section should be clearly separated or removed. The CN/SEA herbal content should be de-emphasised in favour of Australian natives.

---

*Report generated by AI subagent for Vincent's review.*
