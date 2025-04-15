import tkinter as tk
import time # For debouncing updates

# Import all node types
from nodes.input_node import InputNode
from nodes.brightness_node import BrightnessNode
from nodes.output_node import OutputNode
# Add new node imports here
from nodes.contrast_node import ContrastNode # Assuming you create this
from nodes.blur_node import BlurNode         # Assuming you create this
from nodes.splitter_node import SplitterNode
from nodes.threshold_node import ThresholdNode
from nodes.edge_node import EdgeNode

APP_FONT = ("Segoe UI", 9)
APP_FONT_BOLD = ("Segoe UI", 10, "bold")


class NodeGraph:
    def __init__(self, master, preview_window):
        self.master = master
        self.preview_window = preview_window
        self.nodes = []
        self.links = [] # Store links as tuples: (start_node, end_node, line_id)

        self.canvas_bg_color = '#4D4D4D' # Slightly lighter dark gray
        self.canvas = tk.Canvas(master, width=800, height=600, bg=self.canvas_bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # --- State Variables ---
        self.selected_node = None
        self.linking_in_progress = False
        self.link_start_node = None
        self.link_start_pos = None
        self.temporary_link_line = None
        self.drag_canvas = False
        self.last_drag_x = 0
        self.last_drag_y = 0
        self.pan_sensitivity = 0.02 # Panning sensitivity factor

        # --- Update Scheduling ---
        self.needs_update = False # Flag to indicate if processing is required
        self.debounce_time = 0.05 # Shorten debounce time (50 milliseconds)
        self.update_scheduled_id = None # Store the ID from root.after

        # --- Bindings ---
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<ButtonPress-2>", self.on_canvas_pan_press) # Middle mouse button pan
        self.canvas.bind("<ButtonPress-3>", self.on_canvas_context_menu) # Right click
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<B2-Motion>", self.on_canvas_pan_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<ButtonRelease-2>", self.on_canvas_pan_release)
        self.canvas.bind("<MouseWheel>", self.on_zoom) # Windows/macOS specific delta
        # Linux scroll events
        self.canvas.bind("<Button-4>", lambda e: self.on_zoom(e, 1)) # Scroll up
        self.canvas.bind("<Button-5>", lambda e: self.on_zoom(e, -1)) # Scroll down
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.master.bind_all("<Delete>", self.delete_selected) # Bind delete key globally
        self.master.bind_all("<BackSpace>", self.delete_selected) # Also Backspace

        # --- Node Type Mapping ---
        self.node_classes = {
            "Input": InputNode,
            "Brightness": BrightnessNode,
            "Output": OutputNode,
            "Contrast": ContrastNode,
            "Blur": BlurNode,
            "Splitter": SplitterNode,
            "Threshold": ThresholdNode,
            "Edge Detect": EdgeNode, # Renamed slightly for UI
        }
        # No initial schedule needed, only schedule when requested


    def add_node(self, node_type, x=None, y=None):
        node_class = self.node_classes.get(node_type)
        if node_class:
            # Calculate initial position if not provided (e.g., center view)
            if x is None or y is None:
                 # Get current view center
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                view_x = self.canvas.canvasx(0) # Get world coordinate at view origin x
                view_y = self.canvas.canvasy(0) # Get world coordinate at view origin y
                x = view_x + canvas_width / 2
                y = view_y + canvas_height / 2


            print(f"[NODE] Creating node: {node_type} at ({int(x)}, {int(y)})")
            node = node_class(self, x, y)
            self.nodes.append(node)
            node.draw()
            self.request_update() # Request update when a node is added
            return node
        else:
            print(f"[ERROR] Unknown node type: {node_type}")
            return None

    def select_node(self, node):
        if self.selected_node and self.selected_node != node:
            self.selected_node.deselect()
        self.selected_node = node
        if node:
            node.selected = True # Ensure node knows it's selected internally
            node.node_graph.canvas.itemconfig(node.id, outline="deep sky blue", width=2) # Highlight
        # Properties panel update removed for brevity, assumed handled elsewhere if needed

    def delete_selected(self, event=None):
        if self.selected_node:
            print(f"[NODE] Deleting node: {self.selected_node.node_type}")
            node_to_delete = self.selected_node
            self.select_node(None) # Deselect first
            node_to_delete.delete() # Node handles canvas cleanup and disconnects
            if node_to_delete in self.nodes:
                self.nodes.remove(node_to_delete)
            self.draw_links() # Redraw links as some might be removed
            self.request_update() # Request update after deletion
        else:
             print("[INFO] No node selected to delete.")


    # --- Event Handlers ---

    def on_canvas_press(self, event):
        self.canvas.focus_set()
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        clicked_on_node = None
        for node in reversed(self.nodes): # Check topmost nodes first
            if node.is_within(canvas_x, canvas_y):
                if hasattr(node, 'on_element_click') and node.on_element_click(canvas_x, canvas_y):
                    return
                if node.is_over_connector(canvas_x, canvas_y):
                     self.on_connector_press(event, node, canvas_x, canvas_y)
                     return
                clicked_on_node = node
                break

        if clicked_on_node:
            clicked_on_node.on_press(event)
        else:
            if self.selected_node:
                self.selected_node.deselect()
            self.select_node(None)


    def on_canvas_drag(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if self.linking_in_progress:
            self.canvas.coords(self.temporary_link_line, self.link_start_pos[0], self.link_start_pos[1], canvas_x, canvas_y)
        elif self.selected_node:
             self.selected_node.on_drag(event)
             # Node drag handles link updates


    def on_canvas_release(self, event):
        if self.linking_in_progress:
            self.on_link_release(event)
        # Node's own release/selection handled elsewhere

    def on_canvas_pan_press(self, event):
        self.drag_canvas = True
        self.last_drag_x = event.x
        self.last_drag_y = event.y
        self.canvas.config(cursor="fleur")

    def on_canvas_pan_drag(self, event):
        if self.drag_canvas:
            dx = event.x - self.last_drag_x
            dy = event.y - self.last_drag_y
            sensitive_dx = dx * self.pan_sensitivity
            sensitive_dy = dy * self.pan_sensitivity
            self.canvas.xview_scroll(int(-sensitive_dx), "units")
            self.canvas.yview_scroll(int(-sensitive_dy), "units")
            self.last_drag_x = event.x
            self.last_drag_y = event.y

    def on_canvas_pan_release(self, event):
        self.drag_canvas = False
        self.canvas.config(cursor="")

    def on_canvas_context_menu(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        for node_type in self.node_classes:
            menu.add_command(label=f"Add {node_type}", command=lambda nt=node_type: self.add_node(nt, canvas_x, canvas_y))
        if self.selected_node:
            menu.add_separator()
            menu.add_command(label=f"Delete {self.selected_node.node_type}", command=self.delete_selected)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def on_zoom(self, event, direction=None):
        scale_factor = 1.1
        delta = 0
        if direction is not None: delta = direction
        elif hasattr(event, 'delta') and event.delta != 0: delta = event.delta
        else: return

        factor = scale_factor if delta > 0 else 1 / scale_factor
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        self.canvas.scale("all", canvas_x, canvas_y, factor, factor)

    def on_double_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        for node in reversed(self.nodes):
            if node.is_within(canvas_x, canvas_y):
                print(f"Double clicked node: {node.node_type}")
                break


    # --- Linking Logic ---

    def on_connector_press(self, event, node, canvas_x, canvas_y):
        connector_type = node.get_connector_type(canvas_x, canvas_y)
        if connector_type == "output":
            self.linking_in_progress = True
            self.link_start_node = node
            self.link_start_pos = node.get_output_pos()
            self.temporary_link_line = self.canvas.create_line(
                self.link_start_pos[0], self.link_start_pos[1], canvas_x, canvas_y,
                fill="cyan", width=2, dash=(4, 4), tags="temp_link"
            )
            self.canvas.lift(self.temporary_link_line)
            print(f"[LINK] Started linking from {node.node_type} output")
        elif connector_type == "input":
             if node.input_node:
                 print(f"[LINK] Breaking link to {node.node_type} input")
                 existing_link = self.find_link(node.input_node, node)
                 if existing_link:
                     self.remove_link(existing_link) # Visual removal handled here
                 node.disconnect_input() # Data model update
                 # No need to call request_update here, disconnect_input does it

    def on_link_release(self, event):
        if not self.linking_in_progress: return

        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        link_completed = False

        for target_node in self.nodes:
            if target_node != self.link_start_node and target_node.input_hit(canvas_x, canvas_y):
                if target_node.input_node:
                     print(f"[LINK] Target input {target_node.node_type} already connected. Breaking old link.")
                     old_source_node = target_node.input_node
                     existing_link = self.find_link(old_source_node, target_node)
                     if existing_link:
                         self.remove_link(existing_link) # Visual removal
                     target_node.disconnect_input() # Data model update (triggers update request)

                print(f"[LINK] Completing link: {self.link_start_node.node_type} -> {target_node.node_type}")
                self.add_link(self.link_start_node, target_node) # Handles visual and data connection (triggers update request)
                link_completed = True
                break

        if not link_completed:
            print("[LINK] Link released over empty space or invalid target.")

        if self.temporary_link_line:
            self.canvas.delete(self.temporary_link_line)
            self.temporary_link_line = None
        self.linking_in_progress = False
        self.link_start_node = None
        self.link_start_pos = None


    def add_link(self, start_node, end_node):
        if self.find_link(start_node, end_node):
             print("[LINK] Link already exists.")
             return

        x1, y1 = start_node.get_output_pos()
        x2, y2 = end_node.get_input_pos()
        line_id = self.canvas.create_line(x1, y1, x2, y2, fill="#a0a0a0", width=2, tags="link")
        link_data = (start_node, end_node, line_id)
        self.links.append(link_data)

        # Update node data connections (triggers update request via node methods)
        start_node.connect_output(end_node)
        # self.request_update() # Already triggered by connect_output->connect_input

    def remove_link(self, link_data):
         start_node, end_node, line_id = link_data
         print(f"[LINK] Removing visual link: {start_node.node_type} -> {end_node.node_type}")
         self.canvas.delete(line_id)
         if link_data in self.links:
              self.links.remove(link_data)
         # Data disconnection handled by node methods (which should trigger update request)

    def find_link(self, start_node, end_node):
         for link in self.links:
             if link[0] == start_node and link[1] == end_node:
                 return link
         return None

    def draw_links(self):
        links_to_remove = []
        for i, (start, end, line_id) in enumerate(self.links):
             if start not in self.nodes or end not in self.nodes:
                 print(f"[WARN] Link references deleted node. Removing link visual.")
                 self.canvas.delete(line_id)
                 links_to_remove.append(self.links[i])
                 continue

             start_pos = start.get_output_pos()
             end_pos = end.get_input_pos()
             if start_pos and end_pos:
                 self.canvas.coords(line_id, start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                 self.canvas.itemconfig(line_id, state='normal') # Ensure visible
             else:
                 print(f"[WARN] Could not get valid positions for link {start.node_type}->{end.node_type}. Hiding line.")
                 self.canvas.itemconfig(line_id, state='hidden') # Hide if positions invalid

        # Remove links referencing deleted nodes from the list
        for link in links_to_remove:
            if link in self.links:
                 self.links.remove(link)


    def update_node_links(self, node):
        """Updates only the links connected to a specific node when it moves."""
        links_to_update = []
        # Find incoming link
        if node.input_node:
            link = self.find_link(node.input_node, node)
            if link: links_to_update.append(link)
        # Find outgoing links
        for target_node in node.output_nodes:
             link = self.find_link(node, target_node)
             if link: links_to_update.append(link)

        # Update coordinates
        for start, end, line_id in links_to_update:
             start_pos = start.get_output_pos()
             end_pos = end.get_input_pos()
             if start_pos and end_pos:
                 self.canvas.coords(line_id, start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                 self.canvas.itemconfig(line_id, state='normal')
             else:
                  self.canvas.itemconfig(line_id, state='hidden')


    # --- Update Scheduling Methods (REVISED) ---

    def request_update(self):
         """Flags that an update is needed and schedules processing."""
         # print("[DEBUG] request_update called") # Optional debug print
         self.needs_update = True
         self.schedule_update()

    def schedule_update(self):
         """Schedules the process_graph method after a debounce delay."""
         # If an update is already scheduled, cancel it first
         if self.update_scheduled_id:
             try:
                 self.master.after_cancel(self.update_scheduled_id)
                 # print(f"[DEBUG] Cancelled previous schedule: {self.update_scheduled_id}") # Optional
             except ValueError:
                 # This can happen if the ID is invalid (e.g., callback already ran)
                 # print(f"[DEBUG] Failed to cancel schedule ID: {self.update_scheduled_id} (may have already run)") # Optional
                 pass
             self.update_scheduled_id = None # Clear the old ID

         # Schedule the actual processing check
         # print(f"[DEBUG] Scheduling _process_if_needed in {int(self.debounce_time * 1000)} ms") # Optional
         self.update_scheduled_id = self.master.after(int(self.debounce_time * 1000), self._process_if_needed)

    def _process_if_needed(self):
         """Internal method called by the scheduler. Processes if needs_update is True."""
         # print("[DEBUG] _process_if_needed called") # Optional debug print
         # Clear the ID now that this scheduled call is running
         self.update_scheduled_id = None

         if self.needs_update:
             # Reset the flag *before* processing to catch changes during processing
             self.needs_update = False
             self.process_graph() # This now updates the preview at the end
         else:
             # print("[DEBUG] Skipping process, needs_update is False") # Optional
             pass


    # --- Processing Logic ---

    def process_graph(self):
        """Executes the node graph operations and updates the preview."""
        print("\n--- Processing Graph ---")
        start_time = time.time()

        # 1. Build dependency graph and find execution order
        execution_order = self.get_execution_order()
        if execution_order is None:
            print("[ERROR] Cyclic dependency detected in the graph. Cannot process.")
            if self.preview_window:
                self.preview_window.update_image(None) # Clear preview on cycle error
            return

        # print(f"Execution Order: {[node.node_type for node in execution_order]}") # Reduced verbosity

        # 2. Execute nodes in order
        processed_count = 0
        for node in execution_order:
             try:
                 # print(f"Processing Node: {node.node_type} ({id(node)})") # Reduced verbosity
                 node.process() # Node fetches its own input and calculates output
                 processed_count += 1
             except Exception as e:
                 print(f"[ERROR] Failed to process node {node.node_type}: {e}")
                 # Depending on desired behavior, you might want to stop processing

        # --- START: Preview Update Logic ---
        final_output_image = None
        # Find the first OutputNode in the execution order (or all nodes as fallback)
        output_nodes_in_order = [node for node in execution_order if isinstance(node, OutputNode)]

        if output_nodes_in_order:
            # Use the output data from the first output node found in the valid execution path
            final_output_image = output_nodes_in_order[0].output_data
            # print(f"[PREVIEW] Found OutputNode in execution path. Data type: {type(final_output_image)}") # Reduced verbosity
        else:
            # Fallback: Check all nodes if no OutputNode was in the execution path
            all_output_nodes = [node for node in self.nodes if isinstance(node, OutputNode)]
            if all_output_nodes:
                 final_output_image = all_output_nodes[0].output_data
                 # print(f"[PREVIEW] Found disconnected OutputNode. Data type: {type(final_output_image)}") # Reduced verbosity
            # else:
                # print("[PREVIEW] No OutputNode found in the graph.") # Reduced verbosity

        # Update the preview window
        if self.preview_window:
            self.preview_window.update_image(final_output_image)
        # --- END: Preview Update Logic ---


        end_time = time.time()
        print(f"--- Graph Processing Finished ({processed_count}/{len(execution_order)} nodes) in {end_time - start_time:.3f}s ---")

        # Ensure links are visually up-to-date (already here, good practice)
        self.draw_links()


    def get_execution_order(self):
        """Performs a topological sort to find the order of node execution."""
        # Kahn's algorithm
        graph = {node: set() for node in self.nodes}
        in_degree = {node: 0 for node in self.nodes}

        # Build graph and in-degrees based on *actual* node connections, not self.links
        for node in self.nodes:
            if node.input_node: # Check if node has an input connection
                 source_node = node.input_node
                 if source_node in graph: # Ensure source node exists
                     if node not in graph[source_node]:
                          graph[source_node].add(node)
                          in_degree[node] += 1

        # Initialize queue with nodes having zero in-degree
        queue = [node for node in self.nodes if in_degree[node] == 0]
        result = []

        while queue:
            # Sort queue for deterministic order (optional, aids debugging)
            queue.sort(key=lambda n: (n.y, n.x))
            node = queue.pop(0)
            result.append(node)

            # Process neighbors (nodes that have 'node' as input)
            # Need to iterate through all nodes to find neighbors since graph tracks output->input
            neighbors = []
            for potential_neighbor in self.nodes:
                if potential_neighbor.input_node == node:
                    neighbors.append(potential_neighbor)

            # Sort neighbors for deterministic order
            neighbors.sort(key=lambda n: (n.y, n.x))

            for neighbor in neighbors:
                 # Since we process node, decrement neighbor's in-degree
                 in_degree[neighbor] -= 1
                 # If in-degree becomes 0, add to queue
                 if in_degree[neighbor] == 0:
                     queue.append(neighbor)

        # Check for cycles
        if len(result) != len(self.nodes):
            print("[ERROR] Cycle detected! Processed nodes:", [n.node_type for n in result])
            # Identify nodes involved in cycle (more complex, requires tracking visited state)
            return None

        return result