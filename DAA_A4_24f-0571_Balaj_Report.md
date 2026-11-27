# National University of Computer & Emerging Sciences (FAST-NUCES)
### Chiniot-Faisalabad Campus — Department of Computer Science
### CS2009: Design and Analysis of Algorithms — Fall 2026
---
# ASSIGNMENT NO. 4 REPORT
## Intelligent Robot Navigation & Minimum Spanning Trees

**Student Name:** Balaj  
**Roll Number:** 24f-0571  
**Instructor:** Dr. Hashim Yasin  
**Submission Date:** 27 November 2026  
**Repository / Folder Name:** `DAA_A4_24f-0571_Balaj`  

---

## Executive Summary

This report documents the complete design, algorithmic formulation, implementation, empirical evaluation, and theoretical analysis for **Assignment 4: Intelligent Robot Navigation and Minimum Spanning Trees (MST)**. 

The assignment addresses two central algorithmic challenges on a $15 \times 15$ grid environment:
1. **Intelligent State-Space Search (BFS and DFS):** Guiding an energy-constrained robot from Start $(7, 1)$ to Goal $(15, 14)$ across permanent obstacles and destructible blue obstacles ($B, B+, B-$) with asymmetric movement costs, energy depletion, bonus gains, and negative edge weights.
2. **Minimum Spanning Tree Computation (Prim’s and Kruskal’s):** Transforming the grid into an undirected weighted graph to compute the optimal spanning tree connecting all accessible cells with zero cycles at minimal geometric weight.
3. **Comprehensive Complexity and Theoretical Proofs:** Formal asymptotic analysis of representations (adjacency matrix vs. adjacency list) and proofs regarding Kruskal tie-handling and linear-time MST construction with bounded integer weights.

