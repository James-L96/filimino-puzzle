import random

import pytest

from generator import DIFFICULTIES, generate_puzzle
from solver import count_solutions, is_valid_complete


class TestGeneratePuzzle:
    @pytest.mark.parametrize("difficulty", DIFFICULTIES)
    def test_generates_unique_puzzle(self, difficulty):
        puzzle = generate_puzzle(6, difficulty, rng=random.Random(42))

        assert puzzle["rows"] == 6
        assert puzzle["cols"] == 6
        n = 36
        assert len(puzzle["solution"]) == n
        assert is_valid_complete(puzzle["solution"], 6, 6)

        givens = puzzle["givens"]
        assert 0 < len(givens) <= n
        for row, col, value in givens:
            assert 0 <= row < 6 and 0 <= col < 6
            assert puzzle["solution"][row * 6 + col] == value

        flat = [None] * n
        for row, col, value in givens:
            flat[row * 6 + col] = value
        assert count_solutions(flat, 6, 6) == 1

    def test_same_seed_gives_same_puzzle(self):
        a = generate_puzzle(6, "easy", rng=random.Random(7))
        b = generate_puzzle(6, "easy", rng=random.Random(7))
        assert a["givens"] == b["givens"]
        assert a["solution"] == b["solution"]

    def test_hard_target_is_smaller_than_easy(self):
        from generator import GIVEN_FRACTIONS

        assert GIVEN_FRACTIONS["easy"] > GIVEN_FRACTIONS["medium"] > GIVEN_FRACTIONS["hard"]

    def test_invalid_difficulty_raises(self):
        with pytest.raises(ValueError):
            generate_puzzle(6, "nightmare")

    @pytest.mark.parametrize("size", (3, 21, -1, "8"))
    def test_invalid_size_raises(self, size):
        with pytest.raises(ValueError):
            generate_puzzle(size, "easy")
