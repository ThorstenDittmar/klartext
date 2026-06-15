# QA Review Report Format

Every QA sub-agent run ends with a report in exactly this format.

---

## QA Review Report

### ✅ Complete
List each checked category and what was found to be complete.
Be specific: name the class, method, or test that was checked.

Example:
- Domain tests: `UserDomain` — all 3 public methods have tests
- Infrastructure: `/users/health` endpoint exists and is tested
- Fake contract: `FakeUserRepository` implements full interface

### ⚠️ Gaps found — RED tests written

For each gap: state the test file, the missing test name, and mark [WRITTEN] if
the test was written, or [NEEDS MANUAL ACTION] if it requires human input.

Example:
**test_user_service.py** — missing error cases:
→ `test_get_by_id_raises_for_inactive_user` [WRITTEN]
→ `test_change_email_raises_for_duplicate_email` [WRITTEN]

**test_users_router.py** — missing health endpoint test:
→ `test_users_health_returns_200` [WRITTEN]

### ❌ Requires manual decision

List anything the sub-agent cannot resolve automatically, with a specific reason.

Example:
- Integration test for `find_by_email` missing.
  Reason: query contains PostgREST filter — fake cannot verify this.
  Action needed: write `@pytest.mark.integration` test against real database.

---

## Rules for the sub-agent

1. Write [WRITTEN] tests directly into the appropriate test file — do not just describe them.
2. Written tests must be syntactically valid and fail when run (RED).
3. Never mark a gap as [WRITTEN] without actually writing the code.
4. If a test file does not exist yet, create it with the correct imports first.
5. Always run the written tests to confirm they are RED before reporting.
