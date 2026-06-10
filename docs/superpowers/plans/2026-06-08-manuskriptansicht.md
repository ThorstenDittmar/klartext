# Manuskriptansicht — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Manuscript View — a continuous prose editor where each Fragment is an editable `<textarea>`, changes autosave via debounce (1.5s), and the writer sees the full narrative as a scrollable document.

**Architecture:** Five backend-independent components (Breadcrumb, WordCountLabel, SceneBreak, BottomBar, AutosaveIndicator) can be built in parallel with the backend. The `ManuscriptView` page is built after the backend plan (`2026-06-08-narrative-unit-domain.md`) is merged and the API contract is stable. Each Fragment maps to one `<textarea>`. Autosave uses `useRef` debounce — not a library. No external editor library (ADR-0004: Inline-Styles only).

**Tech Stack:** React 18, TypeScript, plain `<textarea>`, inline styles only (ADR-0004). No TipTap (ADR-0008). Storybook 7 for component development. `fetch` for API calls.

**Branch for components:** `task/H01-B1/manuscript-components`  
**Branch for page:** `task/H01-B2/manuscript-view-page` (depends on backend branch merged)

**Design reference:** `design/components/` specs + NovelCrafter write interface (continuous scroll, no panels, scene breaks as headings).

---

## File Map

### Phase 1 — Backend-independent (can start now)

| Path | Status | Responsibility |
|---|---|---|
| `frontend/src/index.css` | MODIFY | Add design tokens (spacing, typography, radius, semantic colors) |
| `frontend/src/utils/wordCount.ts` | CREATE | `countWords(text: string): number` |
| `frontend/src/components/WordCountLabel/index.tsx` | CREATE | "X Wörter" display |
| `frontend/src/components/WordCountLabel/WordCountLabel.stories.tsx` | CREATE | Storybook story |
| `frontend/src/components/AutosaveIndicator/index.tsx` | CREATE | "Gespeichert ✓" / "Speichert…" |
| `frontend/src/components/AutosaveIndicator/AutosaveIndicator.stories.tsx` | CREATE | Storybook story |
| `frontend/src/components/Breadcrumb/index.tsx` | CREATE | Navigation path display |
| `frontend/src/components/Breadcrumb/Breadcrumb.stories.tsx` | CREATE | Storybook story |
| `frontend/src/components/SceneBreak/index.tsx` | CREATE | Visual scene separator |
| `frontend/src/components/SceneBreak/SceneBreak.stories.tsx` | CREATE | Storybook story |
| `frontend/src/components/BottomBar/index.tsx` | CREATE | Fixed bottom bar (word count + autosave) |
| `frontend/src/components/BottomBar/BottomBar.stories.tsx` | CREATE | Storybook story |

### Phase 2 — API integration (after backend merged)

| Path | Status | Responsibility |
|---|---|---|
| `frontend/src/lib/api.ts` | MODIFY | Add NarrativeUnit types + tree/CRUD functions |
| `frontend/src/pages/ManuscriptView/index.tsx` | CREATE | Full manuscript page |
| `frontend/src/pages/ManuscriptView/ManuscriptView.test.tsx` | CREATE | Smoke tests |
| `frontend/src/App.tsx` | MODIFY | Add `/narrative/:id/manuscript` route |

---

## Design Token Reference

All style values must use CSS custom properties. No hex values directly in `style` props (ADR-0004).

```typescript
// Correct
style={{ color: 'var(--color-accent)', padding: 'var(--space-2) var(--space-4)' }}

// Wrong — ADR-0004 violation
style={{ color: '#0C447C', padding: '8px 16px' }}
```

---

## Phase 1 — Backend-independent

### Task 0: Design Tokens in index.css

**Files:**
- Modify: `frontend/src/index.css`

- [ ] **Step 1: Read the current index.css**

```bash
cat frontend/src/index.css
```

Current content (for reference):
```css
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
  --color-bg: #FFFFFF;
  --color-bg-subtle: #F7F7F7;
  /* ... existing color tokens ... */
}
```

- [ ] **Step 2: Add the token blocks**

Append the following blocks inside `:root { }`, after the existing color variables:

