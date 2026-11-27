"""
q2_mst.py   -   Question 2 : Prim's and Kruskal's algorithms on the undirected MST graph

Graph construction (as required by the assignment)
    vertices : every NON-permanent cell (free cells + ALL blue cells, assumed destroyed)
    edges    : two vertices are joined if they are horizontal / vertical / diagonal neighbours
               (the movement rules contain Right, Left, Up, Down, Up-Right, Up-Left; ignoring
               direction this means every pair of 8-neighbours is connected)
    weights  : horizontal = 1, vertical = 1, diagonal = sqrt(2)
Each undirected edge is generated exactly once (offsets (1,0), (0,1), (1,1), (-1,1)).
"""
import sys
from data_structures import MinHeap, DSU, merge_sort
from grid_loader import load_grid, WALL

SQRT2 = 1.4142135623730951          # constant (no math library needed)
OFFSETS = [(1, 0, 1.0, "H"), (0, 1, 1.0, "V"), (1, 1, SQRT2, "D"), (-1, 1, SQRT2, "D")]


def build_graph(grid):
    ids, cells = {}, []
    for y in range(1, grid.height + 1):
        for x in range(1, grid.width + 1):
            if grid.kind(x, y) != WALL:
                ids[(x, y)] = len(cells)
                cells.append((x, y))
    edges = []                                   # (weight, u, v, type)
    adj = [[] for _ in cells]
    for (x, y) in cells:
        u = ids[(x, y)]
        for dx, dy, w, t in OFFSETS:
            c = (x + dx, y + dy)
            if c in ids:
                v = ids[c]
                edges.append((w, u, v, t))
                adj[u].append((v, w))
                adj[v].append((u, w))
    return cells, ids, edges, adj


def name(cells, i):
    return "(%d,%d)" % cells[i]


def prim(n, adj):
    """Prim with a binary heap, restarted from every unvisited vertex (=> spanning forest)."""
    in_tree = [False] * n
    chosen = []
    components = []                      # list of (root, size)
    for root in range(n):
        if in_tree[root]:
            continue
        heap = MinHeap()
        in_tree[root] = True
        size = 1
        for v, w in adj[root]:
            heap.push(w, (root, v))
        while not heap.is_empty():
            w, (u, v) = heap.pop_min()
            if in_tree[v]:
                continue
            in_tree[v] = True
            size += 1
            chosen.append((w, u, v))
            for x, wx in adj[v]:
                if not in_tree[x]:
                    heap.push(wx, (v, x))
        components.append((root, size))
    return chosen, components


def kruskal(n, edges):
    ordered = merge_sort(edges, key=lambda e: e[0])
    dsu = DSU(n)
    chosen = []
    for w, u, v, t in ordered:
        if dsu.union(u, v):
            chosen.append((w, u, v))
    return ordered, chosen, dsu


def total(chosen):
    s = 0.0
    for w, _, _ in chosen:
        s += w
    return s


