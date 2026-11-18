import os
import sys

# إضافة المجلد الرئيسي لضمان الاستيراد الصحيح
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import build_graph
from src.algorithms import bfs_search, ucs_search, a_star_search, shortest_distance_search
from data.network_data import NODES_COORDINATES, TRAFFIC_MULTIPLIERS

# المستشفيات المسجلة في الرسم البياني للشبكة
AVAILABLE_HOSPITALS = ['Hospital_A', 'Hospital_B', 'Hospital_C']

ALGORITHMS = {'BFS': bfs_search, 'UCS': ucs_search, 'A*': a_star_search}


class RoutingInputError(ValueError):
    """مدخلات غير صحيحة (عقدة غير موجودة، زحمة غير معروفة ...)"""


def validate_inputs(ambulance_start, emergency_site, selected_hospital, traffic_condition, algorithm, blocked_roads):
    for label, node in (('Ambulance start', ambulance_start), ('Emergency site', emergency_site)):
        if node not in NODES_COORDINATES:
            raise RoutingInputError(f"{label} '{node}' is not a node in the network.")
    if selected_hospital is not None and selected_hospital not in AVAILABLE_HOSPITALS:
        raise RoutingInputError(f"'{selected_hospital}' is not a registered hospital {AVAILABLE_HOSPITALS}.")
    if traffic_condition not in TRAFFIC_MULTIPLIERS:
        raise RoutingInputError(f"Traffic must be one of {list(TRAFFIC_MULTIPLIERS)}.")
    if algorithm not in ALGORITHMS:
        raise RoutingInputError(f"Algorithm must be one of {list(ALGORITHMS)}.")
    for a, b in blocked_roads:
        if a not in NODES_COORDINATES or b not in NODES_COORDINATES:
            raise RoutingInputError(f"Blocked road ({a}, {b}) contains an unknown node.")


def solve_emergency_routing(
    ambulance_start='Ambulance_Base',
    emergency_site='Emergency_Site',
    selected_hospital=None,  # None = Automatic Selection
    traffic_condition='Low',
    algorithm='A*',
    blocked_roads=None
):
    """
    Two-phase ambulance emergency routing engine.
    Phase 1: Ambulance -> Emergency Site            (using the chosen algorithm)
    Selection: lowest-travel-time hospital          (cost-aware A*, so BFS also gets a fair choice)
    Phase 2: Emergency Site -> Selected Hospital    (using the chosen algorithm)
    """
    blocked_roads = list(blocked_roads or [])
    validate_inputs(ambulance_start, emergency_site, selected_hospital, traffic_condition, algorithm, blocked_roads)

    graph = build_graph(blocked_roads=blocked_roads, traffic_condition=traffic_condition)
    search_func = ALGORITHMS[algorithm]

    # Phase 1
    p1_path, p1_dist, p1_time, p1_exp, p1_exec = search_func(graph, ambulance_start, emergency_site)
    if not p1_path:
        return {'success': False, 'message': 'Unable to reach the emergency site. All paths are blocked!'}

    # Hospital selection (automatic = lowest estimated travel time)
    candidates = [selected_hospital] if selected_hospital else AVAILABLE_HOSPITALS
    evaluated, sel_exp, sel_exec = [], 0, 0.0
    for hosp in candidates:
        path, dist, t, exp, ex = a_star_search(graph, emergency_site, hosp)
        sel_exp += exp
        sel_exec += ex
        if path:
            evaluated.append({'hospital': hosp, 'time_min': round(t, 2), 'distance_km': round(dist, 2)})
    if not evaluated:
        return {'success': False, 'message': 'Unable to reach any hospital from the emergency site!'}
    best_hospital = min(evaluated, key=lambda h: h['time_min'])['hospital']

    # Phase 2
    p2_path, p2_dist, p2_time, p2_exp, p2_exec = search_func(graph, emergency_site, best_hospital)

    return {
        'success': True,
        'algorithm': algorithm,
        'traffic_condition': traffic_condition,
        'selected_hospital': best_hospital,
        'auto_selected': selected_hospital is None,
        'hospital_evaluation': evaluated,
        'phase1': {'from': ambulance_start, 'to': emergency_site, 'path': p1_path,
                   'distance_km': round(p1_dist, 2), 'time_min': round(p1_time, 2),
                   'expanded_nodes': p1_exp},
        'phase2': {'from': emergency_site, 'to': best_hospital, 'path': p2_path,
                   'distance_km': round(p2_dist, 2), 'time_min': round(p2_time, 2),
                   'expanded_nodes': p2_exp},
        'total_distance_km': round(p1_dist + p2_dist, 2),
        'total_time_min': round(p1_time + p2_time, 2),
        'total_expanded_nodes': p1_exp + p2_exp,          # Phase 1 + Phase 2 (search algorithm only)
        'selection_expanded_nodes': sel_exp,              # extra cost of hospital selection (A*)
        'total_execution_time_ms': round(p1_exec + p2_exec + sel_exec, 4)
    }


def compare_nearest_vs_fastest_hospital(emergency_site='Emergency_Site', traffic_condition='Heavy', blocked_roads=None):
    """
    Nearest hospital by DISTANCE (true shortest-distance path) vs fastest hospital by TIME
    (time-optimal path). Each metric uses its own optimal path.
    """
    graph = build_graph(blocked_roads=blocked_roads, traffic_condition=traffic_condition)
    rows = []
    for hosp in AVAILABLE_HOSPITALS:
        d_path, d_dist, d_time_on_dpath, *_ = shortest_distance_search(graph, emergency_site, hosp)
        t_path, t_dist, t_time, *_ = ucs_search(graph, emergency_site, hosp)
        if d_path and t_path:
            rows.append({
                'hospital': hosp,
                'min_distance_km': round(d_dist, 2),
                'distance_path': ' -> '.join(d_path),
                'time_on_distance_path_min': round(d_time_on_dpath, 2),
                'travel_time_min': round(t_time, 2),
                'distance_km': round(t_dist, 2),
                'path': ' -> '.join(t_path),
            })
    if not rows:
        return None
    nearest = min(rows, key=lambda r: r['min_distance_km'])
    fastest = min(rows, key=lambda r: r['travel_time_min'])
    return {
        'evaluated_hospitals': rows,
        'nearest_by_distance': {'hospital': nearest['hospital'], 'distance_km': nearest['min_distance_km'],
                                'time_min': nearest['time_on_distance_path_min']},
        'fastest_by_time': {'hospital': fastest['hospital'], 'travel_time_min': fastest['travel_time_min'],
                            'distance_km': fastest['distance_km']},
        'are_identical': nearest['hospital'] == fastest['hospital']
    }
