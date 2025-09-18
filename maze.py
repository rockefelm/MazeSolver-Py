from __future__ import annotations
from window import Window
from cell import Cell
import random
import time

class Maze:
    def __init__(
            self,
            x1,
            y1,
            num_rows,
            num_cols,
            cell_size_x,
            cell_size_y,
            win: Window=None,
            seed=None
            ):
        # Validate dimensions early to provide a clear error for callers
        if not isinstance(num_rows, int) or not isinstance(num_cols, int):
            raise TypeError("num_rows and num_cols must be integers")
        if num_rows <= 0 or num_cols <= 0:
            raise ValueError("num_rows and num_cols must be positive integers")
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.seed = random.seed(seed)
        self.win = win
        PADDING = 10
        needed_w = self.num_cols * self.cell_size_x + self.x1 + PADDING
        needed_h = self.num_rows * self.cell_size_y + self.y1 + PADDING
        if self.win:
            self.win.resize(needed_w, needed_h)
        self.__cells = []

        self.__create_cells()
        self.__break_entrance_and_exit()
        self.__break_walls_r(0, 0)
        self.__reset_cells_visited()
    
    def __create_cells(self):
        for col in range(self.num_cols):
            self.__cells.append([])
            for row in range(self.num_rows):
                cell = Cell(self.win)
                self.__cells[col].append(cell)
                self.__draw_cell(col, row)

    def __draw_cell(self, col, row):
        x1 = self.x1 + col * self.cell_size_x
        y1 = self.y1 + row * self.cell_size_y
        x2 = x1 + self.cell_size_x
        y2 = y1 + self.cell_size_y
        self.__cells[col][row].draw(x1, x2, y1, y2)
        self.__animate()

    def __break_entrance_and_exit(self):
        # break entrance (top-left)
        self.__cells[0][0].has_top_wall = False
        self.__draw_cell(0, 0)
        # break exit (bottom-right)
        self.__cells[self.num_cols - 1][self.num_rows - 1].has_bottom_wall = False
        self.__draw_cell(self.num_cols - 1, self.num_rows - 1)
    
    def __animate(self):
        if self.win:
            self.win.redraw()
        time.sleep(0.05)

    def __break_walls_r(self, col, row):
        self.__cells[col][row].visited = True
        while True:
            next_index_list = []

            # determine which cell(s) to visit next
            # left
            if col > 0 and not self.__cells[col - 1][row].visited:
                next_index_list.append((col - 1, row))
            # right
            if col < self.num_cols - 1 and not self.__cells[col + 1][row].visited:
                next_index_list.append((col + 1, row))
            # up
            if row > 0 and not self.__cells[col][row - 1].visited:
                next_index_list.append((col, row - 1))
            # down
            if row < self.num_rows - 1 and not self.__cells[col][row + 1].visited:
                next_index_list.append((col, row + 1))

            # if there is nowhere to go from here
            # just break out
            if len(next_index_list) == 0:
                self.__draw_cell(col, row)
                return

            # randomly choose the next direction to go
            direction_index = random.randrange(len(next_index_list))
            next_index = next_index_list[direction_index]

            # knock out walls between this cell and the next cell(s)
            # right
            if next_index[0] == col + 1:
                self.__cells[col][row].has_right_wall = False
                self.__cells[col + 1][row].has_left_wall = False
            # left
            if next_index[0] == col - 1:
                self.__cells[col][row].has_left_wall = False
                self.__cells[col - 1][row].has_right_wall = False
            # down
            if next_index[1] == row + 1:
                self.__cells[col][row].has_bottom_wall = False
                self.__cells[col][row + 1].has_top_wall = False
            # up
            if next_index[1] == row - 1:
                self.__cells[col][row].has_top_wall = False
                self.__cells[col][row - 1].has_bottom_wall = False

            # recursively visit the next cell
            self.__break_walls_r(next_index[0], next_index[1])
    
    def __reset_cells_visited(self):
        
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                self.__cells[col][row].visited = False

    def solve(self):
        return self._solve_r(0,0)
    
    def _solve_r(self, col, row):
        if self.__cells[col][row].visited:
            return False
        self.__cells[col][row].visited = True
        # visiting a cell; drawing/animation is handled by Cell.draw_move

        # if we've reached the exit cell
        if col == self.num_cols - 1 and row == self.num_rows - 1:
            return True
        
        # try moving in each possible direction; draw the forward move before recursing
        # right
        if not self.__cells[col][row].has_right_wall and not self.__cells[col + 1][row].visited:
            # draw forward
            self.__cells[col][row].draw_move(self.__cells[col + 1][row], undo=False)
            if self._solve_r(col + 1, row):
                return True
            # backtrack visually
            self.__cells[col][row].draw_move(self.__cells[col + 1][row], undo=True)
        # down
        if not self.__cells[col][row].has_bottom_wall and not self.__cells[col][row + 1].visited:
            self.__cells[col][row].draw_move(self.__cells[col][row + 1], undo=False)
            if self._solve_r(col, row + 1):
                return True
            self.__cells[col][row].draw_move(self.__cells[col][row + 1], undo=True)
        # left
        if not self.__cells[col][row].has_left_wall and not self.__cells[col - 1][row].visited:
            self.__cells[col][row].draw_move(self.__cells[col - 1][row], undo=False)
            if self._solve_r(col - 1, row):
                return True
            self.__cells[col][row].draw_move(self.__cells[col - 1][row], undo=True)
        # up
        if not self.__cells[col][row].has_top_wall and not self.__cells[col][row - 1].visited:
            self.__cells[col][row].draw_move(self.__cells[col][row - 1], undo=False)
            if self._solve_r(col, row - 1):
                return True
            self.__cells[col][row].draw_move(self.__cells[col][row - 1], undo=True)
        
        # backtrack - no valid moves from here
        # draw the backtrack move (undo) in red
        if col > 0 and not self.__cells[col][row].has_left_wall and self.__cells[col - 1][row].visited:
            self.__cells[col][row].draw_move(self.__cells[col - 1][row], undo=True)
        elif col < self.num_cols - 1 and not self.__cells[col][row].has_right_wall and self.__cells[col + 1][row].visited:
            self.__cells[col][row].draw_move(self.__cells[col + 1][row], undo=True)
        elif row > 0 and not self.__cells[col][row].has_top_wall and self.__cells[col][row - 1].visited:
            self.__cells[col][row].draw_move(self.__cells[col][row - 1], undo=True)
        elif row < self.num_rows - 1 and not self.__cells[col][row].has_bottom_wall and self.__cells[col][row +1].visited:
            self.__cells[col][row].draw_move(self.__cells[col][row + 1], undo=True)
        return False