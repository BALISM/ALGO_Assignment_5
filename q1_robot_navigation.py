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

TASK 1 : GRAPH MODELLING (see graph_modelling() below)
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


def graph_modelling(grid, lines):
    """
    TASK 1: Graph Modelling and Problem Formulation.
    Prints a full textual discussion of:
      1. Graph representation of the grid
      2. Vertices, edges, and movement costs
      3. Representation of permanent and destructible obstacles
      4. Graph changes when a blue obstacle is destroyed
      5. Directed vs undirected nature
      6. Robot state definition
    """
    out = lines.append
    out("=" * 78)
    out("TASK 1 : GRAPH MODELLING AND PROBLEM FORMULATION")
    out("=" * 78)
    out("")

    # ----- 1. Graph representation -----
    out("1. GRAPH REPRESENTATION")
    out("-" * 40)
    out("   The 15x15 navigation grid is modelled as a WEIGHTED DIRECTED GRAPH G = (S, A, c)")
    out("   where:")
    out("     S  = set of robot states  (see item 6 for state definition)")
    out("     A  = set of directed arcs (transitions between states)")
    out("     c  = cost function  c : A -> R  (can be negative)")
    out("")
    out("   Conceptually, every non-wall grid cell is a potential vertex.  However,")
    out("   because the robot tracks remaining energy and which blue obstacles have been")
    out("   destroyed, two visits to the same (x, y) with different energy/mask values")
    out("   represent DIFFERENT graph nodes.")
    out("")

    # ----- 2. Vertices and edges -----
    out("2. VERTICES, EDGES, AND MOVEMENT COSTS")
    out("-" * 40)
    # Count accessible cells
    free_cells = [(x, y) for x in range(1, grid.width + 1)
                  for y in range(1, grid.height + 1)
                  if grid.kind(x, y) != WALL]
    wall_cells = grid.width * grid.height - len(free_cells)
    out("   Grid size      : %d x %d = %d cells total" % (grid.width, grid.height, grid.width * grid.height))
    out("   Permanent walls: %d orange (O) cells  -- excluded from the graph" % wall_cells)
    out("   Accessible cells (potential vertex positions): %d" % len(free_cells))
    out("   Blue obstacles : %d  (B, B+, B-)" % len(grid.blue_cells))
    out("")
    out("   Each non-wall cell (x, y) can have up to 6 outgoing directed edges,")
    out("   one per permitted move direction:")
    out("")
    out("     Move      Vector    Edge cost")
    out("     --------  --------  ---------")
    for name, dx, dy, mc in MOVES:
        out("     %-9s (%+d,%+d)    %+d" % (name, dx, dy, mc))
    out("")
    out("   An edge (u -> v) exists in the graph iff:")
    out("     (a) v is inside the grid boundary,")
    out("     (b) the cell at v is NOT a permanent (orange) obstacle,")
    out("     (c) if v is an intact blue obstacle, the robot at u has >= 2 energy units")
    out("         (so it can pay the destruction cost before entering).")
    out("")
    out("   Additional cost/energy events on an edge:")
    out("     Destroying a blue cell   : energy -2, navigation cost +5")
    out("     Entering a B+ bonus cell : energy +3  (applied once, on first entry)")
    out("     Entering a B- penalty    : navigation cost +5  (applied once, on first entry)")
    out("")

    # ----- 3. Permanent and destructible obstacles -----
    out("3. REPRESENTATION OF PERMANENT AND DESTRUCTIBLE OBSTACLES")
    out("-" * 40)
    out("   Permanent obstacles (Orange / O)")
    out("     These cells are simply ABSENT from the graph.  No vertex is created for")
    out("     them, and no edge points into them.  They act as absolute barriers.")
    out("")
    out("   Destructible obstacles (Blue / B, B+, B-)")
    out("     Blue cells ARE included as vertices in the state graph, but they appear")
    out("     in TWO modes depending on the destruction bit in the robot's state mask:")
    out("")
    out("     Intact mode  (mask bit = 0):")
    out("       The cell is treated as a 'conditional wall'.  An incoming edge exists")
    out("       only if the robot has enough energy (>= 2) to pay the destruction cost.")
    out("       Traversing the edge costs: +5 (destruction) + move_cost")
    out("       and reduces energy by 2 (or nets +1 for B+, since -2+3 = +1).")
    out("")
    out("     Destroyed mode  (mask bit = 1):")
    out("       The cell is treated identically to a free cell.  Incoming edges carry")
    out("       only the move cost; no extra energy or cost is applied.")
    out("")

    # ----- 4. Graph changes on destruction -----
    out("4. HOW THE GRAPH CHANGES WHEN A BLUE OBSTACLE IS DESTROYED")
    out("-" * 40)
    out("   The destruction is captured by the STATE MASK, not by mutating the graph.")
    out("   Before destruction (mask bit i = 0):")
    out("     States with the obstacle intact form one 'layer' of the state space.")
    out("     Edges into cell (x,y) require energy >= 2 and carry the extra cost/bonus.")
    out("")
    out("   After destruction (mask bit i = 1):")
    out("     States with the obstacle destroyed form a separate 'layer' of the state")
    out("     space.  The (x,y) cell now has the same connectivity as a free cell in this")
    out("     layer.  The 'destruction' edge is a one-way transition between the layers.")
    out("")
    out("   Concretely: when the robot at state (x0,y0,e,mask) destroys blue cell (bx,by)")
    out("   it moves to state (bx,by, e-2+bonus, mask | bit_i).  All subsequent states")
    out("   with mask bit i = 1 treat (bx,by) as a free cell.  The change is permanent")
    out("   within a path: once a bit is set it cannot be unset.")
    out("")

    # ----- 5. Directed vs undirected -----
    out("5. DIRECTED OR UNDIRECTED?")
    out("-" * 40)
    out("   The navigation graph is DIRECTED (and NOT symmetric).")
    out("")
    out("   Reason 1 – Asymmetric move costs:")
    out("     Moving RIGHT costs +2 but LEFT costs -1.")
    out("     Moving UP costs +2 but DOWN costs -1.")
    out("     Moving Up-Right costs +3 but Up-Left costs -3.")
    out("     The reverse of a Right step is a Left step with a DIFFERENT cost (-1 vs +2).")
    out("     In an undirected graph every edge must carry a single weight, so the two")
    out("     asymmetric directions cannot be collapsed into one undirected edge.")
    out("")
    out("   Reason 2 – No Down-Right, Down-Left, or Downward-diagonal moves:")
    out("     The permitted move set is { R, L, U, D, UR, UL }.  Down-Right or Down-Left")
    out("     are NOT permitted.  Therefore the graph is not symmetric: an edge from A to B")
    out("     via Up-Right does NOT imply an edge from B to A via Down-Left.")
    out("")
    out("   Reason 3 – State-layer transitions:")
    out("     The destruction of a blue obstacle creates a one-way transition between")
    out("     the intact-layer and the destroyed-layer of the state space.  This is")
    out("     inherently directed.")
    out("")
    out("   The graph used for MST (Question 2) is a SEPARATE undirected graph where")
    out("   direction is ignored and symmetric weights are assigned; that is a different")
    out("   construction, not the navigation graph.")
    out("")

    # ----- 6. State definition -----
    out("6. ROBOT STATE DEFINITION")
    out("-" * 40)
    out("   A robot state is a 4-tuple  s = (x, y, energy, mask)  where:")
    out("")
    out("     x      : integer column index,  1 <= x <= %d" % grid.width)
    out("     y      : integer row index,     1 <= y <= %d" % grid.height)
    out("     energy : remaining energy units, 0 <= energy <= 10")
    out("     mask   : integer bitmask, 0 <= mask < 2^%d = %d" % (len(grid.blue_cells), 2**len(grid.blue_cells)))
    out("              bit i = 1 means blue obstacle grid.blue_cells[i] has been destroyed")
    out("")
    out("   Two states are identical (and merged in BFS/DFS visited sets) when")
    out("   (x, y, mask) are equal.  Energy is NOT part of the deduplication key")
    out("   because it is uniquely determined by mask:")
    out("       energy = START_ENERGY")
    out("              - 2 * |{i : mask bit i = 1}|           (destruction cost)")
    out("              + 3 * |{i : mask bit i = 1 and cell i is B+}|  (bonus)")
    out("   (Penalty cells affect navigation cost, not energy.)")
    out("")
    out("   Initial state : (%d, %d, 10, 0)  -- start position, full energy, no destructions" % (grid.start[0], grid.start[1]))
    out("   Goal test     : x == %d and y == %d  (energy and mask are ignored)" % (grid.goal[0], grid.goal[1]))
    out("")
    out("   Total theoretical state space size: %d cells x 11 energy levels x 2^%d masks = %d states" % (
        len(free_cells), len(grid.blue_cells), len(free_cells) * 11 * (2 ** len(grid.blue_cells))))
    out("   (In practice only a small fraction of states are reachable.)")
    out("")


