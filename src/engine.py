import os
import sys

# إضافة المجلد الرئيسي لضمان الاستيراد الصحيح
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import build_graph
from src.algorithms import bfs_search, ucs_search, a_star_search

# المستشفيات المسجلة في الرسم البياني للشبكة
AVAILABLE_HOSPITALS = ['Hospital_A', 'Hospital_B', 'Hospital_C']

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
    Phase 1: Ambulance -> Emergency Site
    Phase 2: Emergency Site -> Best Hospital (lowest travel time)
    """
    if blocked_roads is None:
        blocked_roads = []

    # بناء الرسم البياني بناءً على حالة المرور والمسارات المسدودة
    graph = build_graph(blocked_roads=blocked_roads, traffic_condition=traffic_condition)

    # اختيار خوارزمية البحث
    algo_map = {
        'BFS': bfs_search,
        'UCS': ucs_search,
        'A*': a_star_search
    }
    search_func = algo_map.get(algorithm, a_star_search)

    # -------------------------------------------------------------
    # Phase 1: Ambulance to Emergency Site
    # -------------------------------------------------------------
    p1_path, p1_dist, p1_time, p1_exp, p1_exec = search_func(graph, ambulance_start, emergency_site)

    if not p1_path:
        return {
            'success': False,
            'message': 'Unable to reach the emergency site. All paths are blocked!'
        }

    # -------------------------------------------------------------
    # Phase 2: Emergency Site to Best Hospital
    # -------------------------------------------------------------
    best_hospital = None
    best_p2_data = None
    min_travel_time = float('inf')

    target_hospitals = [selected_hospital] if selected_hospital else AVAILABLE_HOSPITALS

    for hosp in target_hospitals:
        p2_path, p2_dist, p2_time, p2_exp, p2_exec = search_func(graph, emergency_site, hosp)
        
        # اختيار المستشفى صاحب أقل زمن سفر
        if p2_path and p2_time < min_travel_time:
            min_travel_time = p2_time
            best_hospital = hosp
            best_p2_data = (p2_path, p2_dist, p2_time, p2_exp, p2_exec)

    if not best_p2_data:
        return {
            'success': False,
            'message': 'Unable to reach any hospital from the emergency site!'
        }

    p2_path, p2_dist, p2_time, p2_exp, p2_exec = best_p2_data

    return {
        'success': True,
        'algorithm': algorithm,
        'traffic_condition': traffic_condition,
        'selected_hospital': best_hospital,
        'phase1': {
            'from': ambulance_start,
            'to': emergency_site,
            'path': p1_path,
            'distance_km': round(p1_dist, 2),
            'time_min': round(p1_time, 2)
        },
        'phase2': {
            'from': emergency_site,
            'to': best_hospital,
            'path': p2_path,
            'distance_km': round(p2_dist, 2),
            'time_min': round(p2_time, 2)
        },
        'total_distance_km': round(p1_dist + p2_dist, 2),
        'total_time_min': round(p1_time + p2_time, 2),
        'total_expanded_nodes': p1_exp + p2_exp,
        'total_execution_time_ms': round(p1_exec + p2_exec, 4)
    }


def compare_nearest_vs_fastest_hospital(emergency_site='Emergency_Site', traffic_condition='Heavy', blocked_roads=None):
    """
    Comparative analysis: Nearest hospital by distance vs. Fastest hospital by travel time.
    """
    graph = build_graph(blocked_roads=blocked_roads, traffic_condition=traffic_condition)
    
    evaluated_hospitals = []
    for hosp in AVAILABLE_HOSPITALS:
        path, dist, travel_time, _, _ = a_star_search(graph, emergency_site, hosp)
        if path:
            evaluated_hospitals.append({
                'hospital': hosp,
                'distance_km': round(dist, 2),
                'travel_time_min': round(travel_time, 2),
                'path': ' -> '.join(path)
            })
    
    if not evaluated_hospitals:
        return None

    nearest_by_distance = min(evaluated_hospitals, key=lambda x: x['distance_km'])
    fastest_by_time = min(evaluated_hospitals, key=lambda x: x['travel_time_min'])
    
    return {
        'evaluated_hospitals': evaluated_hospitals,
        'nearest_by_distance': nearest_by_distance,
        'fastest_by_time': fastest_by_time,
        'are_identical': nearest_by_distance['hospital'] == fastest_by_time['hospital']
    }