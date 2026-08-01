# AI Notes

I used Claude (Anthropic) as part of building this assignment. Here's how.

## 1. What was AI-generated vs. written by me

I started from an expense-tracker project I'd already built earlier (a Flask API with JSON-file
storage), which had a similar shape to what this assignment asks for but didn't match its exact
spec. I gave Claude the assignment email and my existing code and asked it to rebuild the API to
match the spec exactly.

- **AI-generated:** the restructured `src/app.py` (routes, request validation, JSON storage
  helpers in `storage.py`), the `tests/test_app.py` suite, `requirements.txt`, and this repo
  layout (`src/`, `tests/`, README).
- **Written/decided by me:** the choice of which endpoints to keep from my original project vs.
  drop, the field names to standardize on (`title`, `amount`, `category`, `date`, matching the
  spec instead of my original `note`/`type`/`currency` fields), and the decision to pick the
  monthly-summary bonus rather than search, Swagger, or Docker.

## 2. What I validated, tested, or changed, and why

- Ran the full `pytest` suite (11 tests) against a clean install to confirm everything the README
  claims actually works — install → run → test, exactly as a reviewer would do it.
- Manually hit each endpoint with a Python test client (add, list, filter by category
  case-insensitively, delete, monthly summary) to sanity-check response shapes and status codes
  before trusting the generated tests.
- Changed the original `datetime.utcnow()` calls to timezone-aware `datetime.now(timezone.utc)`
  after noticing deprecation warnings during test runs.
- Added explicit `400` validation for missing `title`/`amount` on the add-expense endpoint —
  the original project didn't validate input at all, it just defaulted silently.

## 3. AI suggestions I decided not to use

- Claude's first pass kept my original project's extra features (budgets, loans, savings goals,
  transaction splitting, CSV/PDF export, SMS parsing) alongside the new expense endpoints. I
  decided to drop all of that from this submission — none of it was asked for, and keeping it
  would add untested surface area to something that's being reviewed by an automated process.
- I also chose not to add Swagger/OpenAPI docs or Docker support (both were offered as bonus
  options) since the assignment says to pick at most one bonus, and the monthly summary endpoint
  was the most natural one to build well given my existing `/api/reports` logic.
