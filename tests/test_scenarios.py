import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine import solve_emergency_routing, compare_nearest_vs_fastest_hospital

LINE = "-" * 90


def run_all_test_scenarios():
    print("=" * 90)
    print("      AMBULANCE ROUTE FINDER - TEST SCENARIOS & COMPARATIVE ANALYSIS      ")
    print("=" * 90 + "\n")

    # Scenario 1: BFS vs UCS vs A*
    for traffic in ('Low', 'Heavy'):
        print(f"--- [Scenario 1]: BFS vs UCS vs A* [{traffic} traffic] ---")
        for algo in ('BFS', 'UCS', 'A*'):
            res = solve_emergency_routing(traffic_condition=traffic, algorithm=algo)
            print(f"[{algo:^4}] | Time: {res['total_time_min']:>6.2f} min | Dist: {res['total_distance_km']:>5.2f} km | "
                  f"Expanded: {res['total_expanded_nodes']:>3} | Exec: {res['total_execution_time_ms']:>6.3f} ms | "
                  f"Hospital: {res['selected_hospital']}")
        print(LINE + "\n")

    # Scenario 2: blocked road
    print("--- [Scenario 2]: Dynamic Rerouting on Road Closure (Node_3 <-> Emergency_Site) ---")
    blocked = [('Node_3', 'Emergency_Site')]
    for label, b in (('Road Open   ', []), ('Road Blocked', blocked)):
        r = solve_emergency_routing(traffic_condition='Medium', algorithm='A*', blocked_roads=b)
        print(f"{label} -> {' -> '.join(r['phase1']['path'])} | Total: {r['total_time_min']} min")
    print(LINE + "\n")

    # Scenario 3: traffic changes the hospital choice
    print("--- [Scenario 3]: Nearest (distance) vs Fastest (time) hospital under each traffic level ---")
    for traffic in ('Low', 'Medium', 'Heavy'):
        c = compare_nearest_vs_fastest_hospital(traffic_condition=traffic)
        n, f = c['nearest_by_distance'], c['fastest_by_time']
        print(f"{traffic:<7}| nearest: {n['hospital']} ({n['distance_km']} km, {n['time_min']} min) | "
              f"fastest: {f['hospital']} ({f['travel_time_min']} min, {f['distance_km']} km) | "
              f"{'SAME' if c['are_identical'] else 'DIFFERENT'}")
    print("Conclusion: the nearest hospital by distance is NOT always the fastest by time.")
    print("=" * 90 + "\n")


if __name__ == '__main__':
    run_all_test_scenarios()
