import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine import solve_emergency_routing, compare_nearest_vs_fastest_hospital

def run_all_test_scenarios():
    print("=" * 85)
    print("      AMBULANCE ROUTE FINDER - TEST SCENARIOS & COMPARATIVE ANALYSIS      ")
    print("=" * 85 + "\n")

    # -------------------------------------------------------------
    # Scenario 1: Algorithm Comparison (BFS vs UCS vs A*)
    # -------------------------------------------------------------
    print("--- [Scenario 1]: Algorithm Performance Comparison (BFS vs UCS vs A*) [Heavy Traffic] ---")
    algorithms = ['BFS', 'UCS', 'A*']
    
    for algo in algorithms:
        res = solve_emergency_routing(
            ambulance_start='Ambulance_Base',
            emergency_site='Emergency_Site',
            traffic_condition='Heavy',
            algorithm=algo
        )
        if res['success']:
            print(f"[{algo:^4}] | Total Time: {res['total_time_min']:>6.2f} min | "
                  f"Total Dist: {res['total_distance_km']:>5.2f} km | "
                  f"Expanded Nodes: {res['total_expanded_nodes']:>3} | "
                  f"Exec Time: {res['total_execution_time_ms']:>6.3f} ms | "
                  f"Hospital: {res['selected_hospital']}")
    print("-" * 85 + "\n")

    # -------------------------------------------------------------
    # Scenario 2: Blocked Roads Test
    # -------------------------------------------------------------
    print("--- [Scenario 2]: Dynamic Rerouting on Road Closure ---")
    blocked_edge = [('Node_3', 'Emergency_Site')]
    
    print(f"Case 1 (Road Open)    -> ", end="")
    res_open = solve_emergency_routing(traffic_condition='Medium', algorithm='A*')
    print(f"Path: {' -> '.join(res_open['phase1']['path'])} | Time: {res_open['total_time_min']} min")
    
    print(f"Case 2 (Road Blocked) -> ", end="")
    res_blocked = solve_emergency_routing(traffic_condition='Medium', algorithm='A*', blocked_roads=blocked_edge)
    print(f"Path: {' -> '.join(res_blocked['phase1']['path'])} | Time: {res_blocked['total_time_min']} min")
    print("-" * 85 + "\n")

    # -------------------------------------------------------------
    # Scenario 3: Nearest vs. Fastest Hospital Analysis
    # -------------------------------------------------------------
    print("--- [Scenario 3]: Nearest Hospital (Distance) vs. Fastest Hospital (Travel Time) ---")
    comp_res = compare_nearest_vs_fastest_hospital(traffic_condition='Heavy', blocked_roads=[('Node_3', 'Hospital_A')])
    
    if comp_res:
        print("Evaluated Hospitals from Emergency Site:")
        for h in comp_res['evaluated_hospitals']:
            print(f"  • {h['hospital']:<10} | Dist: {h['distance_km']:>5.2f} km | Time: {h['travel_time_min']:>5.2f} min | Path: {h['path']}")
        
        print("\nAnalytical Verdict:")
        print(f"  • Nearest Hospital by Distance   : {comp_res['nearest_by_distance']['hospital']} ({comp_res['nearest_by_distance']['distance_km']} km)")
        print(f"  • Fastest Hospital by Travel Time: {comp_res['fastest_by_time']['hospital']} ({comp_res['fastest_by_time']['travel_time_min']} min)")
        
        if not comp_res['are_identical']:
            print("  ✓ RESULT: The nearest hospital by distance is NOT the fastest by travel time!")
        else:
            print("  • RESULT: Both nearest and fastest hospitals are identical under these conditions.")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_all_test_scenarios()