```css
  /* ─── Semantic color aliases ─────────────────────────── */
  --color-surface:     var(--color-bg);
  --color-background:  var(--color-bg);
  --color-accent:      var(--color-blue-text);
  --color-on-accent:   var(--color-text-inverse);
  --color-success:     var(--color-green-text);
  --color-error:       var(--color-red-text);

  /* ─── Spacing (4 px base scale) ─────────────────────── */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-6:  24px;
  --space-8:  32px;
  --space-12: 48px;
  --space-16: 64px;

  /* ─── Typography ─────────────────────────────────────── */
  --font-size-xs:    11px;
  --font-size-sm:    13px;
  --font-size-base:  16px;
  --font-size-prose: 18px;
  --font-family-prose: Georgia, 'Times New Roman', serif;

  /* ─── Shape ──────────────────────────────────────────── */
  --radius-sm: 4px;
  --radius-md: 8px;

  /* ─── Layout ─────────────────────────────────────────── */
  --bottom-bar-height: 40px;
```

The final `:root` block should look like this:

```css
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
  --color-bg:             #FFFFFF;
  --color-bg-subtle:      #F7F7F7;
  --color-border:         #E5E5E5;
  --color-border-subtle:  #F0F0F0;
  --color-text-primary:   #1A1A1A;
  --color-text-secondary: #6B6B6B;
  --color-text-tertiary:  #9B9B9B;
  --color-text-inverse:   #FFFFFF;
  --color-green-bg:   #EAF3DE;
  --color-green-text: #3B6D11;
  --color-amber-bg:   #FAEEDA;
  --color-amber-text: #854F0B;
  --color-red-bg:     #FCEBEB;
  --color-red-text:   #A32D2D;
  --color-blue-bg:    #E6F1FB;
  --color-blue-text:  #0C447C;
  --color-teal-bg:    #E1F5EE;
  --color-teal-text:  #0F6E56;

  /* ─── Semantic color aliases ─────────────────────────── */
  --color-surface:     var(--color-bg);
  --color-background:  var(--color-bg);
  --color-accent:      var(--color-blue-text);
  --color-on-accent:   var(--color-text-inverse);
  --color-success:     var(--color-green-text);
  --color-error:       var(--color-red-text);

  /* ─── Spacing (4 px base scale) ─────────────────────── */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-6:  24px;
  --space-8:  32px;
  --space-12: 48px;
  --space-16: 64px;

  /* ─── Typography ─────────────────────────────────────── */
  --font-size-xs:    11px;
  --font-size-sm:    13px;
  --font-size-base:  16px;
  --font-size-prose: 18px;
  --font-family-prose: Georgia, 'Times New Roman', serif;

  /* ─── Shape ──────────────────────────────────────────── */
  --radius-sm: 4px;
  --radius-md: 8px;

  /* ─── Layout ─────────────────────────────────────────── */
  --bottom-bar-height: 40px;
}
```

- [ ] **Step 3: Verify Storybook still loads**

```bash
cd frontend && npm run storybook &
sleep 5 && curl -s http://localhost:6006 | grep -c "storybook"
```

Expected: a number > 0 (Storybook running).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/index.css
git commit -m "feat: add design tokens (spacing, typography, radius, semantic colors)"
```

---

### Task 1: wordCount utility

**Files:**
- Create: `frontend/src/utils/wordCount.ts`

- [ ] **Step 1: Write the utility**

```typescript
/**
 * Counts the number of words in a text string.
 * Splits on whitespace and filters empty tokens.
 * Returns 0 for empty or whitespace-only strings.
 */
export function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(token => token.length > 0).length;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/utils/wordCount.ts
git commit -m "feat: add countWords utility"
```

---

### Task 2: WordCountLabel

**Files:**
- Create: `frontend/src/components/WordCountLabel/index.tsx`
- Create: `frontend/src/components/WordCountLabel/WordCountLabel.stories.tsx`

- [ ] **Step 1: Create the component folder and file**

```bash
mkdir -p frontend/src/components/WordCountLabel
```

```typescript
// frontend/src/components/WordCountLabel/index.tsx
import React from 'react';
import { countWords } from '../../utils/wordCount';

interface WordCountLabelProps {
  /** The full text to count words in. */
  text: string;
}

/**
 * Displays "X Wörter" — a live word count for a block of text.
 * Used in the BottomBar of the Manuscript View.
 */