In strict adherence to course guidelines, **no built-in or library data structures** (such as Python's `heapq`, `collections.deque`, `queue`, or `sorted()`) were used. All data structures—including a FIFO Queue, LIFO Stack, Binary Min-Heap, Disjoint-Set Union (DSU with union by rank and path compression), and Merge Sort—were built entirely from scratch.

---

## 1. Question 1: Intelligent Robot Navigation using BFS & DFS

### 1.1 Problem Formulation & Environment Overview

The navigation environment is defined on a $15 \times 15$ grid with coordinate convention $(1, 1)$ at the bottom-left and $(15, 15)$ at the top-right. The robot begins at $(7, 1)$ with $10$ initial energy units and must navigate to $(15, 14)$.

```
Coordinates: (1,1) = Bottom-Left, (15,15) = Top-Right
Start Position : (7, 1)   [Free cell]
Goal Position  : (15, 14)  [Free cell]
Grid Dimensions: 15 rows x 15 columns = 225 total cells
Total Walls    : 82 permanent orange obstacle cells (O)
Accessible Cells: 143 cells (free + blue destructibles)
Blue Obstacles : 15 cells (Normal B: 5, Bonus B+: 5, Penalty B-: 5)
```

#### Movement Rules & Step Costs
The robot can execute at most one step at a time from its current cell across six permitted directions:
* **Right:** $(+1, 0)$ with cost $+2$
* **Left:** $(-1, 0)$ with cost $-1$
* **Up:** $(0, +1)$ with cost $+2$
* **Down:** $(0, -1)$ with cost $-1$
* **Diagonally Up-Right:** $(+1, +1)$ with cost $+3$
* **Diagonally Up-Left:** $(-1, +1)$ with cost $-3$

*Note:* Downward diagonal movements (Down-Right and Down-Left) are strictly disallowed.

#### Destructible Obstacle Rules & Energy Constraints
1. Robot starts with $10$ energy units.
2. The robot cannot step directly onto an intact blue cell; it must **destroy** the obstacle from an adjacent accessible cell prior to entry.
3. Destroying any blue cell consumes **2 energy units** and incurs a **navigation cost of +5 units**.
4. Once destroyed, a blue obstacle permanently becomes an ordinary free cell and remains accessible for all subsequent movements.
5. **Bonus cells ($B+$):** Entering a bonus cell awards $+3$ energy units upon first entry.
6. **Penalty cells ($B-$):** Entering a penalty cell incurs an additional navigation cost of $+5$ units upon first entry.
7. Energy can never become negative; if remaining energy $< 2$, destruction cannot occur, rendering that intact blue cell impassable.
8. Each bonus or penalty effect applies **exactly once** per cell.

---

### 1.2 Task 1: Graph Modelling and State Representation

#### 1. Graph Representation of the Grid
The navigation grid cannot be modelled merely as a static 2D planar graph because the connectivity of the environment changes dynamically as obstacles are destroyed, and the legality of moves depends on available energy. We model the problem as a **Weighted Directed State-Space Graph** $\mathcal{G} = (\mathcal{S}, \mathcal{A}, c)$:
* $\mathcal{S}$: The set of all reachable robot states.
* $\mathcal{A}$: Directed transitions between valid states representing a move or a destruction followed by a move.
* $c$: The cost function $c: \mathcal{A} \rightarrow \mathbb{R}$, which can take positive, zero, or negative values.

#### 2. Identification of Vertices, Edges, and Movement Costs
* **Vertices:** Each vertex is a state tuple $s = (x, y, \text{energy}, \text{mask})$.
* **Edges:** A directed edge exists from state $s$ to state $s'$ if:
  1. $(x', y')$ is within grid boundaries ($1 \le x', y' \le 15$).
  2. $(x', y')$ is not a permanent orange obstacle ($O$).
  3. If $(x', y')$ is an intact blue cell, the robot has energy $\ge 2$ to destroy it.
* **Costs:** 
  $$\text{Edge Cost} = \text{Movement Cost} + (\text{Destruction Cost if intact: } 5) + (\text{Penalty Cost if } B-: 5)$$

#### 3. Representation of Permanent and Destructible Obstacles
* **Permanent Obstacles ($O$):** Excluded entirely from the vertex set. No directed edge enters an orange cell.
* **Destructible Obstacles ($B, B+, B-$):** Maintained via an indexed bitmask. An intact blue cell acts as a conditional barrier requiring an energy threshold of $2$. Once destroyed, its bit is set to $1$ in the bitmask, and it acts as an ordinary free cell carrying standard movement costs with no further energy deduction or bonus/penalty re-triggering.

#### 4. How the Graph Evolves Upon Destruction
Graph evolution is captured without mutating the underlying grid array by transitioning between **state-space layers**. The bitmask has $15$ bits (one per blue cell). Destruction transitions the robot from a state in layer $\text{mask}$ to a state in layer $\text{mask} \mid (1 \ll i)$. In this new layer, cell $i$ has incoming edges from all adjacent accessible cells with normal step costs, reflecting permanent accessibility.

#### 5. Directed vs. Undirected Nature of the Graph
The navigation graph is strictly **DIRECTED** for three fundamental reasons:
1. **Asymmetry of Movement Costs:** Reversing a move has an asymmetric cost. Moving Right has cost $+2$, but moving Left has cost $-1$. Moving Up has cost $+2$, but moving Down has cost $-1$. Moving Up-Right has cost $+3$, but its reverse is not even an allowed movement.
2. **Asymmetry of Movement Directions:** Permitted directions are $\{R, L, U, D, UR, UL\}$. Downward diagonal transitions ($DR, DL$) do not exist. Therefore, an edge $(x, y) \rightarrow (x+1, y+1)$ via $UR$ has no reciprocal edge $(x+1, y+1) \rightarrow (x, y)$.
3. **One-Way State Transitions:** Destroying an obstacle consumes energy and permanently alters the bitmask. This is an irreversible, strictly one-way state transition.

#### 6. Robot State Definition
A state is formally defined as:
$$s = (x, y, \text{energy}, \text{mask})$$
Where:
* $x \in \{1, \dots, 15\}$: Column coordinate.
* $y \in \{1, \dots, 15\}$: Row coordinate.
* $\text{energy} \in \{0, \dots, 10\}$: Current remaining energy units.
* $\text{mask} \in \{0, \dots, 2^{15}-1\}$: An integer bitmask where bit $i = 1$ indicates that the $i$-th blue obstacle has been destroyed.

*Deduplication Key:* Since energy is a deterministic function of the destroyed mask ($\text{energy} = 10 - 2 \cdot |\text{destroyed}| + 3 \cdot |\text{destroyed } B+|$) along any cycle-free path, visited state equality is uniquely determined by $(x, y, \text{mask})$.

---

### 1.3 Task 2: Breadth-First Search (BFS) Navigation

BFS explores the state space level-by-level using a FIFO queue.

```
--------------------------------------------------------------------------------
ALGORITHM 1: Breadth-First Search (FIFO Queue)
--------------------------------------------------------------------------------
Input : Robot start state s0 = (7, 1, 10, 0), Goal coordinate (15, 14)
Output: Optimal path in terms of edge hops, action sequence, cost, remaining energy
1: Queue Q <- empty; Visited <- empty set; Parent <- empty map
2: Q.enqueue(s0); Visited.add(key(s0)); Parent[key(s0)] <- null
3: while Q is not empty do
4:     s <- Q.dequeue()
5:     if (s.x, s.y) == Goal then return ReconstructPath(s, Parent)
6:     for each (s', step_cost, actions) in Robot.Successors(s) do
7:         if key(s') not in Visited then
8:             Visited.add(key(s'))
9:             Parent[key(s')] <- (s, step_cost, actions)
10:            Q.enqueue(s')
11: return Failure
--------------------------------------------------------------------------------
```

#### BFS Empirical Results
* **States Expanded (Traversal Length):** 984 states
* **Goal Reachability:** **YES** — reached at $(15, 14)$
* **Path Length:** **15 moves**
* **Total Navigation Cost:** **51 units**
* **Remaining Energy:** **6 units**
* **Blue Obstacles Destroyed (2):** $(9, 3)$ $[B]$ and $(11, 11)$ $[B-]$

#### Complete Reconstructed BFS Path
$$(7,1) \xrightarrow{\text{Up}} (7,2) \xrightarrow{\text{UR}} (8,3) \xrightarrow{\text{Destroy+Right}} (9,3) \xrightarrow{\text{UR}} (10,4) \xrightarrow{\text{Up}} (10,5) \xrightarrow{\text{Up}} (10,6) \xrightarrow{\text{Up}} (10,7) \xrightarrow{\text{Up}} (10,8) \xrightarrow{\text{Up}} (10,9) \xrightarrow{\text{Up}} (10,10) \xrightarrow{\text{Destroy+UR}} (11,11) \xrightarrow{\text{UR}} (12,12) \xrightarrow{\text{UR}} (13,13) \xrightarrow{\text{UR}} (14,14) \xrightarrow{\text{Right}} (15,14)$$

#### Step-by-Step Action Sequence (BFS)
```
 1. MOVE Up       to (7,2)   move cost +2                     [Energy: 10]
 2. MOVE Up-Right to (8,3)   move cost +3                     [Energy: 10]
 3. DESTROY (9,3) [B]        energy -2, cost +5               [Energy:  8]
 4. MOVE Right    to (9,3)   move cost +2                     [Energy:  8]
 5. MOVE Up-Right to (10,4)  move cost +3                     [Energy:  8]
 6. MOVE Up       to (10,5)  move cost +2                     [Energy:  8]
 7. MOVE Up       to (10,6)  move cost +2                     [Energy:  8]
 8. MOVE Up       to (10,7)  move cost +2                     [Energy:  8]
 9. MOVE Up       to (10,8)  move cost +2                     [Energy:  8]
10. MOVE Up       to (10,9)  move cost +2                     [Energy:  8]
11. MOVE Up       to (10,10) move cost +2                     [Energy:  8]
12. DESTROY (11,11) [B-]     energy -2, cost +5               [Energy:  6]
13. MOVE Up-Right to (11,11) move cost +3, penalty cost +5    [Energy:  6]
14. MOVE Up-Right to (12,12) move cost +3                     [Energy:  6]
15. MOVE Up-Right to (13,13) move cost +3                     [Energy:  6]
16. MOVE Up-Right to (14,14) move cost +3                     [Energy:  6]
17. MOVE Right    to (15,14) move cost +2                     [Energy:  6]
Total Navigation Cost = 2 + 3 + (5+2) + 3 + 2 + 2 + 2 + 2 + 2 + 2 + (5+3+5) + 3 + 3 + 3 + 2 = 51
```

#### Discussion: Does BFS Guarantee a Minimum-Cost Path?
**Answer: NO.** BFS guarantees the shortest path **only in terms of edge count (unweighted fewest hops)**, or when all edge weights are identical and positive. 

In this environment, BFS does not guarantee a minimum-cost path because:
1. **Asymmetric & Negative Edge Costs:** Edge costs vary from $-3$ to $+3$. A path with fewer hops can accumulate expensive positive edges, whereas a longer path utilizing negative edges (Left $-1$, Down $-1$, Up-Left $-3$) can achieve a lower total cost.
2. **Negative-Cost Cycles:** The graph contains directed cycles with negative net cost:
   $$\text{Up-Left } (-3) + \text{Right } (+2) + \text{Down } (-1) = -2$$
   Traversing this 3-cell loop returns the robot to the starting coordinate with a net cost reduction of $-2$. Because BFS ignores costs during frontier expansion, it fails to exploit cost-reducing transitions.
3. **Empirical Proof:** BFS found a 15-move path costing **51**. However, our DFS experiment with reverse successor ordering discovered a 78-move path costing only **34**. This conclusively proves that BFS does not minimize cost in this setting.

---

### 1.4 Task 3: Depth-First Search (DFS) Navigation

Two DFS implementations were developed:
* **(a) Iterative DFS:** Implemented with an explicit custom LIFO Stack. To ensure strict equivalence with recursive DFS, successor states are pushed in **reverse order** so that the first successor is popped and explored first. Marking occurs upon pop.
* **(b) Recursive DFS:** Implemented via recursive function calls using a dedicated large-stack worker thread (`threading.Thread` with 256MB stack) to prevent recursion limit overflows on large state graphs.

#### DFS Empirical Results
Both implementations produced **identical traversal orders and paths**:

| Metric | Iterative DFS (Stack) | Recursive DFS |
|---|:---:|:---:|
| **States Expanded** | 42 | 42 |
| **Goal Reachable** | YES | YES |
| **Path Moves** | 40 moves | 40 moves |
| **Total Navigation Cost** | 68 units | 68 units |
| **Remaining Energy** | 7 units | 7 units |
| **Blue Obstacles Destroyed** | 3: $(9,3), (13,11), (12,11)$ | 3: $(9,3), (13,11), (12,11)$ |
| **Identical Traversal Order** | **TRUE** | **TRUE** |
| **Identical Final Path** | **TRUE** | **TRUE** |

#### Complete Reconstructed DFS Path (40 moves)
$$(7,1) \rightarrow (6,1) \rightarrow (6,2) \rightarrow (7,2) \rightarrow (7,3) \rightarrow (8,3) \xrightarrow{\text{Destroy}} (9,3) \rightarrow (10,3) \rightarrow (10,4) \rightarrow (11,4) \rightarrow (12,4) \rightarrow (13,4) \rightarrow (14,4) \rightarrow (14,5) \rightarrow (13,5) \rightarrow (12,5) \rightarrow (11,5) \rightarrow (10,5) \rightarrow (10,6) \rightarrow (10,7) \rightarrow (10,8) \rightarrow (10,9) \rightarrow (9,9) \rightarrow (9,10) \rightarrow (10,10) \rightarrow (11,10) \rightarrow (12,10) \rightarrow (13,10) \xrightarrow{\text{Destroy}} (13,11) \xrightarrow{\text{Destroy}} (12,11) \rightarrow (13,11) \rightarrow (13,12) \rightarrow (14,12) \rightarrow (13,13) \rightarrow (12,13) \rightarrow (11,13) \rightarrow (11,14) \rightarrow (12,14) \rightarrow (13,14) \rightarrow (14,14) \rightarrow (15,14)$$

Energy calculation:
$$\text{Start (10)} - \text{Destroy }(9,3) [2] - \text{Destroy }(13,11) [2] + \text{Bonus }(13,11) [3] - \text{Destroy }(12,11) [2] = 7 \text{ units remaining}$$

#### Successor Ordering Experiment
To demonstrate the sensitivity of DFS to successor generation order, three ordering configurations were tested:

| Order Label | Successor Exploration Sequence | States Expanded | Moves | Total Cost | Final Energy |
|---|---|:---:|:---:|:---:|:---:|
| **Default** | Right, Left, Up, Down, Up-Right, Up-Left | 42 | 40 | 68 | 7 |
| **Goal-ward** | Up-Right, Up, Right, Up-Left, Left, Down | 43 | 42 | 75 | 4 |
| **Reverse** | Up-Left, Up-Right, Down, Up, Left, Right | 91 | 78 | **34** | 4 |

#### Discussion: Why DFS Does Not Produce an Optimal Path
DFS operates on a **greedy commitment** paradigm: it follows a single branch until it either hits a dead-end or discovers the goal. Once the goal is encountered, search terminates immediately.
1. **Lack of Cost Consideration:** DFS does not evaluate edge weights or accumulated path costs. It returns the *first discovered path*, which depends entirely on arbitrary tie-breaking and successor ordering.
2. **Successor Ordering Impact:** When configured with the Goal-ward heuristic, DFS rapidly plunges toward the top-right, incurring high positive move costs ($+3, +2$), yielding a path cost of $75$. Conversely, Reverse order prioritizes Up-Left ($-3$) and Down ($-1$), wandering through $78$ moves but driving the net cost down to $34$.
3. **No Backtracking for Optimality:** Without exhaustive exploration of all paths (which would require exponential time $O(b^d)$) or branch-and-bound pruning, DFS cannot guarantee optimality in any weighted environment.

---

## 2. Question 2: Intelligent Robot Navigation using Prim’s and Kruskal’s Algorithms

### 2.1 MST Problem Formulation & Graph Construction

To compute Minimum Spanning Trees (MST), the directional, asymmetric navigation graph is transformed into an **undirected, weighted graph** under the following rules:
* **Vertices ($V$):** Every non-permanent cell represents a vertex. All blue obstacles ($B, B+, B-$) are treated as accessible free cells. Permanent orange obstacles ($O$) are excluded.
  $$|V| = 225 - 82 = 143 \text{ vertices}$$
* **Edges ($E$):** An undirected edge connects two cells if they are adjacent under at least one permitted movement direction, ignoring direction. Because horizontal ($R, L$), vertical ($U, D$), and diagonal ($UR, UL$) directions are permitted, every non-wall cell connects to its horizontal, vertical, and both diagonal neighbors.
* **Weights:**
  * Horizontal connections: $w = 1.0$
  * Vertical connections: $w = 1.0$
  * Diagonal connections: $w = \sqrt{2} \approx 1.414214$
* Total candidate edges considered: **343 undirected edges** (96 Horizontal, 102 Vertical, 145 Diagonal).

---

### 2.2 Task 1: Prim’s Algorithm

Prim’s algorithm builds the MST by greedily attaching the minimum-weight edge connecting a vertex in the growing tree to a vertex outside the tree, utilizing our custom binary `MinHeap`.

```
--------------------------------------------------------------------------------
ALGORITHM 2: Prim's MST with Minimum Spanning Forest Handling
--------------------------------------------------------------------------------
Input : Graph G = (V, E) with adjacency lists, |V| = n
Output: Selected edges forming MST or Minimum Spanning Forest (MSF)
1: in_tree <- array of False of size n; chosen_edges <- empty list; components <- empty list
2: for root = 0 to n - 1 do
3:     if in_tree[root] then continue
4:     heap <- MinHeap(); in_tree[root] <- True; comp_size <- 1
5:     for each (v, w) in Adj[root] do heap.push(w, (root, v))
6:     while heap is not empty do
7:         w, (u, v) <- heap.pop_min()
8:         if in_tree[v] then continue
9:         in_tree[v] <- True; comp_size <- comp_size + 1
10:        chosen_edges.append((w, u, v))
11:        for each (x, wx) in Adj[v] do
12:            if not in_tree[x] then heap.push(wx, (v, x))
13:    components.append((root, comp_size))
14: return chosen_edges, components
--------------------------------------------------------------------------------
```

#### Prim’s Empirical Results
* **Vertices Included:** 143
* **Edges Selected:** Exactly $142$ edges ($|V| - 1 = 143 - 1 = 142$)
* **Total MST Weight:** **142.000000**
* **Edge Breakdown:**
  * Horizontal edges ($w = 1.0$): **74**
  * Vertical edges ($w = 1.0$): **68**
  * Diagonal edges ($w = \sqrt{2}$): **0**
* **Connected Component Determination:**
  * **Result:** Exactly **1 connected component** containing all $143$ vertices.
  * The graph is **fully connected**; the algorithm produces a single MST without needing a disconnected forest.

---

### 2.3 Task 2: Kruskal’s Algorithm

Kruskal’s algorithm sorts all $343$ edges in ascending order using custom stable `merge_sort` and repeatedly incorporates edges that connect distinct components using a Disjoint-Set Union (`DSU`) data structure with path compression and union by rank.

```
--------------------------------------------------------------------------------
ALGORITHM 3: Kruskal's MST (Merge Sort + DSU)
--------------------------------------------------------------------------------
Input : Graph G = (V, E), edge list
Output: Selected MST edges, final forest components
1: sorted_edges <- merge_sort(E, key = weight)
2: dsu <- DSU(n = |V|)
3: chosen_edges <- empty list
4: for each (w, u, v) in sorted_edges do
5:     if dsu.union(u, v) == True then       # True iff u and v were in different sets
6:         chosen_edges.append((w, u, v))
7:         if len(chosen_edges) == |V| - 1 then break
8: return chosen_edges, dsu.components
--------------------------------------------------------------------------------
```

#### Kruskal’s Empirical Results
* **Total Edges Processed:** 343 edges (198 edges with weight $1.0$, 145 edges with weight $\sqrt{2}$).
* **Edges Selected:** Exactly $142$ edges.
* **Total MST Weight:** **142.000000**
* **Edge Breakdown:**
  * Horizontal edges ($w = 1.0$): **40**
  * Vertical edges ($w = 1.0$): **102**
  * Diagonal edges ($w = \sqrt{2}$): **0**
* **Final Components:** 1 (Single MST).

---

### 2.4 Comparative Analysis: Prim vs. Kruskal

| Comparison Metric | Prim’s Algorithm | Kruskal’s Algorithm | Match / Status |
|---|:---:|:---:|:---:|
| **Total Edges Selected** | 142 | 142 | **Identical** ($|V|-1$) |
| **Total Tree Weight** | **142.000000** | **142.000000** | **Identical** ($\Delta = 0$) |
| **Edges of Weight 1.0** | 142 | 142 | **Identical** |
| **Edges of Weight $\sqrt{2}$** | 0 | 0 | **Identical** |
| **Connected Components** | 1 (Single MST) | 1 (Single MST) | **Identical** |
| **Common Edges Shared** | 103 of 142 | 103 of 142 | 72.5% overlap |
| **Differing Edges** | 39 | 39 | Valid alternative MSTs |

#### Discussion on Differing Edges
While both algorithms produce the **exact same optimal weight (142.000000)**, the individual edges selected differ on $39$ edges. 

*Theoretical Justification:* An MST is **unique if and only if all edge weights in the graph are distinct**. In this grid, there are 198 horizontal/vertical edges that all tie at weight $1.0$. 
* Prim grows a single local tree outward from vertex $(1,1)$, breaking ties based on neighbor adjacency discovery order.
* Kruskal sorts all edges globally via `merge_sort` and processes them in coordinate index order across the entire grid.

Both edge sets form valid, spanning, cycle-free trees of minimal weight, providing empirical confirmation of the Cut and Cycle properties of MSTs.

---

## 3. Question 3: Time & Space Complexity Analysis

Let $V$ denote the number of accessible vertices ($|V| = 143$) and $E$ the number of edges.

### 3.1 BFS Complexity Analysis [5 Marks]

BFS visits each vertex once and traverses each outgoing edge once.

| Representation | Time Complexity | Space Complexity | Analytical Justification |
|---|:---:|:---:|---|
| **Adjacency Matrix** | $\mathcal{O}(V^2)$ | $\mathcal{O}(V^2)$ | **Time:** To find neighbors of vertex $u$, BFS must scan row $u$ of length $V$. For $V$ vertices: $V \times \mathcal{O}(V) = \mathcal{O}(V^2)$.<br>**Space:** Dominated by the $V \times V$ matrix $\mathcal{O}(V^2)$; queue and visited sets require $\mathcal{O}(V)$. |
| **Adjacency List** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V + E)$ | **Time:** Vertex dequeued once $\mathcal{O}(V)$; each outgoing edge inspected once across all lists $\mathcal{O}(E)$. For sparse grids ($E \le 6V$), $\mathcal{O}(V+E) = \mathcal{O}(V)$.<br>**Space:** Lists store $V$ headers and $2E$ nodes $\mathcal{O}(V+E)$. |

