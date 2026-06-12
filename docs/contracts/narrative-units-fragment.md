# API Contract: POST /narrative-units (typ=fragment)

**Owner:** Narrative Expert (backend is canonical source of truth; consumers adapt)
**Status:** Active — approved 2026-06-10, Variant R1 (Lazy-create)
**Relates to:** H01-422 (422 Walking Skeleton fix)

---

## Contract

```
POST /narrative-units
Content-Type: application/json

{
  "typ": "fragment",
  "content": "<non-empty string>",   ← required, must not be empty or whitespace-only
  "position": <int>,
  "parent_id": "<scene-id>",
  "narrative_id": "<narrative-id>"
}
```

**Success:** `201 Created` — returns the created `NarrativeUnitResponse`

**Error:** `422 Unprocessable Entity` — if `content` is missing, empty, or whitespace-only

```json
{ "error": "content must not be empty" }
```

---

## Rationale (backend invariant)

`Fragment` is the atomic editing unit of a narrative — one prose paragraph. A Fragment without
content is not a Fragment. The domain invariant `Fragment.create()` enforces this:

```python
if not content.strip():
    raise NarrativeUnitValidationError("content must not be empty")
```

This invariant is intentional and stays. It ensures the database never holds empty Fragment rows,
which would produce invisible gaps in the Manuscript View and break position-based rendering.

Variant R1 was chosen over the alternative (relaxing the invariant to allow empty content) because
an empty Fragment has no meaning at the domain level. The frontend handles the UX gap instead.

---

## Consumer guidance (UX/UI — Lazy-create pattern)

The frontend must **not** send `POST /narrative-units` for a Fragment before the user has entered
content. Instead:

1. When the user clicks "+ Absatz hinzufügen", create a **local pending state** in React (e.g.
   `{ id: null, content: "", isPending: true }`).
2. Render a `<textarea>` immediately so the user can start typing.
3. Send `POST /narrative-units` only when the user leaves the field (`onBlur`) **or** after a
   debounce period, and only if `content.trim().length > 0`.
4. On success: replace the pending state with the server-assigned `id`.
5. If the user discards the field without typing: remove the pending state locally, no API call.

This approach keeps the domain invariant intact and gives the user immediate visual feedback
without an API round-trip.

---

## Contract test reference

QA owns the contract test verifying this behaviour. See: `api/tests/` (to be added by QA as
part of H01-422 Step 2).

---

# API Contract: DELETE /narrative-units/{id}

**Owner:** Narrative Expert (backend is canonical source of truth; consumers adapt)
**Status:** Active — approved 2026-06-12, SA Sign-off: Option B (strikt)
**Relates to:** DELETE-404

---

## Contract

```
DELETE /narrative-units/{id}
```

**Success:** `204 No Content` — unit deleted (including descendants via ON DELETE CASCADE)

**Error:** `404 Not Found` — if no unit with the given ID exists

```json
{ "error": "Narrative unit not found: <id>" }
```

---

## Rationale

`DELETE` follows the same strict semantics as `PUT`: a request targeting a non-existent ID
is a client error and must not be silently swallowed. Returning 204 for an unknown ID would
mask bugs such as double-deletes or stale IDs in the frontend.

Consistency with `update()` (RC3): both mutating verbs raise `NarrativeUnitNotFoundError`
when the target does not exist. The router translates this to 404 via the central exception
handler in `main.py`.

---

## Consumer guidance (UX/UI)

A `DELETE` on a unit that no longer exists must be handled explicitly:

- On `404`: show a neutral message (e.g. "Element wurde bereits entfernt") and refresh the
  local tree state — do not leave a ghost entry in the UI.
- Do not retry `DELETE` on `404` — the absence is the correct final state.

---

## Contract test reference

QA owns the contract test verifying this behaviour:
- `DELETE /narrative-units/{id}` with existing ID → 204
- `DELETE /narrative-units/{id}` with unknown ID → 404
