import os
import sys
import glob
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maze_utils import load_maze, find_default_endpoints
from algorithms import ALGORITHMS

# colors
COLOR_WALL = "#222222"
COLOR_PATH = "#ffffff"
COLOR_START = "#22c55e"     # green
COLOR_END = "#ef4444"       # red
COLOR_VISITED = "#93c5fd"   # light blue
COLOR_PATH_FOUND = "#f59e0b" # amber / gold

class MazeApp:
    
    def __init__(self, root):
        
        self.root = root
        self.root.title("Maze Solver - DAA Lab Project")
        self.root.geometry("1050x700")
        
        self.maze = None
        self.start = None
        self.end = None
        
        self.cell_items = {}
        
        self.is_running = False
        self.is_paused = False
        self.anim_job = None
        
        self.result = None
        self.visited_idx = 0
        self.path_idx = 0
        
        self.create_widgets()
        self.load_first_maze()

    def create_widgets(self):
        
        # main layout: left side canvas, right side controls
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side: Canvas
        canvas_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f3f4f6")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)
        
        # Right side: Control panel
        panel = tk.Frame(main_frame, width=380)
        panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        panel.pack_propagate(False)
        
        # Title
        tk.Label(panel, text="Maze Solver & Comparison", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Controls Frame
        ctrl_frame = tk.LabelFrame(panel, text="Controls", padx=8, pady=8)
        ctrl_frame.pack(fill=tk.X, pady=5)
        
        # Maze selection
        row1 = tk.Frame(ctrl_frame)
        row1.pack(fill=tk.X, pady=4)
        tk.Label(row1, text="Maze:", width=8, anchor="w").pack(side=tk.LEFT)
        self.maze_combo = ttk.Combobox(row1, state="readonly", width=16)
        self.maze_combo.pack(side=tk.LEFT, padx=5)
        self.maze_combo.bind("<<ComboboxSelected>>", self.on_maze_select)
        
        btn_browse = tk.Button(row1, text="Browse", command=self.browse_file)
        btn_browse.pack(side=tk.RIGHT)
        
        # Algorithm selection
        row2 = tk.Frame(ctrl_frame)
        row2.pack(fill=tk.X, pady=4)
        tk.Label(row2, text="Algorithm:", width=8, anchor="w").pack(side=tk.LEFT)
        self.alg_combo = ttk.Combobox(row2, values=list(ALGORITHMS.keys()), state="readonly", width=16)
        self.alg_combo.current(0)
        self.alg_combo.pack(side=tk.LEFT, padx=5)
        
        # Speed slider
        row3 = tk.Frame(ctrl_frame)
        row3.pack(fill=tk.X, pady=4)
        tk.Label(row3, text="Speed:", width=8, anchor="w").pack(side=tk.LEFT)
        self.speed_slider = tk.Scale(row3, from_=1, to=100, orient=tk.HORIZONTAL)
        self.speed_slider.set(80)
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(ctrl_frame)
        btn_frame.pack(fill=tk.X, pady=8)
        
        self.btn_run = tk.Button(btn_frame, text="Run", width=7, command=self.start_solving, bg="#22c55e", fg="white", font=("Arial", 9, "bold"))
        self.btn_run.pack(side=tk.LEFT, padx=2)
        
        self.btn_pause = tk.Button(btn_frame, text="Pause", width=7, command=self.toggle_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=2)
        
        self.btn_reset = tk.Button(btn_frame, text="Reset", width=7, command=self.reset_maze)
        self.btn_reset.pack(side=tk.LEFT, padx=2)
        
        self.btn_compare = tk.Button(btn_frame, text="Compare All", command=self.compare_all, bg="#6366f1", fg="white", font=("Arial", 9, "bold"))
        self.btn_compare.pack(side=tk.RIGHT, padx=2)
        
        # Metrics Frame
        metrics_frame = tk.LabelFrame(panel, text="Current Run Metrics", padx=8, pady=8)
        metrics_frame.pack(fill=tk.X, pady=5)
        
        self.lbl_status = self.add_metric_row(metrics_frame, "Status:", "Ready")
        self.lbl_path = self.add_metric_row(metrics_frame, "Path Length:", "-")
        self.lbl_explored = self.add_metric_row(metrics_frame, "Explored States:", "-")
        self.lbl_memory = self.add_metric_row(metrics_frame, "Peak Memory:", "-")
        self.lbl_time = self.add_metric_row(metrics_frame, "Time Taken:", "-")
        
        # Comparison Table
        table_frame = tk.LabelFrame(panel, text="Comparison on This Maze", padx=5, pady=5)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        cols = ("alg", "path", "explored", "memory", "time")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=4)
        
        self.tree.heading("alg", text="Algorithm")
        self.tree.heading("path", text="Path")
        self.tree.heading("explored", text="Explored")
        self.tree.heading("memory", text="Memory")
        self.tree.heading("time", text="Time (ms)")
        
        self.tree.column("alg", width=75, anchor="center")
        self.tree.column("path", width=60, anchor="center")
        self.tree.column("explored", width=65, anchor="center")
        self.tree.column("memory", width=65, anchor="center")
        self.tree.column("time", width=75, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)

    def add_metric_row(self, parent, label_text, default_val):
        
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        
        tk.Label(row, text=label_text, anchor="w").pack(side=tk.LEFT)
        val_lbl = tk.Label(row, text=default_val, font=("Arial", 9, "bold"), anchor="e")
        val_lbl.pack(side=tk.RIGHT)
        
        return val_lbl

    def load_first_maze(self):
        
        maze_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mazes")
        files = sorted(glob.glob(os.path.join(maze_dir, "*.txt")))
        
        names = [os.path.basename(f) for f in files]
        self.maze_combo["values"] = names
        
        if len(names) > 0:
            self.maze_combo.current(0)
            self.load_file(files[0])

    def on_maze_select(self, event=None):
        
        name = self.maze_combo.get()
        if name:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mazes", name)
            self.load_file(path)

    def browse_file(self):
        
        file_path = filedialog.askopenfilename(
            title="Select Maze File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        
        self.stop_animation()
        
        try:
            self.maze = load_maze(file_path)
            self.start, self.end = find_default_endpoints(self.maze)
            self.draw_maze()
            self.lbl_status.config(text=f"Loaded ({self.maze.shape[0]}x{self.maze.shape[1]})", fg="#22c55e")
            self.clear_metrics()
            self.compare_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_resize(self, event=None):
        if self.maze is not None:
            self.draw_maze()

    def draw_maze(self):
        
        self.canvas.delete("all")
        self.cell_items.clear()
        
        if self.maze is None:
            return
            
        rows, cols = self.maze.shape
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w <= 1 or h <= 1:
            w = 550
            h = 550
            
        cell_size = max(2, min(w // cols, h // rows))
        
        offset_x = (w - cell_size * cols) // 2
        offset_y = (h - cell_size * rows) // 2
        
        outline = "#e5e7eb" if cell_size >= 12 else ""
        
        for r in range(rows):
            for c in range(cols):
                
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                if self.maze[r, c] == 0:
                    fill = COLOR_WALL
                elif (r, c) == self.start:
                    fill = COLOR_START
                elif (r, c) == self.end:
                    fill = COLOR_END
                else:
                    fill = COLOR_PATH
                    
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline)
                self.cell_items[(r, c)] = rect

    def reset_maze(self):
        
        self.stop_animation()
        
        if self.maze is not None:
            for (r, c), rect_id in self.cell_items.items():
                if self.maze[r, c] == 0:
                    fill = COLOR_WALL
                elif (r, c) == self.start:
                    fill = COLOR_START
                elif (r, c) == self.end:
                    fill = COLOR_END
                else:
                    fill = COLOR_PATH
                self.canvas.itemconfig(rect_id, fill=fill)
                
        self.clear_metrics()
        self.lbl_status.config(text="Reset", fg="black")

    def clear_metrics(self):
        self.lbl_path.config(text="-")
        self.lbl_explored.config(text="-")
        self.lbl_memory.config(text="-")
        self.lbl_time.config(text="-")

    def start_solving(self):
        
        if self.maze is None:
            return
            
        self.reset_maze()
        alg_name = self.alg_combo.get()
        
        fn = ALGORITHMS.get(alg_name)
        if fn is None:
            return
            
        self.lbl_status.config(text=f"Running {alg_name}...", fg="#6366f1")
        self.root.update_idletasks()
        
        # run algorithm
        self.result = fn(self.maze, self.start, self.end)
        
        # update metrics
        self.lbl_time.config(text=f"{self.result.execution_time_ms:.3f} ms")
        self.lbl_memory.config(text=str(self.result.peak_frontier_size))
        
        self.visited_idx = 0
        self.path_idx = 0
        self.is_running = True
        self.is_paused = False
        self.btn_pause.config(text="Pause")
        
        self.step_animation()

    def toggle_pause(self):
        
        if not self.is_running:
            return
            
        if self.is_paused:
            self.is_paused = False
            self.btn_pause.config(text="Pause")
            self.step_animation()
        else:
            self.is_paused = True
            self.btn_pause.config(text="Resume")
            if self.anim_job:
                self.root.after_cancel(self.anim_job)

    def stop_animation(self):
        
        self.is_running = False
        self.is_paused = False
        
        if self.anim_job:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None

    def step_animation(self):
        
        if not self.is_running or self.is_paused or self.result is None:
            return
            
        speed = self.speed_slider.get()
        
        # calculate step batch and delay based on slider
        if speed >= 90:
            batch = 20
            delay = 1
        elif speed >= 70:
            batch = 5
            delay = 5
        elif speed >= 40:
            batch = 2
            delay = 15
        else:
            batch = 1
            delay = int(100 - speed)
            
        # 1. Animate visited cells
        if self.visited_idx < len(self.result.visited_order):
            for _ in range(batch):
                if self.visited_idx >= len(self.result.visited_order):
                    break
                    
                node = self.result.visited_order[self.visited_idx]
                if node != self.start and node != self.end:
                    rect = self.cell_items.get(node)
                    if rect:
                        self.canvas.itemconfig(rect, fill=COLOR_VISITED)
                        
                self.visited_idx += 1
                
            self.lbl_explored.config(text=str(self.visited_idx))
            self.anim_job = self.root.after(delay, self.step_animation)
            return
            
        # 2. Animate shortest path
        if self.result.success and self.path_idx < len(self.result.path):
            for _ in range(max(1, batch // 2)):
                if self.path_idx >= len(self.result.path):
                    break
                    
                node = self.result.path[self.path_idx]
                if node != self.start and node != self.end:
                    rect = self.cell_items.get(node)
                    if rect:
                        self.canvas.itemconfig(rect, fill=COLOR_PATH_FOUND)
                        
                self.path_idx += 1
                
            self.anim_job = self.root.after(delay, self.step_animation)
            return
            
        # done
        self.is_running = False
        if self.result.success:
            self.lbl_status.config(text="Path Found!", fg="#22c55e")
            self.lbl_path.config(text=f"{self.result.path_length} steps")
        else:
            self.lbl_status.config(text="No Path", fg="#ef4444")

    def compare_all(self):
        
        if self.maze is None:
            return
            
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for name, fn in ALGORITHMS.items():
            res = fn(self.maze, self.start, self.end)
            self.tree.insert("", tk.END, values=(
                name,
                res.path_length,
                res.states_explored,
                res.peak_frontier_size,
                f"{res.execution_time_ms:.3f}"
            ))

def main():
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
