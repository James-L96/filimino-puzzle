// Frontend renderer script - runs in the browser context
const API_URL = "http://127.0.0.1:5000";

const boardEl = document.getElementById("board");
const overlayEl = document.getElementById("overlay");
const statusEl = document.getElementById("status");
const sizeSelect = document.getElementById("sizeSelect");
const difficultySelect = document.getElementById("difficultySelect");
const newPuzzleBtn = document.getElementById("newPuzzleBtn");

let state = {
  rows: 8,
  cols: 8,
  givens: new Set(),
  values: [],
  cellColors: [],
  selected: -1,
  solved: false,
};

let cells = [];

const GROUP_COLORS = 12;

function componentCells(index) {
  const v = state.values[index];
  if (v === null || v === undefined) return [];
  const rows = state.rows;
  const cols = state.cols;
  const seen = new Set([index]);
  const stack = [index];
  while (stack.length > 0) {
    const j = stack.pop();
    const r = Math.floor(j / cols);
    const c = j % cols;
    const candidates = [];
    if (r > 0) candidates.push(j - cols);
    if (r + 1 < rows) candidates.push(j + cols);
    if (c > 0) candidates.push(j - 1);
    if (c + 1 < cols) candidates.push(j + 1);
    for (const k of candidates) {
      if (state.values[k] === v && !seen.has(k)) {
        seen.add(k);
        stack.push(k);
      }
    }
  }
  return [...seen];
}

function assignGroupColor(index) {
  const comp = componentCells(index);
  if (comp.length === 0) return;
  let color = null;
  for (const i of comp) {
    if (state.cellColors[i] !== null && state.cellColors[i] !== undefined) {
      color = state.cellColors[i];
      break;
    }
  }
  if (color === null) {
    const used = new Set();
    for (let i = 0; i < state.values.length; i++) {
      const cc = state.cellColors[i];
      if (cc !== null && cc !== undefined) used.add(cc);
    }
    color = 0;
    for (let step = 0; step < GROUP_COLORS && used.has(color); step++) {
      color = (color + 1) % GROUP_COLORS;
    }
  }
  for (const i of comp) state.cellColors[i] = color;
}

function cycleGroupColor(index) {
  const v = state.values[index];
  if (v === null || v === undefined) return;
  const comp = componentCells(index);
  let current = null;
  for (const i of comp) {
    if (state.cellColors[i] !== null && state.cellColors[i] !== undefined) {
      current = state.cellColors[i];
      break;
    }
  }
  const next = ((current === null ? -1 : current) + 1) % GROUP_COLORS;
  for (const i of comp) state.cellColors[i] = next;
  applyGroupColors();
}

function applyGroupColors() {
  for (let i = 0; i < cells.length; i++) {
    const cell = cells[i];
    for (let c = 0; c < GROUP_COLORS; c++) {
      cell.classList.remove(`gc-${c}`);
    }
    const cc = state.cellColors[i];
    if (cc !== null && cc !== undefined) cell.classList.add(`gc-${cc}`);
  }
}

function setStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.className = kind || "";
}

function showOverlay(visible) {
  overlayEl.classList.toggle("hidden", !visible);
}

async function loadPuzzle() {
  const size = Number(sizeSelect.value);
  const difficulty = difficultySelect.value;
  showOverlay(true);
  setStatus("");
  try {
    const response = await fetch(
      `${API_URL}/api/puzzle?size=${size}&difficulty=${difficulty}&refresh=1`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const puzzle = await response.json();

    state.rows = puzzle.rows;
    state.cols = puzzle.cols;
    state.givens = new Set(puzzle.givens.map(([r, c]) => `${r},${c}`));
    state.values = new Array(puzzle.rows * puzzle.cols).fill(null);
    for (const [r, c, v] of puzzle.givens) {
      state.values[r * puzzle.cols + c] = v;
    }
    state.selected = -1;
    state.solved = false;
    state.cellColors = new Array(puzzle.rows * puzzle.cols).fill(null);
    for (let i = 0; i < state.values.length; i++) {
      if (state.values[i] !== null) assignGroupColor(i);
    }

    renderBoard();
  } catch (error) {
    console.error("Puzzle request failed:", error);
    setStatus(
      "Could not reach the API. Make sure the Flask backend is running (cd backend, python app.py).",
      "err"
    );
  } finally {
    showOverlay(false);
  }
}

function renderBoard() {
  const n = state.rows;
  boardEl.innerHTML = "";
  boardEl.style.setProperty("--n", n);
  boardEl.style.gridTemplateColumns = `repeat(${state.cols}, 1fr)`;
  cells = [];

  for (let i = 0; i < state.values.length; i++) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.dataset.index = i;
    cell.addEventListener("click", () => onCellClick(i));
    cell.addEventListener("contextmenu", (event) => {
      event.preventDefault();
      cycleGroupColor(i);
    });
    boardEl.appendChild(cell);
    cells.push(cell);
    updateCell(i);
  }

  applyGroupColors();
}

