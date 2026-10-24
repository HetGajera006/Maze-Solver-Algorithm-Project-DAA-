import time
import heapq
from collections import deque
import os
import sys

# make sure local files import properly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maze_utils import get_neighbors

class Result:
    def __init__(self, name, path, explored, visited_order, time_ms, memory):
        self.name = name
        self.algorithm_name = name
        self.path = path
        self.path_length = len(path) - 1 if len(path) > 0 else 0
        self.states_explored = explored
        self.explored = explored
        self.visited_order = visited_order
        self.execution_time_ms = time_ms
        self.time_ms = time_ms
        self.peak_frontier_size = memory
        self.memory = memory
        self.success = len(path) > 0

def reconstruct_path(parent, end):
    
    path = []
    curr = end
    
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
        
    path.reverse()
    return path

def bfs(maze, start, end):
    
    start_time = time.perf_counter()
    
    # queue for BFS, set for fast lookup
    queue = deque([start])
    visited = set([start])
    parent = {start: None}
    visited_order = []
    
    peak_memory = 1
    found = False
    
    while len(queue) != 0:
        
        if len(queue) > peak_memory:
            peak_memory = len(queue)
            
        curr = queue.popleft()
        visited_order.append(curr)
        
        if curr == end:
            found = True
            break
            
        for neighbor in get_neighbors(maze, curr):
            
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                queue.append(neighbor)
                
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    path = []
    if found:
        path = reconstruct_path(parent, end)
        
    return Result("BFS", path, len(visited_order), visited_order, round(total_time, 3), peak_memory)

def dfs(maze, start, end):
    
    start_time = time.perf_counter()
    
    stack = [start]
    visited = set()
    parent = {start: None}
    visited_order = []
    
    peak_memory = 1
    found = False
    
    while len(stack) != 0:
        
        if len(stack) > peak_memory:
            peak_memory = len(stack)
            
        curr = stack.pop()
        
        if curr in visited:
            continue
            
        visited.add(curr)
        visited_order.append(curr)
        
        if curr == end:
            found = True
            break
            
        neighbors = get_neighbors(maze, curr)
        neighbors.reverse()
        
        for neighbor in neighbors:
            if neighbor not in visited:
                parent[neighbor] = curr
                stack.append(neighbor)
                
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    path = []
    if found:
        path = reconstruct_path(parent, end)
        
    return Result("DFS", path, len(visited_order), visited_order, round(total_time, 3), peak_memory)

def dijkstra(maze, start, end):
    
    start_time = time.perf_counter()
    
    pq = []
    heapq.heappush(pq, (0, 0, start))
    
    dist = {start: 0}
    parent = {start: None}
    visited = set()
    visited_order = []
    
    count = 0
    peak_memory = 1
    found = False
    
    while len(pq) != 0:
        
        if len(pq) > peak_memory:
            peak_memory = len(pq)
            
        cost, _, curr = heapq.heappop(pq)
        
        if curr in visited:
            continue
            
        visited.add(curr)
        visited_order.append(curr)
        
        if curr == end:
            found = True
            break
            
        for neighbor in get_neighbors(maze, curr):
            new_cost = cost + 1
            
            if neighbor not in dist or new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                parent[neighbor] = curr
                count += 1
                heapq.heappush(pq, (new_cost, count, neighbor))
                
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    path = []
    if found:
        path = reconstruct_path(parent, end)
        
    return Result("Dijkstra", path, len(visited_order), visited_order, round(total_time, 3), peak_memory)

ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "Dijkstra": dijkstra
}