export function WordCountLabel({ text }: WordCountLabelProps): React.ReactElement {
  const count = countWords(text);

  return (
    <span
      style={{
        fontSize: 'var(--font-size-sm)',
        color: 'var(--color-text-secondary)',
        fontVariantNumeric: 'tabular-nums',
      }}
    >
      {count} Wörter
    </span>
  );
}
```

- [ ] **Step 2: Write the Storybook story**

```typescript
// frontend/src/components/WordCountLabel/WordCountLabel.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { WordCountLabel } from './index';

const meta: Meta<typeof WordCountLabel> = {
  title: 'Atoms/WordCountLabel',
  component: WordCountLabel,
};

export default meta;
type Story = StoryObj<typeof WordCountLabel>;

export const Empty: Story = {
  args: { text: '' },
};

export const ShortText: Story = {
  args: { text: 'Hallo Welt' },
};

export const LongText: Story = {
  args: {
    text: 'Im Jahr 2026 begann eine neue Ära der epistemischen Transparenz in Deutschland.',
  },
};
```

- [ ] **Step 3: Open Storybook and verify at `Atoms/WordCountLabel`**

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/WordCountLabel/
git commit -m "feat: add WordCountLabel component"
```

---

### Task 3: AutosaveIndicator

**Files:**
- Create: `frontend/src/components/AutosaveIndicator/index.tsx`
- Create: `frontend/src/components/AutosaveIndicator/AutosaveIndicator.stories.tsx`

- [ ] **Step 1: Create the component**

```bash
mkdir -p frontend/src/components/AutosaveIndicator
```

```typescript
// frontend/src/components/AutosaveIndicator/index.tsx
import React from 'react';

interface AutosaveIndicatorProps {
  /** When true, shows "Speichert…"; when false, shows "Gespeichert ✓". */
  saving: boolean;
}

/**
 * Indicates autosave state in the Manuscript View bottom bar.
 * Shows a saving message during the debounce window, success after.
 */
export function AutosaveIndicator({ saving }: AutosaveIndicatorProps): React.ReactElement {
  return (
    <span
      style={{
        fontSize: 'var(--font-size-sm)',
        color: saving ? 'var(--color-text-secondary)' : 'var(--color-success)',
        transition: 'color 0.3s ease',
      }}
    >
      {saving ? 'Speichert…' : 'Gespeichert ✓'}
    </span>
  );
}
```

- [ ] **Step 2: Write the story**

```typescript
// frontend/src/components/AutosaveIndicator/AutosaveIndicator.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { AutosaveIndicator } from './index';

const meta: Meta<typeof AutosaveIndicator> = {
  title: 'Atoms/AutosaveIndicator',
  component: AutosaveIndicator,
};

export default meta;
type Story = StoryObj<typeof AutosaveIndicator>;

export const Saving: Story = {
  args: { saving: true },
};

export const Saved: Story = {
  args: { saving: false },
};
```

- [ ] **Step 3: Verify in Storybook at `Atoms/AutosaveIndicator`**

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/AutosaveIndicator/
git commit -m "feat: add AutosaveIndicator component"
```

---

### Task 4: Breadcrumb

**Files:**
- Create: `frontend/src/components/Breadcrumb/index.tsx`
- Create: `frontend/src/components/Breadcrumb/Breadcrumb.stories.tsx`

- [ ] **Step 1: Create the component**

```bash
mkdir -p frontend/src/components/Breadcrumb
```

```typescript
// frontend/src/components/Breadcrumb/index.tsx
import React from 'react';

export interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
}

interface BreadcrumbProps {
  /** Ordered path segments. The last item is the current location (not clickable). */
  items: BreadcrumbItem[];
}

/**
 * Navigation breadcrumb path.
 * All items except the last are rendered as clickable buttons.
 * Separator: › (right angle quotation mark).
 */
export function Breadcrumb({ items }: BreadcrumbProps): React.ReactElement {
  return (
    <nav aria-label="Breadcrumb">
      <ol
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-1)',
          listStyle: 'none',
          margin: 0,
          padding: 0,
        }}
      >
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li
              key={index}
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}
            >
              {isLast ? (
                <span
                  aria-current="page"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-primary)',
                    fontWeight: 500,
                  }}
                >
                  {item.label}
                </span>
              ) : (
                <>
                  <button
                    onClick={item.onClick}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: item.onClick ? 'pointer' : 'default',
                      fontSize: 'var(--font-size-sm)',
                      color: item.onClick
                        ? 'var(--color-accent)'
                        : 'var(--color-text-secondary)',
                      textDecoration: item.onClick ? 'underline' : 'none',
                    }}
                  >
                    {item.label}
                  </button>
                  <span
                    aria-hidden="true"
                    style={{
                      color: 'var(--color-text-secondary)',
                      fontSize: 'var(--font-size-sm)',
                    }}
                  >
                    ›
                  </span>
                </>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
