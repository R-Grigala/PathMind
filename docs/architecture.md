# Architecture

PathMind is a small, browser-first teaching application.

```text
Browser UI (frontend/)
  ├─ local search + step animation (A*, Dijkstra, BFS)
  └─ REST calls ──> FastAPI (backend/main.py)
                     ├─ algorithms/search.py
                     └─ maze/generator.py
```

The browser performs the search so animation remains responsive and works without a round trip per node. The API provides a reusable solver and seeded maze generator for other clients. Grids are rectangular integer matrices: `0` is normal terrain, `1` is blocked, and values `>=2` are traversal costs. Moves are four-directional; entering a weighted tile incurs its value. BFS intentionally treats all passable cells as equal cost.

## Run locally

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000. API documentation is at `/docs`.
