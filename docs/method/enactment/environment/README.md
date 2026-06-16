# Environment Work Products

> **Scope.** Home of our **environment Work Products** — version-bound, falsifiable knowledge about the tools
> we *use* but do not *build* (the Claude Code app/CLI, git/GitHub, Supabase, macOS). One file per Resource
> (or coherent fact-cluster).
> **Out of scope.** The practice that governs these files lives in `../practices/environment-knowledge.md`;
> the external reference *assets* themselves (decks, PDFs) are **Resources**, home `assets-local/`.
> **Anti-pattern guarded.** A stale environment fact silently driving a decision (RC4).
> **Language.** English — documentation-language rule.
>
> **Owner:** OE (form + home) · empirical content owned by the agent who verified it (four-eyes).

Each file carries: the fact(s) with a **status tag** (tested / observed-untested / inferred / superseded),
the **version-binding** (tool version + build + date + verifier), a manual **Canary** checklist, and the
**dependency chain** of what relies on the fact. Produced and maintained via the **Environment Knowledge**
practice.

| Work Product | Resource | Version-bound to | Status |
|---|---|---|---|
| `claude-code-app.md` | Claude Code desktop app | v1.12603.1 (Build 3df4fd) | **frozen v1** (DevOps sign-off 2026-06-13) |
