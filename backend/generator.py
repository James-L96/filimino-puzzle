"""Fillomino puzzle generator using the solve-then-remove algorithm.

A random complete solution is produced first (by growing random regions), then
cells are removed from the givens one at a time in random order while re-checking
that the puzzle still has exactly one solution. Removal stops when the difficulty
target or the time budget is reached, so every returned puzzle is guaranteed to
be unique and solvable.
"""

import random
import time

from solver import MAX_VALUE, count_solutions, neighbors, solve

DIFFICULTIES = ("easy", "medium", "hard")

MIN_SIZE = 4
MAX_SIZE = 20

# Target fraction of cells kept as givens per difficulty (fewer givens = harder).
GIVEN_FRACTIONS = {"easy": 0.5, "medium": 0.38, "hard": 0.26}

# Wall-clock budget in seconds for the removal phase per difficulty.
TIME_BUDGETS = {"easy": 4.0, "medium": 12.0, "hard": 30.0}


def _node_budget(n):
    """Search-node cap for one uniqueness check on an n-cell grid.

    Per-node cost grows roughly linearly with n, so scale the budget down to
    keep each check near a second of wall time. An aborted count is treated as
    "not unique", which makes the generator keep that given (keeps generation
    time bounded and every accepted puzzle unique).
    """
    return max(300, int(320_000 / n))


def generate_puzzle(size, difficulty="medium", rng=None):
    """Generate a unique Fillomino puzzle.

    Returns a dict with rows, cols, givens (list of [row, col, value]) and the
    hidden solution as a flat list (strip it before sending to clients).
    """
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"Invalid difficulty {difficulty!r}. Must be one of {DIFFICULTIES}")
    if not isinstance(size, int) or not (MIN_SIZE <= size <= MAX_SIZE):
        raise ValueError(f"size must be an integer between {MIN_SIZE} and {MAX_SIZE}")

    rng = rng or random.Random()
    rows = cols = size
    n = rows * cols

    solution = _random_tiling(rows, cols, rng)
    if solution is None:
        raise RuntimeError("Failed to generate a base Fillomino solution")

    # Remove cells one at a time in random order. Removal is monotone: if
    # dropping cell i leaves the puzzle non-unique, it stays non-unique after
    # any further removals (every second solution still satisfies fewer
    # givens). So each cell needs to be checked exactly once; cells that fail
    # are essential and never worth retrying.
    givens = set(range(n))
    target = max(1, int(GIVEN_FRACTIONS[difficulty] * n))
    deadline = time.monotonic() + TIME_BUDGETS[difficulty]

    order = list(range(n))
    rng.shuffle(order)
    for i in order:
        if len(givens) <= target or time.monotonic() >= deadline:
            break
        puzzle = [None] * n
        for j in givens:
            if j != i:
                puzzle[j] = solution[j]
        if count_solutions(puzzle, rows, cols, rng=rng, limit=2, node_budget=_node_budget(n)) == 1:
            givens.discard(i)

    return {
        "rows": rows,
        "cols": cols,
        "givens": sorted([i // cols, i % cols, solution[i]] for i in givens),
        "solution": solution,
    }


def _random_tiling(rows, cols, rng, max_attempts=200):
    """Build a random valid complete grid by growing regions one at a time.

    Each new region gets a size 1..MAX_VALUE (capped by the connected empty
    pocket around its seed). A size is "safe" when no filled cell on the
    pocket rim bears it; safe sizes can never conflict and growth provably
    succeeds, so they are always preferred. Only when every size is risky does
    placement possibly fail, in which case other seeds are tried before the
    whole attempt restarts. Falls back to solve() as a last resort.
    """
    n = rows * cols
    deadline = time.monotonic() + 15.0

    for _ in range(max_attempts):
        if time.monotonic() > deadline:
            break
        values = [None] * n
        filled = 0
        stuck = False

        while filled < n:
            empty = [i for i in range(n) if values[i] is None]
            rng.shuffle(empty)
            placed_any = False
            for seed in empty:
                pocket = _empty_pocket(values, seed, rows, cols)
                max_size = min(MAX_VALUE, len(pocket))
                # Placed regions are labelled with their own size, so any value
                # on the pocket rim is a size that would conflict if touched.
                risky = set()
                for p in pocket:
                    for m in neighbors(p, rows, cols):
                        if values[m] is not None:
                            risky.add(values[m])
                safe_sizes = [s for s in range(1, max_size + 1) if s not in risky]
                rng.shuffle(safe_sizes)
                risky_sizes = [s for s in range(1, max_size + 1) if s in risky]
                rng.shuffle(risky_sizes)

                placed = False
                for size in safe_sizes + risky_sizes:
                    region = _grow_region(values, seed, size, rows, cols, rng)
                    if (
                        region is None
                        or _has_size_conflict(values, region, size, rows, cols)
                        or _creates_dead_cell(values, region, size, rows, cols)
                    ):
                        continue
                    for i in region:
                        values[i] = size
                    filled += len(region)
                    placed_any = True
                    placed = True
                    break
                if placed:
                    break
            if not placed_any:
                stuck = True
                break

        if not stuck and all(v is not None for v in values):
            return values

    return solve([None] * n, rows, cols, rng=rng)


def _empty_pocket(values, seed, rows, cols):
    """Set of empty cells orthogonally connected to seed."""
    seen = {seed}
    stack = [seed]
    while stack:
        j = stack.pop()
        for k in neighbors(j, rows, cols):
            if values[k] is None and k not in seen:
                seen.add(k)
                stack.append(k)
    return seen


def _grow_region(values, seed, size, rows, cols, rng):
    """Grow a random connected region of exactly `size` empty cells from seed.

    Returns the set of cell indices, or None if growth gets stuck (cannot
    happen when size <= the seed's pocket size).
    """
    region = {seed}
    frontier = [k for k in neighbors(seed, rows, cols) if values[k] is None]
    while len(region) < size:
        if not frontier:
            return None
        j = rng.choice(frontier)
        frontier.remove(j)
        if j in region:
            continue
        region.add(j)
        for k in neighbors(j, rows, cols):
            if values[k] is None and k not in region:
                frontier.append(k)
    return region


def _has_size_conflict(values, region, size, rows, cols):
    """True if any filled neighbour of the region belongs to a component of `size`.

    Placed regions are complete and labelled with their own size, so a filled
    neighbour's value is exactly its region's size.
    """
    for i in region:
        for k in neighbors(i, rows, cols):
            if values[k] == size:
                return True
    return False


def _creates_dead_cell(values, region, size, rows, cols):
    """True if placing this region would isolate an empty cell next to a monomino.

    An isolated empty cell can only become a 1, which conflicts with any
    orthogonally adjacent monomino -- so such a placement is always a dead end.
    """
    for i in region:
        for k in neighbors(i, rows, cols):
            if values[k] is not None or k in region:
                continue
            isolated = True
            mono_adjacent = False
            for m in neighbors(k, rows, cols):
                if m in region:
                    if size == 1:
                        mono_adjacent = True
                elif values[m] is None:
                    isolated = False
                elif values[m] == 1:
                    mono_adjacent = True
            if isolated and mono_adjacent:
                return True
    return False
