import math
import os
import sys

# إضافة المجلد الرئيسي للمسار لضمان استيراد data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.network_data import NODES_COORDINATES, ROADS_NETWORK, TRAFFIC_MULTIPLIERS

def calculate_heuristic(current_node, goal_node, max_speed_kmh=100.0):
    """
    حساب الدالة الحدسية المقبولة (Admissible Heuristic) لحجم A*
    باستخدام المسافة المستقيمة (Euclidean Distance) مقسومة على أقصى سرعة مسموحة
    """
    if current_node not in NODES_COORDINATES or goal_node not in NODES_COORDINATES:
        return 0.0
    
    x1, y1 = NODES_COORDINATES[current_node]
    x2, y2 = NODES_COORDINATES[goal_node]
    
    # حساب المسافة المستقيمة بالـ كم
    straight_distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    # تحويل المسافة إلى زمن بالدقائق
    estimated_time_minutes = (straight_distance / max_speed_kmh) * 60.0
    return estimated_time_minutes

def build_graph(blocked_roads=None, traffic_condition='Low'):
    """
    تحويل بيانات الشبكة إلى الرسم البياني (Adjacency List)
    مع حساب زمن السفر بناءً على الازدحام ومسارات الطوارئ
    """
    if blocked_roads is None:
        blocked_roads = []
        
    graph = {}
    traffic_factor = TRAFFIC_MULTIPLIERS.get(traffic_condition, 1.0)
    
    for u, v, distance, base_speed, is_emergency_lane in ROADS_NETWORK:
        # التحقق مما إذا كان الطريق مسدوداً
        if (u, v) in blocked_roads or (v, u) in blocked_roads:
            continue
            
        # حساب خصائص السفر
        # خصم 30% لزمن السفر إذا كان مسار طوارئ مخصص
        emergency_discount = 0.7 if is_emergency_lane else 1.0
        travel_time = (distance / base_speed) * 60.0 * traffic_factor * emergency_discount
        
        if u not in graph: graph[u] = []
        if v not in graph: graph[v] = []
        
        # إضافة الوصلة في الاتجاهين (Undirected Graph)
        graph[u].append({'neighbor': v, 'distance': distance, 'time': travel_time})
        graph[v].append({'neighbor': u, 'distance': distance, 'time': travel_time})
        
    return graph