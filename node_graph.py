import tkinter as tk
from nodes.input_node import InputNode
from nodes.brightness_node import BrightnessNode
from nodes.output_node import OutputNode
from nodes.contrast_node import ContrastNode 
from nodes.blur_node import BlurNode         
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
        self.links = [] 

        self.canvas_bg_color = '#4D4D4D' 
        self.canvas = tk.Canvas(master, width=800, height=600, bg=self.canvas_bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.selected_node = None
        self.linking_in_progress = False
        self.link_start_node = None
        self.link_start_pos = None
        self.temporary_link_line = None
        self.drag_canvas = False
        self.last_drag_x = 0
        self.last_drag_y = 0
        self.pan_sensitivity = 0.02 
        
        self.needs_update = False 
        self.debounce_time = 0.05 
        self.update_scheduled_id = None 

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<ButtonPress-2>", self.on_canvas_pan_press) 
        self.canvas.bind("<ButtonPress-3>", self.on_canvas_context_menu) 
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<B2-Motion>", self.on_canvas_pan_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<ButtonRelease-2>", self.on_canvas_pan_release)
        self.canvas.bind("<MouseWheel>", self.on_zoom) 
        
        self.canvas.bind("<Button-4>", lambda e: self.on_zoom(e, 1)) 
        self.canvas.bind("<Button-5>", lambda e: self.on_zoom(e, -1)) 
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.master.bind_all("<Delete>", self.delete_selected) 
        self.master.bind_all("<BackSpace>", self.delete_selected) 
        
        self.node_classes = {"Input": InputNode, "Brightness": BrightnessNode, "Output": OutputNode, "Contrast": ContrastNode, "Blur": BlurNode, "Splitter": SplitterNode, "Threshold": ThresholdNode, "Edge Detect": EdgeNode, }
        

    def add_node(self, node_type, x=None, y=None):
        node_class = self.node_classes.get(node_type)
        if node_class:
            if x is None or y is None:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                view_x = self.canvas.canvasx(0) 
                view_y = self.canvas.canvasy(0) 
                x = view_x + canvas_width / 2
                y = view_y + canvas_height / 2

            node = node_class(self, x, y)
            self.nodes.append(node)
            node.draw()
            self.request_update() 
            return node
        else: return None

    def select_node(self, node):
        if self.selected_node and self.selected_node != node: self.selected_node.deselect()
        self.selected_node = node
        if node:
            node.selected = True 
            node.node_graph.canvas.itemconfig(node.id, outline="deep sky blue", width=2) 

    def delete_selected(self, event=None):
        if self.selected_node:
            node_to_delete = self.selected_node
            self.select_node(None) 
            node_to_delete.delete() 
            if node_to_delete in self.nodes: self.nodes.remove(node_to_delete)
            self.draw_links() 
            self.request_update() 
        else: print("[INFO] No node selected to delete.")

    def on_canvas_press(self, event):
        self.canvas.focus_set()
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        clicked_on_node = None
        for node in reversed(self.nodes): 
            if node.is_within(canvas_x, canvas_y):
                if hasattr(node, 'on_element_click') and node.on_element_click(canvas_x, canvas_y): return
                if node.is_over_connector(canvas_x, canvas_y):
                     self.on_connector_press(event, node, canvas_x, canvas_y)
                     return
                clicked_on_node = node
                break

        if clicked_on_node: clicked_on_node.on_press(event)
        else:
            if self.selected_node: self.selected_node.deselect()
            self.select_node(None)

    def on_canvas_drag(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if self.linking_in_progress: self.canvas.coords(self.temporary_link_line, self.link_start_pos[0], self.link_start_pos[1], canvas_x, canvas_y)
        elif self.selected_node: self.selected_node.on_drag(event)
             
    def on_canvas_release(self, event):
        if self.linking_in_progress: self.on_link_release(event)

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
        for node_type in self.node_classes: menu.add_command(label=f"Add {node_type}", command=lambda nt=node_type: self.add_node(nt, canvas_x, canvas_y))
        if self.selected_node:
            menu.add_separator()
            menu.add_command(label=f"Delete {self.selected_node.node_type}", command=self.delete_selected)
        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

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
            if node.is_within(canvas_x, canvas_y): break

    def on_connector_press(self, event, node, canvas_x, canvas_y):
        connector_type = node.get_connector_type(canvas_x, canvas_y)
        if connector_type == "output":
            self.linking_in_progress = True
            self.link_start_node = node
            self.link_start_pos = node.get_output_pos()
            self.temporary_link_line = self.canvas.create_line(self.link_start_pos[0], self.link_start_pos[1], canvas_x, canvas_y,fill="cyan", width=2, dash=(4, 4), tags="temp_link")
            self.canvas.lift(self.temporary_link_line)
        elif connector_type == "input":
             if node.input_node:
                 existing_link = self.find_link(node.input_node, node)
                 if existing_link: self.remove_link(existing_link) 
                 node.disconnect_input() 

    def on_link_release(self, event):
        if not self.linking_in_progress: return

        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        link_completed = False

        for target_node in self.nodes:
            if target_node != self.link_start_node and target_node.input_hit(canvas_x, canvas_y):
                if target_node.input_node:
                     old_source_node = target_node.input_node
                     existing_link = self.find_link(old_source_node, target_node)
                     if existing_link: self.remove_link(existing_link) 
                     target_node.disconnect_input() 

                self.add_link(self.link_start_node, target_node) 
                link_completed = True
                break

        if not link_completed: print("[LINK] Link released over empty space or invalid target.")

        if self.temporary_link_line:
            self.canvas.delete(self.temporary_link_line)
            self.temporary_link_line = None
        self.linking_in_progress = False
        self.link_start_node = None
        self.link_start_pos = None

    def add_link(self, start_node, end_node):
        if self.find_link(start_node, end_node): return

        x1, y1 = start_node.get_output_pos()
        x2, y2 = end_node.get_input_pos()
        line_id = self.canvas.create_line(x1, y1, x2, y2, fill="#a0a0a0", width=2, tags="link")
        link_data = (start_node, end_node, line_id)
        self.links.append(link_data)
        start_node.connect_output(end_node)
        
    def remove_link(self, link_data):
         start_node, end_node, line_id = link_data
         self.canvas.delete(line_id)
         if link_data in self.links: self.links.remove(link_data)

    def find_link(self, start_node, end_node):
         for link in self.links:
             if link[0] == start_node and link[1] == end_node: return link
         return None

    def draw_links(self):
        links_to_remove = []
        for i, (start, end, line_id) in enumerate(self.links):
             if start not in self.nodes or end not in self.nodes:
                 self.canvas.delete(line_id)
                 links_to_remove.append(self.links[i])
                 continue

             start_pos = start.get_output_pos()
             end_pos = end.get_input_pos()
             if start_pos and end_pos:
                 self.canvas.coords(line_id, start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                 self.canvas.itemconfig(line_id, state='normal') 
             else: self.canvas.itemconfig(line_id, state='hidden') 
        
        for link in links_to_remove:
            if link in self.links: self.links.remove(link)


    def update_node_links(self, node):
        links_to_update = []
        if node.input_node:
            link = self.find_link(node.input_node, node)
            if link: links_to_update.append(link)
        
        for target_node in node.output_nodes:
             link = self.find_link(node, target_node)
             if link: links_to_update.append(link)

        for start, end, line_id in links_to_update:
             start_pos = start.get_output_pos()
             end_pos = end.get_input_pos()
             if start_pos and end_pos:
                 self.canvas.coords(line_id, start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                 self.canvas.itemconfig(line_id, state='normal')
             else: self.canvas.itemconfig(line_id, state='hidden')

    def request_update(self):
         self.needs_update = True
         self.schedule_update()

    def schedule_update(self):
         if self.update_scheduled_id:
             try: self.master.after_cancel(self.update_scheduled_id)
             except ValueError: pass
             self.update_scheduled_id = None 
         self.update_scheduled_id = self.master.after(int(self.debounce_time * 1000), self._process_if_needed)

    def _process_if_needed(self):
         self.update_scheduled_id = None
         if self.needs_update: 
            self.needs_update = False
            self.process_graph() 
         else: pass

    def process_graph(self):
        execution_order = self.get_execution_order()
        if execution_order is None:
            print("[ERROR] Cyclic dependency detected in the graph. Cannot process.")
            if self.preview_window: self.preview_window.update_image(None) ; return
        
        processed_count = 0
        for node in execution_order:
             try:
                node.process() 
                processed_count += 1
             except Exception as e: print(f"[ERROR] Failed to process node {node.node_type}: {e}")
        
        final_output_image = None
        output_nodes_in_order = [node for node in execution_order if isinstance(node, OutputNode)]
        if output_nodes_in_order: final_output_image = output_nodes_in_order[0].output_data
        else:
            all_output_nodes = [node for node in self.nodes if isinstance(node, OutputNode)]
            if all_output_nodes: final_output_image = all_output_nodes[0].output_data
                 
        if self.preview_window: self.preview_window.update_image(final_output_image)
        self.draw_links()


    def get_execution_order(self):
        graph = {node: set() for node in self.nodes}
        in_degree = {node: 0 for node in self.nodes}
        
        for node in self.nodes:
            if node.input_node: 
                 source_node = node.input_node
                 if source_node in graph: 
                     if node not in graph[source_node]:
                          graph[source_node].add(node)
                          in_degree[node] += 1
        
        queue = [node for node in self.nodes if in_degree[node] == 0]
        result = []

        while queue:
            queue.sort(key=lambda n: (n.y, n.x))
            node = queue.pop(0)
            result.append(node)
            
            neighbors = []
            for potential_neighbor in self.nodes:
                if potential_neighbor.input_node == node: neighbors.append(potential_neighbor)
            
            neighbors.sort(key=lambda n: (n.y, n.x))

            for neighbor in neighbors:
                 in_degree[neighbor] -= 1
                 if in_degree[neighbor] == 0: queue.append(neighbor)

        
        if len(result) != len(self.nodes):
            print("[ERROR] Cycle detected! Processed nodes:", [n.node_type for n in result])
            return None

        return result