# Impeccable AI Slop Detection & Craft Floor Rule

## Mandatory Instruction
Every time a code edit touches frontend views, styles, typography, layouts, or copy:
1. Run the Impeccable detector against all running application routes:
   ```powershell
   & "f:\SIH64\.agents\skills\impeccable\scripts\impeccable.cmd" detect http://localhost:5173 http://localhost:5173/complaints http://localhost:5173/overlaps http://localhost:5173/institutions http://localhost:5173/reports http://localhost:5173/admin http://localhost:5173/login
   ```
2. The audit MUST exit with code 0 (0 anti-patterns and 0 warnings) before presenting results to the user.

## Core Anti-Slop & Craft Constraints
- **Contrast**: Muted text on `#252526` dark panels must have WCAG AA contrast (≥ 4.5:1). Use `#989898` (5.34:1) or `#aaaaaa` for input placeholders. Red alert pills must use `#c72e2e` (4.67:1), not `#f14c4c` (3.6:1).
- **Layout & Structure**: No nested cards inside cards (`[nested-cards]`). Use subtle line dividers (`divide-y divide-[#2d2d2d]`) or section headers instead of bordered child containers.
- **Typography & Stragglers**: Use `[text-wrap:pretty]` on prose/empty states and `[text-wrap:balance]` on headlines/titles.
- **Sizing**: Minimum text size is `text-xs` (`12px`). Never use `text-[10px]`.
- **Spacing**: Avoid non-standard padding like `p-4.5`. Standardize on `p-4` or `p-5`.
- **Copywriting**: Run copy through `humanizer` standards — eliminate AI buzzwords, cheerleading, staged triads, and robotic filler.
