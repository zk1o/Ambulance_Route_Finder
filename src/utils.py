import math
import os
import sys

# إضافة المجلد الرئيسي للمسار لضمان استيراد data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.network_data import (NODES_COORDINATES, ROADS_NETWORK, TRAFFIC_MULTIPLIERS,
                               CONGESTION_SENSITIVITY, EMERGENCY_TIME_FACTOR)

def _euclid(a, b):
    (x1, y1), (x2, y2) = NODES_COORDINATES[a], NODES_COORDINATES[b]
    return math.hypot(x1 - x2, y1 - y2)


def edge_travel_time(u, v, distance, base_speed, is_emergency_lane, traffic_condition):
    """زمن السفر بالدقائق لطريق واحد مع الزحمة وخصم الطوارئ"""
    mult = TRAFFIC_MULTIPLIERS.get(traffic_condition, 1.0)
    sensitivity = CONGESTION_SENSITIVITY.get(frozenset((u, v)), 1.0)
    traffic_factor = 1.0 + (mult - 1.0) * sensitivity
    discount = EMERGENCY_TIME_FACTOR if is_emergency_lane else 1.0
    return (distance / base_speed) * 60.0 * traffic_factor * discount


def _max_effective_speed():
    """أعلى سرعة فعلية (وحدة إحداثيات / دقيقة) في الشبكة تحت أفضل الظروف (Low).
    الزحمة لا تقلل الزمن أبداً (العامل >= 1) فهذه الحدّ الأعلى لكل الحالات."""
    best = 0.0
    for u, v, dist, speed, emerg in ROADS_NETWORK:
        t = edge_travel_time(u, v, dist, speed, emerg, 'Low')
        best = max(best, _euclid(u, v) / t)
    return best

MAX_SPEED = _max_effective_speed()


def calculate_heuristic(current_node, goal_node):
    """
    Admissible heuristic: h(n) = EuclideanDistance(n, goal) / MAX_SPEED
    MAX_SPEED محسوبة من بيانات الشبكة نفسها، فلا يمكن أن يتجاوز h التكلفة الحقيقية
    (الطريق لا يمكن أن يكون أسرع من أسرع طريق في الشبكة، ولا أقصر من الخط المستقيم).
    """
    if current_node not in NODES_COORDINATES or goal_node not in NODES_COORDINATES:
        return 0.0
    return _euclid(current_node, goal_node) / MAX_SPEED

def build_graph(blocked_roads=None, traffic_condition='Low'):
    """
    تحويل بيانات الشبكة إلى الرسم البياني (Adjacency List)
    مع حساب زمن السفر بناءً على الازدحام ومسارات الطوارئ
    """
    if blocked_roads is None:
        blocked_roads = []
        
    graph = {}
    for u, v, distance, base_speed, is_emergency_lane in ROADS_NETWORK:
        # التحقق مما إذا كان الطريق مسدوداً
        if (u, v) in blocked_roads or (v, u) in blocked_roads:
            continue
            
        # زمن السفر = الزحمة (حسب حساسية الطريق) + خصم مسار الطوارئ
        travel_time = edge_travel_time(u, v, distance, base_speed, is_emergency_lane, traffic_condition)
        
        if u not in graph: graph[u] = []
        if v not in graph: graph[v] = []
        
        # إضافة الوصلة في الاتجاهين (Undirected Graph)
        graph[u].append({'neighbor': v, 'distance': distance, 'time': travel_time})
        graph[v].append({'neighbor': u, 'distance': distance, 'time': travel_time})
        
    return graph