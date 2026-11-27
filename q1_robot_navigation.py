"""
q1_robot_navigation.py   -   Question 1 : BFS and DFS (iterative + recursive)

State of the robot  s = (x, y, energy, mask)
    x, y   : position
    energy : remaining energy units
    mask   : bit i = 1  <=>  i-th blue obstacle (grid.blue_cells[i]) has been destroyed
Two states are the SAME node of the search graph iff (x, y, mask) are equal
(energy is a function of mask:  energy = 10 - 2*|destroyed| + 3*|destroyed bonus cells|).

Actions (successor generation, see Robot.successors):
    MOVE      into a free / already destroyed cell            cost = move cost
    DESTROY+MOVE into an intact blue cell: robot first destroys it from the current
              (adjacent) cell: energy -2, cost +5 (needs energy >= 2), then moves in:
              move cost, +3 energy if B+, +5 cost if B-.
The bonus / penalty is therefore applied exactly once per cell (a destroyed cell is
free afterwards, so entering it again triggers nothing).
"""
import sys
import threading
from data_structures import Queue, Stack
from grid_loader import load_grid, WALL, BLUE, BONUS, PENALTY

# name, dx, dy, cost      (default successor order = order of the assignment text)
MOVES = [("Right", 1, 0, 2), ("Left", -1, 0, -1), ("Up", 0, 1, 2),
         ("Down", 0, -1, -1), ("Up-Right", 1, 1, 3), ("Up-Left", -1, 1, -3)]

START_ENERGY = 10
DESTROY_ENERGY = 2
DESTROY_COST = 5
BONUS_ENERGY = 3
PENALTY_COST = 5


class Robot:
    def __init__(self, grid, moves=None):
        self.g = grid
        self.moves = moves if moves is not None else MOVES

    def initial(self):
        return (self.g.start[0], self.g.start[1], START_ENERGY, 0)

    @staticmethod
    def key(s):
        return (s[0], s[1], s[3])

    def is_goal(self, s):
        return (s[0], s[1]) == self.g.goal

    def successors(self, s):
        """list of (new_state, step_cost, [action strings])"""
        x, y, energy, mask = s
        g = self.g
        out = []
        for name, dx, dy, mc in self.moves:
            nx, ny = x + dx, y + dy
            if not g.inside(nx, ny):
                continue
            kind = g.kind(nx, ny)
            if kind == WALL:
                continue
            if kind in (BLUE, BONUS, PENALTY):
                bit = 1 << g.blue_index[(nx, ny)]
                if not (mask & bit):                       # intact blue obstacle
                    if energy < DESTROY_ENERGY:            # cannot destroy -> cannot enter
                        continue
                    ne = energy - DESTROY_ENERGY
                    cost = DESTROY_COST + mc
                    acts = ["DESTROY (%d,%d) [%s]  energy -%d, cost +%d"
                            % (nx, ny, kind, DESTROY_ENERGY, DESTROY_COST)]
                    note = ""
                    if kind == BONUS:
                        ne += BONUS_ENERGY
                        note = "  bonus: energy +%d" % BONUS_ENERGY
                    elif kind == PENALTY:
                        cost += PENALTY_COST
                        note = "  penalty: cost +%d" % PENALTY_COST
                    acts.append("MOVE %-8s to (%d,%d)  move cost %+d%s" % (name, nx, ny, mc, note))
                    out.append(((nx, ny, ne, mask | bit), cost, acts))
                    continue
            out.append(((nx, ny, energy, mask), mc,
                        ["MOVE %-8s to (%d,%d)  move cost %+d" % (name, nx, ny, mc)]))
        return out


# --------------------------------------------------------------------------- BFS
def bfs(robot):
    start = robot.initial()
    q = Queue()
    q.enqueue(start)
    visited = {robot.key(start)}
    parent = {robot.key(start): None}
    order = []
    while not q.is_empty():
        s = q.dequeue()
        order.append(s)
        if robot.is_goal(s):
            return s, parent, order
        for ns, c, acts in robot.successors(s):
            k = robot.key(ns)
            if k not in visited:
                visited.add(k)
                parent[k] = (s, c, acts)
                q.enqueue(ns)
    return None, parent, order


