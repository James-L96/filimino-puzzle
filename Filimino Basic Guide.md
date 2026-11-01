# Problem
- Objective: Build a working Fillomino puzzle first (generator + playable UI), then build a bot that solves them.

# Roadmap
## Phase 1 - Working puzzle
- Solver core: backtracking with MRV heuristic (needed to verify generation; reused by the bot later)
- Puzzle generator: solve-then-remove with uniqueness guarantee; difficulties easy/medium/hard
- API: fetch puzzle, make move, validate against the rules in docs/rules.md
- Frontend: N×N grid UI — click a cell, enter 1–9, givens locked

## Phase 2 - Bot
- Reuse the solver core to solve generated and scraped puzzles; measure the metrics below

# Metrics
- Completion Rate: Percentage of puzzle done correctly without rules broken.
- Inference Speed:  How long it takes to solve 10x10 vs 20x20 (Polyo daily ladder: 8×8, 12×12, 16×16, 20×20)

# Data Acquisition
- Polyo daily puzzles (browsable by date and size, solutions published) as a test set with known answers.
- Website scraper/a script/ Dataset from Kaggle?
- Could youse Numpy to create a grid

# Install dependencies
# pip install pandas scikit-learn matplotlib seaborn
```python
# Install dependencies: 
# pip install pandas scikit-learn matplotlib seaborn numpy

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split