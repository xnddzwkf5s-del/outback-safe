+++
title = "Gates"
description = "The weakest point in any wall — designing gates that resist attack"
weight = 3
+++

# Gates

Every wall must have openings — for people, animals, and vehicles. Every opening is a weakness. The art of gate design is making those openings defensible.

## The Problem

Consider a 200 m perimeter wall with a 3 m gate:

- **200 m of wall**: Attackers must scale a vertical face while defenders shoot at them from above and drop things on them
- **3 m of gate**: Attackers face a door. Behind that door is... inside.

The gate represents 1.5% of your perimeter but 90% of an attacker's focus. Plan accordingly.

## Gate Design Principles

### 1. The Gate Is a Killing Zone

The approach to your gate should be a place no attacker wants to be. Defenders should be able to engage attackers from above, from the sides, and from behind (via sally ports).

### 2. Never a Straight Approach

A straight path to your gate allows attackers to build momentum (a battering ram charge). Force turns:

```
    BAD (straight approach):
    
    ═══════════╦═══════════
               ║
    ATTACKERS ─►╠══ GATE
               ║
    ═══════════╩═══════════
    
    GOOD (angled approach):
    
    ═══════════╦═══════════
               ║
               ║  GATE
               ║
               ╚═══════════
                    ▲
                    │
               ┌────┘
               │
    ATTACKERS ─┘
```

A 90° turn just before the gate forces attackers to slow down and exposes their flank to defenders on the wall.

### 3. Redundancy

Two barriers are better than one:

```
    OUTSIDE ──► OUTER GATE ──► "KILLING CHAMBER" ──► INNER GATE ──► INSIDE
```

If the outer gate is breached, attackers find themselves in an enclosed space with defenders on the walls above. This is a killing chamber (barbican).

### 4. Overhead Coverage

The gate passage should be covered. Defenders drop things through murder holes in the ceiling while attackers try to break through the inner gate.

```
        ┌─────────────────────┐
        │  DEFENDERS HERE     │
        │        │            │
        │   ┌────▼────┐       │
        │   │ MURDER   │       │
        │   │ HOLES    │       │
        │   └────┬────┘       │
        │        │            │
    ────┼────────▼────────┼───
        │   GATE PASSAGE   │
        │                  │
    ════╪══════════════════╪═══  ← Wall
        │   ┌──────────┐   │
        │   │  INNER   │   │
        │   │  GATE    │   │
        └───┴──────────┴───┘
```

## Gate Construction

### Gate Leaves (Doors)

**Materials:**
- Heavy timbers (15–20 cm thick), vertically oriented
- Cross-braced on the inside with diagonal timbers
- Iron or steel reinforcing straps (if available)
- Heavy iron hinges

**Design:**

```
    OUTSIDE VIEW:
    
    ┌────────────────────┐
    │┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃│  ← Vertical timber planks
    │┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃│     (15-20 cm thick)
    │┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃│
    │┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃│
    │┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃│
    └────────────────────┘
    
    INSIDE VIEW:
    
    ┌────────────────────┐
    │┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃│
    │┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃ ┃│
    │┃ ┃\┃ ┃ ┃ ┃ ┃/┃ ┃ ┃│  ← Diagonal braces
    │┃ ┃ ┃\┃ ┃ ┃/┃ ┃ ┃ ┃│
    │┃ ┃ ┃ ┃\┃/┃ ┃ ┃ ┃ ┃│
    │┃ ┃ ┃ ┃ ┃X┃ ┃ ┃ ┃ ┃│  ← Cross-brace centre
    │┃ ┃ ┃ ┃/┃\┃ ┃ ┃ ┃ ┃│
    └────────────────────┘
           ↑     ↑
         Heavy iron hinges
```

{% steps() %}
Frame the gate opening — Heavy timber frame set into the wall. The frame, not the wall, carries the gate weight and impact loads.;
Fabricate the gate leaves — Each leaf is 1.5–2 m wide (for a 3–4 m total opening). Timber planks 15–20 cm thick, edge-jointed with tongue-and-groove or shiplap.;
Install diagonal bracing — On the inside face, braces run from the hinge side (bottom) to the latch side (top). This transfers impact loads to the hinges and frame rather than sagging the gate.;
Install hinges — Heavy iron strap hinges. Each leaf needs at least two hinges (three for gates over 2.5 m tall). The hinge pins should be at least 25 mm diameter.;
Install the latch beam — A heavy timber bar (drawbar) that slides across both leaves from the inside. This bar takes the impact of a ram, not the latch mechanism.;
Install a wicket gate (optional) — A small person-sized door set into one leaf. Allows passage without opening the heavy main gate. The wicket itself must be heavily reinforced — it becomes a target.
{% end %}