# ----------------------------------------------------------- iterative DFS (stack)
def dfs_iterative(robot):
    """Successors are pushed in REVERSE order so the first successor is explored first;
    a node is marked visited when it is POPPED (so the traversal equals recursive DFS)."""
    start = robot.initial()
    st = Stack()
    st.push((start, None))
    visited = set()
    parent = {}
    order = []
    while not st.is_empty():
        s, via = st.pop()
        k = robot.key(s)
        if k in visited:
            continue
        visited.add(k)
        parent[k] = via
        order.append(s)
        if robot.is_goal(s):
            return s, parent, order
        succ = robot.successors(s)
        for i in range(len(succ) - 1, -1, -1):
            ns, c, acts = succ[i]
            if robot.key(ns) not in visited:
                st.push((ns, (s, c, acts)))
    return None, parent, order


# ------------------------------------------------------------------ recursive DFS
def dfs_recursive(robot):
    start = robot.initial()
    visited = set()
    parent = {robot.key(start): None}
    order = []
    result = [None]

    def visit(s):
        visited.add(robot.key(s))
        order.append(s)
        if robot.is_goal(s):
            result[0] = s
            return True
        for ns, c, acts in robot.successors(s):
            k = robot.key(ns)
            if k not in visited:
                parent[k] = (s, c, acts)
                if visit(ns):
                    return True
        return False

    visit(start)
    return result[0], parent, order


# ------------------------------------------------------------------- reporting
def rebuild(robot, goal_state, parent):
    """walk parent links back to the start -> (list of states, list of (cost, actions))"""
    states, steps = [], []
    s = goal_state
    while True:
        states.append(s)
        p = parent[robot.key(s)]
        if p is None:
            break
        steps.append((p[1], p[2]))
        s = p[0]
    states.reverse()
    steps.reverse()
    return states, steps


def fmt_pos(s):
    return "(%d,%d)" % (s[0], s[1])


def report(title, robot, goal_state, parent, order, lines):
    out = lines.append
    out("=" * 78)
    out(title)
    out("=" * 78)
    out("States expanded (traversal order length) : %d" % len(order))
    out("Traversal order (position of each expanded state, left to right):")
    row = []
    for i, s in enumerate(order):
        row.append(fmt_pos(s))
        if len(row) == 12 or i == len(order) - 1:
            out("   " + " ".join(row))
            row = []
    if goal_state is None:
        out("Goal reachable : NO")
        return None
    out("Goal reachable : YES")
    states, steps = rebuild(robot, goal_state, parent)
    out("Path (%d moves):" % (len(states) - 1))
    row = []
    for i, s in enumerate(states):
        row.append(fmt_pos(s))
        if len(row) == 12 or i == len(states) - 1:
            out("   " + " -> ".join(row))
            row = []
    out("Sequence of actions:")
    total = 0
    n = 0
    destroyed = []
    for i, (c, acts) in enumerate(steps, 1):
        for a in acts:
            n += 1
            out("   %4d. %s" % (n, a))
            if a.startswith("DESTROY"):
                destroyed.append(a.split()[1])
        total += c
    out("Total navigation cost : %d" % total)
    out("Remaining energy      : %d" % goal_state[2])
    out("Moves in path         : %d" % (len(states) - 1))
    out("Blue obstacles destroyed (%d): %s" % (len(destroyed), " ".join(destroyed) if destroyed else "none"))
    out("")
    return {"cost": total, "energy": goal_state[2], "moves": len(states) - 1,
            "destroyed": len(destroyed), "states": states, "expanded": len(order)}


