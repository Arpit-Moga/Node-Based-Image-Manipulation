###### THIS IS WORKING!!!
# nodes/base_node.py
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
        # Height might need adjustment depending on controls added by subclasses
        self.height = 120
        self.title_height = 25
        self.selected = False
        self.id = None # Canvas ID for the main rectangle
        self.text_id = None # Canvas ID for title text
        self.ui_elements = {} # Stores widget references mainly
        self.widget_windows = {} # Stores canvas window IDs for widgets
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.input_data = None
        self.output_data = None
        self.input_node = None
        self.output_nodes = []
        self.input_connector = None
        self.output_connector = None
        self.connector_radius = 6
        # Generate unique tag for all parts of this node instance
        self.node_tag = f"node_{id(self)}"

        self.node_color = "#F0F0F0" # Light gray node body
        self.title_bg_color = "#D0D0D0" # Medium gray title bar
        self.outline_color = "#333333" # Dark gray outline
        self.selected_outline_color = "#007AFF" # System blue for selection
        self.connector_in_color = "#4488FF" # Blue input
        self.connector_out_color = "#FF6666" # Reddish output
        self.connector_outline = "#222222"

    def draw(self):
        # Node Body
        self.id = self.node_graph.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.node_color, outline=self.outline_color, width=1, tags=("node", self.node_tag))

        # Title Bar
        title_bg = self.node_graph.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.title_height,
            fill=self.title_bg_color, outline="", tags=("node_title", self.node_tag))

        # Node Title Text - Use updated font
        self.text_id = self.node_graph.canvas.create_text(
            self.x + self.width / 2, self.y + self.title_height / 2,
            text=self.node_type, anchor=tk.CENTER, font=NODE_FONT_BOLD, # Use bold font
            tags=("node_text", self.node_tag))

        # Input Connector
        input_pos = self.get_input_pos()
        if input_pos:
            self.input_connector = self.node_graph.canvas.create_oval(
                input_pos[0] - self.connector_radius, input_pos[1] - self.connector_radius,
                input_pos[0] + self.connector_radius, input_pos[1] + self.connector_radius,
                fill=self.connector_in_color, outline=self.connector_outline, width=1,
                tags=("connector", "input", self.node_tag))

        # Output Connector
        output_pos = self.get_output_pos()
        if output_pos is not None:
            self.output_connector = self.node_graph.canvas.create_oval(
                output_pos[0] - self.connector_radius, output_pos[1] - self.connector_radius,
                output_pos[0] + self.connector_radius, output_pos[1] + self.connector_radius,
                fill=self.connector_out_color, outline=self.connector_outline, width=1,
                tags=("connector", "output", self.node_tag))
        else:
            self.output_connector = None

        # Draw Controls (Subclasses implement this, ensure they use self.node_tag and ttk widgets)
        self.draw_controls() # This might need height adjustment after controls are drawn

        # Event Binding
        self.node_graph.canvas.tag_bind(self.node_tag, "<ButtonPress-1>", self.on_press)
        self.node_graph.canvas.tag_bind(self.node_tag, "<B1-Motion>", self.on_drag)
        self.node_graph.canvas.tag_bind(self.node_tag, "<ButtonRelease-1>", self.on_release)

    def draw_controls(self):
        """Subclasses override this. Use ttk widgets and common fonts."""
        pass # Base implementation does nothing

    def get_control_area_start_y(self):
        # Add a little padding below title bar
        return self.y + self.title_height + 5

    def on_press(self, event):
        canvas_x = self.node_graph.canvas.canvasx(event.x)
        canvas_y = self.node_graph.canvas.canvasy(event.y)
        clicked_items = self.node_graph.canvas.find_overlapping(canvas_x-1, canvas_y-1, canvas_x+1, canvas_y+1)
        if not clicked_items or not any(self.node_tag in self.node_graph.canvas.gettags(item) for item in clicked_items):
             return

        top_item = clicked_items[-1]
        item_tags = self.node_graph.canvas.gettags(top_item)

        if "connector" in item_tags and self.node_tag in item_tags:
            if self.is_over_connector(canvas_x, canvas_y):
                self.node_graph.on_connector_press(event, self, canvas_x, canvas_y)
                return

        is_widget_window = False
        try:
            if self.node_graph.canvas.itemcget(top_item, 'window') and self.node_tag in item_tags:
                 is_widget_window = True
        except tk.TclError:
             pass

        if is_widget_window:
             return # Let Tkinter handle widget clicks

        # Select node if click wasn't on widget/connector
        self.node_graph.select_node(self) # Selection highlighting handled by NodeGraph now
        self.drag_offset_x = canvas_x - self.x
        self.drag_offset_y = canvas_y - self.y
        self.node_graph.canvas.lift(self.node_tag)


    def on_drag(self, event):
        # Only drag if selected AND the drag didn't start on a widget
        if self.selected:
            canvas_x = self.node_graph.canvas.canvasx(event.x)
            canvas_y = self.node_graph.canvas.canvasy(event.y)
            new_x = canvas_x - self.drag_offset_x
            new_y = canvas_y - self.drag_offset_y
            dx = new_x - self.x
            dy = new_y - self.y

            # Move ALL elements tagged with the unique node tag in one go
            self.node_graph.canvas.move(self.node_tag, dx, dy)

            # Update internal coordinates
            self.x = new_x
            self.y = new_y

            # Update non-widget UI elements (e.g., InputNode preview area position)
            self.update_ui_element_positions()

            # Update connection lines
            self.node_graph.update_node_links(self)

    def on_release(self, event):
        # Check if linking was in progress FROM this node
        if self.node_graph.linking_in_progress and self.node_graph.link_start_node == self:
            # Let NodeGraph handle link completion/cancellation
            self.node_graph.on_link_release(event)
            # Don't deselect yet if linking
            return

        # If simply releasing after a drag, selection state is handled by NodeGraph's canvas click checks

    def select(self):
         if not self.selected:
             self.selected = True
             self.node_graph.canvas.itemconfig(self.id, outline=self.selected_outline_color, width=2)

    def deselect(self):
        if self.selected:
            self.selected = False
            self.node_graph.canvas.itemconfig(self.id, outline=self.outline_color, width=1)

    # --- is_within, is_over_connector, get_connector_type, input_hit, output_hit ---
    # (No changes needed in these helper methods)
    def is_within(self, x, y):
        margin = self.connector_radius
        return (self.x - margin <= x <= self.x + self.width + margin and
                self.y - margin <= y <= self.y + self.height + margin)

    def is_over_connector(self, x, y):
        # Check precisely based on connector positions
        return self.input_hit(x, y) or self.output_hit(x, y)

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

    # --- get_input_pos, get_output_pos ---
    # (No changes needed)
    def get_input_pos(self):
        return self.x, self.y + self.title_height + (self.height - self.title_height) / 2

    def get_output_pos(self):
        return self.x + self.width, self.y + self.title_height + (self.height - self.title_height) / 2


    # --- connect/disconnect methods ---
    # (No changes needed)
    def connect_input(self, source_node):
        self.disconnect_input() # Ensure only one input
        self.input_node = source_node
        if self not in source_node.output_nodes:
             source_node.output_nodes.append(self)
        print(f"[LINK] Connected {source_node.node_type} -> {self.node_type}")
        self.node_graph.needs_update = True

    def connect_output(self, target_node):
        target_node.connect_input(self) # Target handles its input

    def disconnect_input(self):
        if self.input_node:
            source_node = self.input_node # Store reference before clearing
            self.input_node = None
            self.input_data = None
            if self in source_node.output_nodes:
                source_node.output_nodes.remove(self)
            print(f"[LINK] Disconnected {source_node.node_type} from {self.node_type}")
            self.node_graph.needs_update = True

    def disconnect_output(self, target_node):
         # Disconnecting output means telling the target to disconnect its input
         if target_node in self.output_nodes:
             # Check if the target's input is actually this node before disconnecting
             if target_node.input_node == self:
                 target_node.disconnect_input() # Target handles removing from our output list via disconnect_input

    def disconnect_all(self):
        self.disconnect_input()
        # Create a copy because target.disconnect_input() modifies self.output_nodes via callbacks
        outputs_to_disconnect = list(self.output_nodes)
        for node in outputs_to_disconnect:
            if node.input_node == self:
                node.disconnect_input()
        # Ensure list is clear even if disconnect_input failed for some reason
        self.output_nodes = []


    def delete(self):
        """Removes the node and its UI elements from the canvas."""
        self.disconnect_all()
        # Destroy actual Tkinter widgets stored in ui_elements
        for key, widget in list(self.ui_elements.items()):
             if isinstance(widget, tk.Widget):
                 widget.destroy()
                 del self.ui_elements[key]

        # No need to individually delete widget windows if they are tagged
        # Just delete everything associated with the node's unique tag
        self.node_graph.canvas.delete(self.node_tag)

        # Clear tracking dictionaries
        self.ui_elements = {}
        self.widget_windows = {}
        # Clear references
        self.input_connector = None
        self.output_connector = None
        self.id = None
        self.text_id = None


    def process(self):
        """Base processing: Get input data."""
        if self.input_node:
            self.input_data = self.input_node.output_data
        else:
            self.input_data = None
        # Default: pass through data
        self.output_data = self.input_data

    def update_ui_element_positions(self):
        """Handles NON-WIDGET UI elements. Override if needed (like InputNode)."""
        pass

    # get_params method remains removed/commented out