#!/usr/bin/env python3
"""Audit codebase text and UI copy against Humanizer guidelines (SKILL.md).

Scans frontend components, views, templates, and documentation for:
- Overused AI vocabulary (§12)
- Inflated claims & sales language (§13, §16)
- Staged run-ups (§4)
- Chatbot residue (§22)
- False contrasts (§1)
- Em dashes in narrative prose (§8)

Exits with code 0 if all clean, or code 1 if violations are detected.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories and files to check
CHECK_TARGETS = [
    ROOT / "frontend" / "src",
    ROOT / "AGENTS.md",
    ROOT / "README.md",
]

# File extensions to inspect
ALLOWED_EXTENSIONS = {".vue", ".ts", ".js", ".html", ".md"}

# Files or subpaths to skip
IGNORE_SUBSTRINGS = [
    "node_modules",
    ".git",
    "dist",
    ".venv",
    "pgsql",
    "skills/humanizer/SKILL.md",  # The skill definition itself contains reference examples
    "skills/humanizer/README.md",
    "skills/humanizer/CHANGELOG.md",
]

# Rules definitions: (Rule Code, Rule Title, Pattern)
RULES = [
    (
        "§12",
        "Overused AI words",
        re.compile(
            r"\b(seamless|seamlessly|delve|delving|delved|testament|tapestry|pivotal|"
            r"streamline|streamlined|streamlining|beacon|groundbreaking|"
            r"foster|fostering|fosters|empower|empowering|empowers|empowerment|"
            r"unlock|unlocking|unlocks|harness|harnessing|interplay|"
            r"intricate|intricacies|meticulous|meticulously|showcase|showcasing|showcases|"
            r"underscore|underscores|underscoring|vibrant|deep dive|bolster|bolstered|bolstering|"
            r"crucial|enduring|elevate|elevating|transformative|cutting-edge|game-changer|"
            r"revolutionary|unleash|unleashing|paramount)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "§4",
        "Staged run-up before the point",
        re.compile(
            r"\b(let's dive in|let's explore|let's break this down|here's what you need to know|"
            r"without further ado|quick note|heads up|real talk|here's the thing|let's be honest)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "§22",
        "Chatbot residue",
        re.compile(
            r"\b(I hope this helps|Certainly!|Of course!|Great question!|You're absolutely right|"
            r"Would you like me to|Let me know if you|As an AI language model)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "§1",
        "Not X but Y formula",
        re.compile(
            r"\b(not just\b.*?\bbut\b|not only\b.*?\bbut\b|not merely\b.*?\bbut\b)",
            re.IGNORECASE,
        ),
    ),
    (
        "§13/§16",
        "Inflated claims & sales language",
        re.compile(
            r"\b(stands as a testament|hallmark capability|breathtaking|diverse array|"
            r"rich cultural|in the heart of|step in the right direction|exciting times ahead|"
            r"future looks bright)\b",
            re.IGNORECASE,
        ),
    ),
]


def should_check_file(path: Path) -> bool:
    path_str = str(path).replace("\\", "/")
    for ignore in IGNORE_SUBSTRINGS:
        if ignore in path_str:
            return False
    return path.suffix in ALLOWED_EXTENSIONS


def is_rule_discussion_line(line: str) -> bool:
    """Per SKILL.md §When not to act:
    'Leave a watched phrase alone inside a quotation, a title, a proper name,
    or a passage that discusses the phrase rather than uses it.'
    """
    lower = line.lower()
    return any(
        marker in lower
        for marker in (
            "banned ai vocabulary",
            "do not use stock words",
            "avoid *not just",
            "avoid *let's",
            "do not use narrative",
            "remove assistant pleasantries",
            "watch for:",
        )
    )


def audit_file(path: Path) -> list[tuple[int, str, str, str]]:
    violations = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"Warning: could not read {path}: {exc}", file=sys.stderr)
        return []

    lines = content.splitlines()
    in_code_block = False

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Handle fenced markdown code blocks ```
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Ignore comments
        if stripped.startswith("//") or stripped.startswith("*"):
            continue

        # Ignore lines discussing banned terms (meta-instructions/rules)
        if is_rule_discussion_line(stripped):
            continue

        # Per SKILL.md: ignore inline code (backticks)
        cleaned_line = re.sub(r"`[^`]*`", "", line)

        for rule_id, rule_name, regex in RULES:
            matches = list(regex.finditer(cleaned_line))
            for m in matches:
                matched_text = m.group(0)
                violations.append((idx, rule_id, rule_name, matched_text))

        # Check for narrative em dashes in text/prose (excluding code fallback return '—')
        if "—" in cleaned_line:
            # If it's a code fallback like `return '—'` or `|| '—'` or `: '—'`, it's a data null marker
            if not re.search(r"['\"]—['\"]", line):
                if not stripped.startswith("<!--"):
                    violations.append((idx, "§8", "Narrative em-dash connector", "—"))

    return violations


def main() -> int:
    total_files = 0
    total_violations = 0

    print("==================================================")
    print("Humanizer Quality Audit (AICTE SIH 2026 Portal)")
    print("Enforcing .agents/skills/humanizer guidelines")
    print("==================================================")

    results: dict[Path, list[tuple[int, str, str, str]]] = {}

    for target in CHECK_TARGETS:
        if target.is_file():
            if should_check_file(target):
                total_files += 1
                v = audit_file(target)
                if v:
                    results[target] = v
                    total_violations += len(v)
        elif target.is_dir():
            for root, _, files in os.walk(target):
                for file in files:
                    file_path = Path(root) / file
                    if should_check_file(file_path):
                        total_files += 1
                        v = audit_file(file_path)
                        if v:
                            results[target / file_path.relative_to(target)] = v
                            total_violations += len(v)

    if not results:
        print(f"\nAudit PASSED: {total_files} files checked. 0 humanizer violations found.")
        return 0

    print(f"\nFound {total_violations} violation(s) across {len(results)} file(s):\n")
    for file_path, file_violations in results.items():
        rel_path = file_path.resolve()
        try:
            rel_display = file_path.relative_to(ROOT)
        except ValueError:
            rel_display = file_path
        print(f"File: {rel_display}")
        for line_no, rule_id, rule_name, match_text in file_violations:
            print(f"  Line {line_no:4d} | {rule_id} {rule_name}: flagged '{match_text}'")
        print()

    print(f"FAILED: {total_violations} humanizer violation(s) require rewriting.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
