import numpy as np
import random

def get_neighbors(maze, pos):
    
    r = pos[0]
    c = pos[1]
    rows, cols = maze.shape
    
    nodes = []
    
    # 4 directions: Up, Down, Left, Right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        nr = r + dr
        nc = c + dc
        
        if 0 <= nr < rows and 0 <= nc < cols:
            if maze[nr, nc] == 1:
                nodes.append((nr, nc))
                
    return nodes

def load_maze(file_path):
    
    grid = []
    
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            
            if len(line) == 0:
                continue
                
            if " " in line:
                row = [int(val) for val in line.split()]
            else:
                row = [int(val) for val in line]
                
            grid.append(row)
            
    return np.array(grid, dtype=int)

def save_maze(maze, file_path):
    
    with open(file_path, "w") as f:
        for row in maze:
            line = "".join([str(val) for val in row])
            f.write(line + "\n")

def find_default_endpoints(maze):
    
    rows, cols = maze.shape
    start = None
    end = None
    
    # find first open cell from top
    for r in range(rows):
        for c in range(cols):
            if maze[r, c] == 1:
                start = (r, c)
                break
        if start is not None:
            break
            
    # find last open cell from bottom
    for r in range(rows - 1, -1, -1):
        for c in range(cols - 1, -1, -1):
            if maze[r, c] == 1:
                end = (r, c)
                break
        if end is not None:
            break
            
    if start is None or end is None:
        raise ValueError("No open path in maze")
        
    return start, end

def generate_maze(rows, cols, braid_prob=0.15, seed=None):
    
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        
    if rows % 2 == 0:
        rows = rows + 1
    if cols % 2 == 0:
        cols = cols + 1
        
    grid = np.zeros((rows, cols), dtype=int)
    
    start_r, start_c = 1, 1
    grid[start_r, start_c] = 1
    
    stack = [(start_r, start_c)]
    visited = set([(start_r, start_c)])
    
    while len(stack) != 0:
        
        cr, cc = stack[-1]
        neighbors = []
        
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr = cr + dr
            nc = cc + dc
            
            if 0 < nr < rows - 1 and 0 < nc < cols - 1:
                if (nr, nc) not in visited:
                    neighbors.append((nr, nc, dr, dc))
                    
        if len(neighbors) != 0:
            nr, nc, dr, dc = random.choice(neighbors)
            
            grid[cr + dr // 2, cc + dc // 2] = 1
            grid[nr, nc] = 1
            
            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()
            
    # add some loops so there are multiple paths to compare
    if braid_prob > 0:
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r, c] == 0:
                    if (grid[r-1, c] == 1 and grid[r+1, c] == 1) or (grid[r, c-1] == 1 and grid[r, c+1] == 1):
                        if random.random() < braid_prob:
                            grid[r, c] = 1
                            
    return grid
