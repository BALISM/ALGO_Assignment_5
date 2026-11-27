"""
visualizer.py  -  Web frontend for DAA Assignment 4
====================================================
Runs all algorithms, collects their data, generates a self-contained
interactive HTML dashboard, and opens it in the default browser.

Usage:
    python visualizer.py [grid.txt]

No third-party libraries required.  Uses only:
    - Python standard library (json, webbrowser, os, sys, threading)
    - The project's own modules (grid_loader, q1_robot_navigation, q2_mst,
      q3_analysis, q4_theory)
"""

import sys, os, json, threading, webbrowser
sys.setrecursionlimit(100_000)

# ── locate project root ───────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from grid_loader import load_grid, FREE, WALL, BLUE, BONUS, PENALTY
import q1_robot_navigation as q1
import q2_mst as q2
import q3_analysis as q3
import q4_theory  as q4


# ── run all algorithms and collect data ───────────────────────────────────────
def collect_data(grid_path="grid.txt"):
    grid = load_grid(grid_path)
    robot = q1.Robot(grid)

    # ---------- Q1 ----------
    def run_bfs():
        g, p, o = q1.bfs(robot)
        path, steps = q1.rebuild(robot, g, p) if g else ([], [])
        return g, p, o, path, steps

    def run_dfs_iter():
        g, p, o = q1.dfs_iterative(robot)
        path, steps = q1.rebuild(robot, g, p) if g else ([], [])
        return g, p, o, path, steps

    result_bfs   = [None]
    result_dfsi  = [None]
    result_dfsr  = [None]

    def _run():
        result_bfs[0]  = run_bfs()
        result_dfsi[0] = run_dfs_iter()
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

    # ---------- Q2 ----------
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

    # ---------- Grid ----------
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

    # ---------- Q3 / Q4 text ----------
    q3_text = q3.build_analysis(grid_path)
    q4_text = q4.build_theory()

    return grid_data, q1_data, q2_data, q3_text, q4_text


# ── HTML template ─────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>DAA Assignment 4 — Robot Navigation Visualizer</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0f1117;color:#e2e8f0;min-height:100vh}