---

### 3.2 DFS Complexity Analysis [5 Marks]

Both Iterative (Stack) and Recursive DFS exhibit identical asymptotic bounds:

| Representation | Time (Iterative) | Time (Recursive) | Space (Iterative) | Space (Recursive) |
|---|:---:|:---:|:---:|:---:|
| **Adjacency Matrix** | $\mathcal{O}(V^2)$ | $\mathcal{O}(V^2)$ | $\mathcal{O}(V^2)$ | $\mathcal{O}(V^2)$ |
| **Adjacency List** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V + E)$ | $\mathcal{O}(V + E)$ | $\mathcal{O}(V + E)$ |

#### Justification
* **Adjacency Matrix:** Finding unvisited neighbors requires scanning an entire row of length $V$ for each vertex $\rightarrow \mathcal{O}(V^2)$ time. Space is $\mathcal{O}(V^2)$ for the matrix storage.
* **Adjacency List:** Every vertex and incident edge is explored once $\rightarrow \mathcal{O}(V + E)$ time. Space requires $\mathcal{O}(V + E)$ for adjacency storage.
* **Auxiliary Memory Difference:**
  * Iterative DFS uses an explicit heap-allocated `Stack` of maximum depth $V \rightarrow \mathcal{O}(V)$.
  * Recursive DFS uses OS call-stack frames of maximum depth $V \rightarrow \mathcal{O}(V)$. In environments with limited stack sizes (e.g. Python default of 1,000 frames), deep recursion risks `RecursionError` unless execution is isolated in a thread with expanded stack memory.

