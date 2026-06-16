# Essence Element Card — template & well-formedness contract

> **Purpose.** Every method element (Practice, Pattern, Work Product, Resource, Method, Alpha
> extension) is described on **one card**. This template defines what makes a card a **well-formed
> Essence element** — half (ii) of the F0 acceptance criterion (ADR-0013). A card that omits a
> mandatory field, or restates an external Resource instead of declaring it, is **not** well-formed.
> **Owner:** OE (form) · **SA** ratifies well-formedness · the path (L3 `library/` vs L2 `enactment/`)
> classifies the layer — do **not** add a `layer:` field (a path cannot lie; frontmatter drifts).

---

## Mandatory fields (every card)

Grounded in `semat-definition.md` §3: a Practice references **the Alphas it advances, the Work
Products it produces, and the Activities/Activity Spaces it fills.**

| Field | Meaning | Required |
|---|---|---|
| **Element** | The name. | ✓ |
| **Essence type** | Practice · Pattern · Work Product · Resource · Method · Alpha/sub-Alpha. | ✓ |
| **Advances Alpha** | Which kernel Alpha (+ sub-Alpha) this element progresses. | ✓ for Practice/Pattern/Activity |
| **Work Products** | The tangible artifacts it produces (a Resource produces none — see below). | ✓ for Practice |
| **Activity / Activity Space** | The kernel Activity Space it fills, with the concrete Activity. | ✓ for Practice |
| **External dependencies (referenced Resources)** | Every external Resource this element **references but does not own** (e.g. `superpowers:test-driven-development`, the Essence Kernel/Language). **Empty is allowed and must be written as `none`** — silence is not allowed. | ✓ (NEW) |
| **Enforcement** | mechanical · ritual · convention. | ✓ |
| **NN (non-negotiable)** | ✓ = must run when its trigger applies (skipping needs a recorded deviation); — = strong convention. | ✓ |
| **Status** | living · retired · `superseded by <element>` (+ one-line rationale; elements are never deleted). | ✓ |
| **Owner** | The accountable agent/role. | ✓ |
| **Enacted as** | The skill/hook/script that executes this element today, if any. | when applicable |

> **CI-check scope (SA ratification, PR #137 + #142) — TYPE-CONDITIONAL.** The half-(ii)
> well-formedness check (F0.3, DevOps) is **type-aware**, not a flat 5-field mandate:
> - **Always required (every *standalone* card):** `Essence type` (a clean enum token — keep clarifiers OUT
>   of the value) and `External dependencies` (`none` is allowed; silence is not). **Exception — a delegating
>   L2 card** (one that carries an `L3 definition:` pointer) inherits `Essence type` / `External dependencies`
>   / §3 from its L3 sibling and need not repeat them (see the delegate-XOR-standalone note below).
> - **Required for `Practice` cards only:** `Advances Alpha`, `Work Products`, `Activity Space`
>   (per `semat-definition.md` §3 — these describe a Practice; a Work-Product / Resource / element card
>   is not obliged to carry them).
> The remaining fields (Enforcement, NN, Status, Owner, Enacted as) are klartext **operating** fields,
> not a §3 requirement — the CI check must not demand them. Build the check type-aware, or it checks the
> wrong set.

> **Siblingless-L2 practice cards (SA ratification, PR #150).** Well-formedness is type-driven, not
> stem-driven. A practice card's §3 fields (Advances Alpha / Work Products / Activity Space) must appear on
> exactly one card: on the **L3 sibling** for a split practice (the L2 card delegates via its
> `L3 definition:` pointer), or **inline** for a wholly-L2 practice that has no L3 sibling. The half-(ii)
> check accepts an L2 practice card iff it either delegates (carries an `L3 definition:` pointer) or carries
> the §3 fields inline.
>
> **delegate-XOR-standalone (the unified rule — OE F0.3 ruling, SA to confirm).** Exactly one must hold:
> *(a) delegating* — has an `L3 definition:` pointer; `Essence type` / `External dependencies` / §3 live on
> the L3 sibling, so the L2 card carries only the pointer + klartext bindings. *(b) standalone* — has
> `Essence type` + `External dependencies` (+ §3 inline if a Practice) and **no** `L3 definition:` pointer.
> A card carrying **both** a pointer **and** its own `Essence type` is a malformed half-split (the mechanical
> "mixed-card" signal for the half-(i) gate). Verified 2026-06-16: all 16 L2 cards conform (13 delegating, 3
> standalone) — no rework.

## The wrapper rule (composition over an external Resource)

If the element **wraps** an external Resource (the L3 generic definition lives *upstream*, not with
us — e.g. `tdd` over `superpowers`):

- **Declare** the Resource in *External dependencies*. **Do not restate/paraphrase** the upstream
  content — that is vendoring-by-paraphrase (RC4, second source of truth) and makes the card
  **malformed**.
- The card's own body describes **only the klartext composition/extension delta** (what we add on
  top), plus a one-line pointer to the upstream definition.
- The generic *declaration of the composition* belongs in **L3**; the klartext-specific bindings
  (checklists, levels, tooling) belong in **L2**. Most ritual skills split exactly this way.

## Type-specific notes

- **Resource card** (L3): declares external material we *reference but do not produce* — provenance,
  version binding, and the rule **referenced, never vendored, never extracted** (a consumer installs
  it themselves). Has no Work Products. First instances: `superpowers` plugin, Essence Kernel/Language.
  *(SA ratification, PR #137: "never extracted" applies to the referenced **material**, not to the
  Resource **card** — the card is itself a normal L3 object and travels with the `filter-repo`
  extraction. The extraction author must not exclude Resource cards from the L3 stem.)*
- **Method card** (L2): klartext's method = the composition of L3 Library practices in use, with
  their lived Alpha states. Lists the composed practices; does not redefine them.
- **Pattern card**: a named recurring structure; advances an Alpha, has enforcement, usually no
  Work Product.

---

## Skeleton (copy this)

```markdown
# <Element name>

> **Essence type:** <Practice|Pattern|Work Product|Resource|Method|Alpha>
> **Advances Alpha:** <Alpha (+ sub-Alpha)>  ·  **Work Products:** <…|none>
> **Activity / Activity Space:** <Activity Space → concrete Activity>
> **External dependencies (referenced Resources):** <Resource(s) | none>
> **Enforcement:** <mechanical|ritual|convention>  ·  **NN:** <✓|—>
> **Status:** <living|retired|superseded by …>  ·  **Owner:** <agent/role>
> **Enacted as:** <skill/hook/script | —>

## Purpose
<One paragraph: the repeatable way of doing something, with its clear purpose.>

## Definition / delta
<For a self-owned element: the generic definition.
 For a wrapper: ONLY the klartext composition/extension delta + a pointer to the upstream Resource —
 never a paraphrase of the upstream content.>

## Related
<[[links]] to related cards, the ADR/Improvement-Register row that carries the full why.>
```
