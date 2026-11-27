"""
run_all.py  -  Convenience runner for all four questions.
CS2009 Design and Analysis of Algorithms  -  Assignment 4

Usage:
    python run_all.py [grid.txt]

Runs Q1, Q2, Q3, Q4 in sequence and saves output files:
    outputs/q1_output.txt
    outputs/q2_output.txt
    outputs/q3_output.txt
    outputs/q4_output.txt
"""

import sys
import os
import threading

def run_q1(grid_path):
    """Run Q1 robot navigation (BFS + DFS) in a large-stack thread."""
    import q1_robot_navigation as q1
    # patch argv so q1.main() uses the correct grid path
    orig = sys.argv[:]
    sys.argv = ["q1_robot_navigation.py", grid_path]
    sys.setrecursionlimit(100_000)
    for mb in (256, 128, 64, 32, 16):
        try:
            threading.stack_size(mb * 1024 * 1024)
            break
        except (ValueError, RuntimeError):
            continue
    t = threading.Thread(target=q1.main)
    t.start()
    t.join()
    sys.argv = orig

def run_q2(grid_path):
    import q2_mst as q2
    orig = sys.argv[:]
    sys.argv = ["q2_mst.py", grid_path]
    q2.main()
    sys.argv = orig

def run_q3(grid_path):
    import q3_analysis as q3
    orig = sys.argv[:]
    sys.argv = ["q3_analysis.py", grid_path]
    q3.main()
    sys.argv = orig

def run_q4():
    import q4_theory as q4
    q4.main()

def main():
    grid_path = sys.argv[1] if len(sys.argv) > 1 else "grid.txt"
    os.makedirs("outputs", exist_ok=True)

    print("\n" + "=" * 78)
    print("RUNNING Q1 : Robot Navigation  (BFS + Iterative DFS + Recursive DFS)")
    print("=" * 78 + "\n")
    run_q1(grid_path)

    print("\n" + "=" * 78)
    print("RUNNING Q2 : MST  (Prim + Kruskal)")
    print("=" * 78 + "\n")
    run_q2(grid_path)

    print("\n" + "=" * 78)
    print("RUNNING Q3 : Time & Space Complexity Analysis")
    print("=" * 78 + "\n")
    run_q3(grid_path)

    print("\n" + "=" * 78)
    print("RUNNING Q4 : Theoretical Proofs")
    print("=" * 78 + "\n")
    run_q4()

    print("\n" + "=" * 78)
    print("ALL DONE.  Output files written to outputs/ directory.")
    print("=" * 78 + "\n")

if __name__ == "__main__":
    main()
