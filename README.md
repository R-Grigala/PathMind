# PathMind

An interactive pathfinding lab for learning how search algorithms explore a grid. Draw walls and weighted terrain, generate a maze, and visualize or compare A*, Dijkstra, and BFS.

## Features

- Interactive 31 × 19 board with draggable start and goal nodes.
- Wall, weight, and erase tools; seeded-capable depth-first maze generation through the API.
- Animated exploration and final path, pause/resume, reset, and speed control.
- A*, Dijkstra, and BFS comparison on the same board with node, path, cost, and timing metrics.
- FastAPI endpoints for solving grids and generating mazes, with OpenAPI docs.
- WebSocket event delivery, dynamic-grid replanning, prioritized multi-agent routes, and a tabular Q-learning API demo.
- Unit and API tests, Docker, and GitHub Actions CI.

## Run locally

Requires Python 3.10+.

```sh
python -m venv .venv
. .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn backend.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Interactive API docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Run with Docker

```sh
docker compose up --build
```

Then open http://127.0.0.1:8000.

## Controls

- Select an algorithm and edit tool in the left panel.
- Click or drag on the grid to draw. Drag the green start or gold goal marker to move it.
- **Visualize path** runs the selected algorithm. **Compare all** evaluates all three on the same board.
- Keyboard shortcuts: `Space` run/pause, `R` reset animation, `G` generate maze.

## Algorithms and grid rules

Moves are four-directional. In the grid matrix, `0` is regular terrain, `1` is a wall, and values greater than `1` are entry costs. A* uses Manhattan distance; Dijkstra minimizes total terrain cost; BFS treats all traversable cells as equal. Thus, BFS is optimal by number of steps only on unweighted grids.

## API

See [docs/api.md](docs/api.md), or use `/docs` while the server is running. The UI uses the core solver and maze routes; the learning, dynamic, multi-agent, and WebSocket interfaces are available to API clients.

```sh
curl -X POST http://127.0.0.1:8000/api/solve \
  -H 'Content-Type: application/json' \
  -d '{"maze":[[0,1,0],[0,0,0]],"start":[0,0],"goal":[1,2],"algorithm":"astar"}'
```

## Tests

```sh
python -m pytest
```

## Project structure

```text
backend/
  algorithms/search.py       # A*, Dijkstra, BFS
  maze/generator.py          # randomized DFS maze generation
  main.py                    # FastAPI application and static frontend host
frontend/
  index.html
  static/styles.css
  static/favicon/favicon.ico
  static/images/OfDigital_Logo.png
  static/images/PathMind_Logo.png
  app.js
tests/
docs/
.github/workflows/ci.yml
Dockerfile
docker-compose.yml
```

## Next extensions

Persistent saved mazes, a historical benchmark dashboard, and 3D visualization are natural follow-up modules.

## License

MIT. See [LICENSE](LICENSE).
