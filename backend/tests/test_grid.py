import pytest
from models.cell import Cell
from models.grid import Grid, MoveResult


class TestCell:
    def test_cell_default_values(self):
        cell = Cell()
        assert cell.value is None
        assert cell.is_given is False

    def test_cell_with_value(self):
        cell = Cell(value=5, is_given=True)
        assert cell.value == 5
        assert cell.is_given is True

    def test_cell_set_user_value(self):
        cell = Cell()
        cell.value = 3
        cell.is_given = False
        assert cell.value == 3
        assert cell.is_given is False


class TestGrid:
    @pytest.fixture
    def empty_3x3_grid(self):
        return Grid(3, 3)

    @pytest.fixture
    def grid_with_givens(self):
        givens = [(0, 0, 2), (1, 2, 1)]
        return Grid(3, 3, givens)

    @pytest.fixture
    def empty_5x5_grid(self):
        return Grid(5, 5)

    @pytest.fixture
    def non_square_grid(self):
        return Grid(2, 4)

    def test_create_empty_grid_has_correct_dimensions(self, empty_3x3_grid):
        assert empty_3x3_grid.rows == 3
        assert empty_3x3_grid.cols == 3

    def test_empty_grid_cells_are_none_not_given(self, empty_3x3_grid):
        cell = empty_3x3_grid.get_cell(0, 0)
        assert cell.value is None
        assert cell.is_given is False

    def test_all_empty_grid_cells_are_none_not_given(self, empty_3x3_grid):
        for r in range(empty_3x3_grid.rows):
            for c in range(empty_3x3_grid.cols):
                cell = empty_3x3_grid.get_cell(r, c)
                assert cell.value is None
                assert cell.is_given is False

    def test_grid_with_givens_initializes_correctly(self, grid_with_givens):
        assert grid_with_givens.rows == 3
        assert grid_with_givens.cols == 3

    def test_given_cell_has_value_and_is_given_true(self, grid_with_givens):
        cell = grid_with_givens.get_cell(0, 0)
        assert cell.value == 2
        assert cell.is_given is True

    def test_second_given_cell(self, grid_with_givens):
        cell = grid_with_givens.get_cell(1, 2)
        assert cell.value == 1
        assert cell.is_given is True

    def test_non_given_cells_remain_empty(self, grid_with_givens):
        cell = grid_with_givens.get_cell(0, 1)
        assert cell.value is None
        assert cell.is_given is False

    def test_grid_to_dict_format(self, grid_with_givens):
        result = grid_with_givens.to_dict()
        expected = [
            [{"value": 2, "is_given": True}, {"value": None, "is_given": False}, {"value": None, "is_given": False}],
            [{"value": None, "is_given": False}, {"value": None, "is_given": False}, {"value": 1, "is_given": True}],
            [{"value": None, "is_given": False}, {"value": None, "is_given": False}, {"value": None, "is_given": False}]
        ]
        assert result == expected

    def test_set_cell_user_value(self, empty_3x3_grid):
        empty_3x3_grid.set_cell(1, 1, 7, is_given=False)
        cell = empty_3x3_grid.get_cell(1, 1)
        assert cell.value == 7
        assert cell.is_given is False

    def test_set_cell_overwrite_existing(self, grid_with_givens):
        grid_with_givens.set_cell(0, 0, 9, is_given=False)
        cell = grid_with_givens.get_cell(0, 0)
        assert cell.value == 9
        assert cell.is_given is False

    def test_5x5_empty_grid_dimensions(self, empty_5x5_grid):
        assert empty_5x5_grid.rows == 5
        assert empty_5x5_grid.cols == 5

    def test_non_square_grid_dimensions(self, non_square_grid):
        assert non_square_grid.rows == 2
        assert non_square_grid.cols == 4


class TestMove:
    @pytest.fixture
    def grid_with_givens(self):
        givens = [(0, 0, 2), (1, 2, 1)]
        return Grid(3, 3, givens)

    def test_make_move_to_empty_cell_success(self, grid_with_givens):
        result = grid_with_givens.make_move(0, 1, 3)
        assert result.success is True
        cell = grid_with_givens.get_cell(0, 1)
        assert cell.value == 3

    def test_make_move_message_on_success(self, grid_with_givens):
        result = grid_with_givens.make_move(2, 2, 5)
        assert "Placed 5 at (2, 2)" in result.message

    def test_make_move_rejects_given_cell(self, grid_with_givens):
        result = grid_with_givens.make_move(0, 0, 5)
        assert result.success is False
        assert "Cannot modify given cells" in result.message

    def test_make_move_idempotent_same_value(self, grid_with_givens):
        grid_with_givens.set_cell(2, 1, 4, is_given=False)
        result = grid_with_givens.make_move(2, 1, 4)
        assert result.success is True
        assert "already has this value" in result.message

    def test_make_move_replaces_different_value(self, grid_with_givens):
        grid_with_givens.set_cell(0, 1, 3, is_given=False)
        cell = grid_with_givens.get_cell(0, 1)
        assert cell.value == 3

        result = grid_with_givens.make_move(0, 1, 7)
        assert result.success is True
        assert cell.value == 7

    def test_make_move_out_of_bounds_row(self, grid_with_givens):
        result = grid_with_givens.make_move(5, 0, 3)
        assert result.success is False
        assert "Invalid position" in result.message

    def test_make_move_out_of_bounds_col(self, grid_with_givens):
        result = grid_with_givens.make_move(0, 5, 3)
        assert result.success is False
        assert "Invalid position" in result.message

    def test_make_move_negative_coordinates(self, grid_with_givens):
        result = grid_with_givens.make_move(-1, 0, 3)
        assert result.success is False
        assert "Invalid position" in result.message

    def test_given_cell_unchanged_after_rejected_move(self, grid_with_givens):
        original_cell = grid_with_givens.get_cell(0, 0)
        assert original_cell.value == 2
        assert original_cell.is_given is True

        result = grid_with_givens.make_move(0, 0, 99)
        assert result.success is False

        still_cell = grid_with_givens.get_cell(0, 0)
        assert still_cell.value == 2
        assert still_cell.is_given is True
