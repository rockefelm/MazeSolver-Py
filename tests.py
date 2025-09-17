import unittest
from unittest.mock import patch

from maze import Point, Line, Cell, Maze


class TestWindow:
    """Lightweight test double for Window used by Maze/Cell.

    It records drawn Line objects and the colors used so tests can assert
    expected drawing behavior without instantiating tkinter.
    """
    def __init__(self):
        self.drawn = []  # list of tuples (Line, color)

    def draw_line(self, line: Line, fill_color):
        self.drawn.append((line, fill_color))

    def redraw(self):
        # no-op for tests
        pass

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
        # only right and bottom walls should be drawn
        self.assertEqual(len(win.drawn), 2)

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
        self.assertEqual(color, "red")
        self.assertEqual(line.start.x, c1.get_center().x)
        self.assertEqual(line.start.y, c1.get_center().y)
        self.assertEqual(line.end.x, c2.get_center().x)
        self.assertEqual(line.end.y, c2.get_center().y)

        # test undo draws gray
        win.drawn.clear()
        c1.draw_move(c2, undo=True)
        self.assertEqual(len(win.drawn), 1)
        _, color = win.drawn[0]
        self.assertEqual(color, "gray")

    @patch("time.sleep", return_value=None)
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

    @patch("time.sleep", return_value=None)
    def test_maze_zero_dimensions(self, _sleep):
        m = Maze(0, 0, 0, 0, 10, 10)
        self.assertEqual(len(m._Maze__cells), 0)


if __name__ == "__main__":
    unittest.main()