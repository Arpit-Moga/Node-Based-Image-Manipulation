import tkinter as tk

NODE_FONT_NORMAL = ("Segoe UI", 9)
NODE_FONT_BOLD = ("Segoe UI", 10, "bold")
NODE_FONT_SMALL = ("Segoe UI", 8)


class BaseNode:
    def __init__(self, node_graph, node_type, x, y):
        self.node_graph = node_graph
        self.node_type = node_type
        self.x = x
        self.y = y
        self.width = 150
        
        self.height = 120
        self.title_height = 25
        self.selected = False
        self.id = None 
        self.text_id = None 
        self.ui_elements = {} 
        self.widget_windows = {} 
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.input_data = None
        self.output_data = None
        self.input_node = None
        self.output_nodes = []
        self.input_connector = None
        self.output_connector = None
        self.connector_radius = 6
        
        self.node_tag = f"node_{id(self)}"

        self.node_color = "#F0F0F0" 
        self.title_bg_color = "#D0D0D0" 
        self.outline_color = "#333333" 
        self.selected_outline_color = "#007AFF" 
        self.connector_in_color = "#4488FF" 
        self.connector_out_color = "#FF6666" 
        self.connector_outline = "#222222"

    def draw(self):        
        self.id = self.node_graph.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.node_color, outline=self.outline_color, width=1, tags=("node", self.node_tag))

        self.text_id = self.node_graph.canvas.create_text(
            self.x + self.width / 2, self.y + self.title_height / 2,
            text=self.node_type, anchor=tk.CENTER, font=NODE_FONT_BOLD, 
            tags=("node_text", self.node_tag))
        
        input_pos = self.get_input_pos()
        if input_pos:
            self.input_connector = self.node_graph.canvas.create_oval(
                input_pos[0] - self.connector_radius, input_pos[1] - self.connector_radius,
                input_pos[0] + self.connector_radius, input_pos[1] + self.connector_radius,
                fill=self.connector_in_color, outline=self.connector_outline, width=1,
                tags=("connector", "input", self.node_tag))

        output_pos = self.get_output_pos()
        if output_pos is not None:
            self.output_connector = self.node_graph.canvas.create_oval(
                output_pos[0] - self.connector_radius, output_pos[1] - self.connector_radius,
                output_pos[0] + self.connector_radius, output_pos[1] + self.connector_radius,
                fill=self.connector_out_color, outline=self.connector_outline, width=1,
                tags=("connector", "output", self.node_tag))
        else: self.output_connector = None

        self.draw_controls() 
        self.node_graph.canvas.tag_bind(self.node_tag, "<ButtonPress-1>", self.on_press)
        self.node_graph.canvas.tag_bind(self.node_tag, "<B1-Motion>", self.on_drag)
        self.node_graph.canvas.tag_bind(self.node_tag, "<ButtonRelease-1>", self.on_release)

    def draw_controls(self): pass 

    def get_control_area_start_y(self): return self.y + self.title_height + 5

    def on_press(self, event):
        canvas_x = self.node_graph.canvas.canvasx(event.x)
        canvas_y = self.node_graph.canvas.canvasy(event.y)
        clicked_items = self.node_graph.canvas.find_overlapping(canvas_x-1, canvas_y-1, canvas_x+1, canvas_y+1)
        if not clicked_items or not any(self.node_tag in self.node_graph.canvas.gettags(item) for item in clicked_items): return

        top_item = clicked_items[-1]
        item_tags = self.node_graph.canvas.gettags(top_item)

        if "connector" in item_tags and self.node_tag in item_tags:
            if self.is_over_connector(canvas_x, canvas_y):
                self.node_graph.on_connector_press(event, self, canvas_x, canvas_y)
                return

        is_widget_window = False
        try:
            if self.node_graph.canvas.itemcget(top_item, 'window') and self.node_tag in item_tags: is_widget_window = True
        except tk.TclError: pass

        if is_widget_window: return 
        self.node_graph.select_node(self) 
        self.drag_offset_x = canvas_x - self.x
        self.drag_offset_y = canvas_y - self.y
        self.node_graph.canvas.lift(self.node_tag)


    def on_drag(self, event):
        if self.selected:
            canvas_x = self.node_graph.canvas.canvasx(event.x)
            canvas_y = self.node_graph.canvas.canvasy(event.y)
            new_x = canvas_x - self.drag_offset_x
            new_y = canvas_y - self.drag_offset_y
            dx = new_x - self.x
            dy = new_y - self.y

            self.node_graph.canvas.move(self.node_tag, dx, dy)
            self.x = new_x
            self.y = new_y
            self.update_ui_element_positions()
            self.node_graph.update_node_links(self)

    def on_release(self, event):
        if self.node_graph.linking_in_progress and self.node_graph.link_start_node == self:
            self.node_graph.on_link_release(event)
            return

    def select(self):
         if not self.selected:
             self.selected = True
             self.node_graph.canvas.itemconfig(self.id, outline=self.selected_outline_color, width=2)

    def deselect(self):
        if self.selected:
            self.selected = False
            self.node_graph.canvas.itemconfig(self.id, outline=self.outline_color, width=1)
    
    def is_within(self, x, y):
        margin = self.connector_radius
        return (self.x - margin <= x <= self.x + self.width + margin and self.y - margin <= y <= self.y + self.height + margin)

    def is_over_connector(self, x, y): return self.input_hit(x, y) or self.output_hit(x, y)

    def get_connector_type(self, x, y):
        if self.input_hit(x, y): return "input"
        if self.output_hit(x, y): return "output"
        return None

    def input_hit(self, x, y):
        if not self.input_connector: return False
        cx, cy = self.get_input_pos()
        return (x - cx)**2 + (y - cy)**2 <= self.connector_radius**2

    def output_hit(self, x, y):
        if not self.output_connector: return False
        output_pos = self.get_output_pos()
        if output_pos is None: return False
        cx, cy = output_pos
        return (x - cx)**2 + (y - cy)**2 <= self.connector_radius**2
    
    def get_input_pos(self): return self.x, self.y + self.title_height + (self.height - self.title_height) / 2

    def get_output_pos(self): return self.x + self.width, self.y + self.title_height + (self.height - self.title_height) / 2

    def connect_input(self, source_node):
        self.disconnect_input() 
        self.input_node = source_node
        if self not in source_node.output_nodes: source_node.output_nodes.append(self)
        self.node_graph.needs_update = True

    def connect_output(self, target_node): target_node.connect_input(self) 

    def disconnect_input(self):
        if self.input_node:
            source_node = self.input_node 
            self.input_node = None
            self.input_data = None
            if self in source_node.output_nodes: source_node.output_nodes.remove(self)
            self.node_graph.needs_update = True

    def disconnect_output(self, target_node):
         if target_node in self.output_nodes:
             if target_node.input_node == self: target_node.disconnect_input() 

    def disconnect_all(self):
        self.disconnect_input()
        outputs_to_disconnect = list(self.output_nodes)
        for node in outputs_to_disconnect:
            if node.input_node == self: node.disconnect_input()
        self.output_nodes = []


    def delete(self):
        self.disconnect_all()        
        for key, widget in list(self.ui_elements.items()):
             if isinstance(widget, tk.Widget):
                 widget.destroy()
                 del self.ui_elements[key]

        self.node_graph.canvas.delete(self.node_tag)
        self.ui_elements = {}
        self.widget_windows = {}
        self.input_connector = None
        self.output_connector = None
        self.id = None
        self.text_id = None

    def process(self):
        if self.input_node: self.input_data = self.input_node.output_data
        else: self.input_data = None
        self.output_data = self.input_data