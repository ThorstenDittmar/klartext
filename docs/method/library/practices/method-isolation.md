# Method Isolation

> **Essence type:** Practice
> **Advances Alpha:** Way of Working  ·  **Work Products:** a classified artefact inventory (every artefact sorted method-vs-product) · the separated method layer (its own L3/L2 tree) · the wired keep-separated enforcement (a classification gate / path-ownership)
> **Activity / Activity Space:** Support the Endeavour → isolate an entangled endeavour's transferable **method** from its product **Fachlichkeit**, so the method can be exported and updated without product content bleeding across
> **External dependencies (referenced Resources):** none (the cut criterion is defined by ADR-0013, an internal decision, not an external Resource)
> **Enforcement:** ritual  ·  **NN:** ✓ (when extracting a method from an existing endeavour, or before opening a bidirectional method-transfer channel)
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** the F0→F3 method/product isolation (see `enactment/method-seed-export-plan.md` for klartext's worked run); a `method-isolation` skill is a candidate

## Purpose

**Isolate an entangled endeavour into a transferable *method* layer and its product *Fachlichkeit*** — so the
method can be lifted into a seed and **kept** separate as updates flow back and forth. This is the **export side**
of the method/product cut, and the macro sibling of the two existing cuts: [`document-scoping.md`](document-scoping.md)
cuts a *single document*; this practice cuts the *whole endeavour*; [`project-onboarding.md`](project-onboarding.md)
then stands a *new project up from the seed* (the import side). Triad: **isolate → seed → onboard.**

The driving risk is **bleed**. Method transfer through a hub (OE) is **bidirectional**: a consumer adopts the
seed, adapts it, and later its changes flow back. If the method layer was never cleanly isolated — product
Fachlichkeit left mixed in, or product-specific content lifted as if generic — then that content travels in both
directions, and a consumer's domain can **bleed into the source** through the return channel. Isolation is the
safeguard on **both** ends, not a one-time export chore.

Guards three failure modes: an **incomplete cut** (product Fachlichkeit left in the method layer — it bleeds on
export and on return); **over-extraction** (product-specific content lifted into the method as if it were
generic — a copy-fork at the source); and a **cut with no enforcement** (nothing prevents re-entanglement, so
the layers silently re-tangle — the RC2 "documentation, not a standard" failure applied to the boundary itself).

## Definition / delta

Isolation proceeds **classify-before-move** — sort every artefact *before* relocating anything — in six steps:

1. **Establish the cut criterion.** Make the method/product distinction explicit (ADR-0013): the generic,
   transferable **mechanism** is method; the lived, endeavour-specific **content** is product (and travels, if at
   all, only as a *worked example*). This single criterion drives every later judgement.
2. **Inventory and classify.** Sort **every** artefact into one of five categories — **as-is** (generic, transfers
   unchanged), **template** (structure transfers, content → placeholder/example), **config** (transfers but needs
   path/name parameterization), **declared-not-shipped** (an external dependency the consumer provides; never
   vendored), **exclude** (product Fachlichkeit; never ships). An unclassified artefact is an un-cut artefact.
3. **Separate physically.** Move the method artefacts into their **own layer** (a dedicated tree — e.g. L3 generic
   definitions + L2 enactment), leaving product in the product stack. The boundary must be a *place*, not a
   convention in someone's head.
4. **Cut the entanglement points.** Files that mix both — shared config, the CLI, harness settings — are
   **parameterized, not copied**: the endeavour-specific literals move to a single config source, the structure
   stays generic. (The anti-pattern this closes: de-source-ification as a global `sed`, the fragile mirror of
   over-extraction.)
5. **Wire the keep-separated enforcement.** Install the mechanism that catches re-entanglement — a classification
   gate over the method surfaces, path-ownership, a zero-product-literal check. Until this lands, the cut is a
   one-time snapshot that re-tangles on the next commit; *staying* isolated is the property that defeats bleed.
6. **Verify the cut.** The method layer carries **zero hard product reference** (grep-checkable); the product
   still builds and runs; the bidirectional channel is clean (a return update touches only method surfaces). The
   endeavour is not "isolated" until all three hold.

**Completion (Done):** the cut criterion is explicit · every artefact is classified into the five categories ·
the method is physically separated into its own layer · entanglement points are parameterized (not copied) · the
keep-separated enforcement is wired · the method layer carries **zero product literal** (grep-checkable) · the
product still works.

**Enforcement note (generic).** A ritual owned by the method/organisation role. Its non-negotiable core is
mechanizable: the **zero-product-literal grep** over the method layer (step 6) and the **classification gate**
that keeps surfaces sorted going forward (step 5). A cut whose enforcement is not wired (step 5 skipped) is not
an isolation — it is a snapshot that re-tangles, the boundary-level form of "a rule without enforcement is
documentation" (see [`../standards-charter.md`](../standards-charter.md)).

## Related

- [`project-onboarding.md`](project-onboarding.md) — the import-side sibling (stand a new project up *from* the
  seed). Isolation produces what onboarding consumes.
- [`document-scoping.md`](document-scoping.md) — the micro sibling (cut a single document); this practice is
  the same discipline at endeavour scale.
- [`../standards-charter.md`](../standards-charter.md) — step 5 is the charter's "rule + check" applied to the
  method/product boundary itself.
- ADR-0013 (separating method from product) — the cut criterion this practice operationalizes.
- `enactment/method-seed-export-plan.md` — klartext's **worked example**: the F0→F3 run of this practice, with the
  five-category taxonomy (§1) and the seed anatomy (§2).
