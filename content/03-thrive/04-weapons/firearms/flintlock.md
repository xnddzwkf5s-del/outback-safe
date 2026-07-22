+++
title = "Flintlock Mechanism"
description = "Flintlock design, flint knapping, tuning, and maintenance"
weight = 2
+++

# Flintlock Mechanism

The flintlock was the dominant firearm ignition system from approximately 1610 to 1830 — over two centuries of service. It strikes a piece of flint against a steel face (the frizzen), showering sparks into the priming pan and igniting the main charge through the touch hole.

## How It Works

```
                ★ ← Cock pivot screw
               /
    ┌─────────┐
    │  COCK   │  ← Spring-loaded hammer holding flint
    │  (Jaw)  │
    │ ┌─────┐ │
    │ │Flint│ │
    │ └──┬──┘ │
    └────┼────┘
         │ Strikes downward
    ┌────▼────────────────────┐
    │  FRIZZEN (Steel)        │  ← Hardened high-carbon face
    │  ┌──────────────────┐   │      Pivots forward when struck
    │  │ PRIMING PAN      │   │      exposing the powder
    │  │ (Priming powder) │   │
    │  └──────────────────┘   │
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │  TOUCH HOLE (1.5-2mm)  │  ← Flash enters barrel here
    │  into main charge      │
    └─────────────────────────┘

Side view of lock plate:

    ┌─────────────────────────────────────────────┐
    │  ● Cock screw         ● Frizzen screw       │
    │  │                    │                     │
    │  ▼                    ▼                     │
    │ ┌───┐    ┌────────┐  ┌───┐                  │
    │ │   │    │ Pan    │  │   │                  │
    │ │ C │    │        │  │ F │   LOCK PLATE     │
    │ │ O │    │ ╔════╗ │  │ R │                  │
    │ │ C │    │ ║PWDR║ │  │ I │                  │
    │ │ K │    │ ╚════╝ │  │ Z │                  │
    │ │   │    └────────┘  │ Z │                  │
    │ └───┘                │ E │                  │
    │                      │ N │                  │
    │                      └───┘                  │
    │  ● Sear screw        ● Tumbler (internal)   │
    └─────────────────────────────────────────────┘
        ↓ Trigger bar connects sear to trigger
```

## Components

| Component | Material | Function |
|-----------|----------|----------|
| **Lock plate** | Iron or steel, 3–4 mm thick | Mounts all components; screws to stock |
| **Cock** (hammer) | Steel, case-hardened | Holds flint in its jaws |
| **Jaw screw** | Steel | Tightens jaws onto flint (with leather/lead cushion) |
| **Frizzen** (steel/battery) | High-carbon steel face, wrought iron body | Struck by flint, creates sparks, covers pan |
| **Frizzen spring** | Spring steel | Holds frizzen closed or open |
| **Pan** | Integral to lock plate or separate brass pan | Holds priming powder |
| **Tumbler** | Steel, case-hardened | Internal rotating part connecting cock to mainspring |
| **Sear** | Steel, hardened tip | Engages tumbler notches for half-cock and full-cock |
| **Sear spring** | Spring steel | Returns sear to engagement position |
| **Mainspring** (V-spring) | Spring steel | Drives the cock forward |

## Manufacturing the Lock

The lock is a precision mechanism — maybe the most precise thing you'll make.

### Materials

- **Wrought iron** for the lock plate, cock body, and frizzen body — forge from scrap iron
- **High-carbon steel** for the frizzen face — can be case-hardened wrought iron (pack in charcoal and bone meal, heat to 900°C for 4 hours, quench)
- **Spring steel** for the mainspring and frizzen spring — can be made from high-carbon steel, hardened and tempered to blue (spring temper, approximately 300°C)

### Case Hardening

If you cannot obtain high-carbon steel, case-harden mild steel or wrought iron:

{% steps() %}
Prepare a case-hardening compound — Mix 60% hardwood charcoal powder, 30% bone meal or leather scraps (nitrogen source), 10% barium carbonate or sodium carbonate (activator).;
Pack the part in this compound inside a sealed clay or iron box;
Heat to 850–900°C and hold for 4–6 hours — Carbon diffuses 0.5–1.0 mm into the surface.;
Quench directly from the box into cold water — The surface becomes high-carbon martensite (hard, ~60 HRC).;
Temper immediately — Heat to appropriate temperature: sear tip at 230°C (straw colour), frizzen face at 200°C (light straw), springs at 300°C (blue).
{% end %}

### Frizzen Hardness

The frizzen must be hard enough to produce sparks but not so hard that it shatters. Target hardness: HRC 55–58.

**Test:** A sharp file should just barely skate across the frizzen face without biting. If the file bites, it's too soft (won't spark). If the file skates without any mark, it's too hard (may shatter).

### Tuning the Geometry

The critical angles:

```
    Flint strikes frizzen at
    approximately 60° angle
    
         COCK
          \
           \ ← 60° strike angle
            \
    ─────────▼────────
         FRIZZEN
    ══════════════════
```