```

- [ ] **Step 2: Write the story**

```typescript
// frontend/src/components/Breadcrumb/Breadcrumb.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import { Breadcrumb } from './index';

const meta: Meta<typeof Breadcrumb> = {
  title: 'Molecules/Breadcrumb',
  component: Breadcrumb,
};

export default meta;
type Story = StoryObj<typeof Breadcrumb>;

export const TwoLevels: Story = {
  args: {
    items: [
      { label: 'Meine Werke', onClick: action('navigate-home') },
      { label: 'Der Aufstand' },
    ],
  },
};

export const ThreeLevels: Story = {
  args: {
    items: [
      { label: 'Meine Werke', onClick: action('navigate-home') },
      { label: 'Der Aufstand', onClick: action('navigate-narrative') },
      { label: 'Kapitel 1' },
    ],
  },
};

export const SingleLevel: Story = {
  args: {
    items: [{ label: 'Der Aufstand' }],
  },
};
```

- [ ] **Step 3: Verify in Storybook at `Molecules/Breadcrumb`**

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Breadcrumb/
git commit -m "feat: add Breadcrumb component"
```

---

### Task 5: SceneBreak

**Files:**
- Create: `frontend/src/components/SceneBreak/index.tsx`
- Create: `frontend/src/components/SceneBreak/SceneBreak.stories.tsx`

- [ ] **Step 1: Create the component**

```bash
mkdir -p frontend/src/components/SceneBreak
```

```typescript
// frontend/src/components/SceneBreak/index.tsx
import React from 'react';

interface SceneBreakProps {
  /** The scene title displayed in the center of the break. */
  title: string;
}

/**
 * Visual separator between scenes in the Manuscript View.
 * Scene title centered between two horizontal rules.
 */
export function SceneBreak({ title }: SceneBreakProps): React.ReactElement {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-3)',
        margin: 'var(--space-8) 0 var(--space-4) 0',
      }}
    >
      <div
        style={{
          flex: 1,
          height: 1,
          backgroundColor: 'var(--color-border)',
        }}
      />
      <span
        style={{
          fontSize: 'var(--font-size-sm)',
          color: 'var(--color-text-secondary)',
          fontWeight: 500,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}
      >
        {title}
      </span>
      <div
        style={{
          flex: 1,
          height: 1,
          backgroundColor: 'var(--color-border)',
        }}
      />
    </div>
  );
}
```

- [ ] **Step 2: Write the story**

```typescript
// frontend/src/components/SceneBreak/SceneBreak.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { SceneBreak } from './index';

const meta: Meta<typeof SceneBreak> = {
  title: 'Molecules/SceneBreak',
  component: SceneBreak,
};

export default meta;
type Story = StoryObj<typeof SceneBreak>;

export const Default: Story = {
  args: { title: 'Szene 1' },
};

export const LongTitle: Story = {
  args: { title: 'Die Verhandlung im Bundesministerium' },
};
```

- [ ] **Step 3: Verify in Storybook at `Molecules/SceneBreak`**

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/SceneBreak/
git commit -m "feat: add SceneBreak component"
```

---

### Task 6: BottomBar

**Files:**
- Create: `frontend/src/components/BottomBar/index.tsx`
- Create: `frontend/src/components/BottomBar/BottomBar.stories.tsx`

- [ ] **Step 1: Create the component**

```bash
mkdir -p frontend/src/components/BottomBar
```

```typescript
// frontend/src/components/BottomBar/index.tsx
import React from 'react';
import { AutosaveIndicator } from '../AutosaveIndicator';
import { WordCountLabel } from '../WordCountLabel';

interface BottomBarProps {
  /** Full text of all fragments concatenated, for word count calculation. */
  fullText: string;
  /** Whether an autosave operation is in flight. */
  saving: boolean;
}

