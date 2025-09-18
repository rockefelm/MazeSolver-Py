from __future__ import annotations
from window import Line, Point, Window
import time

class Cell:
    def __init__(self, win: Window=None):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.visited = False
        self.__x1 = -1
        self.__x2 = -1
        self.__y1 = -1
        self.__y2 = -1
        self._win = win

    def get_center(self):
        size_x = self.__x2 - self.__x1
        size_y = self.__y2 - self.__y1
        center_x = self.__x1 + size_x / 2
        center_y = self.__y1 + size_y / 2
        return Point(center_x, center_y)

    def draw(self, x1, x2, y1, y2):
        if self._win is None:
            return
        self.__x1 = x1
        self.__x2 = x2
        self.__y1 = y1
        self.__y2 = y2

        point1 = Point(self.__x1, self.__y1)
        point2 = Point(self.__x1, self.__y2)
        line1 = Line(point1, point2)
        self._win.draw_line(line1, "black" if self.has_left_wall else self._win.bg)
        point1 = Point(self.__x2, self.__y1)
        point2 = Point(self.__x2, self.__y2)
        line2 = Line(point1, point2)
        self._win.draw_line(line2, "black" if self.has_right_wall else self._win.bg)
        point1 = Point(self.__x1, self.__y1)
        point2 = Point(self.__x2, self.__y1)
        line3 = Line(point1, point2)
        self._win.draw_line(line3, "black" if self.has_top_wall else self._win.bg)
        point1 = Point(self.__x1, self.__y2)
        point2 = Point(self.__x2, self.__y2)
        line4 = Line(point1, point2)
        self._win.draw_line(line4, "black" if self.has_bottom_wall else self._win.bg)

    def draw_move(self, to_cell: Cell, undo=False):
        if self._win is None:
            return
        # Normal move is drawn in gray; when undo/backtracking set to red
        if not undo:
            color = "gray"
        else:
            color = "red"

        point1 = self.get_center()
        point2 = to_cell.get_center()
        line = Line(point1, point2)
        self._win.draw_line(line, color)
        # animate the move (redraw + short sleep) if the window supports it
        try:
            self._win.redraw()
        except Exception:
            pass
        # keep the small delay for visible animation in UI runs
        try:
            time.sleep(0.05)
        except Exception:
            pass