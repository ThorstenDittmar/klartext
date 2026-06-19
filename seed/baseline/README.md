# seed/baseline — generic baseline artefacts (ship as_is)

The endeavour-agnostic starting content of the method seed: the **baseline agent-team framework** and the
**L2 enactment skeleton + worked example**. These are deliberately *generic* — the source endeavour's live
`agents/` is its real team (domain *Fachlichkeit*, excluded from the seed), so the seed cannot ship it. The
files here are authored generic skeletons with `<…>` placeholders and `EXAMPLE — replace with yours` banners.

Disposition in `seed/MANIFEST.toml`: **`as_is`** — copied verbatim into the assembled bundle (no `seed.toml`
rendering); the consumer edits the placeholders.

## Contents

- `agents/<role>/{start.sh, allowed-tools.txt, claude.md}` — the **baseline roles**: `oe` (method/org),
  `devops`, `system-architect`, `qa`, `product-owner`. Each is a thin generic role definition.
- `agents/_domain-expert/**` — the **one cloneable domain template**; clone per consumer domain.
- `agents/team.yaml` — the **baseline roster**.
- `l2/_skeleton.md` — the **L2 enactment card skeleton** (copy per practice you enact).
- `l2/EXAMPLE-improvement-step.md` — **one worked example** of a filled L2 card.

## Language

English now. A bilingual (DE+EN) rendering of the governance/L2 templates is the flagged follow-up
(plan decision 1) — tracked, not dropped.

## Stand-up

`agents/_domain-expert` excepted (it is a `clone-me` template, not a live role), these become the new team's
`agents/` and `team.yaml` after assembly — see the `project-onboarding` L3 practice card.