/**
 * Fixed bottom bar for the Manuscript View.
 * Displays total word count (left) and autosave indicator (right).
 * Uses position: fixed — stays visible during scroll.
 * Main content needs paddingBottom >= var(--bottom-bar-height) to avoid overlap.
 */
export function BottomBar({ fullText, saving }: BottomBarProps): React.ReactElement {
  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: 'var(--bottom-bar-height)',
        backgroundColor: 'var(--color-surface)',
        borderTop: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 var(--space-4)',
        zIndex: 100,
      }}
    >
      <WordCountLabel text={fullText} />
      <AutosaveIndicator saving={saving} />
    </div>
  );
}
```

- [ ] **Step 2: Write the story**

```typescript
// frontend/src/components/BottomBar/BottomBar.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { BottomBar } from './index';

const meta: Meta<typeof BottomBar> = {
  title: 'Molecules/BottomBar',
  component: BottomBar,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<typeof BottomBar>;

export const Idle: Story = {
  args: {
    fullText: 'Im Jahr 2026 begann eine neue Ära der epistemischen Transparenz.',
    saving: false,
  },
};

export const Saving: Story = {
  args: {
    fullText: 'Im Jahr 2026 begann eine neue Ära der epistemischen Transparenz.',
    saving: true,
  },
};
```

- [ ] **Step 3: Verify in Storybook at `Molecules/BottomBar`**

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/BottomBar/
git commit -m "feat: add BottomBar component"
```

---

## Phase 2 — Manuscript View Page

**Prerequisite:** Backend plan `2026-06-08-narrative-unit-domain.md` must be merged to `main` before starting Task 7.

---

### Task 7: API Types + Functions

**Files:**
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: Read the current api.ts to understand the existing structure**

```bash
head -60 frontend/src/lib/api.ts
```

- [ ] **Step 2: Add NarrativeUnit types and API functions**

Add the following block to `frontend/src/lib/api.ts`, after the existing type definitions and before or after the existing functions (match the file's grouping style):

```typescript
// ─── Narrative Units ─────────────────────────────────────────────────────────

export interface NarrativeUnitResponse {
  id: string;
  typ: 'work' | 'part' | 'chapter' | 'scene' | 'fragment';
  title: string | null;
  content: string | null;
  position: number;
  narrative_id: string;
  parent_id: string | null;
  children: NarrativeUnitResponse[];
}

export interface NarrativeTreeResponse {
  narrative_id: string;
  root: NarrativeUnitResponse | null;
}

export interface CreateNarrativeUnitRequest {
  typ: string;
  title?: string | null;
  content?: string | null;
  position: number;
  parent_id?: string | null;
  narrative_id: string;
}

export interface UpdateNarrativeUnitRequest {
  title?: string | null;
  content?: string | null;
}

export async function getNarrativeTree(narrativeId: string): Promise<NarrativeTreeResponse> {
  const response = await fetch(`/narrative-units/tree/${narrativeId}`);
  if (!response.ok) {
    throw new Error(`Failed to load tree: ${response.statusText}`);
  }
  return response.json() as Promise<NarrativeTreeResponse>;
}

export async function createNarrativeUnit(
  body: CreateNarrativeUnitRequest
): Promise<NarrativeUnitResponse> {
  const response = await fetch('/narrative-units', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`Failed to create unit: ${response.statusText}`);
  }
  return response.json() as Promise<NarrativeUnitResponse>;
}

export async function updateNarrativeUnit(
  unitId: string,
  body: UpdateNarrativeUnitRequest
): Promise<NarrativeUnitResponse> {
  const response = await fetch(`/narrative-units/${unitId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`Failed to update unit: ${response.statusText}`);
  }
  return response.json() as Promise<NarrativeUnitResponse>;
}

export async function deleteNarrativeUnit(unitId: string): Promise<void> {
  const response = await fetch(`/narrative-units/${unitId}`, { method: 'DELETE' });
  if (!response.ok && response.status !== 204) {
    throw new Error(`Failed to delete unit: ${response.statusText}`);
  }
}
```

- [ ] **Step 3: Verify TypeScript compiles cleanly**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add NarrativeUnit API types and functions"
```

---

### Task 8: ManuscriptView Page

**Files:**
- Create: `frontend/src/pages/ManuscriptView/index.tsx`

- [ ] **Step 1: Create the page folder**

```bash
mkdir -p frontend/src/pages/ManuscriptView
```