---

### 3.3 Shortest-Path Guarantee [5 Marks]

**Question:** *Which of BFS and DFS guarantees a shortest path in the given robot navigation environment? Explain by considering movement and obstacle-related costs.*

#### Rigorous Answer: NEITHER BFS NOR DFS GUARANTEES A MINIMUM-COST PATH.

1. **Failure of BFS for Cost Minimization:**
   * BFS guarantees the shortest path **strictly in terms of the number of edges (unweighted hop count)**.
   * If edge weights are positive and uniform, fewest hops equals lowest cost.
   * In this environment, costs are **heterogeneous and asymmetric** (ranging from $-3$ for Up-Left to $+3$ for Up-Right, plus $+5$ destruction and penalty fees).
   * Most critically, the directed graph contains **negative-cost cycles**:
     $$\text{Up-Left } (-3) + \text{Right } (+2) + \text{Down } (-1) = -2$$
   * In a graph with negative cycles, a minimum-cost walk is **unbounded below ($-\infty$)** because traversing the loop repeatedly reduces total cost indefinitely. For simple paths (no repeated vertices), the problem is NP-hard. BFS does not evaluate edge weights and thus cannot minimize cost.

2. **Failure of DFS for Cost Minimization:**
   * DFS commits to the first path leading to the goal along its search branch.
   * As demonstrated in our experiments, changing successor ordering alters path cost from $34$ to $75$ on the identical grid. DFS provides zero optimality guarantees.

