from models.cell import Cell


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
