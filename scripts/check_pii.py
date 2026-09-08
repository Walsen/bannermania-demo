#!/usr/bin/env python3
"""PII scanner for the pre-push quality gate.

Scans only the lines *added* by the commits being pushed (not the whole
history) for common personally identifiable information patterns: email
addresses, phone numbers, SSNs, and credit-card-like numbers.

Scoping the scan to added lines means pre-existing, already-reviewed content
(e.g. an author email in pyproject.toml) doesn't re-trigger the gate on every
push — only *new* PII-looking content does.

A line can be explicitly allowlisted with a trailing comment:
    contact_email = "demo@example.com"  # allowlist pii

Usage:
    check_pii.py <git-diff-range>   e.g. check_pii.py abc123..def456

Exit codes:
    0 - no PII-looking content found in the added lines
    1 - potential PII found (see printed report)
    2 - usage / git error
"""

from __future__ import annotations

import re
import subprocess
import sys

ALLOWLIST_MARKER = "allowlist pii"

# Paths excluded from PII scanning: lock files, binaries, generated assets,
# and the secrets baseline itself (which legitimately contains hashes/paths).
EXCLUDED_PATH_PATTERNS = [
    r"^uv\.lock$",
    r"\.lock$",
    r"^\.secrets\.baseline$",
    r"\.venv/",
    r"\.devbox/",
    r"^docs/.*\.(png|gif|jpg|jpeg)$",
    r"\.(png|gif|jpg|jpeg|ico|woff2?|ttf|otf)$",
]

PATTERNS: dict[str, re.Pattern[str]] = {
    "email address": re.compile(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    ),
    "phone number": re.compile(
        r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)"
    ),
    "SSN": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    "credit card number": re.compile(r"(?<!\d)(?:\d[ -]?){13,16}(?!\d)"),
}

# A couple of common false-positive shapes worth exempting outright.
EMAIL_ALLOWLIST_DOMAINS = {"example.com", "example.org", "test.com", "localhost"}


def _is_excluded_path(path: str) -> bool:
    return any(re.search(p, path) for p in EXCLUDED_PATH_PATTERNS)


def _looks_like_placeholder_email(match_text: str) -> bool:
    domain = match_text.rsplit("@", 1)[-1].lower()
    return domain in EMAIL_ALLOWLIST_DOMAINS


def _passes_luhn(digits: str) -> bool:
    digits = re.sub(r"[ -]", "", digits)
    if not digits.isdigit() or not (13 <= len(digits) <= 16):
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _iter_added_lines(diff_range: str) -> list[tuple[str, int, str]]:
    """Yield (file_path, line_number, line_content) for every line added in
    `diff_range`, skipping excluded paths."""
    result = subprocess.run(
        ["git", "diff", "--unified=0", "--diff-filter=ACM", diff_range, "--"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        print(f"error: git diff failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(2)

    findings: list[tuple[str, int, str]] = []
    current_file = None
    current_line_no = None
    skip_file = False

    for raw in result.stdout.splitlines():
        if raw.startswith("+++ "):
            path = raw[6:] if raw.startswith("+++ b/") else raw[4:]
            current_file = path
            skip_file = _is_excluded_path(current_file)
            continue
        if skip_file or current_file is None:
            continue
        if raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            current_line_no = int(m.group(1)) if m else 1
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            findings.append((current_file, current_line_no, raw[1:]))
            current_line_no += 1
    return findings


def scan(diff_range: str) -> list[str]:
    reports = []
    for path, line_no, content in _iter_added_lines(diff_range):
        if ALLOWLIST_MARKER in content:
            continue
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                text = match.group(0)
                if label == "email address" and _looks_like_placeholder_email(text):
                    continue
                if label == "credit card number" and not _passes_luhn(text):
                    continue
                reports.append(f"{path}:{line_no}: possible {label} -> {text!r}")
    return reports


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_pii.py <git-diff-range>", file=sys.stderr)
        return 2

    findings = scan(sys.argv[1])
    if findings:
        print("Potential PII detected in pushed changes:\n")
        for line in findings:
            print(f"  {line}")
        print(
            "\nIf this is a false positive, add `# allowlist pii` at the end "
            "of the line, or remove/redact the value before pushing."
        )
        return 1

    print("check_pii: no PII-looking content in added lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