/* ── top bar ── */
.topbar{background:linear-gradient(135deg,#1e293b,#0f172a);border-bottom:1px solid #334155;
        padding:14px 24px;display:flex;align-items:center;gap:16px}
.topbar h1{font-size:1.3rem;font-weight:700;background:linear-gradient(90deg,#60a5fa,#a78bfa);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.topbar .sub{font-size:.8rem;color:#64748b}

/* ── tabs ── */
.tabs{display:flex;gap:4px;padding:12px 24px 0;background:#0f1117;border-bottom:1px solid #1e293b;flex-wrap:wrap}
.tab{padding:8px 18px;border-radius:8px 8px 0 0;cursor:pointer;font-size:.82rem;font-weight:600;
     background:#1e293b;color:#94a3b8;border:1px solid #334155;border-bottom:none;transition:.15s}
.tab.active{background:#1d4ed8;color:#fff;border-color:#3b82f6}
.tab:hover:not(.active){background:#334155;color:#e2e8f0}

/* ── main layout ── */
.content{display:none;padding:20px 24px;gap:20px;animation:fadeIn .2s}
.content.active{display:flex;flex-wrap:wrap}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}

/* ── cards ── */
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px}
.card h3{font-size:.9rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px}

/* ── grid canvas area ── */
.grid-wrap{flex:0 0 auto}
#gridCanvas{display:block;border-radius:8px;cursor:crosshair}

/* ── stats bar ── */
.stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.stat{background:#0f172a;border:1px solid #334155;border-radius:8px;padding:8px 14px;text-align:center;min-width:90px}
.stat .val{font-size:1.3rem;font-weight:800;color:#60a5fa}
.stat .lbl{font-size:.7rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em}

/* ── legend ── */
.legend{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.leg{display:flex;align-items:center;gap:5px;font-size:.75rem;color:#94a3b8}
.leg-box{width:14px;height:14px;border-radius:3px;border:1px solid #475569}

/* ── action log ── */
.log{font-family:'Courier New',monospace;font-size:.72rem;line-height:1.6;
     max-height:320px;overflow-y:auto;background:#0f172a;border-radius:8px;
     padding:10px;color:#94a3b8;border:1px solid #1e293b}
.log .destroy{color:#f97316}.log .bonus{color:#22c55e}.log .penalty{color:#ef4444}
.log .move{color:#60a5fa}

/* ── controls ── */
.controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
.btn{padding:7px 16px;border-radius:7px;border:none;cursor:pointer;font-size:.8rem;font-weight:600;transition:.15s}
.btn-primary{background:#1d4ed8;color:#fff}.btn-primary:hover{background:#2563eb}
.btn-secondary{background:#334155;color:#e2e8f0}.btn-secondary:hover{background:#475569}
.btn-danger{background:#7f1d1d;color:#fca5a5}.btn-danger:hover{background:#991b1b}
.speed-label{font-size:.75rem;color:#64748b}
input[type=range]{accent-color:#3b82f6;width:100px}

/* ── progress ── */
.progress-bar{height:4px;background:#1e293b;border-radius:2px;overflow:hidden;margin-bottom:10px}
.progress-fill{height:100%;background:linear-gradient(90deg,#3b82f6,#8b5cf6);border-radius:2px;transition:width .1s}

/* ── text panels (Q3/Q4) ── */
.textpanel{background:#0f172a;border-radius:8px;padding:16px;font-family:'Courier New',monospace;
           font-size:.73rem;line-height:1.65;color:#94a3b8;white-space:pre-wrap;overflow:auto;
           max-height:70vh;border:1px solid #1e293b}
.textpanel .h1{color:#60a5fa;font-weight:700}
.textpanel .h2{color:#a78bfa;font-weight:700}
.textpanel .h3{color:#34d399;font-weight:600}
.textpanel .table{color:#fbbf24}

/* ── tooltip ── */
#tooltip{position:fixed;background:#0f172a;border:1px solid #475569;border-radius:6px;
         padding:6px 10px;font-size:.75rem;color:#e2e8f0;pointer-events:none;
         display:none;z-index:999;box-shadow:0 4px 12px rgba(0,0,0,.5)}

/* ── scrollbar ── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#0f1117}
::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}
</style>
</head>
<body>

<div class="topbar">
  <div>
    <h1>🤖 DAA Assignment 4 — Robot Navigation Visualizer</h1>
    <div class="sub">CS2009 Design and Analysis of Algorithms &nbsp;|&nbsp; 15×15 Grid</div>
  </div>
</div>

<div class="tabs">
  <div class="tab active" onclick="showTab('bfs')">Q1 BFS</div>
  <div class="tab" onclick="showTab('dfsi')">Q1 DFS Iterative</div>
  <div class="tab" onclick="showTab('dfsr')">Q1 DFS Recursive</div>
  <div class="tab" onclick="showTab('prim')">Q2 Prim's MST</div>
  <div class="tab" onclick="showTab('kruskal')">Q2 Kruskal's MST</div>
  <div class="tab" onclick="showTab('q3')">Q3 Analysis</div>
  <div class="tab" onclick="showTab('q4')">Q4 Theory</div>
</div>

<!-- BFS tab -->
<div id="tab-bfs" class="content active">
  <div class="card grid-wrap">
    <h3>Grid — BFS Path</h3>
    <div class="legend" id="legend-bfs"></div>
    <canvas id="canvas-bfs" width="540" height="540"></canvas>
    <div id="tip-bfs" style="font-size:.72rem;color:#64748b;margin-top:6px;text-align:center"></div>
  </div>
  <div style="flex:1;min-width:280px;display:flex;flex-direction:column;gap:14px">
    <div class="card">
      <h3>Statistics</h3>
      <div class="stats" id="stats-bfs"></div>
    </div>
    <div class="card">
      <h3>Animation</h3>
      <div class="progress-bar"><div class="progress-fill" id="prog-bfs" style="width:0%"></div></div>
      <div class="controls">
        <button class="btn btn-primary" onclick="play('bfs')">▶ Play</button>
        <button class="btn btn-secondary" onclick="pause('bfs')">⏸ Pause</button>
        <button class="btn btn-secondary" onclick="step('bfs')">⏭ Step</button>
        <button class="btn btn-danger" onclick="reset('bfs')">↺ Reset</button>
        <span class="speed-label">Speed</span>
        <input type="range" min="1" max="10" value="5" id="spd-bfs" title="Speed">
      </div>
      <div style="font-size:.75rem;color:#64748b;margin-bottom:8px" id="phase-bfs">Phase: Idle</div>
    </div>
    <div class="card" style="flex:1">
      <h3>Action Log</h3>
      <div class="log" id="log-bfs"></div>
    </div>
  </div>
</div>

<!-- DFS Iterative tab -->
<div id="tab-dfsi" class="content">
  <div class="card grid-wrap">
    <h3>Grid — DFS Iterative Path</h3>
    <div class="legend" id="legend-dfsi"></div>
    <canvas id="canvas-dfsi" width="540" height="540"></canvas>
    <div id="tip-dfsi" style="font-size:.72rem;color:#64748b;margin-top:6px;text-align:center"></div>
  </div>
  <div style="flex:1;min-width:280px;display:flex;flex-direction:column;gap:14px">
    <div class="card"><h3>Statistics</h3><div class="stats" id="stats-dfsi"></div></div>
    <div class="card">
      <h3>Animation</h3>
      <div class="progress-bar"><div class="progress-fill" id="prog-dfsi" style="width:0%"></div></div>
      <div class="controls">
        <button class="btn btn-primary" onclick="play('dfsi')">▶ Play</button>
        <button class="btn btn-secondary" onclick="pause('dfsi')">⏸ Pause</button>
        <button class="btn btn-secondary" onclick="step('dfsi')">⏭ Step</button>
        <button class="btn btn-danger" onclick="reset('dfsi')">↺ Reset</button>
        <span class="speed-label">Speed</span>
        <input type="range" min="1" max="10" value="5" id="spd-dfsi" title="Speed">
      </div>
      <div style="font-size:.75rem;color:#64748b;margin-bottom:8px" id="phase-dfsi">Phase: Idle</div>
    </div>
    <div class="card" style="flex:1"><h3>Action Log</h3><div class="log" id="log-dfsi"></div></div>
  </div>
</div>

<!-- DFS Recursive tab -->
<div id="tab-dfsr" class="content">
  <div class="card grid-wrap">
    <h3>Grid — DFS Recursive Path</h3>
    <div class="legend" id="legend-dfsr"></div>
    <canvas id="canvas-dfsr" width="540" height="540"></canvas>
    <div id="tip-dfsr" style="font-size:.72rem;color:#64748b;margin-top:6px;text-align:center"></div>
  </div>
  <div style="flex:1;min-width:280px;display:flex;flex-direction:column;gap:14px">
    <div class="card"><h3>Statistics</h3><div class="stats" id="stats-dfsr"></div></div>
    <div class="card">
      <h3>Animation</h3>
      <div class="progress-bar"><div class="progress-fill" id="prog-dfsr" style="width:0%"></div></div>
      <div class="controls">
        <button class="btn btn-primary" onclick="play('dfsr')">▶ Play</button>
        <button class="btn btn-secondary" onclick="pause('dfsr')">⏸ Pause</button>
        <button class="btn btn-secondary" onclick="step('dfsr')">⏭ Step</button>
        <button class="btn btn-danger" onclick="reset('dfsr')">↺ Reset</button>
        <span class="speed-label">Speed</span>
        <input type="range" min="1" max="10" value="5" id="spd-dfsr" title="Speed">
      </div>
      <div style="font-size:.75rem;color:#64748b;margin-bottom:8px" id="phase-dfsr">Phase: Idle</div>
    </div>
    <div class="card" style="flex:1"><h3>Action Log</h3><div class="log" id="log-dfsr"></div></div>
  </div>
</div>

<!-- Prim tab -->
<div id="tab-prim" class="content">
  <div class="card grid-wrap">
    <h3>Grid — Prim's MST Edges</h3>
    <canvas id="canvas-prim" width="540" height="540"></canvas>
    <div id="tip-prim" style="font-size:.72rem;color:#64748b;margin-top:6px;text-align:center"></div>
  </div>
  <div style="flex:1;min-width:280px;display:flex;flex-direction:column;gap:14px">
    <div class="card"><h3>Statistics</h3><div class="stats" id="stats-prim"></div></div>
    <div class="card">
      <h3>Animation</h3>
      <div class="progress-bar"><div class="progress-fill" id="prog-prim" style="width:0%"></div></div>
      <div class="controls">
        <button class="btn btn-primary" onclick="play('prim')">▶ Play</button>
        <button class="btn btn-secondary" onclick="pause('prim')">⏸ Pause</button>
        <button class="btn btn-secondary" onclick="step('prim')">⏭ Step</button>
        <button class="btn btn-danger" onclick="reset('prim')">↺ Reset</button>
        <span class="speed-label">Speed</span>
        <input type="range" min="1" max="10" value="7" id="spd-prim" title="Speed">
      </div>
      <div style="font-size:.75rem;color:#64748b" id="phase-prim">Phase: Idle</div>
    </div>
    <div class="card" style="flex:1">
      <h3>Edge Log</h3><div class="log" id="log-prim"></div>
    </div>
  </div>
</div>

<!-- Kruskal tab -->
<div id="tab-kruskal" class="content">
  <div class="card grid-wrap">
    <h3>Grid — Kruskal's MST Edges</h3>
    <canvas id="canvas-kruskal" width="540" height="540"></canvas>
    <div id="tip-kruskal" style="font-size:.72rem;color:#64748b;margin-top:6px;text-align:center"></div>
  </div>
  <div style="flex:1;min-width:280px;display:flex;flex-direction:column;gap:14px">
    <div class="card"><h3>Statistics</h3><div class="stats" id="stats-kruskal"></div></div>
    <div class="card">
      <h3>Animation</h3>
      <div class="progress-bar"><div class="progress-fill" id="prog-kruskal" style="width:0%"></div></div>
      <div class="controls">
        <button class="btn btn-primary" onclick="play('kruskal')">▶ Play</button>
        <button class="btn btn-secondary" onclick="pause('kruskal')">⏸ Pause</button>
        <button class="btn btn-secondary" onclick="step('kruskal')">⏭ Step</button>
        <button class="btn btn-danger" onclick="reset('kruskal')">↺ Reset</button>
        <span class="speed-label">Speed</span>
        <input type="range" min="1" max="10" value="7" id="spd-kruskal" title="Speed">
      </div>
      <div style="font-size:.75rem;color:#64748b" id="phase-kruskal">Phase: Idle</div>
    </div>
    <div class="card" style="flex:1">
      <h3>Edge Log</h3><div class="log" id="log-kruskal"></div>
    </div>
  </div>
</div>

<!-- Q3 tab -->
<div id="tab-q3" class="content" style="flex-direction:column">
  <div class="card" style="width:100%">
    <h3>Q3 — Time &amp; Space Complexity Analysis</h3>
    <div class="textpanel" id="q3text"></div>
  </div>
</div>

<!-- Q4 tab -->
<div id="tab-q4" class="content" style="flex-direction:column">
  <div class="card" style="width:100%">
    <h3>Q4 — Prim's &amp; Kruskal's: Theoretical Proofs</h3>
    <div class="textpanel" id="q4text"></div>
  </div>
</div>

<div id="tooltip"></div>

<script>
// ═══════════════════════════════════════════════════════════════
// DATA (injected by Python)
// ═══════════════════════════════════════════════════════════════
const GRID  = __GRID__;
const Q1    = __Q1__;
const Q2    = __Q2__;
const Q3TXT = __Q3TXT__;
const Q4TXT = __Q4TXT__;

// ═══════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════
const SZ  = 36;          // cell size px
const PAD = 1;           // gap between cells
const W   = GRID.width;
const H   = GRID.height;
const CVS = SZ * W + PAD * (W + 1);  // canvas width

const COLORS = {
  "0":   "#1e293b",   // free  - dark slate
  "O":   "#374151",   // wall  - darker
  "B":   "#1e40af",   // blue obstacle
  "B+":  "#065f46",   // bonus
  "B-":  "#7f1d1d",   // penalty
};
const BORDER = {
  "0": "#334155","O": "#1f2937","B": "#3b82f6","B+": "#10b981","B-": "#ef4444"
};

// for path/traversal overlays
const C_TRAVERSED = "rgba(234,179,8,0.35)";   // yellow tint
const C_PATH      = "rgba(59,130,246,0.75)";  // blue path
const C_PATH_BORDER = "#93c5fd";
const C_START     = "#7c3aed";  // purple
const C_GOAL      = "#0891b2";  // cyan
const C_CURRENT   = "#f97316"; // orange highlight (current step)
const C_DESTROYED = "rgba(249,115,22,0.3)";  // destroyed blue

// MST colors
const C_MST_H   = "#3b82f6";  // horizontal
const C_MST_V   = "#8b5cf6";  // vertical
const C_MST_D   = "#ec4899";  // diagonal

// ═══════════════════════════════════════════════════════════════
// UTILITY
// ═══════════════════════════════════════════════════════════════
function cellKey(x,y){ return x+","+y; }
function cellCenter(x, y){  // grid coords (1-based, y=1 bottom)
  const cx = PAD + (x-1)*(SZ+PAD) + SZ/2;
  const cy = PAD + (H-y)*(SZ+PAD) + SZ/2;
  return [cx, cy];
}
function cellTopLeft(x, y){
  const tx = PAD + (x-1)*(SZ+PAD);
  const ty = PAD + (H-y)*(SZ+PAD);
  return [tx, ty];
}

// ═══════════════════════════════════════════════════════════════
// DRAW GRID BASE
// ═══════════════════════════════════════════════════════════════
function drawBase(ctx, destroyedSet){
  ctx.clearRect(0,0,CVS,CVS);
  for(let y=1;y<=H;y++){
    for(let x=1;x<=W;x++){
      const k = cellKey(x,y);
      let type = GRID.cells[k];
      const [tx,ty] = cellTopLeft(x,y);
      let fill = COLORS[type] || "#1e293b";
      let stroke = BORDER[type] || "#334155";
      if(destroyedSet && destroyedSet.has(k) && type !== "0" && type !== "O"){
        fill = "#1a2744";   // destroyed blue becomes darker free
        stroke = "#1d4ed8";
      }
      ctx.fillStyle = fill;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(tx,ty,SZ,SZ,3);
      ctx.fill();
      ctx.stroke();
      // labels for special cells
      if(type !== "0" && type !== "O"){
        ctx.fillStyle = type==="B+"?"#6ee7b7":type==="B-"?"#fca5a5":"#93c5fd";
        ctx.font = "bold 9px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(type, tx+SZ/2, ty+SZ/2);
      }
      // coord micro-labels
      ctx.fillStyle = "#1e3a5f";
      ctx.font = "7px sans-serif";
      ctx.textAlign = "left";
      ctx.textBaseline = "top";
      ctx.fillText(x+","+(y), tx+2, ty+1);
    }
  }
  // Start / Goal markers
  drawMarker(ctx, GRID.start[0], GRID.start[1], C_START, "S");
  drawMarker(ctx, GRID.goal[0],  GRID.goal[1],  C_GOAL,  "G");
}

function drawMarker(ctx, x, y, color, label){
  const [cx,cy] = cellCenter(x,y);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(cx,cy,SZ/2-3,0,Math.PI*2);
  ctx.fill();
  ctx.fillStyle = "#fff";
  ctx.font = "bold 11px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(label,cx,cy);
}

function highlightCell(ctx, x, y, color, border){
  const [tx,ty] = cellTopLeft(x,y);
  ctx.fillStyle = color;
  ctx.strokeStyle = border || color;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(tx,ty,SZ,SZ,3);
  ctx.fill();
  if(border){ ctx.stroke(); }
}

function drawArrow(ctx, x1,y1,x2,y2,color){
  const [ax,ay] = cellCenter(x1,y1);
  const [bx,by] = cellCenter(x2,y2);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(ax,ay);
  ctx.lineTo(bx,by);
  ctx.stroke();
  // arrowhead
  const angle = Math.atan2(by-ay,bx-ax);
  const len = 7;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(bx,by);
  ctx.lineTo(bx-len*Math.cos(angle-0.4),by-len*Math.sin(angle-0.4));
  ctx.lineTo(bx-len*Math.cos(angle+0.4),by-len*Math.sin(angle+0.4));
  ctx.closePath();
  ctx.fill();
}

function drawMSTEdge(ctx, x1,y1,x2,y2,type){
  const [ax,ay] = cellCenter(x1,y1);
  const [bx,by] = cellCenter(x2,y2);
  const color = type==="H"?C_MST_H:type==="V"?C_MST_V:C_MST_D;
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.globalAlpha = 0.8;
  ctx.beginPath();
  ctx.moveTo(ax,ay);
  ctx.lineTo(bx,by);
  ctx.stroke();
  ctx.globalAlpha = 1;
}

// ═══════════════════════════════════════════════════════════════
// LEGEND
// ═══════════════════════════════════════════════════════════════
function buildLegend(el){
  const items = [
    ["#1e293b","#334155","Free"],
    ["#374151","#1f2937","Wall (O)"],
    ["#1e40af","#3b82f6","Blue Obstacle (B)"],
    ["#065f46","#10b981","Bonus (B+)"],
    ["#7f1d1d","#ef4444","Penalty (B-)"],
    [C_START,C_START,"Start"],
    [C_GOAL,C_GOAL,"Goal"],
    [C_TRAVERSED,C_TRAVERSED,"Traversed"],
    [C_PATH,"#93c5fd","Final Path"],
  ];
  el.innerHTML = items.map(([bg,bd,lbl])=>
    `<div class="leg"><div class="leg-box" style="background:${bg};border-color:${bd}"></div>${lbl}</div>`
  ).join("");
}

// ═══════════════════════════════════════════════════════════════
// STATS PANEL
// ═══════════════════════════════════════════════════════════════
function buildStats(el, data){
  const items = data.reachable ? [
    [data.expanded,"Expanded"],
    [data.moves,"Path Moves"],
    [data.cost,"Total Cost"],
    [data.energy,"Energy Left"],
    [data.destroyed.length,"Destroyed"],
  ] : [[0,"Expanded"],["N/A","Goal"]];
  el.innerHTML = items.map(([v,l])=>
    `<div class="stat"><div class="val">${v}</div><div class="lbl">${l}</div></div>`
  ).join("");
}

function buildMSTStats(el, mst, label){
  el.innerHTML = [
    [mst.edges.length,"MST Edges"],
    [mst.weight.toFixed(3),"Total Weight"],
    [mst.components,"Components"],
    [mst.edges.filter(e=>e.type==="H").length,"Horizontal"],
    [mst.edges.filter(e=>e.type==="V").length,"Vertical"],
    [mst.edges.filter(e=>e.type==="D").length,"Diagonal"],
  ].map(([v,l])=>
    `<div class="stat"><div class="val">${v}</div><div class="lbl">${l}</div></div>`
  ).join("");
}

// ═══════════════════════════════════════════════════════════════
// ANIMATION ENGINE
// ═══════════════════════════════════════════════════════════════
const state = {};

function initAlgo(id, data){
  state[id] = {
    data, timer: null, stepIdx: 0,
    phase: "traversal",  // "traversal" -> "path"
    traversedSet: new Set(),
    destroyedSet: new Set(),
    done: false,
  };
}

function getDelay(id){
  const spd = document.getElementById("spd-"+id);
  const v = spd ? parseInt(spd.value) : 5;
  return Math.round(600 / v);
}

// play/pause/step/reset are defined below as unified handlers

// returns false when done
function stepOnce(id){
  const s = state[id];
  if(!s || s.done) return false;
  const d = s.data;

  if(s.phase === "traversal"){
    if(s.stepIdx < d.traversal.length){
      const [x,y] = d.traversal[s.stepIdx];
      s.traversedSet.add(cellKey(x,y));
      s.stepIdx++;
      const pct = s.stepIdx / d.traversal.length * 50;
      document.getElementById("prog-"+id).style.width = pct+"%";
      document.getElementById("phase-"+id).textContent =
        "Phase: Traversal — step "+s.stepIdx+" / "+d.traversal.length;
      redraw(id, [x,y]);
      return true;
    } else {
      // switch to path phase
      s.phase = "path";
      s.stepIdx = 0;
      document.getElementById("phase-"+id).textContent = "Phase: Drawing Path…";
      return true;
    }
  }

  if(s.phase === "path"){
    if(!d.reachable){ s.done = true; return false; }
    if(s.stepIdx < d.path.length){
      s.stepIdx++;
      const pct = 50 + s.stepIdx/d.path.length*50;
      document.getElementById("prog-"+id).style.width = pct+"%";
      document.getElementById("phase-"+id).textContent =
        "Phase: Path — step "+s.stepIdx+" / "+d.path.length;
      // log actions near this step
      if(s.stepIdx <= d.actions.length){
        const a = d.actions[s.stepIdx-1];
        if(a) appendLog(id, a);
      }
      redraw(id, null, s.stepIdx);
      return true;
    } else {
      s.done = true;
      document.getElementById("phase-"+id).textContent = "Phase: Complete ✓";
      document.getElementById("prog-"+id).style.width = "100%";
      return false;
    }
  }
  return false;
}

function appendLog(id, action){
  const log = document.getElementById("log-"+id);
  if(!log) return;
  const cls = action.text.startsWith("DESTROY")?"destroy":
              action.text.includes("bonus")?"bonus":
              action.text.includes("penalty")?"penalty":"move";
  const div = document.createElement("div");
  div.className = cls;
  div.textContent = action.n+". "+action.text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function redraw(id, currentCell, pathSteps){
  const canvas = document.getElementById("canvas-"+id);
  if(!canvas) return;
  const ctx = canvas.getContext("2d");
  const s = state[id];
  const d = s.data;

  drawBase(ctx, s.destroyedSet);

  // traversal overlay
  s.traversedSet.forEach(k=>{
    if(k === cellKey(GRID.start[0],GRID.start[1])) return;
    if(k === cellKey(GRID.goal[0],GRID.goal[1])) return;
    const [x,y] = k.split(",").map(Number);
    highlightCell(ctx,x,y,C_TRAVERSED);
  });

  // path overlay
  if(pathSteps && d.path.length > 0){
    const steps = Math.min(pathSteps, d.path.length);
    for(let i=0;i<steps;i++){
      const [x,y] = d.path[i];
      if(i===0||i===steps-1) continue;
      highlightCell(ctx,x,y,C_PATH,C_PATH_BORDER);
    }
    // draw arrows
    for(let i=0;i<steps-1;i++){
      drawArrow(ctx,d.path[i][0],d.path[i][1],d.path[i+1][0],d.path[i+1][1],"rgba(96,165,250,0.6)");
    }
  }

  // current cell highlight
  if(currentCell){
    const [x,y] = currentCell;
    highlightCell(ctx,x,y,"rgba(249,115,22,0.6)","#f97316");
  }

  // re-draw start/goal on top
  drawMarker(ctx, GRID.start[0], GRID.start[1], C_START, "S");
  drawMarker(ctx, GRID.goal[0],  GRID.goal[1],  C_GOAL,  "G");
}

// ═══════════════════════════════════════════════════════════════
// MST ANIMATION
// ═══════════════════════════════════════════════════════════════
const mstState = {};

function initMST(id, edges){
  mstState[id] = { edges, stepIdx:0, timer:null, done:false };
}

function play(id){
  // handle both algo and mst
  if(mstState[id]!==undefined && !state[id]){
    if(mstState[id].done){ resetMST(id); return; }
    if(mstState[id].timer) return;
    mstState[id].timer = setInterval(()=>{ if(!stepMST(id)){ pauseMST(id); } }, getDelay(id));
    return;
  }
  if(!state[id]) return;
  if(state[id].done){ reset2(id); return; }
  if(state[id].timer) return;
  state[id].timer = setInterval(()=>{ if(!stepOnce(id)){ pause2(id); } }, getDelay(id));
}

// unify play/pause/step/reset to handle both
function play(id){
  if(mstState[id] !== undefined && state[id] === undefined){
    if(mstState[id].done){ resetMST(id); return; }
    if(mstState[id].timer) return;
    mstState[id].timer = setInterval(()=>{ if(!stepMST(id)) pauseMST(id); }, getDelay(id));
  } else if(state[id]){
    if(state[id].done){ reset(id); return; }
    if(state[id].timer) return;
    state[id].timer = setInterval(()=>{ if(!stepOnce(id)) pause(id); }, getDelay(id));
  }
}
function pause(id){
  if(mstState[id] !== undefined && state[id] === undefined){ pauseMST(id); }
  else if(state[id]){ clearInterval(state[id].timer); state[id].timer=null; }
}
function step(id){
  pause(id);
  if(mstState[id] !== undefined && state[id] === undefined) stepMST(id);
  else stepOnce(id);
}
function reset(id){
  pause(id);
  if(mstState[id] !== undefined && state[id] === undefined){ resetMST(id); return; }
  if(!state[id]) return;
  state[id].stepIdx=0; state[id].phase="traversal";
  state[id].traversedSet=new Set(); state[id].destroyedSet=new Set(); state[id].done=false;
  redraw(id); 
  document.getElementById("prog-"+id).style.width="0%";
  document.getElementById("phase-"+id).textContent="Phase: Idle";
  document.getElementById("log-"+id).innerHTML="";
}

function pauseMST(id){ clearInterval(mstState[id].timer); mstState[id].timer=null; }
function resetMST(id){
  pauseMST(id);
  mstState[id].stepIdx=0; mstState[id].done=false;
  drawMSTBase(id,0);
  document.getElementById("prog-"+id).style.width="0%";
  document.getElementById("phase-"+id).textContent="Phase: Idle";
  document.getElementById("log-"+id).innerHTML="";
}

function stepMST(id){
  const s = mstState[id];
  if(s.done) return false;
  if(s.stepIdx >= s.edges.length){ s.done=true; document.getElementById("phase-"+id).textContent="Complete ✓"; return false; }
  s.stepIdx++;
  const pct = s.stepIdx/s.edges.length*100;
  document.getElementById("prog-"+id).style.width=pct+"%";
  document.getElementById("phase-"+id).textContent="Edge "+s.stepIdx+" / "+s.edges.length;
  drawMSTBase(id, s.stepIdx);
  // log
  const e = s.edges[s.stepIdx-1];
  const log = document.getElementById("log-"+id);
  const div = document.createElement("div");
  const col = e.type==="H"?"color:#3b82f6":e.type==="V"?"color:#8b5cf6":"color:#ec4899";
  div.style.cssText = col;
  div.textContent = s.stepIdx+". ("+e.u+") -- ("+e.v+")  w="+e.w+"  ["+e.type+"]";
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return true;
}

function drawMSTBase(id, upTo){
  const canvas = document.getElementById("canvas-"+id);
  if(!canvas) return;
  const ctx = canvas.getContext("2d");
  const edges = id==="prim" ? Q2.prim.edges : Q2.kruskal.edges;
  drawBase(ctx, null);
  for(let i=0;i<Math.min(upTo,edges.length);i++){
    const e = edges[i];
    // highlight the two endpoint vertices
    const [x1,y1] = e.u; const [x2,y2] = e.v;
    if(GRID.cells[cellKey(x1,y1)] !== "O") highlightCell(ctx,x1,y1,"rgba(59,130,246,0.2)");
    if(GRID.cells[cellKey(x2,y2)] !== "O") highlightCell(ctx,x2,y2,"rgba(59,130,246,0.2)");
    drawMSTEdge(ctx,x1,y1,x2,y2,e.type);
  }
  // current edge highlight
  if(upTo>0 && upTo<=edges.length){
    const e = edges[upTo-1];
    const c1 = cellCenter(e.u[0],e.u[1]);
    const c2 = cellCenter(e.v[0],e.v[1]);
    ctx.strokeStyle = "#fbbf24";
    ctx.lineWidth = 3;
    ctx.setLineDash([4,3]);
    ctx.beginPath();
    ctx.moveTo(c1[0],c1[1]);
    ctx.lineTo(c2[0],c2[1]);
    ctx.stroke();
    ctx.setLineDash([]);
  }
  drawMarker(ctx,GRID.start[0],GRID.start[1],C_START,"S");
  drawMarker(ctx,GRID.goal[0],GRID.goal[1],C_GOAL,"G");
}

// ═══════════════════════════════════════════════════════════════
// TEXT PANELS (Q3/Q4)
// ═══════════════════════════════════════════════════════════════
function colorizeText(raw){
  return raw
    .replace(/^(={3,}.+={3,})$/gm, '<span style="color:#60a5fa;font-weight:700">$1</span>')
    .replace(/^(Q3\.|Q4\.).+$/gm, s=>'<span style="color:#a78bfa;font-weight:700">'+s+'</span>')
    .replace(/^\s*([-]{3,}.+[-]{3,})\s*$/gm, s=>'<span style="color:#34d399">'+s+'</span>')
    .replace(/O\(([^)]+)\)/g,'<span style="color:#fbbf24">O($1)</span>');
}

// ═══════════════════════════════════════════════════════════════
// TAB SWITCHING
// ═══════════════════════════════════════════════════════════════
function showTab(id){
  document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
  document.querySelectorAll(".content").forEach(c=>c.classList.remove("active"));
  document.getElementById("tab-"+id).classList.add("active");
  event.target.classList.add("active");
  // draw initial grid for canvas tabs
  if(["bfs","dfsi","dfsr"].includes(id)){
    const s = state[id];
    if(s && s.stepIdx===0) redraw(id);
  }
  if(id==="prim"||id==="kruskal"){
    const s = mstState[id];
    if(s && s.stepIdx===0) drawMSTBase(id,0);
  }
}

// ═══════════════════════════════════════════════════════════════
// TOOLTIP (hover on canvas)
// ═══════════════════════════════════════════════════════════════
function setupTooltip(canvasId, tabId){
  const canvas = document.getElementById(canvasId);
  if(!canvas) return;
  const tip = document.getElementById("tooltip");
  canvas.addEventListener("mousemove",e=>{
    const r = canvas.getBoundingClientRect();
    const mx = e.clientX-r.left, my = e.clientY-r.top;
    // find cell
    const col = Math.floor(mx/(SZ+PAD))+1;
    const row = H - Math.floor(my/(SZ+PAD));
    if(col<1||col>W||row<1||row>H){ tip.style.display="none"; return; }
    const k = cellKey(col,row);
    const type = GRID.cells[k]||"?";
    const labels = {"0":"Free","O":"Permanent Obstacle","B":"Blue Obstacle","B+":"Blue Bonus","B-":"Blue Penalty"};
    let txt = "("+col+","+row+")  "+labels[type];
    if(col===GRID.start[0]&&row===GRID.start[1]) txt += "  ★ Start";
    if(col===GRID.goal[0]&&row===GRID.goal[1])   txt += "  ★ Goal";
    tip.textContent = txt;
    tip.style.display = "block";
    tip.style.left = (e.clientX+12)+"px";
    tip.style.top  = (e.clientY-28)+"px";
  });
  canvas.addEventListener("mouseleave",()=>{ tip.style.display="none"; });
}

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════
(function init(){
  // algo tabs
  ["bfs","dfsi","dfsr"].forEach(id=>{
    initAlgo(id, Q1[id]);
    buildLegend(document.getElementById("legend-"+id));
    buildStats(document.getElementById("stats-"+id), Q1[id]);
    const canvas = document.getElementById("canvas-"+id);
    canvas.width = CVS; canvas.height = CVS;
    redraw(id);
    setupTooltip("canvas-"+id, id);
  });

  // MST tabs
  initMST("prim",    Q2.prim.edges);
  initMST("kruskal", Q2.kruskal.edges);
  buildMSTStats(document.getElementById("stats-prim"),    Q2.prim,    "Prim");
  buildMSTStats(document.getElementById("stats-kruskal"), Q2.kruskal, "Kruskal");
  ["prim","kruskal"].forEach(id=>{
    const canvas = document.getElementById("canvas-"+id);
    canvas.width = CVS; canvas.height = CVS;
    drawMSTBase(id,0);
    setupTooltip("canvas-"+id, id);
  });

  // text tabs
  document.getElementById("q3text").innerHTML = colorizeText(Q3TXT);
  document.getElementById("q4text").innerHTML = colorizeText(Q4TXT);
})();
</script>
</body>
</html>
"""


# ── generate and open HTML ────────────────────────────────────────────────────
def generate(grid_path="grid.txt"):
    print("Loading grid and running algorithms…")
    grid_data, q1_data, q2_data, q3_text, q4_text = collect_data(grid_path)
    print("  ✓  Q1 BFS / DFS complete")
    print("  ✓  Q2 Prim / Kruskal complete")
    print("  ✓  Q3 / Q4 text ready")

    html = HTML_TEMPLATE
    html = html.replace("__GRID__",   json.dumps(grid_data, separators=(',',':')))
    html = html.replace("__Q1__",     json.dumps(q1_data,   separators=(',',':')))
    html = html.replace("__Q2__",     json.dumps(q2_data,   separators=(',',':')))
    html = html.replace("__Q3TXT__",  json.dumps(q3_text,   ensure_ascii=False))
    html = html.replace("__Q4TXT__",  json.dumps(q4_text,   ensure_ascii=False))

    out_path = os.path.join(ROOT, "outputs", "visualizer.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("\n  ✓  HTML saved to:", out_path)
    return out_path


def main():
    grid_path = sys.argv[1] if len(sys.argv) > 1 else "grid.txt"
    out_path = generate(grid_path)
    print("  Opening in browser…\n")
    webbrowser.open("file:///" + out_path.replace("\\", "/"))


if __name__ == "__main__":
    main()
