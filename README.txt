DAA Assignment 4 (Fall 2026) - code package
===========================================
Requires only Python 3 (no third-party libraries).

Files
  grid.txt                input grid (Figure 1) - format explained in grid_loader.py
  data_structures.py      own Queue, Stack, MinHeap, merge sort, Disjoint-Set Union
  grid_loader.py          reads grid.txt
  q1_robot_navigation.py  Q1: BFS, iterative DFS, recursive DFS  (state = x, y, energy, destroyed-mask)
  q2_mst.py               Q2: Prim and Kruskal on the undirected MST graph
  outputs/                saved console output of both programs

Run
  python3 q1_robot_navigation.py grid.txt     -> prints results and writes outputs/q1_output.txt
  python3 q2_mst.py grid.txt                  -> prints results and writes outputs/q2_output.txt
