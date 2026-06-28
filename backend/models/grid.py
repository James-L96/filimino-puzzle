from dataclasses import dataclass

from models.cell import Cell


@dataclass
class MoveResult:
    success: bool
    message: str


class Grid:
    def __init__(self, rows: int, cols: int, givens: list[tuple[int, int, int]] | None = None):
        self.rows = rows
        self.cols = cols
        self._grid = [[Cell() for _ in range(cols)] for _ in range(rows)]

        if givens:
            for row, col, value in givens:
                self.set_cell(row, col, value, is_given=True)

    def get_cell(self, row: int, col: int) -> Cell:
        return self._grid[row][col]

    def set_cell(self, row: int, col: int, value: int | None, is_given: bool = False):
        self._grid[row][col].value = value
        self._grid[row][col].is_given = is_given

    def to_dict(self) -> list[list[dict]]:
        return [
            [{"value": cell.value, "is_given": cell.is_given} for cell in row]
            for row in self._grid
        ]

    def make_move(self, row: int, col: int, value: int) -> MoveResult:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return MoveResult(success=False, message=f"Invalid position ({row}, {col})")

        cell = self._grid[row][col]

        if cell.is_given:
            return MoveResult(
                success=False,
                message="Cannot modify given cells",
            )

        if cell.value == value:
            return MoveResult(success=True, message="Cell already has this value")

        cell.value = value
        return MoveResult(success=True, message=f"Placed {value} at ({row}, {col})")
