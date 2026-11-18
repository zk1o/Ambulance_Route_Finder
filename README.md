# Ambulance Emergency Route Finder

AI4101 – Principles of Artificial Intelligence, Umm Al-Qura University.
Problem 5: finding the fastest ambulance route to an emergency site and then to the best hospital.

## Overview
- Road network: 20 nodes, 33 bidirectional roads, 7 priority lanes, 3 hospitals.
- Two-phase search: ambulance → emergency site, then site → hospital.
- Cost = travel time in minutes, affected by traffic (Low / Medium / Heavy), per-road congestion sensitivity, priority lanes and blocked roads.
- Algorithms: BFS (fewest roads), UCS (optimal), A* (optimal, admissible + consistent heuristic).
- Automatic hospital selection (fastest, not just nearest) and a nearest-vs-fastest comparison.

## Structure
```
main.py              terminal menu (run this)
data/network_data.py nodes, roads, traffic settings
src/utils.py         travel-time model, heuristic, graph builder
src/algorithms.py    BFS, UCS, A*, shortest-distance search
src/engine.py        two-phase routing engine and input validation
tests/               scenario report + unit tests
web/index.html       full web UI (single file, open in a browser)
```

## Run
```
python main.py                          # terminal interface
python tests/test_scenarios.py          # scenario report
python -m unittest tests.test_assertions -v   # unit tests
```
Open `web/index.html` in any browser for the graphical interface (no server needed).
Only the Python 3 standard library is used.

## Web UI features
Route view, algorithm / traffic / hospital comparison, search-steps replay, quick scenarios, side-by-side comparison, click-on-map selection and blocking of roads, CSV and PNG export.
