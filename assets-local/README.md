# assets-local — External Reference Assets

This directory holds downloaded external reference material that **cannot** be committed to the
repository: licensed content, form-gated downloads, large binaries.

The directory itself (and this README) is tracked by git. All other files are gitignored.

## Why not ~/Downloads?

macOS TCC blocks agent shells from reading `~/Downloads` (Operation not permitted).
This directory is inside the repository root and is readable by all agent sessions.

## File register

Add one row per file when you place it here. This is the durable record of what exists, where
it came from, and under what terms — RC1-compliant (no artifact without a home + provenance).

| Filename | Source / URL | License / Terms | Acquired | Notes |
|---|---|---|---|---|
| `alpha_state_cards_ecards.pdf` | IJI Practice Library — https://www.ivarjacobson.com/practicelibrary | Free form-gated download (IJI); content reflects the OMG Essence standard | 2026-06-10 | Essence Alpha State Cards (96 pp.) — 7 kernel Alphas with state checklists; source for `docs/method/library/alpha-states.md` |
| `agile_essentials_practice_cards.pdf` | IJI Practice Library — https://www.ivarjacobson.com/practicelibrary | Free form-gated download (IJI) | 2026-06-10 | Agile Essentials practice pack (7 practices incl. Agile Retrospective Essentials) — source material for our retro practice card |
| `atdd-tdd_card_pack_-_ecards.pdf` | IJI Practice Library — https://www.ivarjacobson.com/practicelibrary | Free form-gated download (IJI) | 2026-06-10 | BDD/ATDD + TDD practice cards — candidate material for RC6 contract surfacing + TDD practice card |

## How to add a file

1. Download directly to this directory (not to `~/Downloads`)
2. Add a row to the table above: filename · source URL · license · date · one-line description
3. Commit the updated README — the binary stays gitignored

## Prerequisites for PDF extraction

To extract text from PDFs into method docs (`docs/superpowers/improvement/`):

```bash
brew install poppler   # provides pdftotext, pdfinfo, pdfimages
```

After installation, **restart Claude Code** (app or IDE extension) so the new Homebrew PATH
takes effect in agent shells.
