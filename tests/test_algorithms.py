import unittest

from backend.algorithms import solve
from backend.algorithms.q_learning import learn


class SolverTests(unittest.TestCase):
    def test_all_algorithms_find_shortest_unweighted_path(self):
        grid = [[0, 0, 0], [1, 1, 0], [0, 0, 0]]
        for algorithm in ("astar", "bfs", "dijkstra"):
            with self.subTest(algorithm=algorithm):
                result = solve(grid, (0, 0), (2, 2), algorithm)
                self.assertTrue(result["found"])
                self.assertEqual(result["cost"], 4)
                self.assertEqual(result["path"][0], [0, 0])
                self.assertEqual(result["path"][-1], [2, 2])

    def test_weighted_search_prefers_cheaper_detour(self):
        grid = [[0, 5, 0], [0, 0, 0]]
        result = solve(grid, (0, 0), (0, 2), "astar")
        self.assertEqual(result["cost"], 4)
        self.assertEqual(result["path"], [[0, 0], [1, 0], [1, 1], [1, 2], [0, 2]])

    def test_bfs_treats_weighted_cells_as_open(self):
        result = solve([[0, 5, 0]], (0, 0), (0, 2), "bfs")
        self.assertEqual(result["cost"], 2)

    def test_unreachable_goal_returns_empty_path(self):
        result = solve([[0, 1], [1, 0]], (0, 0), (1, 1))
        self.assertFalse(result["found"])
        self.assertEqual(result["path"], [])
        self.assertIsNone(result["cost"])

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            solve([[0, 0], [0]], (0, 0), (1, 0))
        with self.assertRaises(ValueError):
            solve([[0]], (0, 0), (0, 1))
        with self.assertRaises(ValueError):
            solve([[0]], (0, 0), (0, 0), "unknown")

    def test_q_learning_learns_a_short_corridor(self):
        result = learn([[0, 0, 0]], (0, 0), (0, 2), episodes=1200, seed=7)
        self.assertTrue(result["found"])
        self.assertEqual(result["path"], [[0, 0], [0, 1], [0, 2]])


if __name__ == "__main__":
    unittest.main()
