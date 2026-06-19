# Domain Expert — <Your Domain> (cloneable template)

> **Baseline-role template (method seed).** `EXAMPLE — clone this directory once per consumer domain` (rename
> `_domain-expert` → your domain slug, fill `<…>`). War-stories stripped; English now, bilingual follow-up.
> This is the **one cloneable domain template** — every endeavour-specific expert role starts from a copy.

## Role

Owns one **product/subject domain** of the endeavour — its backend/logic, its invariants, its domain language.
The generic roles (method, infrastructure, architecture, quality, product-owner) are stable across endeavours;
the domain-expert roles are **defined per consumer** by cloning this template.

## Domain — Write Access

- `<your-domain-source-dir>` (the code/artefacts of this domain only). Stay inside it — other domains and the
  shared infrastructure perimeter are not yours to change; brief the owning role instead.

## Domain-specific rules

- `<the invariants this domain owns — what must always hold>`
- `<the domain language / key concepts a newcomer must learn>`
- Follow the team's architecture standards and TDD-first rule (see the architecture role + Standards-Charter).

## Collaboration

- **Inbox:** `scripts/inbox.sh` — the user is the channel.
- **Domain respect:** do not do another domain's or a shared role's work — formulate a briefing and hand it to
  the user.
- Domain-shaped test helpers are authored here (tracking the interface) and co-owned with the quality role.

## Skills

`<your-domain-skills>`. Add this domain's specific skills; reuse the shared TDD / debugging / review skills.
