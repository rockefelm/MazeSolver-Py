from __future__ import annotations
from tkinter import Tk, BOTH, Canvas


class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._root = Tk()
        self._root.title("Maze Solver")
        self._canvas = Canvas(self._root, height=self.height, width=self.width)
        self._canvas.pack(fill=BOTH, expand=1)
        self._running = False
        self._root.protocol("WM_DELETE_WINDOW", self.close)

    def draw_line(self, line: Line, fill_color):
        line.draw(self._canvas, fill_color)

    def redraw(self):
        self._root.update_idletasks()
        self._root.update()

    def wait_for_close(self):
        self._running = True
        while self._running:
            self.redraw()

    def close(self):
        self._running = False

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
    
    def draw(self, canvas: Canvas, fill_color):
        canvas.create_line(self.start.x,
                            self.start.y,
                            self.end.x,
                            self.end.y,
                            fill=fill_color,
                            width=2)
        
class Cell:
    def __init__(self, win: Window):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
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
        self.__x1 = x1
        self.__x2 = x2
        self.__y1 = y1
        self.__y2 = y2
        if self.has_left_wall:
            point1 = Point(self.__x1, self.__y1)
            point2 = Point(self.__x1, self.__y2)
            line = Line(point1, point2)
            self._win.draw_line(line, "black")
        if self.has_right_wall:
            point1 = Point(self.__x2, self.__y1)
            point2 = Point(self.__x2, self.__y2)
            line = Line(point1, point2)
            self._win.draw_line(line, "black")
        if self.has_top_wall:
            point1 = Point(self.__x1, self.__y1)
            point2 = Point(self.__x2, self.__y1)
            line = Line(point1, point2)
            self._win.draw_line(line, "black")
        if self.has_bottom_wall:
            point1 = Point(self.__x1, self.__y2)
            point2 = Point(self.__x2, self.__y2)
            line = Line(point1, point2)
            self._win.draw_line(line, "black")

    def draw_move(self, to_cell: Cell, undo=False):
        if not undo:
            color = "red"
        else: 
            color = "gray"

        point1 = self.get_center()
        point2 = to_cell.get_center()
        line = Line(point1, point2)
        self._win.draw_line(line, color)
        



def main():
    win = Window(800, 600)
    cell = Cell(win)
    cell.has_top_wall = False
    cell.has_right_wall = False
    cell.draw(100, 200, 100, 200)
    cell2 = Cell(win)
    cell2.draw(200, 300, 200, 300)
    cell.draw_move(cell2)
    win.wait_for_close()
        


if __name__ == "__main__":
    main()
