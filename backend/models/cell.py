from dataclasses import dataclass


@dataclass
class Cell:
    value: int | None = None
    is_given: bool = False
