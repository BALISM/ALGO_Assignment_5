"""
grid_loader.py
Reads the grid from a text file.

File format (grid.txt):
    line 1 : "<width> <height>"            e.g.  15 15
    line 2 : "<start_x> <start_y>"         e.g.  7 1
    line 3 : "<goal_x>  <goal_y>"          e.g.  15 14
    next 15 lines : rows from TOP (y = 15) to BOTTOM (y = 1), tokens separated by spaces
        0  free cell | O permanent obstacle | B blue normal | B+ blue bonus | B- blue penalty

Coordinates: (1,1) = bottom-left, (15,15) = top-right, written (x, y) = (column, row).
"""

FREE, WALL, BLUE, BONUS, PENALTY = "0", "O", "B", "B+", "B-"


class Grid:
    def __init__(self, width, height, start, goal, cells):
        self.width = width
        self.height = height
        self.start = start
        self.goal = goal
        self.cells = cells                  # dict (x, y) -> token
        # every blue cell gets a bit position (used for the 'destroyed' bit-mask)
        self.blue_cells = []
        for y in range(1, height + 1):
            for x in range(1, width + 1):
                if cells[(x, y)] in (BLUE, BONUS, PENALTY):
                    self.blue_cells.append((x, y))
        self.blue_index = {c: i for i, c in enumerate(self.blue_cells)}

    def inside(self, x, y):
        return 1 <= x <= self.width and 1 <= y <= self.height

    def kind(self, x, y):
        return self.cells[(x, y)]

    def show(self):
        lines = []
        for y in range(self.height, 0, -1):
            lines.append("%2d  " % y + " ".join("%-2s" % self.cells[(x, y)] for x in range(1, self.width + 1)))
        lines.append("    " + " ".join("%-2d" % x for x in range(1, self.width + 1)))
        return "\n".join(lines)


def load_grid(path):
    with open(path) as f:
        lines = [ln.strip() for ln in f.read().split("\n") if ln.strip() != ""]
    w, h = [int(t) for t in lines[0].split()]
    start = tuple(int(t) for t in lines[1].split())
    goal = tuple(int(t) for t in lines[2].split())
    rows = lines[3:3 + h]
    cells = {}
    for r, line in enumerate(rows):
        y = h - r
        toks = line.split()
        if len(toks) != w:
            raise ValueError("row %d has %d tokens, expected %d" % (y, len(toks), w))
        for x, tok in enumerate(toks, 1):
            if tok not in (FREE, WALL, BLUE, BONUS, PENALTY):
                raise ValueError("bad token %r at (%d,%d)" % (tok, x, y))
            cells[(x, y)] = tok
    return Grid(w, h, start, goal, cells)
