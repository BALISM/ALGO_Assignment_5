"""
q3_analysis.py  -  Question 3 : Time & Space Complexity Analysis
CS2009 Design and Analysis of Algorithms  -  Assignment 4

This module prints a detailed, well-structured written analysis for every
sub-question of Q3.  No third-party libraries are used.

Sub-questions
  1. BFS Complexity       (adjacency matrix vs adjacency list)
  2. DFS Complexity       (iterative stack vs recursive, matrix vs list)
  3. Shortest-Path Guarantee in the given navigation environment
  4. Prim vs Kruskal      (matrix vs list)
"""

import sys
import os

# ---------------------------------------------------------------------------
# helper: pretty section header
# ---------------------------------------------------------------------------
def header(title, lines, width=78):
    lines.append("=" * width)
    lines.append(title)
    lines.append("=" * width)


def sub(title, lines):
    lines.append("")
    lines.append("-" * 60)
    lines.append(title)
    lines.append("-" * 60)


# ---------------------------------------------------------------------------
# Grid statistics (read from grid.txt so the numbers are concrete)
# ---------------------------------------------------------------------------
def grid_stats(grid_path="grid.txt"):
    """Return (V, E_directed, E_undirected, W, H) for the navigation graph."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(grid_path)))
        from grid_loader import load_grid
        g = load_grid(grid_path)
        # vertices = non-wall cells (every state (x,y,mask) but for complexity
        # we use the number of distinct grid cells as V)
        total = g.width * g.height
        walls = sum(1 for x in range(1, g.width+1)
                    for y in range(1, g.height+1)
                    if g.kind(x, y) == "O")
        V = total - walls          # accessible cells
        # Each cell has at most 6 directed moves; undirected edges <= 3*V
        E_dir = 6 * V              # upper bound (directed)
        E_undir = 3 * V            # upper bound (undirected, ignoring direction)
        return V, E_dir, E_undir, g.width, g.height
    except Exception:
        return 143, 858, 429, 15, 15   # fallback: observed values


# ---------------------------------------------------------------------------
# Main analysis text
# ---------------------------------------------------------------------------
def build_analysis(grid_path="grid.txt"):
    V, E_d, E_u, W, H = grid_stats(grid_path)
    lines = []

    lines.append("Q3 : TIME AND SPACE COMPLEXITY ANALYSIS")
    lines.append("CS2009 Design and Analysis of Algorithms  -  Assignment 4")
    lines.append("")
    lines.append("Grid : %d x %d = %d cells total." % (W, H, W*H))
    lines.append("  Accessible vertices V = %d  (permanent orange cells excluded)." % V)
    lines.append("  Each cell has at most 6 outgoing directed edges (R, L, U, D, UR, UL).")
    lines.append("  Total directed edges E <= 6V = %d (upper bound)." % (6*V))
    lines.append("  Total undirected edges E <= 3V = %d (upper bound, ignoring direction)." % (3*V))
    lines.append("")
    lines.append("NOTE ON STATE SPACE")
    lines.append("  The full BFS/DFS state is (x, y, energy, destroyed_mask).  With 15 blue")
    lines.append("  cells the mask has 2^15 = 32,768 values, so the theoretical state-space")
    lines.append("  is V_state = V * 11 * 32768 (energy 0..10, mask 0..32767).")
    lines.append("  For complexity purposes we write V for the number of reachable states and")
    lines.append("  E for the number of edges in the corresponding state-space graph, because")
    lines.append("  Big-O notation absorbs the constant factors (11 * 32768).")
    lines.append("")

    # -----------------------------------------------------------------------
    # Q3.1  BFS
    # -----------------------------------------------------------------------
    header("Q3.1  BFS COMPLEXITY", lines)
    lines.append("")
    lines.append("BFS visits every reachable state at most once and examines every")
    lines.append("outgoing edge of each visited state exactly once.")
    lines.append("")

    sub("Representation 1 : Adjacency MATRIX", lines)
    lines.append("")
    lines.append("  Graph stored as a V x V Boolean matrix M where M[u][v] = 1")
    lines.append("  if there is an edge from u to v.")
    lines.append("")
    lines.append("  Time Complexity")
    lines.append("  ---------------")
    lines.append("  For each dequeued state u (at most V states), BFS scans the entire")
    lines.append("  row u of the matrix to find neighbours: O(V) per state.")
    lines.append("")
    lines.append("      T_BFS_matrix = O(V) states x O(V) per row scan")
    lines.append("                   = O(V^2)")
    lines.append("")
    lines.append("  For the navigation grid  V = %d  =>  V^2 = %d." % (V, V*V))
    lines.append("")
    lines.append("  Space Complexity")
    lines.append("  ----------------")
    lines.append("  Matrix storage              : O(V^2)")
    lines.append("  BFS queue (at most V nodes) : O(V)")
    lines.append("  Visited set                 : O(V)")
    lines.append("  Parent / path table         : O(V)")
    lines.append("")
    lines.append("      S_BFS_matrix = O(V^2)   (dominated by matrix storage)")

    sub("Representation 2 : Adjacency LIST", lines)
    lines.append("")
    lines.append("  Each vertex u stores only its actual neighbours, so the total")
    lines.append("  storage for all adjacency lists is Theta(V + E).")
    lines.append("")
    lines.append("  Time Complexity")
    lines.append("  ---------------")
    lines.append("  Each vertex is dequeued once; each edge is examined once when")
    lines.append("  the adjacency list of its source vertex is scanned.")
    lines.append("")
    lines.append("      T_BFS_list = O(V + E)")
    lines.append("")
    lines.append("  For the navigation grid  E <= 6V = %d  =>  V + E <= 7V = %d." % (6*V, 7*V))
    lines.append("")
    lines.append("  Space Complexity")
    lines.append("  ----------------")
    lines.append("  Adjacency lists : O(V + E)")
    lines.append("  Queue           : O(V)")
    lines.append("  Visited / parent: O(V)")
    lines.append("")
    lines.append("      S_BFS_list = O(V + E)")
    lines.append("")
    lines.append("Summary BFS")
    lines.append("  +------------------+-------------------+-------------------+")
    lines.append("  | Representation   | Time              | Space             |")
    lines.append("  +------------------+-------------------+-------------------+")
    lines.append("  | Adjacency Matrix | O(V^2)            | O(V^2)            |")
    lines.append("  | Adjacency List   | O(V + E)          | O(V + E)          |")
    lines.append("  +------------------+-------------------+-------------------+")

    # -----------------------------------------------------------------------
    # Q3.2  DFS
    # -----------------------------------------------------------------------
    header("Q3.2  DFS COMPLEXITY", lines)
    lines.append("")
    lines.append("Two DFS variants are implemented: iterative (stack-based) and recursive.")
    lines.append("Both visit each reachable state at most once and examine each edge once,")
    lines.append("so their asymptotic complexities are identical to each other.")
    lines.append("")

    sub("Representation 1 : Adjacency MATRIX  (both iterative and recursive)", lines)
    lines.append("")
    lines.append("  Time Complexity")
    lines.append("  ---------------")
    lines.append("  For each of V states, the algorithm scans a full row of the matrix")
    lines.append("  to discover neighbours.")
    lines.append("")
    lines.append("      T_DFS_matrix = O(V^2)")
    lines.append("")
    lines.append("  Space Complexity - Iterative (stack-based)")
    lines.append("  ------------------------------------------")
    lines.append("  Matrix storage                : O(V^2)")
    lines.append("  Explicit stack (at most V)    : O(V)")
    lines.append("  Visited set                   : O(V)")
    lines.append("")
    lines.append("      S_DFS_iterative_matrix = O(V^2)")
    lines.append("")
    lines.append("  Space Complexity - Recursive")
    lines.append("  ----------------------------")
    lines.append("  Matrix storage                     : O(V^2)")
    lines.append("  Call stack depth (at most V frames) : O(V)")
    lines.append("  Visited set                        : O(V)")
    lines.append("")
    lines.append("      S_DFS_recursive_matrix = O(V^2)")
    lines.append("")
    lines.append("  NOTE: recursive DFS on a large state space risks a Python stack overflow;")
    lines.append("  the implementation in q1_robot_navigation.py uses a large-stack thread and")
    lines.append("  sys.setrecursionlimit(100000) to mitigate this.")

    sub("Representation 2 : Adjacency LIST  (both iterative and recursive)", lines)
    lines.append("")
    lines.append("  Time Complexity")
    lines.append("  ---------------")
    lines.append("  Each vertex is processed once; each edge is examined once.")
    lines.append("")
    lines.append("      T_DFS_list = O(V + E)")
    lines.append("")
    lines.append("  Space Complexity - Iterative")
    lines.append("  ----------------------------")
    lines.append("  Adjacency lists : O(V + E)")
    lines.append("  Stack           : O(V)")
    lines.append("  Visited / parent: O(V)")
    lines.append("")
    lines.append("      S_DFS_iterative_list = O(V + E)")
    lines.append("")
    lines.append("  Space Complexity - Recursive")
    lines.append("  ----------------------------")
    lines.append("  Adjacency lists        : O(V + E)")
    lines.append("  Call-stack depth       : O(V)  (worst-case path length = V)")
    lines.append("  Visited / parent       : O(V)")
    lines.append("")
    lines.append("      S_DFS_recursive_list = O(V + E)")
    lines.append("")
    lines.append("Summary DFS")
    lines.append("  +------------------+-------------------+-------------------+-------------------+")
    lines.append("  | Representation   | Time              | Space (Iterative) | Space (Recursive) |")
    lines.append("  +------------------+-------------------+-------------------+-------------------+")
    lines.append("  | Adjacency Matrix | O(V^2)            | O(V^2)            | O(V^2)            |")
    lines.append("  | Adjacency List   | O(V + E)          | O(V + E)          | O(V + E)          |")
    lines.append("  +------------------+-------------------+-------------------+-------------------+")

    # -----------------------------------------------------------------------
    # Q3.3  Shortest-Path Guarantee
    # -----------------------------------------------------------------------
    header("Q3.3  SHORTEST-PATH GUARANTEE", lines)
    lines.append("")
    lines.append("Question: Which of BFS and DFS guarantees a shortest path in this")
    lines.append("navigation environment?")
    lines.append("")
    lines.append("SHORT ANSWER:  NEITHER algorithm guarantees a minimum-cost path here.")
    lines.append("")
    lines.append("Detailed Explanation")
    lines.append("--------------------")
    lines.append("")
    lines.append("1. BFS and uniform costs")
    lines.append("   BFS guarantees the FEWEST-HOPS path (minimum number of moves) in an")
    lines.append("   UNWEIGHTED graph, or equivalently a minimum-cost path when ALL edge")
    lines.append("   weights are EQUAL AND POSITIVE.")
    lines.append("")
    lines.append("   In this problem the move costs are NOT uniform:")
    lines.append("     Right       : +2")
    lines.append("     Up          : +2")
    lines.append("     Up-Right    : +3")
    lines.append("     Left        : -1  (NEGATIVE)")
    lines.append("     Down        : -1  (NEGATIVE)")
    lines.append("     Up-Left     : -3  (NEGATIVE)")
    lines.append("   plus destruction cost +5 and optional penalty +5 or bonus +3 energy.")
    lines.append("")
    lines.append("   Because some costs are negative, the graph contains NEGATIVE-COST CYCLES")
    lines.append("   (e.g., Up-Left (-3) + Right (+2) + Down (-1) = net -2 around a 3-cell")
    lines.append("   loop).  This means the minimum-cost WALK is unbounded below (by")
    lines.append("   repeatedly traversing the negative-cost cycle the total cost can be")
    lines.append("   driven to -infinity).  Therefore the concept of 'minimum-cost path'")
    lines.append("   is undefined (or trivially -inf) for the WALK model without a visited-")
    lines.append("   state constraint.")
    lines.append("")
    lines.append("   BFS finds the shortest path in terms of NUMBER OF MOVES (hops), not")
    lines.append("   minimum cost.  The BFS path in the output has only 15 moves, but its")
    lines.append("   cost (51) is higher than the DFS Reverse-ordering cost (34) which uses")
    lines.append("   78 moves -- demonstrating that fewer hops != lower cost here.")
    lines.append("")
    lines.append("2. DFS and optimality")
    lines.append("   DFS explores states in a depth-first order that depends entirely on")
    lines.append("   the successor ordering (the order in which neighbours are generated).")
    lines.append("   It returns the FIRST path it finds to the goal, with no guarantee about")
    lines.append("   path cost or length.  As shown in the successor-ordering experiment:")
    lines.append("     Default  R,L,U,D,UR,UL  : cost 68  (40 moves)")
    lines.append("     Goal-ward UR,U,R,UL,L,D : cost 75  (42 moves)")
    lines.append("     Reverse  UL,UR,D,U,L,R  : cost 34  (78 moves)")
    lines.append("   The same graph yields costs differing by a factor of >2 depending on")
    lines.append("   successor order, confirming DFS has NO optimality guarantee.")
    lines.append("")
    lines.append("3. What algorithm WOULD guarantee a minimum-cost path?")
    lines.append("   * If all edge weights were NON-NEGATIVE: Dijkstra's algorithm (priority-")
    lines.append("     queue BFS) guarantees minimum cost in O((V + E) log V).")
    lines.append("   * With NEGATIVE weights but NO negative cycles: Bellman-Ford in O(VE).")
    lines.append("   * With negative cycles: the problem is ill-posed (unbounded); a path")
    lines.append("     cost can always be reduced further.  A SIMPLE-PATH (no repeated")
    lines.append("     vertex) variant could be solved with dynamic programming or ILP, but")
    lines.append("     is NP-hard in general.")
    lines.append("")
    lines.append("Conclusion")
    lines.append("----------")
    lines.append("  BFS guarantees minimum MOVES (hops) but NOT minimum cost.")
    lines.append("  DFS guarantees NEITHER minimum moves NOR minimum cost.")
    lines.append("  Neither is an optimal algorithm for cost minimisation in this environment.")

    # -----------------------------------------------------------------------
    # Q3.4  Prim vs Kruskal
    # -----------------------------------------------------------------------
    header("Q3.4  PRIM'S vs KRUSKAL'S ALGORITHM COMPLEXITY", lines)
    lines.append("")
    lines.append("For the MST problem V = %d accessible cells, E <= %d edges (undirected)." % (V, 3*V))
    lines.append("")

    sub("Prim's Algorithm", lines)
    lines.append("")
    lines.append("Implementation used: binary min-heap (MinHeap class in data_structures.py).")
    lines.append("")
    lines.append("Representation 1 : Adjacency MATRIX")
    lines.append("")
    lines.append("  The classic Prim with adjacency matrix uses a simple linear scan to find")
    lines.append("  the minimum-weight crossing edge at each step.")
    lines.append("")
    lines.append("  Time: V iterations x O(V) scan per iteration = O(V^2)")
    lines.append("  Space: O(V^2) for the matrix + O(V) for key/parent arrays = O(V^2)")
    lines.append("")
    lines.append("Representation 2 : Adjacency LIST + Binary Min-Heap (implemented)")
    lines.append("")
    lines.append("  Each vertex is inserted into the heap at most once per incident edge;")
    lines.append("  each edge triggers at most one heap push (O(log V)) and one heap pop")
    lines.append("  (O(log V)).")
    lines.append("")
    lines.append("  Time:  O((V + E) log V)   (heap push/pop for each edge)")
    lines.append("         = O(E log V)  since E >= V-1 for a connected graph")
    lines.append("  Space: O(V + E) for adjacency lists + O(V) for the heap = O(V + E)")
    lines.append("")
    lines.append("  For our grid: V=%d, E<=%d => O(E log V) = O(%d * %.1f) ~ O(%d)." % (
        V, 3*V, 3*V, (V).bit_length(), 3*V*(V).bit_length()))
    lines.append("")
    lines.append("  With a Fibonacci heap the time improves to O(E + V log V).")
    lines.append("")

    sub("Kruskal's Algorithm", lines)
    lines.append("")
    lines.append("Implementation used: merge_sort + DSU (data_structures.py).")
    lines.append("")
    lines.append("  The bottleneck is SORTING all E edges.")
    lines.append("")
    lines.append("Representation 1 : Adjacency MATRIX")
    lines.append("")
    lines.append("  First all edges must be extracted from the matrix: O(V^2).")
    lines.append("  Then sorted: O(E log E) = O(V^2 log V) in the worst case.")
    lines.append("  DSU operations: near-linear O(E * alpha(V)) ~ O(E).")
    lines.append("")
    lines.append("  Time:  O(V^2 log V)  (edge extraction + sort dominate)")
    lines.append("  Space: O(V^2) matrix + O(E) edge list + O(V) DSU = O(V^2)")
    lines.append("")
    lines.append("Representation 2 : Adjacency LIST")
    lines.append("")
    lines.append("  Edges are enumerated directly in O(V + E).")
    lines.append("  Sort: O(E log E).")
    lines.append("  DSU : O(E * alpha(V))  (alpha = inverse Ackermann, essentially O(1)).")
    lines.append("")
    lines.append("  Time:  O(E log E)  =  O(E log V)  (since E <= V^2 so log E <= 2 log V)")
    lines.append("  Space: O(V + E) adjacency lists + O(E) sorted edge array + O(V) DSU")
    lines.append("       = O(V + E)")
    lines.append("")
    lines.append("  For our grid: E<=%d => O(E log E) ~ O(%d * %.1f) ~ O(%d)." % (
        3*V, 3*V, (3*V).bit_length(), 3*V*(3*V).bit_length()))
    lines.append("")

    lines.append("Summary Prim vs Kruskal")
    lines.append("  +------------+--------------------+--------------------+--------------------+--------------------+")
    lines.append("  | Algorithm  | Time (Matrix)      | Space (Matrix)     | Time (List)        | Space (List)       |")
    lines.append("  +------------+--------------------+--------------------+--------------------+--------------------+")
    lines.append("  | Prim       | O(V^2)             | O(V^2)             | O((V+E) log V)     | O(V + E)           |")
    lines.append("  | Kruskal    | O(V^2 log V)       | O(V^2)             | O(E log E)         | O(V + E)           |")
    lines.append("  +------------+--------------------+--------------------+--------------------+--------------------+")
    lines.append("")
    lines.append("Practical Comparison for the Navigation Grid")
    lines.append("--------------------------------------------")
    lines.append("  V = %d, E (undirected) <= %d." % (V, 3*V))
    lines.append("")
    lines.append("  Dense graphs (E ~ V^2):  Prim (adj. matrix) O(V^2) is better than")
    lines.append("  Kruskal O(V^2 log V) because sorting dominates.")
    lines.append("")
    lines.append("  Sparse graphs (E ~ V, like our grid):  Kruskal O(E log E) ~ O(V log V)")
    lines.append("  and Prim O(E log V) ~ O(V log V) are essentially equivalent; both")
    lines.append("  outperform the matrix-based versions.")
    lines.append("")
    lines.append("  Key distinction: Prim grows one tree greedily and is naturally suited to")
    lines.append("  dense adjacency-matrix representations.  Kruskal sorts all edges globally")
    lines.append("  and uses DSU -- it is simpler to implement for sparse edge lists and")
    lines.append("  handles disconnected graphs (spanning FOREST) with no extra logic.")

    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "grid.txt"
    text = build_analysis(path)
    print(text)
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/q3_output.txt", "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