3. **Algorithm that WOULD Guarantee Shortest Path:**
   * For non-negative weighted graphs: **Dijkstra’s Algorithm** with a priority queue in $\mathcal{O}((V + E) \log V)$.
   * For general graphs with negative edges but NO negative cycles: **Bellman-Ford Algorithm** in $\mathcal{O}(V \cdot E)$.

---

### 3.4 Minimum Spanning Tree Complexity Comparison [5 Marks]

| Algorithm | Representation | Time Complexity | Space Complexity | Optimal Graph Type |
|---|---|:---:|:---:|---|
| **Prim’s** | Adjacency Matrix | $\mathcal{O}(V^2)$ | $\mathcal{O}(V^2)$ | Dense graphs ($E \approx V^2$) |
| **Prim’s** | Adjacency List + Binary Heap | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}(V + E)$ | Sparse graphs ($E \ll V^2$) |
| **Kruskal’s** | Adjacency Matrix | $\mathcal{O}(V^2 \log V)$ | $\mathcal{O}(V^2)$ | Inefficient (must extract edges first) |
| **Kruskal’s** | Adjacency List + DSU | $\mathcal{O}(E \log E)$ | $\mathcal{O}(V + E)$ | Sparse graphs / Edge lists |

#### Comparative Discussion
* On our planar grid, $E \le 4V$, making the graph **sparse**.
* With adjacency lists, Kruskal’s time is $\mathcal{O}(E \log E) \approx \mathcal{O}(V \log V)$, and Prim’s time is $\mathcal{O}(E \log V) \approx \mathcal{O}(V \log V)$. Both run in practically identical, near-linear time.
* Prim grows a localized tree and is simpler when vertices are known in advance. Kruskal processes independent edges globally and naturally constructs Minimum Spanning Forests for disconnected graphs without extra restart logic.