def count_types(chosen, cells):
    h = v = d = 0
    for w, a, b in chosen:
        if w == SQRT2:
            d += 1
        elif cells[a][1] == cells[b][1]:
            h += 1
        else:
            v += 1
    return h, v, d


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "grid.txt"
    grid = load_grid(path)
    cells, ids, edges, adj = build_graph(grid)
    n = len(cells)
    L = []
    out = L.append
    nh = sum(1 for e in edges if e[3] == "H")
    nv = sum(1 for e in edges if e[3] == "V")
    nd = sum(1 for e in edges if e[3] == "D")
    out("GRAPH CONSTRUCTION")
    out("  Vertices (non-permanent cells) : %d   (%d permanent orange cells excluded)" % (n, grid.width * grid.height - n))
    out("  Edges considered               : %d  = %d horizontal (w=1) + %d vertical (w=1) + %d diagonal (w=sqrt2)" % (len(edges), nh, nv, nd))
    out("  Vertex list:")
    row = []
    for i in range(n):
        row.append("%d:%s" % (i, name(cells, i)))
        if len(row) == 10 or i == n - 1:
            out("    " + "  ".join(row)); row = []
    out("  Adjacency list (vertex -> neighbours, weight):")
    for i in range(n):
        out("    %s -> %s" % (name(cells, i), ", ".join("%s[%s]" % (name(cells, v), "1" if w == 1.0 else "1.4142") for v, w in adj[i])))
    out("")

    # ---------------- Prim
    pe, pcomp = prim(n, adj)
    out("=" * 78); out("TASK 1 : PRIM'S ALGORITHM"); out("=" * 78)
    out("Edges selected (in the order added): %d" % len(pe))
    for i, (w, u, v) in enumerate(pe, 1):
        out("  %3d. %-8s -- %-8s  weight %s" % (i, name(cells, u), name(cells, v), "1" if w == 1.0 else "1.414214"))
    pw = total(pe)
    ph, pv, pd = count_types(pe, cells)
    out("Total MST weight : %.6f   (= %d horizontal + %d vertical + %d diagonal x sqrt2)" % (pw, ph, pv, pd))
    out("Connected components : %d" % len(pcomp))
    if len(pcomp) == 1:
        out("All %d accessible cells form ONE connected component -> a single MST." % n)
    else:
        out("The graph is DISCONNECTED -> minimum spanning FOREST with %d trees:" % len(pcomp))
        for k, (r, sz) in enumerate(pcomp, 1):
            out("   tree %d : %d vertices (grown from %s), %d edges" % (k, sz, name(cells, r), sz - 1))
    out("Check: edges = V - components = %d - %d = %d" % (n, len(pcomp), n - len(pcomp)))
    out("")

    # ---------------- Kruskal
    ordered, ke, dsu = kruskal(n, edges)
    out("=" * 78); out("TASK 2 : KRUSKAL'S ALGORITHM"); out("=" * 78)
    out("All %d edges sorted by weight (merge sort): first 5 / last 5" % len(ordered))
    for w, u, v, t in ordered[:5]:
        out("   %-8s -- %-8s  %s" % (name(cells, u), name(cells, v), "1" if w == 1.0 else "1.414214"))
    out("   ...")
    for w, u, v, t in ordered[-5:]:
        out("   %-8s -- %-8s  %s" % (name(cells, u), name(cells, v), "1" if w == 1.0 else "1.414214"))
    out("   (%d edges of weight 1 come first, then %d edges of weight sqrt2)" % (nh + nv, nd))
    out("Edges selected (in the order added): %d" % len(ke))
    for i, (w, u, v) in enumerate(ke, 1):
        out("  %3d. %-8s -- %-8s  weight %s" % (i, name(cells, u), name(cells, v), "1" if w == 1.0 else "1.414214"))
    kw = total(ke)
    kh, kv, kd = count_types(ke, cells)
    out("Total MST weight : %.6f   (= %d horizontal + %d vertical + %d diagonal x sqrt2)" % (kw, kh, kv, kd))
    out("Connected components : %d  -> %s" % (dsu.components,
        "single MST" if dsu.components == 1 else "minimum spanning forest of %d trees" % dsu.components))
    out("")

    # ---------------- comparison
    def keyset(es):
        s = {}
        for w, u, v in es:
            a, b = (u, v) if u < v else (v, u)
            s[(a, b)] = True
        return s
    sp, sk = keyset(pe), keyset(ke)
    common = sum(1 for k in sp if k in sk)
    out("=" * 78); out("COMPARISON  Prim vs Kruskal"); out("=" * 78)
    out("                       Prim          Kruskal")
    out("edges selected       %8d      %8d" % (len(pe), len(ke)))
    out("total weight         %10.6f    %10.6f" % (pw, kw))
    out("1-weight edges       %8d      %8d" % (ph + pv, kh + kv))
    out("diagonal edges       %8d      %8d" % (pd, kd))
    out("components           %8d      %8d" % (len(pcomp), dsu.components))
    out("Same total weight   : %s" % ((pw - kw) < 1e-9 and (kw - pw) < 1e-9))
    out("Edges in common     : %d of %d  (the two trees differ on %d edges because many edges tie in weight;" % (common, len(pe), len(pe) - common))
    out("                       an MST is unique only when all weights are distinct, but its WEIGHT is always unique)")
    text = "\n".join(L)
    print(text)
    with open("outputs/q2_output.txt", "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
