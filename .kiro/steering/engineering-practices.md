---
inclusion: always
---

# Engineering practices

These practices apply to all code written or modified in this project
(currently a Python/Flask + Pillow codebase — examples below use that stack,
but the principles apply regardless of language).

## 1. Clean Code & SOLID

- **Single Responsibility** — each function/class/module does one thing. If a
  function mixes rendering, I/O, and business rules, split it (e.g. keep
  `app.py`'s image-rendering functions separate from Flask route handlers).
- **Open/Closed** — prefer adding new behavior via new functions/strategies
  over editing large conditional chains. When a new effect, pattern, or border
  is added, it should slot into the existing registry (`EFFECTS`, `PATTERNS`,
  `BORDERS`, etc.) without rewriting unrelated branches.
- **Liskov Substitution** — subclasses/implementations must be usable
  wherever their base/interface is expected, without surprising behavior.
- **Interface Segregation** — don't force callers to depend on parameters or
  methods they don't use. Keep function signatures narrow and focused.
- **Dependency Inversion** — depend on abstractions (a font resolver, a
  storage interface) rather than concrete details, especially at boundaries
  like the filesystem, network, or third-party libraries (Flask, Pillow).
- Favor small, well-named functions over long ones. Extract helpers instead of
  nesting deeply. Avoid duplication — if logic is copy-pasted, factor it out.
- Naming should reveal intent (`resolve_font_path`, not `getf`). Comments
  explain *why*, not *what* — the code itself should read clearly enough to
  explain *what*.

## 2. Test-Driven Development (TDD)

- Write a failing test **before** writing the implementation for new
  behavior or bug fixes: red → green → refactor.
- For bug fixes: first write a test that reproduces the bug, confirm it
  fails, then fix the code and confirm it passes.
- Keep tests small and fast; one behavior per test. Use descriptive test
  names that state the expected behavior (`test_hex_to_rgb_rejects_invalid_length`).
- If this project has no test framework configured yet, set one up
  (`pytest` is the standard choice for Python) before adding the first test,
  rather than skipping tests.
- Every new function, route, or class must have tests covering its normal
  case, edge cases, and error cases before being considered done.
- Run the full test suite before presenting any change as complete.

## 3. Design patterns — apply when they fit, not by default

- Reach for a design pattern only when it solves a real structural problem
  (e.g. multiple interchangeable rendering strategies, a family of border
  styles, a factory for font loading) — not as decoration.
- Common fits in this codebase:
  - **Strategy** — text effects, background patterns, and border styles are
    natural strategies; keep each as an independently testable function/class
    selected by name, not a giant if/elif chain.
  - **Factory** — font resolution/loading (`load_font`) is a factory pattern;
    keep creation logic centralized rather than duplicated at call sites.
  - **Template Method** — shared rendering pipeline steps (background → text
    → border) with pluggable steps.
- Document *why* a pattern was chosen in a short comment or docstring when
  it's not immediately obvious.
- Don't over-engineer: a single conditional or a two-line function does not
  need a pattern.

## 4. Robust error handling

- Never let unexpected exceptions leak raw stack traces to users/API
  responses. Catch at the boundary (route handlers, CLI entry points) and
  return meaningful, structured errors.
- Be specific: catch the exact exception types you expect (`OSError`,
  `ValueError`), not bare `except:`. Only catch broader exceptions at a true
  top-level boundary, and re-raise or log there.
- Validate and sanitize external input (query params, uploaded data, file
  paths) before use — fail fast with a clear error message rather than
  letting bad input propagate.
- Every Flask route must handle its failure modes explicitly (e.g. invalid
  color hex, out-of-range width/height, unknown font/effect/pattern/border
  name) and return an appropriate HTTP status code with a clear JSON/error
  body instead of a 500 stack trace.
- Fail loudly in development (clear errors), fail safely in production
  (no leaked internals, no crashed process from a single bad request).

## 5. Robust logging

- Use a structured logger (Python's `logging` module, configured once at
  app startup) — never bare `print()` for anything beyond throwaway local
  debugging.
- Log at the right level: `DEBUG` for developer detail, `INFO` for normal
  operational events (server start, request handled), `WARNING` for
  recoverable issues (fallback font used, clamped size), `ERROR` for handled
  failures, `CRITICAL` for unrecoverable ones.
- Include context in log messages (request path, key params, exception
  info via `logger.exception(...)` in except blocks) without logging
  sensitive data.
- Errors caught and handled per section 4 must still be logged — silent
  failure is not acceptable.
- Configure log format/output (console and/or file) centrally, not ad hoc
  per module.

## Applying these practices

When implementing a feature or fix:
1. Write the failing test(s) first.
2. Implement the smallest clean, SOLID-compliant change to pass them.
3. Introduce a design pattern only if the change reveals a genuine structural
   need for one.
4. Add explicit error handling for the new code's failure modes.
5. Add logging at the appropriate points and levels.
6. Run the test suite and confirm everything passes before considering the
   work done.