---

## 4. Question 4: Prim’s & Kruskal’s Theoretical Proofs

### 4.1 Kruskal’s Algorithm Tie-Handling Proof [7 Marks]

#### Theorem
*Let $G = (V, E, w)$ be a connected, weighted, undirected graph, and let $T$ be an arbitrary Minimum Spanning Tree of $G$. Then there exists an ordering of the edges of $G$ such that Kruskal’s algorithm, when processing edges in this order, outputs exactly $T$.*

#### Formal Inductive Proof
1. **Partition by Weight:**
   Let the distinct edge weights in $G$ be $w_1 < w_2 < \dots < w_k$.
   Partition the entire edge set $E$ into equivalence classes by weight:
   $$E_i = \{e \in E \mid w(e) = w_i\}$$
   Similarly, let $T_i = T \cap E_i$ be the set of edges in $T$ having weight $w_i$.

2. **Construction of Ordering $\sigma$:**
   Construct a total ordering $\sigma$ of $E$ adhering to non-decreasing weights:
   * For each weight class $E_i$, arrange the edges such that all edges belonging to $T_i$ appear **strictly before** all edges in $E_i \setminus T_i$.
   * Concatenate these ordered classes:
     $$\sigma = \big( \text{edges in } T_1, \; E_1 \setminus T_1, \; \text{edges in } T_2, \; E_2 \setminus T_2, \; \dots, \; \text{edges in } T_k, \; E_k \setminus T_k \big)$$