### The Drawbar

The drawbar is the critical component. It's a heavy timber beam (15 × 15 cm minimum) that slides through iron or hardwood brackets on the inside of the gate leaves, spanning the full width and embedded in the frame on both sides.

```
    ┌──────────────────────────────────────┐
    │                                      │
    │  ┌────┐                         ┌────┤
    │  │    │ ════════════════════    │    │
    │  │    │     DRAWBAR           →│    │  ← Slides into socket
    │  └────┘ ════════════════════    └────┤     in frame
    │                                      │
    │         GATE LEAVES                  │
    └──────────────────────────────────────┘
```

A properly seated drawbar distributes the force of a battering ram across the entire gate frame, not just the latch point.

## Barbican (Gatehouse)

A barbican is a fortified gate complex — the outer gate, a killing chamber, and an inner gate:

```
    ┌────────────────────────────────────────────┐
    │                                            │
    │   OUTER GATE    KILLING CHAMBER  INNER GATE│
    │                                            │
    │  ┌────────┐    ┌──────────────┐  ┌───────┐ │
    │  │        │    │              │  │       │ │
    │  │        ├────┤              ├──┤       │ │
    │  │        │    │              │  │       │ │
    │  └────────┘    └──────┬───────┘  └───────┘ │
    │                       │                    │
    └───────────────────────┼────────────────────┘
                            │
                    ┌───────▼───────┐
                    │ MURDER HOLES  │
                    │ (ceiling)     │
                    └───────────────┘
```

### Construction

{% steps() %}
Build two parallel walls extending outward from the main wall — These create the chamber. Length: 5–10 m. Height: At least as high as the main wall, preferably higher.;
Install the outer gate at the outer end — This is the first barrier.;
Install the inner gate at the inner end — Matching the main wall.;
Build the roof — Heavy timber with open gaps (murder holes) between the beams. The roof is walkable — defenders can stand above the passage.;
Add side arrow loops — Slots in the side walls allow defenders to shoot into the chamber from protected positions.;
Portcullis (optional, advanced) — A vertically-sliding grille of heavy timber or iron that drops to seal either gate. See below.
{% end %}

### The Portcullis

A portcullis is a heavy timber (or iron) grille that drops vertically in grooves cut into the gate passage walls.

```
        ┌─────────────────┐
        │   WINDLASS      │  ← Raises/lowers portcullis
        │   (above)       │
        └────────┬────────┘
                 │
                 │ Chain or rope
                 │
    ┌────────────▼────────────┐
    │ ┃  ┃  ┃  ┃  ┃  ┃  ┃  ┃ │
    │ ┃  ┃  ┃  ┃  ┃  ┃  ┃  ┃ │  ← Heavy timber grille
    │ ┃  ┃  ┃  ┃  ┃  ┃  ┃  ┃ │     in vertical groove
    │ ┃  ┃  ┃  ┃  ┃  ┃  ┃  ┃ │
    │ ┃  ┃  ┃  ┃  ┃  ┃  ┃  ┃ │
    └────────────────────────┘
```

The bottom of each vertical timber is pointed or shod with iron. The weight of the portcullis (200–500 kg for a typical gate) drives the points into the ground or a sill, securing the gate.

A portcullis can be dropped quickly (cut the rope) and raised slowly (via windlass). It requires significant metalwork (chains, windlass gears) but is a devastatingly effective gate defense.

## Sally Port

A sally port is a small, concealed gate used for:

- Counter-attacks (sallies) during a siege
- Escape if the main gate is breached
- Quiet entry/exit without opening the main gate

### Design

- **Location:** Hidden from approach paths — behind a building, in a fold of terrain, screened by vegetation
- **Size:** Just large enough for one person at a time (60 cm wide × 150 cm tall)
- **Construction:** As strong as the main gate per unit area
- **Concealment:** From the outside, it should be indistinguishable from the surrounding wall

## Gate Defense During an Attack

If attackers reach your gate:

1. **Close and bar the gate immediately** — Do not wait to see what they intend
2. **Man the wall positions above and beside the gate** — Archers, crossbow users, anyone who can throw rocks
3. **Drop obstacles through murder holes** — Rocks, boiling water, burning material, anything heavy or unpleasant
4. **If a ram is being used**, drop a mattress, straw bale, or anything soft in front of the gate (absorbs impact) — or drop a heavy timber to jam the ram
5. **If the outer gate is breached**, defenders retreat behind the inner gate. The killing chamber is now the battleground — and it's designed to favour the defenders
6. **Sally out** — If the attackers are fully committed to the gate, a sally port on the opposite side allows defenders to exit and attack from behind
