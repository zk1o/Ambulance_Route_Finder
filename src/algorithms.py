import heapq
import time
from src.utils import calculate_heuristic

def bfs_search(graph, start, goal):
    """
    خوارزمية البحث بالاتساع أولاً (Breadth-First Search)
    تتجه نحو أعمق العقد بصفوف (FIFO Queue) وتتجاهل أوزان التكلفة
    """
    start_time = time.perf_counter()
    expanded_nodes = 0
    
    queue = [(start, [start], 0.0, 0.0)] # (العقدة الحالية, المسار, المسافة التراكمية, الزمن التراكمي)
    visited = set()
    
    while queue:
        curr, path, total_dist, total_time = queue.pop(0)
        
        if curr in visited:
            continue
        visited.add(curr)
        expanded_nodes += 1
        
        if curr == goal:
            execution_time = (time.perf_counter() - start_time) * 1000 # بالمللي ثانية
            return path, total_dist, total_time, expanded_nodes, execution_time
            
        for edge in graph.get(curr, []):
            nxt = edge['neighbor']
            if nxt not in visited:
                queue.append((
                    nxt,
                    path + [nxt],
                    total_dist + edge['distance'],
                    total_time + edge['time']
                ))
                
    execution_time = (time.perf_counter() - start_time) * 1000
    return None, 0, 0, expanded_nodes, execution_time


def ucs_search(graph, start, goal):
    """
    خوارزمية البحث بالتكلفة الموحدة (Uniform Cost Search)
    تعتمد على طابور الأولوية (Priority Queue) للتوسع بناءً على الزمن الفعلي g(n)
    """
    start_time = time.perf_counter()
    expanded_nodes = 0
    
    # Priority Queue Elements: (g(n), current_node, path, total_distance)
    pq = [(0.0, start, [start], 0.0)]
    visited = {}
    
    while pq:
        curr_time, curr, path, curr_dist = heapq.heappop(pq)
        
        if curr in visited and visited[curr] <= curr_time:
            continue
        visited[curr] = curr_time
        expanded_nodes += 1
        
        if curr == goal:
            execution_time = (time.perf_counter() - start_time) * 1000
            return path, curr_dist, curr_time, expanded_nodes, execution_time
            
        for edge in graph.get(curr, []):
            nxt = edge['neighbor']
            new_time = curr_time + edge['time']
            new_dist = curr_dist + edge['distance']
            
            heapq.heappush(pq, (new_time, nxt, path + [nxt], new_dist))
            
    execution_time = (time.perf_counter() - start_time) * 1000
    return None, 0, 0, expanded_nodes, execution_time


def a_star_search(graph, start, goal):
    """
    خوارزمية A* Search
    تعتمد على دالة التقييم f(n) = g(n) + h(n) لتوجيه البحث بذكاء
    """
    start_time = time.perf_counter()
    expanded_nodes = 0
    
    # Priority Queue Elements: (f(n), g(n), current_node, path, total_distance)
    h_start = calculate_heuristic(start, goal)
    pq = [(h_start, 0.0, start, [start], 0.0)]
    visited = {}
    
    while pq:
        f_score, g_score, curr, path, curr_dist = heapq.heappop(pq)
        
        if curr in visited and visited[curr] <= g_score:
            continue
        visited[curr] = g_score
        expanded_nodes += 1
        
        if curr == goal:
            execution_time = (time.perf_counter() - start_time) * 1000
            return path, curr_dist, g_score, expanded_nodes, execution_time
            
        for edge in graph.get(curr, []):
            nxt = edge['neighbor']
            new_g = g_score + edge['time']
            new_dist = curr_dist + edge['distance']
            h = calculate_heuristic(nxt, goal)
            new_f = new_g + h
            
            heapq.heappush(pq, (new_f, new_g, nxt, path + [nxt], new_dist))
            
    execution_time = (time.perf_counter() - start_time) * 1000
    return None, 0, 0, expanded_nodes, execution_time