The flint should strike the frizzen about two-thirds of the way up from the pivot. It should scrape down the face, peeling off tiny steel fragments that oxidise (spark) in air. The sparks should shower directly into the pan.

**If sparks go sideways or forward:** The flint is aligned wrong — adjust the leather cushion in the cock jaws.
**If no sparks:** Frizzen too soft (will not spark) or flint worn smooth (re-knap).
**If sparks but no ignition:** Pan powder too coarse or moist, or touch hole blocked.

## Flint Knapping

A good flint lasts 20–30 shots before requiring re-knapping. A skilled user can re-knap a flint in seconds.

### Suitable Materials

| Material | Quality | Locations |
|----------|---------|-----------|
| **English black flint** | ★★★★★ Best | Chalk deposits, SE England |
| **French amber flint** | ★★★★ Very good | Paris basin |
| **Chert** | ★★★★ Very good | Worldwide in limestone |
| **Quartzite** | ★★★ Good | AU outback, many locations |
| **Agate / chalcedony** | ★★★ Good | Volcanic regions, AU gem fields |
| **Obsidian** | ★ Too brittle | Volcanic. Shatters on first strike. Not suitable. |

**AU sources:** Chert nodules common in the Sydney Basin, Flinders Ranges, and Kimberley region. Quartzite abundant throughout Central Australia. Agate found in Queensland gem fields (Agate Creek, Mount Hay).

### Knapping Procedure

{% steps() %}
Start with a flint blank approximately 25 mm wide × 30 mm long × 8 mm thick;
Hold the flint firmly — Leather-padded hand or protected in a vise.;
Using a small hammer or pressure flaker (antler tine or copper rod), strike the edge at approximately 45° — The goal is to remove a flake from the top edge of the flint, creating a fresh, sharp edge.;
Work across the width — A series of small, controlled flakes rather than one large blow.;
The resulting edge should be straight and sharp — Not jagged (catches on frizzen), not rounded (no sparks).;
Test on a piece of steel — A sharp flint should produce visible sparks when scraped firmly.;
Install in the cock — Cinch down with lead or leather cushion between flint and jaws. The cushion prevents cracking and allows angle adjustment.
{% end %}

{% info() %}
**Flint orientation:** Bevel up or bevel down? Both work. French/English military practice favoured bevel-up (flat face against frizzen). Some sporting guns use bevel-down. The important thing is that the striking edge contacts the frizzen at approximately 60°. Experiment to find what works best with your lock geometry.
{% end %}

## Maintenance

### Daily (After Shooting)

{% steps() %}
Wipe the frizzen face clean — Carbon fouling builds up and smothers sparks. A quick wipe with a dry cloth after every few shots.;
Clean the pan — Remove powder residue. A damp patch, then dry.;
Check flint sharpness — If edge is rounded, re-knap.;
Oil all pivot points — Cock screw, frizzen screw, sear engagement.;
Check screws for tightness — Lock screws work loose from vibration.;
Wipe down the entire lock — Light oil film to prevent rust.
{% end %}

### Weekly (During Active Use)

- Remove the lock from the stock (one or two screws)
- Brush out all internal fouling (old toothbrush or dedicated bronze brush)
- Check mainspring for cracks (spring steel fatigues)
- Check sear engagement — sear tip should engage tumbler notch fully, not just on the edge
- Check frizzen spring tension — frizzen should snap firmly closed

### Trigger Pull Tuning

A good trigger pull for a military musket is 2.5–4.5 kg. For a hunting/sporting gun, 1.5–2.5 kg is achievable with careful sear work.

## Common Problems

| Problem | Cause | Fix |
|---------|-------|-----|
| No sparks | Frizzen too soft | Re-harden frizzen face |
| No sparks | Flint dull | Re-knap flint |
| Weak sparks | Frizzen face worn unevenly | Re-face or re-harden |
| Sparks but no ignition | Touch hole blocked | Pick through with vent pick |
| Sparks but no ignition | Priming powder damp or coarse | Replace with fresh, fine (FFFFg) powder |
| Cock falls to half-cock on firing | Sear spring too weak | Re-temper or replace sear spring |
| Cock won't hold at full-cock | Sear tip worn or notch damaged | Re-cut sear tip and/or notch; re-harden |
| Slow ignition ("whoosh-bang") | Touch hole too small or blocked | Open touch hole to 1.5–2.0 mm; ensure clear |
| Frizzen won't stay closed | Frizzen spring broken | Replace spring |
| Flint shatters on first strike | Poor quality flint (obsidian, flawed chert) | Use better flint; softer cushion |

## The Touch Hole

The touch hole is a precision detail that dramatically affects lock time (delay between trigger pull and shot). 

- **Diameter:** 1.5–2.0 mm
- **Location:** Centered in the pan, at or just above the pan floor level
- **Shape:** Coned internally (wider on the inside) is ideal — allows faster flash propagation
- **Material:** A hardened steel vent liner can be threaded into the barrel, providing a replaceable touch hole that resists erosion

A touch hole that is too small (< 1.0 mm) causes slow ignition. One that is too large (> 2.5 mm) vents too much pressure and sprays burning gas out sideways — dangerous to anyone beside the shooter.
