import unittest
from unittest.mock import patch

from window import Point, Line
from cell import Cell
from maze import Maze


class TestWindow:
    """Lightweight test double for Window used by Maze/Cell.

    It records drawn Line objects and the colors used so tests can assert
    expected drawing behavior without instantiating tkinter.
    Implements `bg` and `resize` because `cell.draw` and `Maze.__init__`
    expect those attributes/methods on the real `Window`.
    """
    def __init__(self):
        self.drawn = []  # list of tuples (Line, color)
        self.bg = "white"
        self.width = None
        self.height = None

    def draw_line(self, line: Line, fill_color):
        self.drawn.append((line, fill_color))

    def redraw(self):
        # no-op for tests
        pass

    def resize(self, width, height):
        self.width = width
        self.height = height

    def close(self):
        pass


class FakeCanvas:
    """A minimal canvas replacement that records create_line calls."""

    def __init__(self):
        self.calls = []

    def create_line(self, x1, y1, x2, y2, fill=None, width=None):
        self.calls.append({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "fill": fill,
            "width": width,
        })


class MazeTests(unittest.TestCase):
    def test_point_attributes(self):
        p = Point(3, 4)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 4)

    def test_line_draw_calls_canvas(self):
        p1 = Point(0, 0)
        p2 = Point(10, 20)
        line = Line(p1, p2)
        canvas = FakeCanvas()
        line.draw(canvas, fill_color="blue")
        self.assertEqual(len(canvas.calls), 1)
        call = canvas.calls[0]
        self.assertEqual(call["x1"], 0)
        self.assertEqual(call["y1"], 0)
        self.assertEqual(call["x2"], 10)
        self.assertEqual(call["y2"], 20)
        self.assertEqual(call["fill"], "blue")
        self.assertEqual(call["width"], 2)

    def test_cell_default_center(self):
        c = Cell()
        center = c.get_center()
        # defaults in maze.Cell are -1 for bounds, so center should be -1,-1
        self.assertEqual(center.x, -1)
        self.assertEqual(center.y, -1)

    def test_cell_draw_draws_walls(self):
        win = TestWindow()
        c = Cell(win=win)
        # draw a 10x10 cell at (0,0)->(10,10)
        c.draw(0, 10, 0, 10)
        # default cell has 4 walls -> 4 draw_line calls
        self.assertEqual(len(win.drawn), 4)

    def test_cell_draw_respects_wall_flags(self):
        win = TestWindow()
        c = Cell(win=win)
        # turn off left and top walls
        c.has_left_wall = False
        c.has_top_wall = False
        c.draw(0, 10, 0, 10)
        # `Cell.draw` issues four draw calls but uses the window bg color
        # for walls that are effectively removed. Verify that:
        # order is left, right, top, bottom
        self.assertEqual(len(win.drawn), 4)
        left_color = win.drawn[0][1]
        right_color = win.drawn[1][1]
        top_color = win.drawn[2][1]
        bottom_color = win.drawn[3][1]
        self.assertEqual(left_color, win.bg)
        self.assertEqual(right_color, "black")
        self.assertEqual(top_color, win.bg)
        self.assertEqual(bottom_color, "black")

    def test_cell_draw_move_and_undo(self):
        win = TestWindow()
        c1 = Cell(win=win)
        c2 = Cell(win=win)
        # set coordinates (so get_center returns meaningful values)
        c1.draw(0, 10, 0, 10)
        c2.draw(10, 20, 0, 10)
        # clear recorded wall draws, we only want to inspect draw_move result
        win.drawn.clear()

        c1.draw_move(c2, undo=False)
        self.assertEqual(len(win.drawn), 1)
        line, color = win.drawn[0]
        self.assertEqual(color, "gray")
        self.assertEqual(line.start.x, c1.get_center().x)
        self.assertEqual(line.start.y, c1.get_center().y)
        self.assertEqual(line.end.x, c2.get_center().x)
        self.assertEqual(line.end.y, c2.get_center().y)

    # test undo draws red (backtracking)
        win.drawn.clear()
        c1.draw_move(c2, undo=True)
        self.assertEqual(len(win.drawn), 1)
        _, color = win.drawn[0]
        self.assertEqual(color, "red")

    @patch("maze.time.sleep", return_value=None)
    def test_maze_creates_expected_grid(self, _sleep):
        # create a small maze with a test window so cells get real coordinates
        win = TestWindow()
        num_cols = 3
        num_rows = 2
        m = Maze(0, 0, num_rows, num_cols, 10, 10, win=win)
        # private attribute name-mangled to _Maze__cells
        self.assertEqual(len(m._Maze__cells), num_cols)
        self.assertEqual(len(m._Maze__cells[0]), num_rows)
        # ensure each cell has been assigned the test window
        for col in range(num_cols):
            for row in range(num_rows):
                self.assertIs(m._Maze__cells[col][row]._win, win)

    @patch("maze.time.sleep", return_value=None)
    def test_reset_cells_visited_clears_flags(self, _sleep):
        # Use a small maze; after construction __reset_cells_visited should
        # ensure every Cell.visited is False
        win = TestWindow()
        m = Maze(0, 0, 3, 3, 10, 10, win=win)
        for col in range(m.num_cols):
            for row in range(m.num_rows):
                self.assertFalse(m._Maze__cells[col][row].visited)

    @patch("maze.time.sleep", return_value=None)
    def test_maze_zero_dimensions(self, _sleep):
        # creating a maze with zero rows/cols should raise a ValueError
        with self.assertRaises(ValueError):
            Maze(0, 0, 0, 0, 10, 10)

    def test_maze_non_integer_dimensions(self):
        # non-integer row/col arguments should raise TypeError
        with self.assertRaises(TypeError):
            Maze(0, 0, 5.5, 3, 10, 10)
        with self.assertRaises(TypeError):
            Maze(0, 0, 3, "4", 10, 10)

    @patch("maze.time.sleep", return_value=None)
    def test_entrance_and_exit_broken(self, _sleep):
        win = TestWindow()
        m = Maze(0, 0, 2, 2, 10, 10, win=win)
        # top-left entrance (top wall removed)
        self.assertFalse(m._Maze__cells[0][0].has_top_wall)
        # bottom-right exit (bottom wall removed)
        self.assertFalse(m._Maze__cells[m.num_cols - 1][m.num_rows - 1].has_bottom_wall)

    @patch("maze.time.sleep", return_value=None)
    def test_maze_generation_with_seed(self, _sleep):
        win = TestWindow()
        # Use a fixed seed so generation is deterministic. Check that at least
        # one pair of adjacent cells has their shared wall removed (one side False).
        m = Maze(0, 0, 4, 4, 10, 10, win=win, seed=42)
        removed_wall_found = False
        for col in range(m.num_cols):
            for row in range(m.num_rows):
                # right neighbor
                if col < m.num_cols - 1:
                    if (not m._Maze__cells[col][row].has_right_wall) or (not m._Maze__cells[col + 1][row].has_left_wall):
                        removed_wall_found = True
                        break
                # bottom neighbor
                if row < m.num_rows - 1:
                    if (not m._Maze__cells[col][row].has_bottom_wall) or (not m._Maze__cells[col][row + 1].has_top_wall):
                        removed_wall_found = True
                        break
            if removed_wall_found:
                break
        self.assertTrue(removed_wall_found, "Expected at least one wall to be removed during generation")

    @patch("maze.time.sleep", return_value=None)
    def test_animate_calls_redraw(self, _sleep):
        # TestWindow.redraw will be instrumented to count calls
        class CountingWindow(TestWindow):
            def __init__(self):
                super().__init__()
                self.redraw_calls = 0

            def redraw(self):
                self.redraw_calls += 1

        win = CountingWindow()
        m = Maze(0, 0, 2, 2, 10, 10, win=win)
        # __animate is called during construction several times; ensure redraw was called
        self.assertGreater(win.redraw_calls, 0)

    @patch("maze.time.sleep", return_value=None)
    def test_resize_called_with_expected_dimensions(self, _sleep):
        win = TestWindow()
        num_cols = 5
        num_rows = 4
        cell_size_x = 8
        cell_size_y = 9
        padding = 10
        needed_w = num_cols * cell_size_x + 0 + padding
        needed_h = num_rows * cell_size_y + 0 + padding
        m = Maze(0, 0, num_rows, num_cols, cell_size_x, cell_size_y, win=win)
        self.assertEqual(win.width, needed_w)
        self.assertEqual(win.height, needed_h)


if __name__ == "__main__":
    unittest.main()