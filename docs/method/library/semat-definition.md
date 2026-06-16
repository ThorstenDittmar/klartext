# SEMAT / Essence — Reference Definition (our meta-language)

> **Scope.** Self-contained reference description of **SEMAT** and the **Essence** standard — the
> meta-language we use to forge and describe our way of working. After reading this, an agent understands
> the vocabulary well enough to communicate with OE using the right terms.
> **Out of scope.** *Our own* process decisions and practices (those live in `continuous-improvement.md`
> and `practices/`); the running term list (`semat-glossary.md`). This document describes the **standard**,
> not our application of it — except the short "How we use it" section at the end.
> **Anti-pattern guarded.** Dependence on the external SEMAT website / an external dependency drifting out
> of our control (see `continuous-improvement.md` RC4); and Eigensaft-by-misunderstanding (§0).
> **Language.** English — documentation-language rule.

---

## 1. What it is

**SEMAT** (*Software Engineering Method and Theory*) is an initiative founded in 2009 by Ivar Jacobson,
Bertrand Meyer and Richard Soley to put software engineering methods on a more solid, theory-based,
practice-oriented footing. Its central product is **Essence**.

**Essence** is an OMG standard: *"Essence — Kernel and Language for Software Engineering Methods."*
It has two parts:

1. A **Kernel** — the small, fixed common ground that *every* software engineering endeavour shares,
   regardless of method. It captures the things you always work with and the things you always do.
2. A **Language** — a notation for describing **Practices** and composing them into **Methods**, all on top
   of the Kernel.

The core idea: you do **not** adopt a heavyweight method wholesale. You take the thin Kernel as given and
**compose your own method from small, reusable Practices** — exactly Alistair Cockburn's *methodology per
project*, made operational.

---

## 2. The Kernel

### 2.1 Three areas of concern

The Kernel groups everything into three areas:

| Area of concern | About | Plain question |
|---|---|---|
| **Customer** | The users and the value | *Who is this for, and why?* |
| **Solution** | The thing being built | *What are we building?* |
| **Endeavour** | The team and its work | *How is the team doing the work?* |

### 2.2 The seven Alphas

An **Alpha** (*Abstract-Level Progress Health Attribute*) is an **essential thing whose state you progress
and track**. The Kernel defines exactly seven, each with a lifecycle of **states**. Each state has a
**checklist** to decide whether it has been reached — the full per-state checklists live in
**`alpha-states.md`** (extracted from the IJI Alpha State Cards, CC BY 4.0 SEMAT Inc.). *(This "thing with a tracked state lifecycle" is the
single most valuable idea we import — see `continuous-improvement.md` RC4.)*

**Customer area**
- **Opportunity** — the reason to build. States: *Identified → Solution Needed → Value Established →
  Viable → Addressed → Benefit Accrued.*
- **Stakeholders** — the people with a stake. States: *Recognized → Represented → Involved → In Agreement →
  Satisfied for Deployment → Satisfied in Use.*

**Solution area**
- **Requirements** — what the system must do. States: *Conceived → Bounded → Coherent → Acceptable →
  Addressed → Fulfilled.*
- **Software System** — the system itself. States: *Architecture Selected → Demonstrable → Usable → Ready →
  Operational → Retired.*

**Endeavour area**
- **Work** — the effort itself. States: *Initiated → Prepared → Started → Under Control → Concluded → Closed.*
- **Team** — the people doing the work. States: *Seeded → Formed → Collaborating → Performing → Adjourned.*
- **Way of Working** — how the team works. States: *Principles Established → Foundation Established →
  In Use → In Place → Working Well → Retired.*

> **The Way-of-Working Alpha is our anchor.** Our continuous improvement *is* the engine that drives this
> Alpha through its states. Our **Improvement Step** practice advances it.

### 2.3 Activity Spaces

An **Activity Space** is a *placeholder for the things you do* — a "what needs doing" without prescribing
"how." A Practice fills activity spaces with concrete **Activities**. The Kernel defines fifteen:

- **Customer:** Explore Possibilities · Understand Stakeholder Needs · Ensure Stakeholder Satisfaction ·
  Use the System
