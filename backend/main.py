from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.algorithms import solve
from backend.algorithms.q_learning import learn
from backend.maze.generator import generate_maze

app = FastAPI(title="PathMind API", version="1.0.0", description="Grid pathfinding and maze generation")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class SolveRequest(BaseModel):
    maze: list[list[int]]
    start: tuple[int, int]
    goal: tuple[int, int]
    algorithm: str = "astar"


class MazeRequest(BaseModel):
    rows: int = Field(ge=5, le=100, default=21)
    cols: int = Field(ge=5, le=100, default=31)
    seed: int | None = None


class AgentRequest(BaseModel):
    start: tuple[int, int]
    goal: tuple[int, int]


class MultiAgentRequest(BaseModel):
    maze: list[list[int]]
    agents: list[AgentRequest] = Field(min_length=1, max_length=8)
    algorithm: str = "astar"


class LearningRequest(BaseModel):
    maze: list[list[int]]
    start: tuple[int, int]
    goal: tuple[int, int]
    episodes: int = Field(default=1500, ge=1, le=100000)
    seed: int | None = 0


class DynamicRequest(BaseModel):
    maze: list[list[int]]
    start: tuple[int, int]
    goal: tuple[int, int]
    algorithm: str = "astar"
    scenarios: list[list[tuple[int, int]]] = Field(min_length=1, max_length=20)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "PathMind"}


@app.post("/api/solve")
def solve_route(request: SolveRequest) -> dict:
    try:
        return solve(request.maze, request.start, request.goal, request.algorithm)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/maze")
def maze_route(request: MazeRequest) -> dict:
    try:
        return {"maze": generate_maze(request.rows, request.cols, request.seed)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/multi-agent")
def multi_agent_route(request: MultiAgentRequest) -> dict:
    """Plan prioritized routes; prior routes become blocked for later agents."""
    reserved = [row[:] for row in request.maze]
    plans = []
    try:
        for agent in request.agents:
            route = solve(reserved, agent.start, agent.goal, request.algorithm)
            plans.append({"start": list(agent.start), "goal": list(agent.goal), **route})
            if route["found"]:
                for row, col in route["path"][1:-1]:
                    if [row, col] not in (list(agent.start), list(agent.goal)):
                        reserved[row][col] = 1
        return {"agents": plans, "strategy": "prioritized spatial reservations",
                "note": "Routes avoid earlier agents' interior cells; this is not time-step collision avoidance."}
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/learn")
def learn_route(request: LearningRequest) -> dict:
    try:
        return learn(request.maze, request.start, request.goal, request.episodes, request.seed)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/dynamic/solve")
def dynamic_solve(request: DynamicRequest) -> dict:
    """Re-plan against a sequence of maze snapshots with changed blocked cells."""
    snapshots, current = [], [row[:] for row in request.maze]
    try:
        for changes in request.scenarios:
            for row, col in changes:
                if not (0 <= row < len(current) and 0 <= col < len(current[0])):
                    raise ValueError("scenario coordinate is outside the grid")
                if (row, col) not in (request.start, request.goal):
                    current[row][col] = 0 if current[row][col] == 1 else 1
            snapshots.append(solve(current, request.start, request.goal, request.algorithm))
        return {"snapshots": snapshots, "note": "Each scenario toggles the listed cells, then replans from the original start."}
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.websocket("/api/solve/stream")
async def stream_solve(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        result = solve(payload["maze"], tuple(payload["start"]), tuple(payload["goal"]), payload.get("algorithm", "astar"))
        for index, point in enumerate(result["explored"]):
            await websocket.send_json({"type": "explored", "index": index, "node": point})
        await websocket.send_json({"type": "result", **result})
    except (ValueError, KeyError, TypeError) as exc:
        await websocket.send_json({"type": "error", "detail": str(exc)})
    except WebSocketDisconnect:
        return


frontend = Path(__file__).resolve().parent.parent / "frontend"
if frontend.exists():
    app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
