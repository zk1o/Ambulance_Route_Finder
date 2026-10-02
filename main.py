import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.engine import solve_emergency_routing, compare_nearest_vs_fastest_hospital, AVAILABLE_HOSPITALS
from tests.test_scenarios import run_all_test_scenarios
from data.network_data import NODES_COORDINATES

def display_menu():
    print("\n" + "=" * 65)
    print("      SMART AMBULANCE EMERGENCY ROUTE FINDER SYSTEM      ")
    print("=" * 65)
    print("1. Run All Automated Test Scenarios & Comparative Analysis")
    print("2. Calculate Custom Emergency Route")
    print("3. Analyze Nearest vs. Fastest Hospital")
    print("4. Display Network Graph Nodes & Hospitals")
    print("5. Exit")
    print("=" * 65)

def custom_route_cli():
    print("\n--- [Custom Emergency Route Input] ---")
    
    print("Select Search Algorithm:")
    print("1. A* Search (Recommended)")
    print("2. Uniform Cost Search (UCS)")
    print("3. Breadth-First Search (BFS)")
    algo_choice = input("Enter choice (1-3) [Default: 1]: ").strip()
    algo_map = {'1': 'A*', '2': 'UCS', '3': 'BFS'}
    algo = algo_map.get(algo_choice, 'A*')

    print("\nSelect Traffic Condition:")
    print("1. Low")
    print("2. Medium")
    print("3. Heavy")
    traffic_choice = input("Enter choice (1-3) [Default: 2]: ").strip()
    traffic_map = {'1': 'Low', '2': 'Medium', '3': 'Heavy'}
    traffic = traffic_map.get(traffic_choice, 'Medium')

    block_input = input("\nEnter blocked road edge(s) separated by ';' (e.g. Node_3,Emergency_Site; Node_1,Node_2 or leave empty): ").strip()
    blocked_roads = []
    if block_input:
        road_pairs = block_input.split(';')
        for pair in road_pairs:
            nodes = [n.strip() for n in pair.split(',') if n.strip()]
            if len(nodes) == 2:
                blocked_roads.append((nodes[0], nodes[1]))
            elif len(nodes) > 2:
                print(f"⚠️ Warning: Ignored invalid road segment '{pair}'. A road edge must contain exactly 2 nodes.")

    print(f"\nCalculating route using ({algo}) under ({traffic}) traffic condition...\n")
    
    res = solve_emergency_routing(
        traffic_condition=traffic,
        algorithm=algo,
        blocked_roads=blocked_roads
    )

    if res['success']:
        print("✓ Route Calculated Successfully!")
        print(f" • Algorithm Used    : {res['algorithm']}")
        print(f" • Selected Hospital : {res['selected_hospital']}")
        print(f" • Phase 1 Path      : {' -> '.join(res['phase1']['path'])}")
        print(f" • Phase 2 Path      : {' -> '.join(res['phase2']['path'])}")
        print(f" • Total Distance    : {res['total_distance_km']} km")
        print(f" • Total Time        : {res['total_time_min']} min")
        print(f" • Expanded Nodes    : {res['total_expanded_nodes']} nodes")
        print(f" • Execution Time    : {res['total_execution_time_ms']} ms")
    else:
        print(f"✕ Error: {res['message']}")

def main():
    while True:
        display_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            run_all_test_scenarios()
        elif choice == '2':
            custom_route_cli()
        elif choice == '3':
            print("\n--- [Nearest Distance vs. Fastest Time Analysis] ---")
            traffic = input("Select traffic condition (Low / Medium / Heavy) [Default: Heavy]: ").strip() or 'Heavy'
            comp = compare_nearest_vs_fastest_hospital(traffic_condition=traffic)
            if comp:
                print(f"\nTraffic Condition: {traffic}")
                print(f" • Nearest Hospital (Distance) : {comp['nearest_by_distance']['hospital']} ({comp['nearest_by_distance']['distance_km']} km)")
                print(f" • Fastest Hospital (Time)     : {comp['fastest_by_time']['hospital']} ({comp['fastest_by_time']['travel_time_min']} min)")
                print(f" • Are Identical?              : {'Yes' if comp['are_identical'] else 'No (Fastest route uses emergency lanes or clearer roads)'}")
        elif choice == '4':
            print("\n--- [Registered Graph Network Nodes] ---")
            print("Available Hospitals:", ", ".join(AVAILABLE_HOSPITALS))
            print("Network Node Coordinates (X, Y):")
            for node, coords in NODES_COORDINATES.items():
                print(f"  • {node:<15}: {coords}")
        elif choice == '5':
            print("\nExiting System. Good luck with your project evaluation!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == '__main__':
    main()