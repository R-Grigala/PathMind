import unittest

try:
    from fastapi.testclient import TestClient
    from backend.main import app
except ImportError:  # API tests run when development dependencies are installed.
    TestClient = None
    app = None


@unittest.skipIf(TestClient is None, "install requirements-dev.txt to test the API")
class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").json()["status"], "ok")

    def test_solve_and_validate(self):
        response = self.client.post("/api/solve", json={"maze": [[0, 0]], "start": [0, 0], "goal": [0, 1]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["cost"], 1)
        invalid = self.client.post("/api/solve", json={"maze": [[0]], "start": [0, 0], "goal": [0, 2]})
        self.assertEqual(invalid.status_code, 422)

    def test_maze_endpoint(self):
        response = self.client.post("/api/maze", json={"rows": 9, "cols": 11, "seed": 4})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["maze"]), 9)

    def test_learning_dynamic_and_multi_agent_endpoints(self):
        grid = [[0, 0, 0], [0, 0, 0]]
        learning = self.client.post("/api/learn", json={"maze": grid, "start": [0, 0], "goal": [0, 2], "episodes": 500})
        self.assertEqual(learning.status_code, 200)
        dynamic = self.client.post("/api/dynamic/solve", json={"maze": grid, "start": [0, 0], "goal": [0, 2], "scenarios": [[[0, 1]]]})
        self.assertEqual(dynamic.status_code, 200)
        self.assertNotEqual(dynamic.json()["snapshots"][0]["path"], [[0, 0], [0, 1], [0, 2]])
        agents = self.client.post("/api/multi-agent", json={"maze": grid, "agents": [{"start": [0, 0], "goal": [0, 2]}, {"start": [1, 0], "goal": [1, 2]}]})
        self.assertEqual(agents.status_code, 200)
        self.assertEqual(len(agents.json()["agents"]), 2)


if __name__ == "__main__":
    unittest.main()