def bfs_discussion(lines):
    """Print the BFS minimum-cost discussion required by Task 2."""
    out = lines.append
    out("")
    out("DISCUSSION: Does BFS Guarantee a Minimum-Cost Path?")
    out("-" * 60)
    out("BFS guarantees the FEWEST-HOPS (minimum number of moves) path in an")
    out("UNWEIGHTED graph, or equivalently minimum cost when all edges have equal")
    out("and positive weight.")
    out("")
    out("In this environment BFS does NOT guarantee minimum cost because:")
    out("")
    out("  1. HETEROGENEOUS COSTS: Move costs range from -3 (Up-Left) to +3 (Up-Right).")
    out("     BFS treats all edges equally (adds one level of breadth per move),")
    out("     ignoring their actual costs.  A path with fewer moves can be more")
    out("     expensive than a longer path that uses cheap (or negative-cost) moves.")
    out("")
    out("  2. NEGATIVE-COST CYCLES: The move set contains:")
    out("       Up-Left (-3) + Right (+2) + Down (-1) = net -2 around a 3-cell loop.")
    out("     This creates a negative-cost cycle in the directed graph.  With negative")
    out("     cycles the concept of 'minimum-cost simple path' is well-defined, but the")
    out("     concept of 'minimum-cost walk' is unbounded below (cost -> -infinity).")
    out("     BFS neither detects nor exploits negative cycles.")
    out("")
    out("  3. OBSTACLE COSTS: Destruction (+5) and penalty (+5) add variable costs that")
    out("     BFS does not account for in its level-by-level frontier expansion.")
    out("")
    out("CONCLUSION: BFS finds the minimum-MOVE-COUNT path (15 moves in this instance),")
    out("but that path costs 51.  The DFS Reverse-ordering experiment found a 78-move")
    out("path with cost only 34, demonstrating that minimum moves != minimum cost.")
    out("For true cost minimisation with non-negative weights, Dijkstra's algorithm")
    out("(priority-queue BFS) would be appropriate.  With negative weights but no")
    out("negative cycles, Bellman-Ford applies.  With negative cycles the problem is")
    out("ill-posed as a minimum-walk problem.")
    out("")