- [ ] **Step 2: Write the page**

```typescript
// frontend/src/pages/ManuscriptView/index.tsx
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  createNarrativeUnit,
  getNarrativeTree,
  NarrativeUnitResponse,
  updateNarrativeUnit,
} from '../../lib/api';
import { BottomBar } from '../../components/BottomBar';
import { Breadcrumb } from '../../components/Breadcrumb';
import { SceneBreak } from '../../components/SceneBreak';
import { countWords } from '../../utils/wordCount';

const AUTOSAVE_DELAY_MS = 1500;

/**
 * ManuscriptView — the continuous prose editor for a Narrative.
 *
 * Architecture:
 * - One <textarea> per Fragment (the atomic editing unit).
 * - Optimistic UI: local content state updated immediately on keystroke.
 * - Autosave: debounced PATCH call 1.5s after the last keystroke per fragment.
 * - The tree is loaded once on mount; fragment saves do not trigger a full reload.
 */
export default function ManuscriptView(): React.ReactElement {
  const { id: narrativeId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [tree, setTree] = useState<NarrativeUnitResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Local content overrides: fragment id → current text (optimistic)
  const [contentMap, setContentMap] = useState<Record<string, string>>({});

  // One debounce timer per fragment
  const timers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  // Load tree on mount
  useEffect(() => {
    if (!narrativeId) return;
    setLoading(true);
    getNarrativeTree(narrativeId)
      .then(response => {
        setTree(response.root);
        if (response.root) {
          const initial: Record<string, string> = {};
          collectFragments(response.root).forEach(f => {
            initial[f.id] = f.content ?? '';
          });
          setContentMap(initial);
        }
      })
      .catch(err => setError(String(err)))
      .finally(() => setLoading(false));
  }, [narrativeId]);

  // Debounced autosave per fragment
  const handleFragmentChange = useCallback((fragmentId: string, newContent: string) => {
    setContentMap(prev => ({ ...prev, [fragmentId]: newContent }));
    if (timers.current[fragmentId]) {
      clearTimeout(timers.current[fragmentId]);
    }
    timers.current[fragmentId] = setTimeout(async () => {
      setSaving(true);
      try {
        await updateNarrativeUnit(fragmentId, { content: newContent });
      } catch (err) {
        console.error('Autosave failed:', err);
      } finally {
        setSaving(false);
      }
    }, AUTOSAVE_DELAY_MS);
  }, []);

  // Add a new Scene under the Work root
  const handleAddScene = async () => {
    if (!narrativeId || !tree) return;
    const position = tree.children.filter(c => c.typ === 'scene').length + 1;
    const created = await createNarrativeUnit({
      typ: 'scene',
      title: `Szene ${position}`,
      position,
      parent_id: tree.id,
      narrative_id: narrativeId,
    });
    setTree(prev => prev ? { ...prev, children: [...prev.children, created] } : prev);
  };

  // Add a new Fragment to a Scene
  const handleAddFragment = async (
    sceneId: string,
    sceneChildren: NarrativeUnitResponse[]
  ) => {
    if (!narrativeId) return;
    const position = sceneChildren.filter(c => c.typ === 'fragment').length + 1;
    const created = await createNarrativeUnit({
      typ: 'fragment',
      content: '',
      position,
      parent_id: sceneId,
      narrative_id: narrativeId,
    });
    setContentMap(prev => ({ ...prev, [created.id]: '' }));
    setTree(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        children: prev.children.map(scene =>
          scene.id === sceneId
            ? { ...scene, children: [...scene.children, created] }
            : scene
        ),
      };
    });
  };

  const totalWordCountText = Object.values(contentMap).join(' ');

  if (loading) {
    return (
      <div style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
        <span style={{ color: 'var(--color-text-secondary)' }}>Lädt…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 'var(--space-8)' }}>
        <p style={{ color: 'var(--color-error)' }}>Fehler: {error}</p>
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: 'var(--color-background)',
      }}
    >
      {/* Sticky top bar with breadcrumb */}
      <div
        style={{
          position: 'sticky',
          top: 0,
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border)',
          padding: 'var(--space-2) var(--space-4)',
          zIndex: 10,
        }}
      >
        <Breadcrumb
          items={[
            { label: 'Meine Werke', onClick: () => navigate('/') },
            { label: tree?.title ?? 'Manuskript' },
          ]}
        />
      </div>

      {/* Manuscript content area */}
      <main
        style={{
          flex: 1,
          maxWidth: 720,
          width: '100%',
          margin: '0 auto',
          padding: 'var(--space-8) var(--space-4)',
          paddingBottom: 'calc(var(--bottom-bar-height) + var(--space-8))',
        }}
      >
        {!tree ? (
          <EmptyManuscript narrativeId={narrativeId!} onWorkCreated={setTree} />
        ) : (
          <>
            {tree.children
              .filter(child => child.typ === 'scene')
              .map(scene => (
                <section key={scene.id}>
                  <SceneBreak title={scene.title ?? 'Szene'} />
                  {scene.children
                    .filter(child => child.typ === 'fragment')
                    .map(fragment => (
                      <textarea
                        key={fragment.id}
                        value={contentMap[fragment.id] ?? fragment.content ?? ''}
                        onChange={e => handleFragmentChange(fragment.id, e.target.value)}
                        placeholder="Schreib hier…"
                        style={{
                          width: '100%',
                          minHeight: 120,
                          resize: 'vertical',
                          border: 'none',
                          outline: 'none',
                          backgroundColor: 'transparent',
                          fontFamily: 'var(--font-family-prose)',
                          fontSize: 'var(--font-size-prose)',
                          lineHeight: 1.8,
                          color: 'var(--color-text-primary)',
                          padding: 'var(--space-2) 0',
                        }}
                      />
                    ))}
                  <button
                    onClick={() => handleAddFragment(scene.id, scene.children)}
                    style={{
                      display: 'block',
                      marginTop: 'var(--space-2)',
                      background: 'none',
                      border: '1px dashed var(--color-border)',
                      borderRadius: 'var(--radius-sm)',
                      padding: 'var(--space-1) var(--space-3)',
                      cursor: 'pointer',
                      color: 'var(--color-text-secondary)',
                      fontSize: 'var(--font-size-sm)',
                    }}
                  >
                    + Absatz hinzufügen
                  </button>
                </section>
              ))}
            <div style={{ marginTop: 'var(--space-8)' }}>
              <button
                onClick={handleAddScene}
                style={{
                  background: 'none',
                  border: '1px dashed var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: 'var(--space-2) var(--space-4)',
                  cursor: 'pointer',
                  color: 'var(--color-text-secondary)',
                  fontSize: 'var(--font-size-sm)',
                }}
              >
                + Szene hinzufügen
              </button>
            </div>
          </>
        )}
      </main>

      <BottomBar fullText={totalWordCountText} saving={saving} />
    </div>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Recursively collects all Fragment nodes from a unit subtree. */
function collectFragments(unit: NarrativeUnitResponse): NarrativeUnitResponse[] {
  const fragments: NarrativeUnitResponse[] = [];
  if (unit.typ === 'fragment') fragments.push(unit);
  for (const child of unit.children) {
    fragments.push(...collectFragments(child));
  }
  return fragments;
}

// ─── Empty state ──────────────────────────────────────────────────────────────

function EmptyManuscript({
  narrativeId,
  onWorkCreated,
}: {
  narrativeId: string;
  onWorkCreated: (tree: NarrativeUnitResponse) => void;
}): React.ReactElement {
  const handleCreate = async () => {
    const work = await createNarrativeUnit({
      typ: 'work',
      title: 'Mein Werk',
      position: 1,
      narrative_id: narrativeId,
    });
    onWorkCreated(work);
  };

  return (
    <div
      style={{
        textAlign: 'center',
        padding: 'var(--space-16) var(--space-4)',
      }}
    >
      <p
        style={{
          color: 'var(--color-text-secondary)',
          marginBottom: 'var(--space-4)',
        }}
      >
        Noch kein Inhalt. Beginne mit dem ersten Werk.
      </p>
      <button
        onClick={handleCreate}
        style={{
          padding: 'var(--space-2) var(--space-6)',
          backgroundColor: 'var(--color-accent)',
          color: 'var(--color-on-accent)',
          border: 'none',
          borderRadius: 'var(--radius-md)',
          cursor: 'pointer',
          fontSize: 'var(--font-size-base)',
        }}
      >
        Erstes Werk anlegen
      </button>
    </div>
  );
}
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/ManuscriptView/
git commit -m "feat: add ManuscriptView page with Fragment textareas and debounce autosave"
```

