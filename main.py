import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# يمنع أخطاء الترميز في تيرمنال ويندوز عند طباعة الرموز
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from src.engine import (solve_emergency_routing, compare_nearest_vs_fastest_hospital,
                        AVAILABLE_HOSPITALS, RoutingInputError)
from tests.test_scenarios import run_all_test_scenarios
from data.network_data import NODES_COORDINATES, ROADS_NETWORK, TRAFFIC_MULTIPLIERS

NODE_NAMES = list(NODES_COORDINATES)


def display_menu():
    print("\n" + "=" * 65)
    print("      SMART AMBULANCE EMERGENCY ROUTE FINDER SYSTEM      ")
    print("=" * 65)
    print("1. Run All Automated Test Scenarios & Comparative Analysis")
    print("2. Calculate Custom Emergency Route")
    print("3. Analyze Nearest vs. Fastest Hospital")
    print("4. Display Network Graph Nodes, Roads & Hospitals")
    print("5. Exit")
    print("=" * 65)


def ask_choice(title, options, default_index):
    print(f"\n{title}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    raw = input(f"Enter choice (1-{len(options)}) [Default: {default_index + 1}]: ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1]
    return options[default_index]


def ask_node(prompt, default):
    while True:
        raw = input(f"{prompt} [Default: {default}]: ").strip() or default
        if raw in NODES_COORDINATES:
            return raw
        print(f"  ! Unknown node '{raw}'. Use option 4 in the main menu to list valid nodes.")


def parse_blocked(raw):
    """'Node_3,Emergency_Site; Node_1,Node_2' -> [(a, b), ...] مع التحقق من وجود الطريق"""
    existing = {frozenset((u, v)) for u, v, *_ in ROADS_NETWORK}
    blocked = []
    for pair in raw.split(';'):
        nodes = [n.strip() for n in pair.split(',') if n.strip()]
        if not nodes:
            continue
        if len(nodes) != 2:
            print(f"  ! Ignored '{pair.strip()}': a road must have exactly 2 nodes.")
        elif frozenset(nodes) not in existing:
            print(f"  ! Ignored '{pair.strip()}': no such road in the network.")
        else:
            blocked.append((nodes[0], nodes[1]))
    return blocked


def print_result(res):
    print("\n✓ Route Calculated Successfully!")
    print(f" • Algorithm Used       : {res['algorithm']}   | Traffic: {res['traffic_condition']}")
    mode = 'automatic (lowest travel time)' if res['auto_selected'] else 'manual'
    print(f" • Selected Hospital    : {res['selected_hospital']}  [{mode}]")
    print(f" • Route 1 (Ambulance -> Emergency): {' -> '.join(res['phase1']['path'])}")
    print(f"      {res['phase1']['distance_km']} km, {res['phase1']['time_min']} min, "
          f"{res['phase1']['expanded_nodes']} expanded nodes")
    print(f" • Route 2 (Emergency -> Hospital) : {' -> '.join(res['phase2']['path'])}")
    print(f"      {res['phase2']['distance_km']} km, {res['phase2']['time_min']} min, "
          f"{res['phase2']['expanded_nodes']} expanded nodes")
    print(f" • Total Distance       : {res['total_distance_km']} km")
    print(f" • Total Response Time  : {res['total_time_min']} min")
    print(f" • Expanded Nodes       : {res['total_expanded_nodes']} (+{res['selection_expanded_nodes']} for hospital selection)")
    print(f" • Execution Time       : {res['total_execution_time_ms']} ms")
    if res['auto_selected']:
        print(" • Hospital comparison  : " + " | ".join(
            f"{h['hospital']}={h['time_min']}min/{h['distance_km']}km" for h in res['hospital_evaluation']))


def custom_route_cli():
    print("\n--- [Custom Emergency Route Input] ---")
    start = ask_node("Ambulance starting location", 'Ambulance_Base')
    site = ask_node("Emergency location", 'Emergency_Site')
    hosp = ask_choice("Hospital selection:", ['Automatic (lowest travel time)'] + AVAILABLE_HOSPITALS, 0)
    hosp = None if hosp.startswith('Automatic') else hosp
    algo = ask_choice("Search Algorithm:", ['A*', 'UCS', 'BFS'], 0)
    traffic = ask_choice("Traffic Condition:", list(TRAFFIC_MULTIPLIERS), 1)
    raw = input("\nBlocked road(s) 'NodeA,NodeB; NodeC,NodeD' (empty = none): ").strip()
    blocked = parse_blocked(raw) if raw else []

    print(f"\nCalculating route using ({algo}) under ({traffic}) traffic...")
    try:
        res = solve_emergency_routing(start, site, hosp, traffic, algo, blocked)
    except RoutingInputError as e:
        print(f"✕ Invalid input: {e}")
        return
    print_result(res) if res['success'] else print(f"✕ Error: {res['message']}")


def hospital_analysis_cli():
    print("\n--- [Nearest Distance vs. Fastest Time Analysis] ---")
    traffic = ask_choice("Traffic Condition:", list(TRAFFIC_MULTIPLIERS), 2)
    comp = compare_nearest_vs_fastest_hospital(traffic_condition=traffic)
    if not comp:
        print("No hospital reachable.")
        return
    print(f"\nTraffic Condition: {traffic}")
    for h in comp['evaluated_hospitals']:
        print(f"  • {h['hospital']:<11} shortest {h['min_distance_km']:>5} km | fastest {h['travel_time_min']:>6} min via {h['path']}")
    n, f = comp['nearest_by_distance'], comp['fastest_by_time']
    print(f" • Nearest by distance : {n['hospital']} ({n['distance_km']} km, {n['time_min']} min on that route)")
    print(f" • Fastest by time     : {f['hospital']} ({f['travel_time_min']} min)")
    print(f" • Identical?          : {'Yes' if comp['are_identical'] else 'No - congestion makes the nearest hospital slower'}")


def main():
    while True:
        display_menu()
        choice = input("Select an option (1-5): ").strip()
        if choice == '1':
            run_all_test_scenarios()
        elif choice == '2':
            custom_route_cli()
        elif choice == '3':
            hospital_analysis_cli()
        elif choice == '4':
            print("\nAvailable Hospitals:", ", ".join(AVAILABLE_HOSPITALS))
            print(f"\nNodes ({len(NODES_COORDINATES)}):")
            for node, coords in NODES_COORDINATES.items():
                print(f"  • {node:<15}: {coords}")
            print(f"\nRoads ({len(ROADS_NETWORK)}):  A <-> B (km, km/h, priority lane)")
            for u, v, d, s, e in ROADS_NETWORK:
                print(f"  • {u} <-> {v} ({d} km, {s} km/h{', PRIORITY' if e else ''})")
        elif choice == '5':
            print("\nExiting System.")
            break
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting System.")
