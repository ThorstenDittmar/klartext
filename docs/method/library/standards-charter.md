# Standards Charter

> **Scope.** The generic, transferable **meta-standard** — *how* an endeavour sets and enforces its own
> engineering standards. It defines what makes a rule a **standard** (a rule with an automated check) and the
> few cross-cutting meta-rules that hold regardless of language or stack. A seed artefact: a consumer adopts the
> *meta-standard* and fills it with *its own* concrete standards.
> **Out of scope.** Any specific endeavour's concrete coding standards — its OOP style, layer structure, naming,
> error-handling rules. Those are an endeavour's own choices; they travel only as **worked examples** (§4), never
> as rules a consumer must adopt. The decision-recording mechanism (`adr-mechanism.md`) and the Essence
> meta-language (`semat-definition.md`) are siblings, not part of this charter.
> **Anti-pattern guarded.** A "standard" that is only documentation — written down but with no automated check, so
> it erodes silently under pressure (RC2). A pattern whose check is deferred to "later" — which means never.
> **Language.** English — documentation-language rule.

## 1. What a standard is

A **standard** is a rule **with an automated check**. The check — a linter rule, a test, a CI gate, a pre-commit
hook — is what makes the rule binding. A rule *without* a check is **documentation, not a standard**: it depends
on everyone remembering it, and it decays the moment someone is in a hurry. This is the load-bearing definition of
the whole charter; everything else follows from it.

The corollary is the bar for adding any standard: **if you cannot (yet) mechanize the check, you have written a
convention, not a standard** — and you must say so honestly (an explicitly ritual-enforced rule with a named path
to mechanization, §3), rather than calling documentation a standard.

## 2. The meta-rules

These four rules are **transferable as-is** — they are about *how* you work, not *what* stack you work in:

1. **Rule + check in the same commit.** When you establish a new pattern, its enforcement (the linter rule, the
   test) lands in the **same commit**. A pattern documented now and enforced "later" is documentation now and
   forever. This is the operational form of §1.
2. **Test-first (TDD).** Write the test before the implementation. The test states the *expectation*; the
   implementation satisfies it. This makes the standard's intent executable from the start, not retrofitted.
3. **Enforce by test, not by review comment.** A review comment is forgotten under time pressure; a failing test
   is not. Where a rule matters, encode it as a check that fails loudly — the review catches *judgment*, the test
   catches *regressions*.
4. **A contract change updates its consumers in the same commit.** When a shared contract changes — an API
   schema, an interface, a data shape — every consumer of that contract is updated in the **same commit**, and a
   check (a type-check, a contract test) verifies the two sides agree. This is the generalized form of the
   API-contract rule: contracts never drift silently between producer and consumer.

## 3. The enforcement ladder

A check can sit at several levels, cheapest-and-earliest first:

1. **Pre-commit hook** — fastest feedback, runs on the author's machine before the commit is even made.
2. **CI gate** — the authoritative barrier; nothing merges that does not pass.
3. **Infrastructure / contract test** — for rules a static linter cannot see (a schema actually resolves, a
   migration actually applies, a health endpoint actually answers).

A rule may legitimately start as **ritual** (enforced by a team agreement, not yet by mechanism) — but only when
mechanization is genuinely not yet available, and only **with a named path** to a check. "Ritual forever" is the
RC2 failure wearing a different hat. The direction is always *ritual → mechanized*, never the reverse.

## 4. Transferable charter vs example fillings

This is the same cut as the method/product separation (the generic meta-standard travels; the lived content does
not):

- **Transferable (adopt as-is):** the definition (§1), the four meta-rules (§2), and the enforcement ladder (§3).
  A consumer wires these to its own toolchain — its own linters, its own CI, its own pre-commit framework.
- **Example fillings (read as models, not adopt):** the source endeavour's **concrete** standards — its
  layer-boundary rule, its API-contract rule, its health-endpoint rule, its naming conventions — ship as
  **worked examples** that show what a *mechanized* standard looks like in practice (the rule, plus the linter or
  test that enforces it). They demonstrate the meta-standard; they are **not** norms a consumer must inherit. A
  consumer picks its **own** concrete standards and runs each one through §1–§3.

## 5. Related

- [`adr-mechanism.md`](adr-mechanism.md) — how a standard is **decided** (the ADR lifecycle); this charter is how
  a decided standard is **enforced**. A new cross-cutting standard is typically ratified as an ADR, then lives
  under this charter.
- [`dependency-contract.md`](dependency-contract.md) — a sibling composed L3 element; an external dependency is
  bound with a validity/version check, the dependency-layer form of "a rule with a check".
- This document is registered in the method register `enactment/method.md` as a **composed L3 element** — named in
  the composition statement alongside [`adr-mechanism.md`](adr-mechanism.md). It carries no separate
  Practices/Patterns lifecycle row (it is a charter, not a run-and-validated Practice), but — unlike the pure
  meta-language reference `semat-definition.md` — it *is* a composed element of our way of working.
