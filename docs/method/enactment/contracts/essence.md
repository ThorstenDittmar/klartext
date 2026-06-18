# Dependency Contract (instance): Essence (OMG Kernel & Language)

> **What this is.** The klartext-specific **Dependency Contract** for the **Essence** meta-language — the
> concrete clauses E1–E4 below. For *what a Dependency Contract is* (when to forge one, the clause /
> blast-radius / falsifiable-check structure, the relation to Environment Knowledge's dependency chain), see
> the L3 element card: [`../../library/dependency-contract.md`](../../library/dependency-contract.md).
> **The dependency.** The **OMG Essence specification**, pinned baseline **v1.2** (`formal/18-10-02`, July 2018).
> For provenance, the version pin, and the *referenced-never-vendored-never-extracted* rule see the L3 Resource
> card: [`../../library/resources/essence.md`](../../library/resources/essence.md).
> **Why a contract here.** This is a **seam** like the superpowers one, but with a twist: there is no *install*
> to resolve — Essence is **rendered**, not installed. We **own** a self-contained summary
> (`../../library/semat-definition.md` + `alpha-states.md`) of a standard we **do not own**. If our rendition
> silently drifts from the pinned baseline — by reinterpretation, by mixing in v2.0-beta concepts, or by an
> upstream move we never notice — then the *entire* L3 Library that builds on the Kernel vocabulary rests on an
> unstated baseline, and cross-project transfer (the OE hub) can no longer reconcile our rendition with a
> consumer's adapted copy. The contract turns that silent drift into a caught failure.
> **Language.** English — documentation-language rule.
>
> **Status:** draft v1 (2026-06-18) · **Owner:** OE (contract form + clauses + the rendition); SA (L3
> well-formedness of the rendition) · **Advances Alpha:** Way of Working

## The seam — three parts

| Face | What | Modeled as | Owner |
|---|---|---|---|
| **Uncontrolled** (external) | the OMG Essence standard itself — its Kernel (Alphas, areas, competencies), its Language, the editions OMG publishes (v1.2 formal; v2.0 beta) | the **Resource card** (`../../library/resources/essence.md`) + the version pin; an upstream change is observed, not authored by us | OMG (content) |
| **Controlled** (our artifact) | our **self-contained rendition** (`semat-definition.md` summary + `alpha-states.md` state checklists) **and** our extensions (klartext Practices/Patterns + tracked Work Products) on top of the Kernel | our own L3 files + the practice/pattern cards | OE |
| **The seam** | the invariants below — *whichever* side provides them | **this Dependency Contract** | OE |

## The contract — invariants

Each clause states what must hold, its **blast radius** if violated, and its **falsifiable check** (the
mechanization that makes it checkable, or — where mechanization is not yet built — the explicitly-named ritual
that stands in).

| # | Invariant | Blast radius if violated | Falsifiable check | Holds today? |
|---|---|---|---|---|
| **E1** | The **baseline is pinned** — our rendition declares it summarizes OMG Essence **v1.2** (`formal/18-10-02`), explicitly, in both `semat-definition.md` and the Resource card. | Without the pin, the whole method vocabulary rests on an *unstated* edition; an upstream move (or a consumer's diverged copy) is undetectable — the OE transfer hub cannot reconcile two renditions. | The version string `v1.2` / `formal/18-10-02` is present in `semat-definition.md`'s baseline-pin note **and** the Resource-card provenance table. Grep-able; candidate for the method-classification gate. | ✅ (pinned in both places, #174) |
| **E2** | **Rendition fidelity** — our self-contained summary faithfully represents the *pinned* Kernel (the seven Alphas, the three areas, the state-checklist concept, the Practice/Method language); it is a summary, **not** a divergent reinterpretation. | If our rendition invents or bends Essence concepts, **KB-first lookups return the wrong meta-language** → we forge parallel concepts (Eigensaft, the RC2 class the Classify step guards against) and think we are "in Essence" when we are not. | The rendition is reviewable against the OMG spec **at the pinned version**; SA's L3 well-formedness review + the KB-first rule are the standing checks. Mechanization (a structural diff against a Kernel element list) is open. | ⚠️ **Ritual** — SA-reviewed (L3 well-formedness, #174); no mechanized fidelity diff yet |
| **E3** | **Extensions on top, never modifications** — our additions (klartext Practices/Patterns, tracked Work Products) sit **beside** the Kernel; we never alter the standard's Kernel itself. | If we modify the Kernel (rename an Alpha, change the areas), we **fork Essence** — and lose the "same standard" basis that makes cross-project transfer meaningful (a consumer inheriting our rendition would inherit a non-standard Kernel). | Our extensions are declared as extensions (separate practice/pattern cards); the Kernel description in `semat-definition.md` matches v1.2's elements, unmodified. Reviewable (SA L3); candidate vendoring/fidelity lint. | ✅ (by construction — extensions are separate cards; the Kernel section is rendition-only) |
| **E4** | A **baseline bump is a deliberate, reviewed event**, not a silent adoption — the pin (v1.2) only moves when someone re-reads the new edition (e.g. v2.0 going formal) and confirms our rendition **and** extensions still compose. | An upstream edition can change the Kernel *under us*; silently pulling v2.0 concepts into the rendition while the pin still says v1.2 means our cards reference a baseline the pin does not declare — exactly the **Controlled Method Rollout** "breaking for a drifted consumer" case, now at the meta-language layer. | The pin lives in the Resource card + this contract; moving it requires re-rendering against the new edition, re-checking E2/E3, and updating the pin in the same change. Convention today (a rendition does not auto-update). | ✅ (convention — pin is explicit; no float possible for a frozen rendition) |

**E1/E2 — why a check and not just trust.** Because the rendition is *self-contained*, nothing forces it to
match upstream — that independence is the RC4 medicine (we do not break when the OMG site moves), but it is
also the risk: the rendition can quietly say something the standard does not. E1 catches "no declared baseline";
E2 catches "declared, but the rendition has drifted from it." Both are silent at change-time — the cards still
*read* fine, they just rest on a meta-language that is no longer the pinned standard.

**E2 — the SA seam.** Rendition fidelity against the standard is **SA's L3 well-formedness face** (SA reviews
whether an L3 card is properly generic and standard-conformant). SA reviewed the Resource card + pin on #174;
the rendition body in `semat-definition.md` carries the same review hat. The clause stays ritual until a
mechanized Kernel-element diff lands — an open OE/SA candidate.

## Why a contract here (the lever this seam gives us)

Like superpowers, we **own** the inner face (the rendition + extensions), so the contract is a **design lever**,
not just risk to watch: we *build* the rendition to declare-its-baseline (E1) and to extend-not-modify (E3), so
a violation on **either** side — an upstream edition moving *or* a rendition drifting into reinterpretation — is
caught against the **same** clauses. This is what lets the OE transfer hub later merge our rendition with
semAIt's adapted one: both declare the same pinned baseline, so their delta is *derivable* rather than guessed.

## Relationship to other elements

- **Dependency Contract (L3 element)** (`../../library/dependency-contract.md`) — the generic definition this file instances.
- **Essence Resource card** (`../../library/resources/essence.md`) — the referenced material, its provenance and version pin; this contract states what we *require* of it.
- **superpowers contract** ([`superpowers.md`](superpowers.md)) — the sibling L2 instance; same clause shape, tilted toward an *installed* dependency where this one is tilted toward a *rendered* one.
- **Controlled Method Rollout** — an upstream edition that violates E2/E4 for a drifted consumer is **breaking** → barrier mode. This contract feeds that classification.
- **`semat-definition.md` + `alpha-states.md`** — the rendition the clauses guard.

## Status & open

- **E1** (baseline pinned) — ✅ pinned in `semat-definition.md` + the Resource card (#174).
- **E2** (rendition fidelity) — ⚠️ ritual; SA-reviewed for L3 well-formedness; mechanized Kernel-element diff open.
- **E3** (extend, never modify) — ✅ by construction.
- **E4** (bump is deliberate) — ✅ convention; a frozen rendition cannot auto-float.
- **Open (OE/SA):** whether E2 graduates from ritual to a mechanized fidelity check (a structural diff of the
  rendition's Kernel section against the pinned edition's element list). Non-blocking; tracked as a candidate
  Improvement Step.