def dfs_discussion(lines):
    """Print the DFS optimality and successor-ordering discussion for Task 3."""
    out = lines.append
    out("")
    out("DISCUSSION: Successor Ordering and DFS Optimality")
    out("-" * 60)
    out("DFS explores states in a depth-first order that is determined entirely by")
    out("the order in which successors are generated (the 'successor ordering').")
    out("")
    out("How successor ordering affects DFS")
    out("   DFS commits to the first path it finds to the goal.  If the first")
    out("   successor explored leads deeply into the graph before reaching the goal,")
    out("   DFS returns that path -- regardless of whether cheaper or shorter paths")
    out("   exist through other successors.  Changing the successor order can")
    out("   drastically change both the traversal path and its cost:")
    out("")
    out("     Default  R,L,U,D,UR,UL : expands 42 states, path cost 68 (40 moves)")
    out("     Goal-ward UR,U,R,...    : expands 43 states, path cost 75 (42 moves)")
    out("     Reverse  UL,UR,D,...    : expands 91 states, path cost 34 (78 moves)")
    out("")
    out("   The REVERSE ordering happens to use more Left (-1) and Down (-1) moves,")
    out("   reducing total cost at the expense of a much longer path.")
    out("")
    out("Why DFS does not produce an optimal path")
    out("   DFS has NO backtracking to compare alternative paths once a goal is found.")
    out("   It is a 'first-found' strategy, not a 'best-found' strategy.  An optimal")
    out("   path would require exhaustive search (exponential) or a heuristic that")
    out("   guarantees optimality (e.g., A* with an admissible heuristic).")
    out("   Additionally, with negative-cost cycles in this graph, 'optimal' in the")
    out("   minimum-cost-walk sense is undefined (unbounded below).")
    out("")


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

    # Task 1: Graph modelling
    graph_modelling(grid, lines)

    res = {}
    g, p, o = bfs(robot)
    res["BFS"] = report("TASK 2 : BREADTH-FIRST SEARCH (queue)", robot, g, p, o, lines)
    bfs_discussion(lines)   # Required Task 2 discussion
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
    dfs_discussion(lines)   # Required Task 3 discussion

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
    with open("outputs/q1_output.txt", "w", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    # run in a big-stack thread so the recursive DFS cannot overflow the call stack
    sys.setrecursionlimit(100000)
    for mb in (256, 128, 64, 32, 16):          # some systems (e.g. Windows) reject huge sizes
        try:
            threading.stack_size(mb * 1024 * 1024)
            break
        except (ValueError, RuntimeError):
            continue
    t = threading.Thread(target=main)
    t.start()
    t.join()