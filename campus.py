
import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import time
from collections import deque



BG = "#071225"
PANEL = "#0d1b33"
PANEL2 = "#102542"
BORDER = "#17456a"
CYAN = "#20e6f2"
BLUE = "#258cff"
PURPLE = "#9d75ff"
GREEN = "#30e6a1"
PINK = "#ff5277"
ORANGE = "#ffb84d"
TEXT = "#edf7ff"
MUTED = "#94b5d2"

NODES = {
    "Main Gate": (75, 115),
    "Central Library": (255, 90),
    "Academic Block": (450, 105),
    "Cafeteria": (640, 150),
    "Computer Lab": (135, 280),
    "Auditorium": (365, 270),
    "Sports Complex": (625, 310),
    "Student Hostel": (475, 415),
}

ROADS = [
    ("Main Gate", "Central Library", 180, False),
    ("Main Gate", "Computer Lab", 200, False),
    ("Central Library", "Academic Block", 220, False),
    ("Central Library", "Computer Lab", 210, False),
    ("Central Library", "Auditorium", 250, True),
    ("Academic Block", "Cafeteria", 210, False),
    ("Academic Block", "Auditorium", 190, False),
    ("Academic Block", "Sports Complex", 300, True),
    ("Computer Lab", "Auditorium", 260, False),
    ("Computer Lab", "Student Hostel", 390, True),
    ("Auditorium", "Cafeteria", 340, False),
    ("Auditorium", "Sports Complex", 280, False),
    ("Auditorium", "Student Hostel", 220, False),
    ("Cafeteria", "Sports Complex", 200, False),
    ("Sports Complex", "Student Hostel", 260, False),
]

LOCATION_NAMES = list(NODES.keys())


# ==========================================
# GRAPH FUNCTIONS
# ==========================================

def build_graph(accessible=False):
    graph = {node: [] for node in NODES}

    for a, b, distance, stairs in ROADS:
        if accessible and stairs:
            continue

        graph[a].append((b, distance, stairs))
        graph[b].append((a, distance, stairs))

    return graph


def reconstruct_path(parent, start, end):
    if start == end:
        return [start]

    if end not in parent:
        return []

    path = []
    current = end

    while current is not None:
        path.append(current)
        current = parent.get(current)

    path.reverse()

    return path if path[0] == start else []


def calculate_distance(path, graph):
    total = 0

    for a, b in zip(path, path[1:]):
        for neighbour, weight, _ in graph[a]:
            if neighbour == b:
                total += weight
                break

    return total


def package_result(path, distance, visited, started):
    return {
        "path": path,
        "distance": distance,
        "visited": visited,
        "time": (time.perf_counter() - started) * 1000
    }


# ==========================================
# DIJKSTRA'S SHORTEST PATH ALGORITHM
# ==========================================

def dijkstra(graph, start, end):
    started = time.perf_counter()

    distances = {node: float("inf") for node in graph}
    parent = {start: None}
    visited = []
    queue = [(0, start)]

    distances[start] = 0

    while queue:
        current_distance, current = heapq.heappop(queue)

        if current in visited:
            continue

        visited.append(current)

        if current == end:
            break

        for neighbour, weight, _ in graph[current]:
            new_distance = current_distance + weight

            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                parent[neighbour] = current
                heapq.heappush(
                    queue, (new_distance, neighbour)
                )

    path = (
        reconstruct_path(parent, start, end)
        if distances[end] != float("inf")
        else []
    )

    return package_result(
        path, distances[end], visited, started
    )


# ==========================================
# BREADTH-FIRST SEARCH
# ==========================================

def bfs(graph, start, end):
    started = time.perf_counter()

    queue = deque([start])
    parent = {start: None}
    visited = []

    while queue:
        current = queue.popleft()

        if current in visited:
            continue

        visited.append(current)

        if current == end:
            break

        for neighbour, _, _ in graph[current]:
            if neighbour not in parent:
                parent[neighbour] = current
                queue.append(neighbour)

    path = reconstruct_path(parent, start, end)

    distance = (
        calculate_distance(path, graph)
        if path else float("inf")
    )

    return package_result(
        path, distance, visited, started
    )


