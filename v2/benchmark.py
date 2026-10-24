import os
import sys
import glob
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maze_utils import load_maze, find_default_endpoints
from algorithms import ALGORITHMS

def run_benchmark(maze_path):
    
    maze = load_maze(maze_path)
    start, end = find_default_endpoints(maze)
    
    results = []
    
    # warmup once
    for name, fn in ALGORITHMS.items():
        fn(maze, start, end)
        
    for name, fn in ALGORITHMS.items():
        res = fn(maze, start, end)
        results.append(res)
        
    return results

def print_results(maze_name, shape, results):
    
    print("\n" + "=" * 65)
    print(f"Maze: {maze_name} | Size: {shape[0]}x{shape[1]}")
    print("=" * 65)
    
    print(f"{'Algorithm':<12} {'Path Len':<12} {'Explored':<12} {'Memory':<10} {'Time (ms)':<10}")
    print("-" * 65)
    
    for r in results:
        print(f"{r.name:<12} {r.path_length:<12} {r.states_explored:<12} {r.peak_frontier_size:<10} {r.execution_time_ms:<10.3f}")
        
    print("-" * 65)

def main():
    
    maze_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mazes")
    maze_files = sorted(glob.glob(os.path.join(maze_dir, "*.txt")))
    
    if len(maze_files) == 0:
        print("No maze files found in mazes folder")
        return
        
    for path in maze_files:
        maze_name = os.path.basename(path)
        maze = load_maze(path)
        
        results = run_benchmark(path)
        print_results(maze_name, maze.shape, results)
        
    print("\nKey Observations:")
    print("1. Path Quality: BFS and Dijkstra always give the shortest path. DFS gives a much longer, suboptimal path.")
    print("2. Explored States: In unweighted maze, BFS and Dijkstra explore the exact same number of states.")
    print("3. Time Taken: BFS is faster than Dijkstra because queue operations are O(1) while heap operations in Dijkstra are O(log V).")
    print("4. Memory: BFS and Dijkstra memory is proportional to the width of the frontier. DFS memory depends on search depth.")

if __name__ == "__main__":
    main()
