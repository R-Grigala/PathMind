# API reference

Interactive OpenAPI docs are served at `/docs` when the backend is running.

## `GET /api/health`

Returns service status.

## `POST /api/solve`

```json
{"maze":[[0,1,0],[0,0,0]],"start":[0,0],"goal":[1,2],"algorithm":"astar"}
```

`algorithm` accepts `astar`, `dijkstra`, or `bfs`. The response includes `path`, `cost`, `nodes_explored`, `execution_time_ms`, `explored`, and `found`. Invalid rectangular grids, coordinates, blocked endpoints, or algorithm names return HTTP 422.

## `POST /api/maze`

```json
{"rows":19,"cols":31,"seed":42}
```

Returns a `maze` matrix. Dimensions must be between 5 and 100. Passing the same seed and dimensions produces the same maze.

## `POST /api/learn`

Accepts `maze`, `start`, `goal`, optional `episodes` (1–100,000; defaults to 1,500), and optional `seed`. Returns a path if the tabular Q-learning agent learns one, plus the episode count and number of learned states. This teaching demo is not guaranteed to find a path on every grid.

## `POST /api/dynamic/solve`

Accepts the regular solve fields and `scenarios`, an ordered list of cell-coordinate lists. Each listed coordinate toggles between wall and open terrain, then the solver replans from the original start. The response contains one solve result per snapshot.

## `POST /api/multi-agent`

Accepts `maze`, an `agents` list (up to 8 `{start, goal}` pairs), and an optional algorithm. Agents are planned in order; each successful route's interior cells are reserved against later agents. This is spatial prioritization, not time-based collision avoidance.

## `WS /api/solve/stream`

Connect and send the same JSON payload as `/api/solve`. The server emits ordered `explored` events followed by a `result` event. The current implementation computes the search first and then streams its trace; it does not yet interrupt or update a search while it runs.