---

### Task 9: Smoke Tests

**Files:**
- Create: `frontend/src/pages/ManuscriptView/ManuscriptView.test.tsx`

- [ ] **Step 1: Check which test runner is used**

```bash
grep -E "vitest|jest" frontend/package.json | head -5
```

- [ ] **Step 2: Write smoke tests**

If Vitest (most likely for Vite projects), use `vi.mock`/`vi.fn()`:

```typescript
// frontend/src/pages/ManuscriptView/ManuscriptView.test.tsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';
import ManuscriptView from './index';

vi.mock('../../lib/api', () => ({
  getNarrativeTree: vi.fn().mockResolvedValue({
    narrative_id: 'nar-001',
    root: null,
  }),
  createNarrativeUnit: vi.fn(),
  updateNarrativeUnit: vi.fn(),
  deleteNarrativeUnit: vi.fn(),
}));

function renderManuscript() {
  return render(
    <MemoryRouter initialEntries={['/narrative/nar-001/manuscript']}>
      <Routes>
        <Route path="/narrative/:id/manuscript" element={<ManuscriptView />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('ManuscriptView', () => {
  it('renders without crashing', () => {
    renderManuscript();
    expect(screen.getByText('Lädt…')).toBeInTheDocument();
  });

  it('shows empty state after load when tree is null', async () => {
    renderManuscript();
    const emptyText = await screen.findByText(/Noch kein Inhalt/);
    expect(emptyText).toBeInTheDocument();
  });
});
```

