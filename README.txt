DAA Assignment 4 (Fall 2026) - code package
===========================================
Student Name : Balaj
Roll Number  : 24f-0571
Course       : CS2009 Design and Analysis of Algorithms
Instructor   : Dr. Hashim Yasin
Institution  : FAST-NUCES Chiniot-Faisalabad Campus

Report Files
  DAA_A4_24f-0571_Balaj_Report.pdf   Official submission PDF report (15 pages)
  DAA_A4_24f-0571_Balaj_Report.html  Printable styled HTML report
  DAA_A4_24f-0571_Balaj_Report.md    Complete Markdown report source

Source Code & Assets
  grid.txt                Input grid (Figure 1) - format explained in grid_loader.py
  data_structures.py      Own Queue, Stack, MinHeap, merge sort, Disjoint-Set Union
  grid_loader.py          Reads grid.txt and builds the Grid object

  q1_robot_navigation.py  Q1: Graph modelling (Task 1), BFS (Task 2),
                              Iterative DFS (Task 3a), Recursive DFS (Task 3b)
                              State = (x, y, energy, destroyed-mask)
                              Includes Task 2 BFS discussion and Task 3 DFS discussion.

  q2_mst.py               Q2: Prim's algorithm (Task 1) and Kruskal's algorithm (Task 2)
                              on the undirected weighted MST graph.

  q3_analysis.py          Q3: Written time & space complexity analysis for
                              BFS, DFS (iterative & recursive), shortest-path
                              guarantee discussion, and Prim vs Kruskal comparison.

  q4_theory.py            Q4: Theoretical proofs -
                              (a) Any MST T can be produced by Kruskal with the
                                  right edge ordering (formal proof by induction).
                              (b) Fast Prim and Kruskal for bounded integer weights:
                                  bucket-queue Prim -> O(V+E),
                                  counting-sort Kruskal -> O(E+V) or O(E).

  run_all.py              Convenience runner: executes Q1, Q2, Q3, Q4 in sequence.

  outputs/
    q1_output.txt         Saved console output of q1_robot_navigation.py
    q2_output.txt         Saved console output of q2_mst.py
    q3_output.txt         Saved console output of q3_analysis.py
    q4_output.txt         Saved console output of q4_theory.py

Run individual questions
  python q1_robot_navigation.py grid.txt   -> prints results, writes outputs/q1_output.txt
  python q2_mst.py grid.txt                -> prints results, writes outputs/q2_output.txt
  python q3_analysis.py grid.txt           -> prints results, writes outputs/q3_output.txt
  python q4_theory.py                      -> prints results, writes outputs/q4_output.txt

Run all at once
  python run_all.py grid.txt               -> runs all four and writes all output files
  python visualizer.py grid.txt
Assignment Coverage
  Q1 Task 1 : Graph modelling, vertices/edges, permanent/destructible obstacles,
              state definition, directed vs undirected discussion         [10 marks]
  Q1 Task 2 : BFS implementation + minimum-cost path discussion          [15 marks]
  Q1 Task 3 : Iterative DFS (stack) + Recursive DFS + comparison        [15 marks]
  Q2 Task 1 : Prim's MST algorithm                                       [12 marks]
  Q2 Task 2 : Kruskal's MST algorithm + comparison with Prim             [13 marks]
  Q3        : Time & space complexity for BFS, DFS, MST algorithms       [20 marks]
  Q4(a)     : Proof that any MST can be produced by Kruskal               [7 marks]
  Q4(b)     : Fast Prim/Kruskal with bounded integer weights              [8 marks]
  TOTAL                                                                  [100 marks]
