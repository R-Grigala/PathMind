"""Small tabular Q-learning demo for the gridworld used by PathMind."""
import random


def learn(grid: list[list[int]], start: tuple[int, int], goal: tuple[int, int], episodes: int = 1500,
          seed: int | None = 0) -> dict:
    rows, cols = len(grid), len(grid[0]) if grid else 0
    if not rows or not cols or any(len(row) != cols for row in grid):
        raise ValueError("grid must be a non-empty rectangle")
    for point, name in ((start, "start"), (goal, "goal")):
        if not (0 <= point[0] < rows and 0 <= point[1] < cols):
            raise ValueError(f"{name} is outside the grid")
        if grid[point[0]][point[1]] == 1:
            raise ValueError(f"{name} must be traversable")
    if episodes < 1 or episodes > 100_000:
        raise ValueError("episodes must be between 1 and 100000")

    rng = random.Random(seed)
    actions = ((-1, 0), (0, 1), (1, 0), (0, -1))
    q: dict[tuple[int, int], list[float]] = {}
    max_steps = rows * cols * 2
    for episode in range(episodes):
        state = start
        epsilon = max(0.03, 1 - episode / episodes)
        for _ in range(max_steps):
            values = q.setdefault(state, [0.0] * 4)
            if rng.random() < epsilon:
                action = rng.randrange(4)
            else:
                top = max(values)
                choices = [i for i, value in enumerate(values) if value == top]
                action = rng.choice(choices)
            dr, dc = actions[action]
            nxt = state[0] + dr, state[1] + dc
            if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols) or grid[nxt[0]][nxt[1]] == 1:
                nxt, reward = state, -5.0
            elif nxt == goal:
                reward = 20.0
            else:
                reward = -1.0 - max(1, grid[nxt[0]][nxt[1]]) * 0.1
            future = 0.0 if nxt == goal else max(q.setdefault(nxt, [0.0] * 4))
            values[action] += 0.15 * (reward + 0.9 * future - values[action])
            state = nxt
            if state == goal:
                break

    path = [start]
    seen = {start}
    state = start
    for _ in range(max_steps):
        values = q.get(state)
        if values is None:
            break
        action = max(range(4), key=lambda i: values[i])
        dr, dc = actions[action]
        nxt = state[0] + dr, state[1] + dc
        if (not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols) or grid[nxt[0]][nxt[1]] == 1
                or nxt in seen):
            # Pick the best legal unvisited action when the learned greedy action loops.
            options = []
            for index, (adr, adc) in enumerate(actions):
                candidate = state[0] + adr, state[1] + adc
                if (0 <= candidate[0] < rows and 0 <= candidate[1] < cols
                        and grid[candidate[0]][candidate[1]] != 1 and candidate not in seen):
                    options.append((values[index], candidate))
            if not options:
                break
            _, nxt = max(options, key=lambda option: option[0])
        path.append(nxt)
        seen.add(nxt)
        state = nxt
        if state == goal:
            break
    found = state == goal
    return {"path": [list(point) for point in path] if found else [], "found": found,
            "episodes": episodes, "states_learned": len(q)}