function updateCell(i) {
  const cell = cells[i];
  if (!cell) return;
  const r = Math.floor(i / state.cols);
  const c = i % state.cols;
  cell.textContent = state.values[i] ?? "";
  cell.classList.toggle("given", state.givens.has(`${r},${c}`));
  cell.classList.toggle("selected", i === state.selected);
}

function refreshSelection() {
  for (let i = 0; i < cells.length; i++) {
    cells[i].classList.toggle("selected", i === state.selected);
  }
}

function onCellClick(i) {
  if (state.solved) return;
  const r = Math.floor(i / state.cols);
  const c = i % state.cols;
  if (state.givens.has(`${r},${c}`)) return;

  if (i === state.selected && state.values[i] !== null) {
    setValue(i, null);
    state.selected = -1;
    refreshSelection();
    return;
  }
  state.selected = i;
  refreshSelection();
}

function setValue(i, value) {
  if (i < 0 || i >= state.values.length) return;
  const r = Math.floor(i / state.cols);
  const c = i % state.cols;
  if (state.givens.has(`${r},${c}`)) return;

  state.values[i] = value;
  if (value === null) {
    state.cellColors[i] = null;
  } else {
    assignGroupColor(i);
  }
  updateCell(i);
  applyGroupColors();
  maybeCheck();
}

function moveSelection(dr, dc) {
  let i = state.selected;
  if (i < 0) i = 0;
  const r = Math.min(state.rows - 1, Math.max(0, Math.floor(i / state.cols) + dr));
  const c = Math.min(state.cols - 1, Math.max(0, (i % state.cols) + dc));
  state.selected = r * state.cols + c;
  refreshSelection();
}

async function maybeCheck() {
  if (state.solved || state.values.some((v) => v === null)) return;

  setStatus("Checking…");
  try {
    const response = await fetch(`${API_URL}/api/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows: state.rows, cols: state.cols, values: state.values }),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const result = await response.json();

    if (result.solved) {
      state.solved = true;
      setStatus("Solved! Nice work. Hit New Puzzle for another one.", "ok");
    } else {
      setStatus("Not quite right — some groups don't match their numbers.", "err");
    }
  } catch (error) {
    console.error("Check request failed:", error);
    setStatus("Could not verify the grid. Is the Flask backend running?", "err");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  newPuzzleBtn.addEventListener("click", loadPuzzle);
  sizeSelect.addEventListener("change", loadPuzzle);
  difficultySelect.addEventListener("change", loadPuzzle);

  document.addEventListener("keydown", (event) => {
    const tag = event.target.tagName;
    if (tag === "SELECT" || tag === "INPUT" || tag === "TEXTAREA") return;

    if (/^[1-9]$/.test(event.key)) {
      setValue(state.selected, Number(event.key));
    } else if (event.key === "0" || event.key === "Backspace" || event.key === "Delete") {
      setValue(state.selected, null);
      event.preventDefault();
    } else if (event.key === "ArrowUp") {
      moveSelection(-1, 0);
      event.preventDefault();
    } else if (event.key === "ArrowDown") {
      moveSelection(1, 0);
      event.preventDefault();
    } else if (event.key === "ArrowLeft") {
      moveSelection(0, -1);
      event.preventDefault();
    } else if (event.key === "ArrowRight") {
      moveSelection(0, 1);
      event.preventDefault();
    }
  });

  loadPuzzle();
});
