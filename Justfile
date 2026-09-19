# BannerMania command surface.
# One documented way to run each thing, so CI and a contributor invoke the
# same code path. Recipes run through `uv run` to use the uv-managed venv.

# List available recipes.
default:
    @just --list

# Run the test suite (must pass with no network beyond localhost).
test *args:
    uv run pytest {{args}}

# Lint with ruff.
lint:
    uv run ruff check .

# Auto-fix lint issues that ruff can fix safely.
lint-fix:
    uv run ruff check --fix .

# Check formatting without modifying files.
fmt-check:
    uv run ruff format --check .

# Format the codebase.
fmt:
    uv run ruff format .

# Scan for committed secrets against the tracked baseline.
secrets:
    uv run detect-secrets scan --baseline .secrets.baseline

# Run the project's PII check.
pii:
    uv run python scripts/check_pii.py

# Run the Flask web app locally (http://127.0.0.1:5001).
run *args:
    uv run python app.py {{args}}

# --- desktop-app spec ---
# These recipes activate once the desktop-app tasks land the entry point and
# PyInstaller spec. Kept here as the single documented command surface.

# Launch the native desktop app.
desktop:
    uv run python -m bannermania_demo.desktop

# Build a standalone desktop executable with PyInstaller.
package:
    uv run pyinstaller bannermania-desktop.spec
