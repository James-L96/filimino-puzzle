"""Backtracking solver for Fillomino puzzles.

A puzzle is a flat list of length rows * cols where each entry is either an
integer (given or placed value) or None (empty cell). In any valid solution,
every cell's value equals the size of its orthogonally connected group of
equal values, which also guarantees that no two regions of equal size touch.
"""

import random
import sys

MAX_VALUE = 9


def neighbors(index, rows, cols):
    r, c = divmod(index, cols)
    if r > 0:
        yield index - cols
    if r + 1 < rows:
        yield index + cols
    if c > 0:
        yield index - 1
    if c + 1 < cols:
        yield index + 1


_NBR_CACHE = {}


def neighbor_lists(rows, cols):
    """Cached list of orthogonal neighbour indices for each cell."""
    key = (rows, cols)
    cached = _NBR_CACHE.get(key)
    if cached is None:
        n = rows * cols
        cached = []
        for i in range(n):
            r, c = divmod(i, cols)
            lst = []
            if r > 0:
                lst.append(i - cols)
            if r + 1 < rows:
                lst.append(i + cols)
            if c > 0:
                lst.append(i - 1)
            if c + 1 < cols:
                lst.append(i + 1)
            cached.append(lst)
        _NBR_CACHE[key] = cached
    return cached


def _analyze(values, rows, cols):
    """Compute equal-value components and check partial-grid consistency.

    Returns (comp_id, comp_size, comp_value, consistent, forced). comp_id[i] is
    the component index of filled cell i (-1 for empty cells). forced is a list
    of (cell_index, value) pairs that hold in every completion of this state.

    A state is inconsistent when a component exceeds its target size, or when a
    component still needing to grow has no legal frontier cell, or when the
    connected empty pocket it can grow into holds fewer cells than it needs.
    When the pocket holds exactly as many cells as needed, all of them are
    forced to take that component's value.
    """
    n = rows * cols
    nbrs = neighbor_lists(rows, cols)
    comp_id = [-1] * n
    comp_size = []
    comp_value = []
    comp_cells = []

    for i in range(n):
        v = values[i]
        if v is None or comp_id[i] != -1:
            continue
        cid = len(comp_size)
        size = 0
        cells = []
        stack = [i]
        comp_id[i] = cid
        while stack:
            j = stack.pop()
            size += 1
            cells.append(j)
            for k in nbrs[j]:
                if values[k] == v and comp_id[k] == -1:
                    comp_id[k] = cid
                    stack.append(k)
        comp_size.append(size)
        comp_value.append(v)
        comp_cells.append(cells)

    consistent = True
    forced_map = {}

    def force(cell, value):
        nonlocal consistent
        prev = forced_map.get(cell)
        if prev is not None and prev != value:
            consistent = False
        else:
            forced_map[cell] = value

    for cid, size in enumerate(comp_size):
        target = comp_value[cid]
        if size > target:
            consistent = False
            break
        if size == target:
            continue
        need = target - size

        frontier = set()
        for i in comp_cells[cid]:
            for k in nbrs[i]:
                if values[k] is None:
                    frontier.add(k)
        if not frontier:
            # smaller than its target with no empty neighbour at all: dead
            consistent = False
            break

        # At least one frontier cell must legally accept the value. Illegality
        # is permanent (components only ever grow), so this prunes early.
        can_extend = False
        for k in frontier:
            total = 1 + size
            seen = set()
            for m in nbrs[k]:
                if values[m] == target and comp_id[m] != cid and comp_id[m] not in seen:
                    seen.add(comp_id[m])
                    total += comp_size[comp_id[m]]
            if total <= target:
                can_extend = True
                break
        if not can_extend:
            consistent = False
            break

        # Pocket rules (only sound when no same-value component can merge):
        # the pocket holds every empty cell this component could ever grow
        # into. If it is smaller than needed the state is dead; if it is
        # exactly as big, all of its cells are forced to take this value.
        # The pocket contains the frontier, so when the frontier alone already
        # exceeds what is needed neither rule can fire and the BFS is skipped.
        if len(frontier) > need:
            continue

        pocket = set()
        stack = list(frontier)
        while stack:
            j = stack.pop()
            if j in pocket:
                continue
            pocket.add(j)
            for k in nbrs[j]:
                if values[k] is None and k not in pocket:
                    stack.append(k)

        mergeable = False
        for p in pocket:
            for m in nbrs[p]:
                if values[m] == target and comp_id[m] != cid:
                    mergeable = True
                    break
            if mergeable:
                break

        if not mergeable:
            if len(pocket) < need:
                consistent = False
                break
            if len(pocket) == need:
                for cell in pocket:
                    force(cell, target)
                if not consistent:
                    break

    return comp_id, comp_size, comp_value, consistent, list(forced_map.items())