# ==========================================
# DEPTH-FIRST SEARCH
# ==========================================

def dfs(graph, start, end):
    started = time.perf_counter()

    stack = [start]
    parent = {start: None}
    visited = []

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.append(current)

        if current == end:
            break

        for neighbour, _, _ in reversed(graph[current]):
            if neighbour not in parent:
                parent[neighbour] = current
                stack.append(neighbour)

    path = reconstruct_path(parent, start, end)

    distance = (
        calculate_distance(path, graph)
        if path else float("inf")
    )

    return package_result(
        path, distance, visited, started
    )


# ==========================================
# MAIN APPLICATION
# ==========================================

class CampusNavigator:

    def __init__(self, root):
        self.root = root

        root.title("Campus Navigator Pro | DAA Project")
        root.geometry("1350x850")
        root.minsize(1100, 700)
        root.configure(bg=BG)

        self.start = tk.StringVar(value="Main Gate")
        self.end = tk.StringVar(value="Student Hostel")
        self.algorithm = tk.StringVar(
            value="Dijkstra — Shortest Distance"
        )
        self.accessible = tk.BooleanVar(value=False)

        self.current_path = []
        self.current_graph = build_graph()

        self.setup_styles()
        self.create_interface()
        self.find_route()

    # --------------------------------------
    # STYLES
    # --------------------------------------

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground=PANEL2,
            background=PANEL2,
            foreground=TEXT,
            arrowcolor=CYAN,
            padding=8
        )

        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL2)],
            foreground=[("readonly", TEXT)]
        )

        style.configure(
            "Treeview",
            background="#08172b",
            foreground=TEXT,
            fieldbackground="#08172b",
            rowheight=30
        )

        style.configure(
            "Treeview.Heading",
            background=PANEL2,
            foreground=CYAN,
            font=("Segoe UI", 9, "bold")
        )

    # --------------------------------------
    # REUSABLE UI COMPONENTS
    # --------------------------------------

    def make_panel(self, parent, title, subtitle=None):
        frame = tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tk.Label(
            frame,
            text=title,
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=13, pady=(12, 5))

        if subtitle:
            tk.Label(
                frame,
                text=subtitle,
                bg=PANEL,
                fg=MUTED,
                font=("Segoe UI", 8),
                wraplength=300
            ).pack(anchor="w", padx=13, pady=(0, 8))

        return frame

    def make_button(self, parent, text, command, color=PANEL2):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=BG if color == CYAN else TEXT,
            activebackground=BLUE,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=10
        )

        button.bind(
            "<Enter>",
            lambda event: button.configure(bg=BLUE)
        )

        button.bind(
            "<Leave>",
            lambda event: button.configure(bg=color)
        )

        return button

    def make_stat(self, parent, title, value, color):
        box = tk.Frame(parent, bg=PANEL2)

        tk.Label(
            box,
            text=title,
            bg=PANEL2,
            fg=MUTED,
            font=("Segoe UI", 7, "bold")
        ).pack(pady=(7, 2))

        value_label = tk.Label(
            box,
            text=value,
            bg=PANEL2,
            fg=color,
            font=("Segoe UI", 13, "bold")
        )
        value_label.pack(pady=(0, 8))

        return box, value_label

    # --------------------------------------
    # BUILD THE DASHBOARD
    # --------------------------------------

    def create_interface(self):

        header = tk.Frame(
            self.root,
            bg="#061020",
            height=80
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⌖",
            bg="#061020",
            fg=CYAN,
            font=("Segoe UI Symbol", 36, "bold")
        ).pack(side="left", padx=(20, 10))

        title_area = tk.Frame(header, bg="#061020")
        title_area.pack(side="left", pady=12)

        tk.Label(
            title_area,
            text="CAMPUS NAVIGATOR",
            bg="#061020",
            fg=TEXT,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="EXPLORE  •  NAVIGATE  •  REACH YOUR DESTINATION",
            bg="#061020",
            fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="DAA MINI PROJECT  |  GRAPH ALGORITHMS",
            bg="#061020",
            fg=CYAN,
            font=("Segoe UI", 10, "bold")
        ).pack(side="right", padx=20)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        body.columnconfigure(0, weight=0, minsize=250)
        body.columnconfigure(1, weight=1, minsize=400)
        body.columnconfigure(2, weight=0, minsize=270)
        body.rowconfigure(0, weight=1)

        self.create_controls(body)
        self.create_map_section(body)
        self.create_results_section(body)

        footer = tk.Frame(
            self.root,
            bg="#061020",
            height=28
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.status = tk.StringVar(
            value="READY  •  Select locations to begin"
        )

        tk.Label(
            footer,
            textvariable=self.status,
            bg="#061020",
            fg=GREEN,
            font=("Consolas", 8)
        ).pack(side="left", padx=14, pady=5)

        tk.Label(
            footer,
            text="PYTHON + TKINTER  •  BFS / DFS / DIJKSTRA",
            bg="#061020",
            fg=MUTED,
            font=("Consolas", 8)
        ).pack(side="right", padx=14)

    # --------------------------------------
    # LEFT CONTROL PANEL
    # --------------------------------------

    def create_controls(self, body):

        panel = self.make_panel(
            body,
            "✦  PLAN YOUR JOURNEY",
            "Choose your locations and route algorithm."
        )

        panel.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        tk.Label(
            panel,
            text="STARTING LOCATION",
            bg=PANEL,
            fg=GREEN,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=13, pady=(15, 4))

        ttk.Combobox(
            panel,
            textvariable=self.start,
            values=LOCATION_NAMES,
            state="readonly"
        ).pack(fill="x", padx=13)

        tk.Label(
            panel,
            text="DESTINATION",
            bg=PANEL,
            fg=PINK,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=13, pady=(15, 4))

        ttk.Combobox(
            panel,
            textvariable=self.end,
            values=LOCATION_NAMES,
            state="readonly"
        ).pack(fill="x", padx=13)

        tk.Label(
            panel,
            text="ROUTE ALGORITHM",
            bg=PANEL,
            fg=PURPLE,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=13, pady=(15, 4))

        ttk.Combobox(
            panel,
            textvariable=self.algorithm,
            values=[
                "Dijkstra — Shortest Distance",
                "BFS — Fewest Edges",
                "DFS — Depth First"
            ],
            state="readonly"
        ).pack(fill="x", padx=13)

        tk.Checkbutton(
            panel,
            text="Accessible route (avoid stairs)",
            variable=self.accessible,
            command=self.find_route,
            bg=PANEL,
            fg=TEXT,
            selectcolor=PANEL2,
            activebackground=PANEL,
            activeforeground=CYAN,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=9, pady=14)

        self.make_button(
            panel,
            "➤   FIND BEST ROUTE",
            self.find_route,
            CYAN
        ).pack(fill="x", padx=13, pady=5)

        self.make_button(
            panel,
            "⇄   SWAP LOCATIONS",
            self.swap_locations
        ).pack(fill="x", padx=13, pady=5)

        self.make_button(
            panel,
            "▦   COMPARE ALGORITHMS",
            self.compare_algorithms
        ).pack(fill="x", padx=13, pady=5)

        tip = tk.Frame(
            panel,
            bg="#092a3b",
            highlightbackground="#12617b",
            highlightthickness=1
        )
        tip.pack(fill="x", padx=13, pady=(22, 10))

        tk.Label(
            tip,
            text="PRO TIP",
            bg="#092a3b",
            fg=ORANGE,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10, pady=(9, 3))

        tk.Label(
            tip,
            text=(
                "Dijkstra considers road distances.\n"
                "BFS finds fewer edges.\n"
                "DFS explores deeply first."
            ),
            bg="#092a3b",
            fg=TEXT,
            justify="left",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=10, pady=(0, 10))

        tk.Label(
            panel,
            text="DEMO DATA • DISTANCES IN METERS",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 7)
        ).pack(side="bottom", pady=12)

    # --------------------------------------
    # CENTER MAP
    # --------------------------------------

    def create_map_section(self, body):

        center = tk.Frame(body, bg=BG)
        center.grid(
            row=0, column=1,
            sticky="nsew",
            padx=(0, 10)
        )

        center.rowconfigure(0, weight=1)
        center.rowconfigure(1, weight=0)
        center.columnconfigure(0, weight=1)

        map_panel = self.make_panel(
            center,
            "⌘  INTERACTIVE CAMPUS MAP",
            "Green = start  •  Pink = destination  •  Cyan = selected route"
        )

        map_panel.grid(
            row=0, column=0,
            sticky="nsew",
            pady=(0, 10)
        )

        map_panel.rowconfigure(1, weight=1)
        map_panel.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            map_panel,
            bg="#07172b",
            highlightthickness=0,
            height=470
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(5, 12)
        )

        self.canvas.bind(
            "<Configure>",
            lambda event: self.draw_map()
        )

        bottom = tk.Frame(center, bg=BG)
        bottom.grid(row=1, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)

        insight_panel = self.make_panel(
            bottom,
            "✧  ALGORITHM INSIGHT"
        )
        insight_panel.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 5)
        )

        self.insight_text = tk.Label(
            insight_panel,
            text="Select a route to see algorithm information.",
            bg=PANEL,
            fg=TEXT,
            justify="left",
            wraplength=250,
            font=("Segoe UI", 9)
        )
        self.insight_text.pack(
            anchor="w",
            padx=13,
            pady=(8, 14)
        )

        graph_panel = self.make_panel(
            bottom,
            "⌘  GRAPH DATA"
        )
        graph_panel.grid(
            row=0, column=1,
            sticky="nsew",
            padx=(5, 0)
        )

        tk.Label(
            graph_panel,
            text=(
                f"{len(NODES)} locations\n"
                f"{len(ROADS)} roads\n"
                "Weighted undirected graph"
            ),
            bg=PANEL,
            fg=MUTED,
            justify="left",
            font=("Consolas", 10)
        ).pack(anchor="w", padx=13, pady=(8, 14))

    # --------------------------------------
    # RIGHT RESULTS PANEL
    # --------------------------------------

    def create_results_section(self, body):

        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=2, sticky="nsew")
        right.columnconfigure(0, weight=1)

        route_panel = self.make_panel(
            right,
            "✦  ROUTE DETAILS"
        )
        route_panel.grid(
            row=0, column=0,
            sticky="ew",
            pady=(0, 10)
        )

        self.route_text = tk.Label(
            route_panel,
            text="Your route will appear here.",
            bg=PANEL,
            fg=TEXT,
            justify="left",
            wraplength=235,
            font=("Segoe UI", 9)
        )

        self.route_text.pack(
            anchor="w",
            padx=13,
            pady=(8, 12)
        )

        stats = tk.Frame(route_panel, bg=PANEL2)
        stats.pack(fill="x", padx=10, pady=(0, 12))

        box, self.distance_value = self.make_stat(
            stats, "DISTANCE", "—", CYAN
        )
        box.pack(side="left", expand=True, fill="x")

        box, self.time_value = self.make_stat(
            stats, "TIME (ms)", "—", GREEN
        )
        box.pack(side="left", expand=True, fill="x")

        box, self.nodes_value = self.make_stat(
            stats, "VISITED", "—", PURPLE
        )
        box.pack(side="left", expand=True, fill="x")

        compare_panel = self.make_panel(
            right,
            "▥  ALGORITHM COMPARISON",
            "Live results for the selected locations"
        )

        compare_panel.grid(
            row=1, column=0,
            sticky="ew",
            pady=(0, 10)
        )

        self.tree = ttk.Treeview(
            compare_panel,
            columns=("algorithm", "distance", "visited", "time"),
            show="headings",
            height=4
        )

        headings = [
            ("algorithm", "Algorithm", 75),
            ("distance", "Meters", 55),
            ("visited", "Visited", 50),
            ("time", "Time ms", 55)
        ]

        for column, heading, width in headings:
            self.tree.heading(column, text=heading)
            self.tree.column(
                column,
                width=width,
                anchor="center"
            )

        self.tree.pack(
            fill="x",
            padx=8,
            pady=(5, 12)
        )

        quote = tk.Frame(
            right,
            bg="#102642",
            highlightbackground="#24658a",
            highlightthickness=1
        )

        quote.grid(row=2, column=0, sticky="ew")

        tk.Label(
            quote,
            text="Same campus.\nDifferent paths.\nChoose smart.",
            bg="#102642",
            fg=CYAN,
            font=("Segoe UI", 14, "bold"),
            justify="left"
        ).pack(anchor="w", padx=14, pady=15)

    # --------------------------------------
    # FIND AND DISPLAY A ROUTE
    # --------------------------------------

    def find_route(self):

        start = self.start.get()
        end = self.end.get()

        graph = build_graph(self.accessible.get())
        self.current_graph = graph

        if start == end:
            self.current_path = [start]
            self.route_text.configure(
                text=f"You are already at {start}."
            )
            self.distance_value.configure(text="0 m")
            self.time_value.configure(text="0")
            self.nodes_value.configure(text="1")
            self.status.set("SAME LOCATION SELECTED")
            self.draw_map()
            self.refresh_comparison()
            return

        selected = self.algorithm.get()

        if selected.startswith("BFS"):
            algorithm = bfs
            algorithm_name = "BFS"

        elif selected.startswith("DFS"):
            algorithm = dfs
            algorithm_name = "DFS"

        else:
            algorithm = dijkstra
            algorithm_name = "Dijkstra"

        data = algorithm(graph, start, end)

        self.current_path = data["path"]

        if not self.current_path:
            self.route_text.configure(
                text="No route is available with these settings."
            )
            self.status.set("NO ROUTE FOUND")
            self.draw_map()
            self.refresh_comparison()
            return

        distance = int(data["distance"])
        estimated_minutes = max(1, round(distance / 75))

        route_lines = "\n   ↓\n".join(self.current_path)

        self.route_text.configure(
            text=(
                f"START  ●  {start}\n\n"
                f"{route_lines}\n\n"
                f"DESTINATION  ◆  {end}\n\n"
                f"Algorithm: {algorithm_name}\n"
                f"Estimated walk: ~{estimated_minutes} min"
            )
        )

        self.distance_value.configure(
            text=f"{distance} m"
        )

        self.time_value.configure(
            text=f"{data['time']:.3f}"
        )

        self.nodes_value.configure(
            text=str(len(data["visited"]))
        )

        if algorithm_name == "Dijkstra":
            insight = (
                "DIJKSTRA\n\n"
                "Selects the lowest known distance first. "
                "It finds a shortest-distance path when "
                "road weights are non-negative.\n\n"
                "Time complexity with a binary heap: "
                "O((V + E) log V)."
            )

        elif algorithm_name == "BFS":
            insight = (
                "BREADTH-FIRST SEARCH\n\n"
                "Explores the graph level by level. "
                "It finds the fewest-edge path, but "
                "that path may not have the shortest "
                "total distance.\n\n"
                "Time complexity: O(V + E)."
            )

        else:
            insight = (
                "DEPTH-FIRST SEARCH\n\n"
                "Explores one branch deeply before "
                "backtracking. It can find a valid path "
                "but does not guarantee the shortest one.\n\n"
                "Time complexity: O(V + E)."
            )

        self.insight_text.configure(text=insight)

        self.status.set(
            f"ROUTE FOUND  •  {distance} m  •  "
            f"{len(self.current_path)} locations  •  {algorithm_name}"
        )

        self.refresh_comparison()
        self.draw_map()

    # --------------------------------------
    # ALGORITHM COMPARISON
    # --------------------------------------

    def refresh_comparison(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        graph = build_graph(self.accessible.get())

        algorithms = [
            ("BFS", bfs),
            ("DFS", dfs),
            ("Dijkstra", dijkstra)
        ]

        for name, function in algorithms:
            data = function(
                graph,
                self.start.get(),
                self.end.get()
            )

            distance = (
                str(int(data["distance"]))
                if data["path"]
                else "No path"
            )

            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    distance,
                    len(data["visited"]),
                    f"{data['time']:.3f}"
                )
            )

    def compare_algorithms(self):

        self.refresh_comparison()

        messagebox.showinfo(
            "Algorithm Comparison",
            "The comparison table has been updated.\n\n"
            "BFS: finds the fewest-edge path.\n"
            "DFS: explores deeply before backtracking.\n"
            "Dijkstra: finds the shortest total distance.\n\n"
            "Execution times vary between runs and "
            "are meaningful only as rough measurements "
            "on this small demonstration graph."
        )

    def swap_locations(self):

        old_start = self.start.get()
        self.start.set(self.end.get())
        self.end.set(old_start)

        self.find_route()

    # --------------------------------------
    # DRAW THE CAMPUS MAP
    # --------------------------------------

    def draw_map(self):

        if not hasattr(self, "canvas"):
            return

        canvas = self.canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 460)
        height = max(canvas.winfo_height(), 350)

        # Background grid
        for x in range(0, width, 28):
            canvas.create_line(
                x, 0, x, height,
                fill="#0c2540"
            )

        for y in range(0, height, 28):
            canvas.create_line(
                0, y, width, y,
                fill="#0c2540"
            )

        pad_x = 40
        pad_y = 35

        scale_x = (width - 2 * pad_x) / 680
        scale_y = (height - 2 * pad_y) / 440

        def get_point(name):
            raw_x, raw_y = NODES[name]

            x = pad_x + (raw_x - 40) * scale_x
            y = pad_y + (raw_y - 40) * scale_y

            return x, y

        # Draw roads
        for a, b, distance, stairs in ROADS:

            if self.accessible.get() and stairs:
                continue

            x1, y1 = get_point(a)
            x2, y2 = get_point(b)

            road_color = (
                "#7a552a" if stairs else "#24415f"
            )

            canvas.create_line(
                x1, y1, x2, y2,
                fill=road_color,
                width=2,
                dash=(5, 4) if stairs else ()
            )

            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2

            canvas.create_rectangle(
                mx - 18, my - 9,
                mx + 18, my + 9,
                fill="#0b1b30",
                outline=""
            )

            canvas.create_text(
                mx, my,
                text=f"{distance}m",
                fill=MUTED,
                font=("Segoe UI", 7, "bold")
            )

        # Highlight selected route
        for a, b in zip(
            self.current_path,
            self.current_path[1:]
        ):

            x1, y1 = get_point(a)
            x2, y2 = get_point(b)

            canvas.create_line(
                x1, y1, x2, y2,
                fill="#0b6075",
                width=10,
                capstyle="round"
            )

            canvas.create_line(
                x1, y1, x2, y2,
                fill=CYAN,
                width=4,
                capstyle="round"
            )

            canvas.create_line(
                x1, y1, x2, y2,
                fill="white",
                width=1,
                arrow=tk.LAST,
                arrowshape=(8, 10, 4)
            )

        # Draw locations
        for name in NODES:

            x, y = get_point(name)

            if name == self.start.get():
                color = GREEN
                marker = "S"

            elif name == self.end.get():
                color = PINK
                marker = "D"

            elif name in self.current_path:
                color = CYAN
                marker = "•"

            else:
                color = "#8eb5d6"
                marker = "•"

            canvas.create_oval(
                x - 15, y - 15,
                x + 15, y + 15,
                fill="#092a43",
                outline=color,
                width=2
            )

            canvas.create_text(
                x, y,
                text=marker,
                fill=color,
                font=("Segoe UI", 10, "bold")
            )

            label_y = y - 28 if y > height * 0.72 else y + 27

            canvas.create_rectangle(
                x - 62, label_y - 10,
                x + 62, label_y + 10,
                fill="#0a1b30",
                outline="#1b4564"
            )

            canvas.create_text(
                x, label_y,
                text=name,
                fill=TEXT,
                font=("Segoe UI", 8, "bold")
            )

        canvas.create_text(
            width - 12, 14,
            text="N ↑",
            fill=MUTED,
            anchor="ne",
            font=("Segoe UI", 8, "bold")
        )

        canvas.create_text(
            12, height - 12,
            text="SAMPLE CAMPUS GRAPH • NOT TO SCALE",
            fill="#6286a5",
            anchor="sw",
            font=("Consolas", 7)
        )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CampusNavigator(root)
    root.mainloop()
