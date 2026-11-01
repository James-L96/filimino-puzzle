import pytest

from solver import MAX_VALUE, count_solutions, is_valid_complete, solve

# A valid 4x4 Fillomino solution (regions: a size-5 P-pentomino, a 2x2 of 4s,
# a vertical triomino of 3s, a domino of 2s, and two isolated monominoes).
VALID_4X4 = [5, 4, 4, 3, 5, 4, 4, 3, 5, 5, 2, 3, 1, 5, 2, 1]

# Five givens that make the puzzle above uniquely solvable.
UNIQUE_4X4_GIVENS = {0: 5, 1: 4, 3: 3, 10: 2, 12: 1}


def grid_from_givens(givens, size=4):
    grid = [None] * (size * size)
    for i, v in givens.items():
        grid[i] = v
    return grid


class TestIsValidComplete:
    def test_valid_grid(self):
        assert is_valid_complete(list(VALID_4X4), 4, 4) is True

    def test_incomplete_grid_is_invalid(self):
        grid = list(VALID_4X4)
        grid[0] = None
        assert is_valid_complete(grid, 4, 4) is False

    def test_wrong_region_size_is_invalid(self):
        # Turn the 2x2 block of 4s into a size-3 region labelled 4.
        grid = list(VALID_4X4)
        grid[1] = 5
        assert is_valid_complete(grid, 4, 4) is False

    def test_wrong_length_is_invalid(self):
        assert is_valid_complete(list(VALID_4X4)[:15], 4, 4) is False

    def test_out_of_range_value_is_invalid(self):
        grid = list(VALID_4X4)
        grid[0] = 99
        assert is_valid_complete(grid, 4, 4) is False


class TestSolve:
    def test_solves_unique_puzzle(self):
        result = solve(grid_from_givens(UNIQUE_4X4_GIVENS), 4, 4)
        assert result == VALID_4X4

    def test_full_grid_is_its_own_solution(self):
        result = solve(list(VALID_4X4), 4, 4)
        assert result == VALID_4X4

    def test_unsolvable_puzzle_returns_none(self):
        # Two orthogonally adjacent monominoes can never be valid.
        grid = [1, 1, None, None, None, None, None, None]
        assert solve(grid, 2, 2) is None

    def test_solution_respects_max_value(self):
        result = solve([None] * 16, 4, 4, max_value=MAX_VALUE)
        assert all(1 <= v <= MAX_VALUE for v in result)


class TestCountSolutions:
    def test_unique_puzzle_counts_one(self):
        assert count_solutions(grid_from_givens(UNIQUE_4X4_GIVENS), 4, 4) == 1

    def test_unsolvable_puzzle_counts_zero(self):
        grid = [1, 1, None, None, None, None, None, None]
        assert count_solutions(grid, 2, 2) == 0

    def test_node_budget_never_exceeds_limit(self):
        result = count_solutions(
            grid_from_givens(UNIQUE_4X4_GIVENS), 4, 4, limit=2, node_budget=1
        )
        assert 0 <= result <= 2
