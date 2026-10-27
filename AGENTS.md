# AICTE SIH 2026 Portal - Development & Quality Rules

## 1. Quality Standards: Impeccable Anti-Slop Audit
Before finishing any prompt or presenting results, execute the Impeccable detector against all live routes:
```powershell
& ".\.agents\skills\impeccable\scripts\impeccable.cmd" detect http://localhost:5173 http://localhost:5173/complaints http://localhost:5173/overlaps http://localhost:5173/institutions http://localhost:5173/reports http://localhost:5173/admin http://localhost:5173/login http://localhost:5173/user
```
All routes must pass with 0 anti-patterns and 0 warnings.

### Key Visual Rules:
- **Contrast**: WCAG AA ≥ 4.5:1. Dark muted text must use `#989898` (not `#858585`), placeholder text `#aaaaaa` (not `#858585`), alert pill `#c72e2e` (not `#f14c4c`).
- **No Nested Cards**: Do not put bordered cards inside cards. Use clean divider lines (`divide-y divide-[#2d2d2d]`) or section headers.
- **Text Sizing**: No `text-[10px]` or smaller. Minimum UI text is `text-xs`.
- **Text Wrapping**: Use `[text-wrap:pretty]` on prose/descriptions and `[text-wrap:balance]` on headlines.
- **Padding**: Use standard Tailwind spacing (`p-4`, `p-5`, `p-6`). Do not use fractional arbitrary padding like `p-4.5`.

## 2. Authentication Policy
- Login is **mandatory**. Unauthenticated visits to protected routes redirect to `/login`.
- Default credentials: User ID `admin` / Password `admin` (also supports official email `admin@aicte.gov.in`).
- Quick-fill credential buttons on `/login` allow one-click testing.

## 3. Humanized Copywriting (Humanizer Skill)
Before finishing any work modifying copy, documentation, or UI text, run the copy audit:
```powershell
python .\scripts\audit_copy.py
```
Copy must pass with 0 violations.

### Key Copy Rules (from .agents/skills/humanizer/SKILL.md):
- **Tone**: Plain, direct, operational Indian public sector voice. No promotional filler and no inflated claims.
- **Banned AI Vocabulary (§12)**: Do not use stock words such as *seamless, delve, testament, tapestry, pivotal, streamline, beacon, groundbreaking, foster, empower, unlock, harness, interplay, intricate, meticulous, showcase, underscore, vibrant, deep dive, bolster, crucial, transformative*.
- **No False Contrasts (§1)**: Avoid *not just X, but Y* or *not only X, but Y*. State the point directly.
- **No Staged Run-Ups (§4)**: Avoid *let's dive in*, *here's what you need to know*, *without further ado*.
- **Punctuation (§8)**: Do not use narrative em-dashes (—) as sentence connectors. Use colons, commas, periods, or parentheses.
- **No Chat Residue (§22)**: Remove assistant pleasantries (*I hope this helps*, *Certainly!*, *Great question!*).
