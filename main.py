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

def main():
    win = Window(800, 600)
    point1 = Point(200,400)
    point2 = Point(400, 500)
    line = Line(point1, point2)
    win.draw_line(line, "red")
    win.wait_for_close()
        


if __name__ == "__main__":
    main()
