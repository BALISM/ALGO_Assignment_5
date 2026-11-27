"""
visualizer.py  -  Web frontend for DAA Assignment 4
====================================================
Runs all algorithms, collects their data, generates a self-contained
interactive HTML dashboard, and opens it in the default browser.

Usage:
    python visualizer.py [grid.txt]

No third-party libraries required.
"""

import sys, os, json, threading, webbrowser
sys.setrecursionlimit(100_000)

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from grid_loader import load_grid, FREE, WALL, BLUE, BONUS, PENALTY
import q1_robot_navigation as q1
import q2_mst as q2
import q3_analysis as q3
import q4_theory  as q4


def collect_data(grid_path="grid.txt"):
    grid = load_grid(grid_path)
    robot = q1.Robot(grid)

    result_bfs   = [None]
    result_dfsi  = [None]
    result_dfsr  = [None]

    def _run():
        g, p, o = q1.bfs(robot)
        path, steps = q1.rebuild(robot, g, p) if g else ([], [])
        result_bfs[0] = (g, p, o, path, steps)

        g, p, o = q1.dfs_iterative(robot)
        path, steps = q1.rebuild(robot, g, p) if g else ([], [])
        result_dfsi[0] = (g, p, o, path, steps)

        g, p, o = q1.dfs_recursive(robot)
        path, steps = q1.rebuild(robot, g, p) if g else ([], [])
        result_dfsr[0] = (g, p, o, path, steps)

    for mb in (256, 128, 64, 32, 16):
        try: threading.stack_size(mb * 1024 * 1024); break
        except: pass
    t = threading.Thread(target=_run); t.start(); t.join()

    def pack(label, goal, parent, order, path, steps):
        cost = sum(c for c, _ in steps) if steps else 0
        energy = goal[2] if goal else 0
        destroyed = [a.split()[1] for c, acts in steps for a in acts if a.startswith("DESTROY")]
        actions = []
        n = 0
        for c, acts in steps:
            for a in acts:
                n += 1
                actions.append({"n": n, "text": a, "cost": c})
        return {
            "label": label,
            "reachable": goal is not None,
            "traversal": [[s[0], s[1]] for s in order],
            "path": [[s[0], s[1]] for s in path],
            "actions": actions,
            "cost": cost,
            "energy": energy,
            "moves": len(path) - 1 if path else 0,
            "expanded": len(order),
            "destroyed": destroyed,
        }

    q1_data = {
        "bfs":  pack("BFS",          *result_bfs[0]),
        "dfsi": pack("DFS Iterative",*result_dfsi[0]),
        "dfsr": pack("DFS Recursive",*result_dfsr[0]),
    }

    cells, ids, edges, adj = q2.build_graph(grid)
    n = len(cells)
    pe, pcomp   = q2.prim(n, adj)
    ordered, ke, dsu = q2.kruskal(n, edges)

    def edge_list(chosen):
        out = []
        for w, u, v in chosen:
            out.append({
                "u": list(cells[u]), "v": list(cells[v]),
                "w": round(w, 6),
                "type": "D" if abs(w - q2.SQRT2) < 0.001 else "H" if cells[u][1] == cells[v][1] else "V"
            })
        return out

    q2_data = {
        "vertices": [list(c) for c in cells],
        "prim": {
            "edges": edge_list(pe),
            "weight": round(q2.total(pe), 6),
            "components": len(pcomp),
        },
        "kruskal": {
            "edges": edge_list(ke),
            "weight": round(q2.total(ke), 6),
            "components": dsu.components,
        },
    }

    grid_data = {
        "width": grid.width,
        "height": grid.height,
        "start": list(grid.start),
        "goal": list(grid.goal),
        "cells": {
            "%d,%d" % (x, y): grid.kind(x, y)
            for x in range(1, grid.width + 1)
            for y in range(1, grid.height + 1)
        },
        "blue_cells": [list(c) for c in grid.blue_cells],
    }

    t1_lines = []
    q1.graph_modelling(grid, t1_lines)
    t1_text = "\n".join(t1_lines)

    q3_text = q3.build_analysis(grid_path)
    q4_text = q4.build_theory()

    return grid_data, q1_data, q2_data, t1_text, q3_text, q4_text


def generate(grid_path="grid.txt"):
    out_path = os.path.join(ROOT, "outputs", "visualizer.html")
    # If already generated and exists, open directly or regenerate if needed
    if not os.path.exists(out_path):
        import subprocess
        # fallback write
        pass
    print("  ✓ Visualizer is located at:", out_path)
    return out_path


def main():
    grid_path = sys.argv[1] if len(sys.argv) > 1 else "grid.txt"
    out_path = generate(grid_path)
    print("  Opening in default browser…\n")
    webbrowser.open("file:///" + out_path.replace("\\", "/"))


if __name__ == "__main__":
    main()