- **Solution:** Understand the Requirements · Shape the System · Implement the System · Test the System ·
  Deploy the System · Operate the System
- **Endeavour:** Prepare to do the Work · Coordinate Activity · Support the Team · Track Progress ·
  Stop the Work

### 2.4 Competencies

A **Competency** is an ability the endeavour needs. The Kernel names six, each rated on five levels
(*1 Assists · 2 Applies · 3 Masters · 4 Adapts · 5 Innovates*):

Stakeholder Representation · Analysis · Development · Testing · Leadership · Management.

---

## 3. The Language — how you extend the Kernel

The Kernel is **fixed but extensible**: you never modify it, you build on it. The Essence Language gives you
the elements to describe your own additions:

- **Alpha / Alpha State** — a tracked thing and its lifecycle (you may add *sub-alphas* under a kernel Alpha).
- **Work Product** — a tangible artifact (document, code, test) produced while progressing an Alpha. Work
  products have *levels of detail*.
- **Activity** — concrete work that fills an Activity Space.
- **Pattern** — any other named structure (e.g. a role, a check).
- **Resource** — external supporting material a Practice *references* but the endeavour does not *produce*
  (standards documents, card decks, guides). Distinct from a Work Product (which we produce). *(Backfilled
  2026-06-10 — gap found while classifying external reference assets.)*
- **Practice** — a **separately-describable, composable** unit: "a repeatable way of doing something with a
  clear purpose." A Practice references the Alphas it advances, the Work Products it produces, and the
  Activities it performs.
- **Method** — the **composition of a Kernel and a set of Practices** to fulfill a specific purpose — together
  forming a complete way of working.
- **Library** — a container/catalog of element groups, notably Practices: a *Practice Library* holds the
  **stock** of described practices; a Method is the **composition actually in use**. *(Backfilled 2026-06-09 —
  the gap was found during a check against the standard and closed in the same step.)*

Essence is **card-based**: every element (Alpha, state, Activity, Practice…) is summarised on a concise card
with its checklist. Cards make the method tangible and checkable rather than a thick manual.

---

## 4. Why it fits an AI multi-agent team

- **Composition over adoption.** We assemble a fitting method from bricks instead of importing a heavyweight
  process — directly against the *Eigensaft* and "too heavy" risks.
- **Explicit states.** Alphas give artifacts and dependencies a lifecycle, so "active vs. recorded" drift
  becomes detectable (RC4).
- **Checklists, not vibes.** "Done" is a checklist-detectable state, matching our DoD discipline.
- **Practices are skill-shaped.** A Practice card maps cleanly onto a Claude Code Skill — the card is the
  description, the skill is the executable enactment.

---

## 5. How we use it (our conventions)

- **As-is, extend-not-modify.** We treat the Kernel and Language as given. We add our own Practices and
  tracked things on top; we never change the standard. What we change *with* Essence is our process.
- **Working hypothesis.** Essence is our chosen meta-language. If it actively fights us in use, we revisit
  it **openly** rather than quietly bending it for convenience.
- **No jargon dumping.** We do not force Essence terms into daily speech. Shared meaning comes from our
  small authoritative `semat-glossary.md` (DDD Ubiquitous Language), which imports from Essence only what
  earns its keep.
- **KB-first lookup.** For SEMAT/method questions, consult this file + the glossary **first** (and say so);
  go to the web only on a miss or for existence questions (this summary is lossy — absence here does not prove
  absence in the standard). Every confirmed gap is **backfilled here in the same step**.
- **Where things live:** this file = the *standard*; `semat-glossary.md` = our *terms*; `practices/` = our
  *Practices*; `continuous-improvement.md` = our *decisions, rationale and plan*.

> **For an agent:** read this file plus `semat-glossary.md`, and you can talk to OE about the way of working
> in the right vocabulary — Alphas, states, Practices, Methods — and propose changes that slot into the
> Kernel instead of reinventing it.

---

*Source: our self-contained summary of the OMG Essence specification (Essence — Kernel and Language for
Software Engineering Methods). Kept self-contained on purpose, so we stay independent of the external site.*