def negative_cycle_demo(lines):
    lines.append("Note on costs: moves Left (-1), Down (-1) and Up-Left (-3) are NEGATIVE.")
    lines.append("   Up-Left(-3) + Right(+2) + Down(-1) returns the robot to the same cell with net cost -2,")
    lines.append("   i.e. the move graph contains NEGATIVE-COST CYCLES, so 'minimum cost walk' is undefined")
    lines.append("   (unbounded below) and neither BFS nor DFS can promise a minimum-cost path (see report).")
    lines.append("")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "grid.txt"
    grid = load_grid(path)
    lines = []
    lines.append("INPUT GRID (read from %s)  x = columns 1..%d, y = rows 1..%d" % (path, grid.width, grid.height))
    lines.append(grid.show())
    lines.append("Start = %s   Goal = %s   Blue obstacles = %d" % (grid.start, grid.goal, len(grid.blue_cells)))
    lines.append("")
    negative_cycle_demo(lines)
    robot = Robot(grid)

    res = {}
    g, p, o = bfs(robot)
    res["BFS"] = report("TASK 2 : BREADTH-FIRST SEARCH (queue)", robot, g, p, o, lines)
    g, p, o = dfs_iterative(robot)
    res["DFS-iterative"] = report("TASK 3(a) : ITERATIVE DFS (stack)", robot, g, p, o, lines)
    ordI, pathI = o, (rebuild(robot, g, p)[0] if g else None)
    g, p, o = dfs_recursive(robot)
    res["DFS-recursive"] = report("TASK 3(b) : RECURSIVE DFS", robot, g, p, o, lines)
    ordR, pathR = o, (rebuild(robot, g, p)[0] if g else None)

    lines.append("=" * 78)
    lines.append("COMPARISON OF ITERATIVE vs RECURSIVE DFS")
    lines.append("=" * 78)
    same_order = [Robot.key(a) for a in ordI] == [Robot.key(a) for a in ordR]
    same_path = pathI is not None and pathR is not None and [Robot.key(a) for a in pathI] == [Robot.key(a) for a in pathR]
    lines.append("Identical traversal order : %s" % same_order)
    lines.append("Identical final path      : %s" % same_path)
    lines.append("")

    # --- successor-ordering experiment (recursive DFS with different move orders)
    lines.append("=" * 78)
    lines.append("EFFECT OF SUCCESSOR ORDERING ON DFS (recursive DFS, different move orders)")
    lines.append("=" * 78)
    M = {m[0]: m for m in MOVES}
    orders = [
        ("Default  R,L,U,D,UR,UL", MOVES),
        ("Goal-ward UR,U,R,UL,L,D", [M["Up-Right"], M["Up"], M["Right"], M["Up-Left"], M["Left"], M["Down"]]),
        ("Reverse  UL,UR,D,U,L,R", [M["Up-Left"], M["Up-Right"], M["Down"], M["Up"], M["Left"], M["Right"]]),
    ]
    lines.append("%-26s %10s %10s %10s %10s" % ("order", "expanded", "moves", "cost", "energy"))
    for name, mv in orders:
        r2 = Robot(grid, mv)
        g2, p2, o2 = dfs_recursive(r2)
        if g2 is None:
            lines.append("%-26s %10d   goal not reachable" % (name, len(o2)))
            continue
        st, sp = rebuild(r2, g2, p2)
        lines.append("%-26s %10d %10d %10d %10d" % (name, len(o2), len(st) - 1, sum(c for c, _ in sp), g2[2]))
    lines.append("")

    lines.append("=" * 78)
    lines.append("SUMMARY")
    lines.append("=" * 78)
    lines.append("%-16s %10s %8s %8s %10s %10s" % ("algorithm", "expanded", "moves", "cost", "energy", "destroyed"))
    for k in ("BFS", "DFS-iterative", "DFS-recursive"):
        r = res[k]
        if r is None:
            lines.append("%-16s goal not reachable" % k)
        else:
            lines.append("%-16s %10d %8d %8d %10d %10d" % (k, r["expanded"], r["moves"], r["cost"], r["energy"], r["destroyed"]))
    text = "\n".join(lines)
    print(text)
    with open("outputs/q1_output.txt", "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    # run in a big-stack thread so the recursive DFS cannot overflow the call stack
    sys.setrecursionlimit(1000000)
    threading.stack_size(512 * 1024 * 1024)
    t = threading.Thread(target=main)
    t.start()
    t.join()
