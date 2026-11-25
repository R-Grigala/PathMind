"""Deterministic-seed capable maze generation helpers."""
import random


def generate_maze(rows: int, cols: int, seed: int | None = None) -> list[list[int]]:
    """Generate a perfect maze using randomized depth-first carving."""
    if rows < 5 or cols < 5:
        raise ValueError("rows and cols must be at least 5")
    rng = random.Random(seed)
    grid = [[1] * cols for _ in range(rows)]
    start = (1, 1)
    grid[1][1] = 0
    stack = [start]
    while stack:
        r, c = stack[-1]
        options = [(r + dr, c + dc, r + dr // 2, c + dc // 2)
                   for dr, dc in ((-2, 0), (0, 2), (2, 0), (0, -2))
                   if 1 <= r + dr < rows - 1 and 1 <= c + dc < cols - 1 and grid[r + dr][c + dc] == 1]
        if not options:
            stack.pop()
            continue
        nr, nc, wr, wc = rng.choice(options)
        grid[wr][wc] = grid[nr][nc] = 0
        stack.append((nr, nc))
    return grid