def is_valid_complete(values, rows, cols):
    """True if values is a fully filled grid satisfying all Fillomino rules."""
    n = rows * cols
    if len(values) != n:
        return False
    for v in values:
        if not isinstance(v, int) or not (1 <= v <= n):
            return False
    _, _, _, consistent, _ = _analyze(values, rows, cols)
    # With no empty cells, consistency forces every component size to equal its value.
    return consistent


def solve(values, rows, cols, max_value=MAX_VALUE, rng=None):
    """Return one solution as a flat list, or None if the puzzle is unsolvable."""
    _ensure_recursion_limit(rows * cols)
    solutions = []
    _search(list(values), rows, cols, max_value, rng or random.Random(), 1, solutions)
    return solutions[0] if solutions else None


def count_solutions(values, rows, cols, max_value=MAX_VALUE, rng=None, limit=2, node_budget=None):
    """Count solutions up to limit (default 2: enough for uniqueness checks).

    With a node_budget, the search aborts early and reports limit (i.e. "not
    proven unique") once too many nodes have been visited. Callers that only
    need a uniqueness guarantee can safely treat an aborted count as non-unique.
    """
    _ensure_recursion_limit(rows * cols)
    budget = [node_budget] if node_budget is not None else None
    result = _search(list(values), rows, cols, max_value, rng or random.Random(), limit, None, budget)
    return limit if result == ABORTED else result


def _ensure_recursion_limit(n):
    needed = n + 100
    if sys.getrecursionlimit() < needed:
        sys.setrecursionlimit(needed)


ABORTED = -1


def _search(values, rows, cols, max_value, rng, limit, solutions, budget=None):
    """Depth-first search. Returns the number of solutions found (capped at limit),
    or ABORTED when the node budget runs out.

    When solutions is not None, each complete solution grid is appended to it.
    Cells filled by propagation are restored before returning so sibling
    branches never see them.
    """
    if budget is not None:
        budget[0] -= 1
        if budget[0] <= 0:
            return ABORTED

    n = rows * cols
    nbrs = neighbor_lists(rows, cols)
    modified = []

    try:
        # Propagation: repeatedly apply forced placements (single-candidate
        # cells and pocket-forced cells) until fixpoint.
        while True:
            comp_id, comp_size, _, consistent, forced = _analyze(values, rows, cols)
            if not consistent:
                return 0

            if forced:
                for cell, value in forced:
                    values[cell] = value
                    modified.append(cell)
                continue

            # Only empty cells touching a filled cell have active constraints; defer the rest.
            frontier = [i for i in range(n) if values[i] is None and any(values[k] is not None for k in nbrs[i])]
            candidates_for = frontier if frontier else [i for i in range(n) if values[i] is None]

            cand_lists = {}
            singletons = []
            for i in candidates_for:
                cands = []
                for v in range(1, max_value + 1):
                    total = 1
                    seen_comps = set()
                    for k in nbrs[i]:
                        if values[k] == v:
                            cid = comp_id[k]
                            if cid not in seen_comps:
                                seen_comps.add(cid)
                                total += comp_size[cid]
                    if total <= v:
                        cands.append(v)
                if not cands:
                    return 0
                cand_lists[i] = cands
                if len(cands) == 1:
                    singletons.append(i)

            if singletons:
                for i in singletons:
                    values[i] = cand_lists[i][0]
                    modified.append(i)
                continue

            break

        if not candidates_for:
            if solutions is not None:
                solutions.append(list(values))
            return 1

        best_i = min(candidates_for, key=lambda i: len(cand_lists[i]))
        rng.shuffle(cand_lists[best_i])
        found = 0
        for v in cand_lists[best_i]:
            values[best_i] = v
            result = _search(values, rows, cols, max_value, rng, limit - found, solutions, budget)
            if result == ABORTED:
                return ABORTED
            found += result
            if found >= limit:
                break
        values[best_i] = None
        return found
    finally:
        for cell in modified:
            values[cell] = None
