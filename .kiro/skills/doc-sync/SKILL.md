---
name: doc-sync
description: Keep project documentation (README, docs/ folder, inline docstrings/comments, API references) in sync whenever source files, resources, or config are created or changed. Use when a file is added or edited in a way that affects features, setup, usage, or the API, or when asked to sync/update/refresh documentation.
---

## Purpose

Whenever a project resource is created or meaningfully changed, make sure the
project's documentation reflects reality. Documentation drift (a README that
describes behavior the code no longer has, or omits behavior it now has) is
treated as a bug.

## When to act

Trigger this workflow when:
- A new source file, template, static asset, or config file is created.
- An existing file changes in a way that affects: features, routes/API
  parameters, setup/install steps, CLI flags, project structure, or
  dependencies.
- The user explicitly asks to "update the docs" / "sync documentation".

Do **not** rewrite documentation for purely internal changes with no
user-visible effect (variable renames, formatting, comments-only diffs,
non-behavioral refactors). Skip those.

## Workflow

1. **Read the actual change** before writing anything. Don't infer behavior
   from a filename — open the file (or diff) and confirm what it does.
2. **Identify affected documentation surfaces.** Check, in this order:
   - `README.md` — features list, quick start / install steps, usage
     instructions, API/parameter tables, project layout tree, examples.
   - `docs/` — any reference docs, diagrams, or images that describe the
     changed area.
   - Inline docstrings / module header comments in the changed file itself.
   - Any other doc files the project maintains (CHANGELOG, CONTRIBUTING,
     API spec files) if present.
3. **Map the change to the right section** rather than dumping new content
   anywhere:
   - New dependency (`requirements.txt`, `pyproject.toml`, `package.json`,
     `devbox.json`, etc.) → update install/quick-start steps if the command
     changes, or note the dependency if the README enumerates them.
   - New/changed HTTP route, CLI flag, or public function signature → update
     the relevant API/parameter table or usage section.
   - New file or directory at the project root or a documented subfolder →
     update the "project layout" / directory tree section.
   - New user-facing capability (effect, mode, option, endpoint) → add it to
     the features list/table.
   - New screenshot/gif in `docs/` → reference it from the README if the
     README showcases similar assets, using the same embed style already
     used nearby.
4. **Match existing conventions exactly**: heading structure, table formats,
   emoji usage (or lack of it), tone, and code block languages. Read a
   neighboring section before editing to mirror its style — don't introduce a
   new documentation style for one section.
5. **Edit surgically.** Use targeted edits to the specific section that
   changed. Don't regenerate the whole file unless it doesn't exist yet.
6. **Verify formatting**: tables have matching column counts, code blocks are
   fenced and runnable as shown, links/paths are valid relative to the doc
   file's location.
7. **State what you updated and why** in one or two sentences — which doc
   file/section changed and which source change it reflects. If no doc update
   was needed, say so briefly instead of making a cosmetic edit just to have
   made one.

## Guardrails

- Never document unverified behavior — if you can't confirm what a change
  does, read the code first; don't guess.
- Don't invent new documentation sections/files unless the project has no
  documentation at all for an area that clearly needs it (e.g. a brand-new
  public API with zero existing docs) — then create the minimum needed,
  matching the project's existing doc format (Markdown, same heading style).
- Keep diffs minimal. A one-line behavior change should produce a one-line
  (or one-row) doc update, not a rewritten section.
- If a change conflicts with existing documented behavior, fix the
  documentation to match the code (the code is the source of truth), and flag
  the discrepancy if it looks unintentional.