If Jest: replace `vi.mock` → `jest.mock`, `vi.fn()` → `jest.fn()`.

- [ ] **Step 3: Run tests**

```bash
cd frontend && npm test
```

Expected: both tests GREEN.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/ManuscriptView/ManuscriptView.test.tsx
git commit -m "test: add ManuscriptView smoke tests"
```

---

### Task 10: Route Wiring

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Read the current routes**

```bash
grep -n "Route\|import" frontend/src/App.tsx | head -20
```

- [ ] **Step 2: Add the import**

Following the existing lazy-import or direct-import pattern:

```typescript
import ManuscriptView from './pages/ManuscriptView';
```

- [ ] **Step 3: Add the route**

In the Routes section, add after the existing narrative routes:

```typescript
<Route path="/narrative/:id/manuscript" element={<ManuscriptView />} />
```

- [ ] **Step 4: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 5: Manual smoke test**

```bash
klartext dev &
cd frontend && npm run dev &
```

Navigate to `http://localhost:5173/narrative/<some-narrative-id>/manuscript`. Verify:
- [ ] Page loads without white screen
- [ ] Breadcrumb shows "Meine Werke › Manuskript"
- [ ] Empty state: "Noch kein Inhalt" + "Erstes Werk anlegen" button visible

- [ ] **Step 6: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: add /narrative/:id/manuscript route"
```

---

## QA Gate

**Phase 1 branch** (`task/H01-B1/manuscript-components`):
```bash
cd frontend && npm run build-storybook 2>&1 | tail -5
npx tsc --noEmit
```
Expected: build succeeds, no TypeScript errors.

**Phase 2 branch** (`task/H01-B2/manuscript-view-page`):
```bash
cd frontend && npx tsc --noEmit
npm test
```
Manual: Navigate to `/narrative/:id/manuscript` and verify:
- Typing in textarea → word count in BottomBar updates live
- 1.5s after typing stops → AutosaveIndicator shows "Speichert…" then "Gespeichert ✓"
- "+ Szene hinzufügen" creates a new SceneBreak
- "+ Absatz hinzufügen" creates a new textarea in the scene

---

## PR Checklist

**Phase 1 PR:** `feat: Manuscript View components + design tokens`
- [ ] All 5 components render in Storybook without error
- [ ] No hex values in style props (all CSS vars)
- [ ] No TypeScript errors
- [ ] Storybook builds cleanly

**Phase 2 PR:** `feat: ManuscriptView page with autosave`
- [ ] Route wired in App.tsx
- [ ] Empty state works (no tree → "Erstes Werk anlegen")
- [ ] Fragment textareas render with content
- [ ] Autosave debounce works (tested manually)
- [ ] BottomBar shows correct word count
- [ ] No TypeScript errors
- [ ] Smoke tests pass
