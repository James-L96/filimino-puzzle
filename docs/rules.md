# Fillomino Rules

Fillomino is a logic puzzle first published in the 1980s in Japan (Puzzle Communication Nikoli). Also published as "Allied Occupation" in the World Puzzle Championship.

## Setup

- A rectangular grid with no standard size; some cells start containing numbers ("givens").
- Daily puzzles (Polyo) use a fixed ladder: 8x8 Easy, 12x12 Easy, 16x16 Medium, 20x20 Weekly Special.

## Rules

The goal is to divide the grid into regions (polyominoes) and fill every cell with a number such that:

1. **Region size equals its number.** Every clue n belongs to a region of exactly n cells, and every cell in a region bears that region's size as its number.
2. **Orthogonal connectivity only.** Cells in the same region are linked horizontally and vertically (no diagonal connections).
3. **No two regions of the same size may be orthogonally adjacent** — equivalently, in a fully numbered grid, the same digit cannot appear on both sides of a border between regions.

Notes:

- Two givens with the same number may belong to the same region (e.g., two 3s inside one triomino).
- A region may contain no given at all; its cells' numbers are deduced.
- Rule 3 is derivable from rules 1–2 once every cell is numbered (two touching regions of equal size would merge into one oversized group), but it is stated explicitly in most rule sets and is the practical check to implement: across any border between two filled cells, the digits must differ.

## Solution properties

- Each published puzzle has exactly one solution.
- Each puzzle can be solved logically, without guessing.

## Solving techniques (from Wikipedia)

Useful heuristics for a solver bot:

- **Overloads.** If placing a number in a cell would create an orthogonally connected run of more copies than that number, the placement is illegal. Classic case: two diagonally adjacent 2s — any cell sharing a side with both cannot be a 2.
- **Limited domains.** A number must expand into exactly n - (current region size) more cells; if it has only one legal direction to grow, those cells are forced. Obvious case: a non-1 bordered on three sides must take the fourth cell.
- **Defined cells.** An empty cell fully surrounded by borders must be 1; two adjacent empty cells surrounded together form a domino (two monominoes cannot share a side). More generally, determine which sizes are legal for an unsolved region and see if only one fits.

## Variants

- Hexagonal grids: same rules with polyhexes instead of polyominoes.
- NIKOJI (Nikoli): letters as givens; matching letters correspond to identical regions in size, shape, orientation, and letter position.
- "Filling" (SGT-Puzzles) / Fields (iOS): player enters numbers, the computer draws region borders — the mode this project implements.

## Sources

- Wikipedia: [Fillomino](https://en.wikipedia.org/wiki/Fillomino) — rules, solution methods, variants.
- Puzzle Baron: Fillomino "How to Play" — uniqueness and logical-solvability guarantee; "same integer cannot be adjacent" phrasing of rule 3.
- Polyo (Daily Fillomino): size/difficulty ladder, daily puzzles by date and size (candidate data source for testing).
