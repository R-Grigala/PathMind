import unittest

from backend.maze.generator import generate_maze


class MazeTests(unittest.TestCase):
    def test_seed_is_reproducible_and_dimensions_are_preserved(self):
        maze = generate_maze(13, 17, seed=42)
        self.assertEqual(maze, generate_maze(13, 17, seed=42))
        self.assertEqual((len(maze), len(maze[0])), (13, 17))
        self.assertEqual(maze[1][1], 0)

    def test_dimensions_are_validated(self):
        with self.assertRaises(ValueError):
            generate_maze(4, 10)


if __name__ == "__main__":
    unittest.main()