3. **Inductive Hypothesis:**
   *Claim:* After Kruskal’s algorithm finishes processing all edges of weight $\le w_i$, the set of edges accepted by Kruskal is exactly:
   $$\bigcup_{j=1}^i T_j$$

4. **Base Case ($i = 0$):**
   Before processing any edges, Kruskal’s accepted edge set is $\emptyset$, matching the base set.

5. **Inductive Step:**
   Assume the claim holds for weight class $w_{i-1}$. That is, the current forest maintained by the Disjoint-Set Union (DSU) structure consists exactly of the edges $T_1 \cup \dots \cup T_{i-1}$.
   Now Kruskal processes edges of weight $w_i$:
   
   * **Phase A (Edges in $T_i$):**
     Let $e = (u, v) \in T_i$. 
     Suppose for contradiction that $u$ and $v$ are already in the same connected component of the DSU. That would imply there exists a path between $u$ and $v$ using only edges from $T_1 \cup \dots \cup T_{i-1} \subseteq T$. But adding $e \in T$ would form a cycle in $T$, violating the fact that $T$ is a tree.
     Therefore, $u$ and $v$ must belong to distinct components:
     $$\text{DSU.find}(u) \neq \text{DSU.find}(v)$$
     Hence, Kruskal **must accept** every edge $e \in T_i$.

   * **Phase B (Edges in $E_i \setminus T_i$):**
     Let $e' = (x, y) \in E_i \setminus T_i$.
     Since $T$ is a spanning tree, adding $e'$ to $T$ produces a unique fundamental cycle $C$.
     Because $T$ is an MST, no edge on $C$ can have a weight strictly greater than $w(e') = w_i$ (by the Cycle Property of MSTs).
     Thus, all edges on cycle $C$ belong to $T$ and have weight $\le w_i$.
     All such edges ($T_1 \cup \dots \cup T_i$) have already been accepted by Kruskal in earlier steps and Phase A.
     Consequently, $x$ and $y$ are already connected in the DSU forest.
     Therefore, Kruskal **must reject** every edge $e' \in E_i \setminus T_i$.

6. **Conclusion:**
   By mathematical induction, the invariant holds across all $k$ weight classes. The total set of edges accepted by Kruskal is:
   $$\bigcup_{i=1}^k T_i = T$$
   Thus, Kruskal’s algorithm outputs exactly $T$. $\blacksquare$

---

### 4.2 Fast MST Algorithms with Bounded Integer Weights [8 Marks]

Standard comparison-based sorting incurs an $\Omega(E \log E)$ lower bound. However, when edge weights are bounded integers, non-comparison methods and specialized priority queues allow significant acceleration.

#### (i) Prim’s Algorithm with Bounded Integer Weights

##### Case 1: Weights are integers in $\{1, 2, \dots, |V|\}$
* **Data Structure:** **Dial’s Algorithm (Bucket Queue)**.
  We maintain an array of buckets numbered $0$ to $|V|$, where bucket $k$ contains a doubly-linked list of vertices whose current minimum cut edge weight is $k$.
* **Operations:**
  * `decrease_key`: Moving a vertex to a smaller bucket index takes $\mathcal{O}(1)$ time.
  * `extract_min`: Scanned sequentially. Since edge weights are bounded by $|V|$, the minimum pointer only advances monotonically forward, scanning at most $|V|$ empty buckets across the entire execution.
* **Running Time:**
  $$\mathcal{O}(V + E + |V|) = \mathcal{O}(V + E)$$
* *Alternative:* Using a **Van Emde Boas (vEB) tree** yields $\mathcal{O}((V + E) \log \log V)$.

##### Case 2: Weights are integers in $\{1, 2, \dots, W\}$ for constant $W$
* Dial’s bucket queue contains only $W$ buckets.
* Bucket pointer wrap-around occurs in $\mathcal{O}(W) = \mathcal{O}(1)$ time.
* **Running Time:**
  $$\mathcal{O}(V + E + W) = \mathcal{O}(V + E)$$

---

#### (ii) Kruskal’s Algorithm with Bounded Integer Weights

The asymptotic bottleneck in Kruskal’s algorithm is sorting the edges.

##### Case 1: Weights are integers in $\{1, 2, \dots, |V|\}$
* **Edge Sorting:** Instead of comparison sort, use **Counting Sort**.
  With $|V|$ buckets and $E$ edges, Counting Sort runs in:
  $$\mathcal{O}(E + |V|) \text{ time and } \mathcal{O}(E + |V|) \text{ space}$$
* **DSU Operations:** Processing $E$ union-find operations with path compression and rank takes:
  $$\mathcal{O}(E \cdot \alpha(V)) \text{ time}$$
* **Total Running Time:**
  $$\mathcal{O}(E + V + E \cdot \alpha(V)) = \mathcal{O}(E \cdot \alpha(V) + V) \approx \mathcal{O}(V + E)$$
  *(Since $\alpha(V) \le 4$ for all practical input sizes, this is essentially linear time).*

##### Case 2: Weights are integers in $\{1, 2, \dots, W\}$ for constant $W$
* Counting Sort requires $W$ counters:
  $$\mathcal{O}(E + W) = \mathcal{O}(E) \text{ time}$$
* **Total Running Time:**
  $$\mathcal{O}(E \cdot \alpha(V)) \approx \mathcal{O}(E)$$
  This matches the theoretical lower bound, as inspecting every edge requires $\Omega(E)$ time.

---

## 5. System Architecture & Custom Data Structures

Course guidelines strictly prohibit built-in algorithmic libraries. All data structures were designed from first principles in [data_structures.py](file:///d:/Documents/Algo_complete%20material/Assignment-5/DAA_A4_RollNo_FirstName/data_structures.py):

```
+-------------------------------------------------------------------------------+
|                        CUSTOM DATA STRUCTURES ARCHITECTURE                    |
+-------------------------------------------------------------------------------+
|  Module               Class / Function   Underlying Design     Complexity     |
|---------------------+------------------+---------------------+----------------|
| data_structures.py  | Queue            | Array + Head Pointer| O(1) ops       |
| data_structures.py  | Stack            | Dynamic Array LIFO  | O(1) push/pop  |
| data_structures.py  | MinHeap          | Binary Heap Array   | O(log n)       |
| data_structures.py  | merge_sort       | Stable Merge Sort   | O(n log n)     |
| data_structures.py  | DSU              | Rank + Compression  | O(alpha(n))    |
+-------------------------------------------------------------------------------+
```

1. **`Queue`:** Implemented with an array and a moving head index (`_head`). Dequeue advances the index in $\mathcal{O}(1)$ time without $\mathcal{O}(n)$ list-shifting penalties.
2. **`Stack`:** Implemented with dynamic list append and pop in $\mathcal{O}(1)$ time.
3. **`MinHeap`:** Binary min-heap storing `(key, payload)` pairs with standard bubble-up and bubble-down routines for Prim's priority queue.
4. **`merge_sort`:** Stable divide-and-conquer sorting algorithm ensuring predictable tie-handling for Kruskal's edge ordering.
5. **`DSU`:** Disjoint-Set Union with path compression (`parent[x] = find(parent[x])`) and union by rank, reducing amortized operation time to inverse Ackermann $\mathcal{O}(\alpha(n))$.

---

## 6. Discussion, Comments, and Conclusion

### 6.1 Critical Observations & Comments
* **The Interplay of Energy and Graph Traversal:** In standard grid pathfinding, visiting the same $(x, y)$ coordinate multiple times indicates a cycle. However, in this problem, revisiting an $(x, y)$ cell with a different destroyed bitmask is often necessary to backtrack, collect bonuses, or circumvent walls.
* **Negative-Cost Cycles in Navigation:** The presence of $UL(-3) + R(+2) + D(-1) = -2$ demonstrates why shortest-path problems with negative cycles are unbounded unless constrained to simple paths.
* **Tie-Breaking in MST:** Both Prim’s and Kruskal’s algorithms found identical MST weights ($142.000$) but differed in edge choices ($103$ shared out of $142$). This empirical result provides practical validation for the cycle-cut theorem and theoretical proof derived in Question 4(a).

### 6.2 Conclusion
All requirements of Assignment 4 have been successfully satisfied:
1. **Graph Modelling:** The grid is fully formulated as a dynamic, directed state-space graph with complete state tuples $(x, y, \text{energy}, \text{mask})$.
2. **Search Algorithms:** BFS and both DFS variants (iterative stack and recursive) were implemented, producing concrete paths, traversal sequences, and energy calculations.
3. **MST Computation:** Both Prim's and Kruskal's algorithms were implemented from first principles, successfully identifying a single connected MST of weight $142.000000$.
4. **Complexity & Theory:** Comprehensive complexity comparisons across adjacency matrix and list models, along with formal mathematical proofs for Kruskal tie-handling and linear-time bounded MST algorithms, were derived and documented.
5. **Interactive Visualization:** An interactive web frontend was developed to visually animate and verify the results on screen.

---
*Report prepared by Balaj (Roll No: 24f-0571) for CS2009 Design and Analysis of Algorithms, FAST-NUCES Chiniot-Faisalabad Campus.*
