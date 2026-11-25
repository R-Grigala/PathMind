"""Grid pathfinding algorithms with consistent metrics and animation traces."""
from __future__ import annotations

from heapq import heappop, heappush
from itertools import count
from time import perf_counter
from typing import Any

Position = tuple[int, int]


def solve(grid: list[list[int]], start: Position, goal: Position, algorithm: str = "astar") -> dict[str, Any]:
    """Solve a 4-way grid; 0 is open, 1 is blocked, values >=2 are terrain costs."""
    rows, cols = len(grid), len(grid[0]) if grid else 0
    if not rows or not cols or any(len(row) != cols for row in grid):
        raise ValueError("grid must be a non-empty rectangle")
    for point, name in ((start, "start"), (goal, "goal")):
        if len(point) != 2 or not (0 <= point[0] < rows and 0 <= point[1] < cols):
            raise ValueError(f"{name} is outside the grid")
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        raise ValueError("start and goal must be traversable")
    algorithm = algorithm.lower()
    if algorithm not in {"astar", "bfs", "dijkstra"}:
        raise ValueError("algorithm must be astar, bfs, or dijkstra")

    began = perf_counter()
    serial = count()
    frontier: list[tuple[float, int, Position]] = []
    heappush(frontier, (0, next(serial), start))
    costs: dict[Position, float] = {start: 0}
    parent: dict[Position, Position] = {}
    discovered = {start}
    explored: list[Position] = []
    closed: set[Position] = set()
    deltas = ((-1, 0), (0, 1), (1, 0), (0, -1))

    while frontier:
        _, _, current = heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        explored.append(current)
        if current == goal:
            break
        for dr, dc in deltas:
            nxt = current[0] + dr, current[1] + dc
            r, c = nxt
            if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] == 1 or nxt in closed:
                continue
            step_cost = max(1, grid[r][c])
            new_cost = costs[current] + step_cost
            if algorithm == "bfs":
                # BFS is defined for unweighted grids; terrain is treated as open.
                new_cost = costs[current] + 1
            if new_cost >= costs.get(nxt, float("inf")):
                continue
            costs[nxt] = new_cost
            parent[nxt] = current
            if nxt not in discovered:
                discovered.add(nxt)
            heuristic = abs(goal[0] - r) + abs(goal[1] - c) if algorithm == "astar" else 0
            heappush(frontier, (new_cost + heuristic, next(serial), nxt))

    path: list[Position] = []
    if goal in closed:
        node = goal
        while node != start:
            path.append(node)
            node = parent[node]
        path.append(start)
        path.reverse()
    path_cost = sum(max(1, grid[r][c]) for r, c in path[1:]) if path else None
    return {
        "path": [list(p) for p in path],
        "path_length": max(0, len(path) - 1) if path else None,
        "cost": path_cost,
        "nodes_explored": len(explored),
        "execution_time_ms": round((perf_counter() - began) * 1000, 3),
        "explored": [list(p) for p in explored],
        "found": bool(path),
    }
