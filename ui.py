import tkinter as tk
from tkinter import ttk # Import ttk
from PIL import Image, ImageTk

# Define a common font
APP_FONT = ("Segoe UI", 9)
APP_FONT_BOLD = ("Segoe UI", 10, "bold")
APP_FONT_SMALL = ("Segoe UI", 8)

class Toolbar:
    def __init__(self, master):
        # Use ttk.Frame for theme integration
        self.frame = ttk.Frame(master, relief=tk.FLAT, borderwidth=0)
        # pack is handled in main.py

        self.option_var = tk.StringVar(value="Input")

        node_types = [
            "Input", "Output", "Brightness", "Contrast", "Blur",
            "Splitter", "Threshold", "Edge Detect"
        ]

        # Use ttk.OptionMenu if desired (looks more native sometimes)
        # Requires slightly different setup than tk.OptionMenu
        # Or keep tk.OptionMenu and style the menubutton part if possible
        self.option_menu = ttk.OptionMenu(self.frame, self.option_var, node_types[0], *node_types)
        self.option_menu.pack(side=tk.LEFT, padx=(5, 2), pady=5)

        # Use ttk.Button
        self.create_button = ttk.Button(self.frame, text="Create Node", command=self.create_node)
        self.create_button.pack(side=tk.LEFT, padx=(2, 5), pady=5)

        self.graph = None

    def set_node_graph(self, graph):
        self.graph = graph

    def create_node(self):
        node_type = self.option_var.get()
        if self.graph and node_type:
            self.graph.add_node(node_type)

class PropertiesPanel:
    def __init__(self, master):
        # Use ttk.Frame, add padding
        self.frame = ttk.Frame(master, relief=tk.GROOVE, borderwidth=1, padding=(5, 5))
        # pack is handled in main.py
        self.graph = None
        self.current_node = None
        self.widgets = {}

        # Use ttk.Label, specify font
        self.title_label = ttk.Label(self.frame, text="Properties", font=APP_FONT_BOLD)
        self.title_label.pack(pady=(0, 10)) # Add padding below title

        # Placeholder label if no node is selected
        self.placeholder_label = ttk.Label(self.frame, text="Select a node to view properties.", font=APP_FONT, foreground="grey")
        self.placeholder_label.pack(pady=20)

    def set_node_graph(self, graph):
        self.graph = graph

    def show_properties(self, node):
        # Clear previous widgets
        for widget in self.widgets.values():
            widget.destroy()
        self.widgets = {}
        self.placeholder_label.pack_forget() # Hide placeholder

        self.current_node = node
        if node is None:
            self.title_label.config(text="Properties")
            self.placeholder_label.pack(pady=20) # Show placeholder
            return

        self.title_label.config(text=f"{node.node_type} Node")

        # If nodes implement get_params() later, this will populate the panel
        if hasattr(node, 'get_params') and callable(node.get_params):
            params = node.get_params()
            for name, info in params.items():
                param_frame = ttk.Frame(self.frame) # Use ttk.Frame
                param_frame.pack(fill=tk.X, pady=2)

                # Use ttk.Label
                label_text = name.replace('_', ' ').title()
                label = ttk.Label(param_frame, text=f"{label_text}:", width=12, anchor='w', font=APP_FONT)
                label.pack(side=tk.LEFT, padx=(0, 5))

                widget_type = info.get('type', 'label')

                if widget_type == 'slider':
                    # Use ttk.Scale
                    scale = ttk.Scale(
                        param_frame,
                        from_=info['range'][0],
                        to=info['range'][1],
                        # resolution not directly supported in ttk.Scale, use rounding in command if needed
                        orient=tk.HORIZONTAL,
                        command=lambda val, n=name: self.update_parameter(n, float(val)) # Pass float value
                    )
                    # ttk.Scale uses value property, not set()
                    scale.set(info['value']) # Use set() for ttk scale too
                    scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.widgets[name] = scale

                    # Optional: Add a label to show the numeric value
                    value_var = tk.DoubleVar(value=info['value'])
                    value_label = ttk.Label(param_frame, textvariable=value_var, font=APP_FONT_SMALL, width=5)
                    value_label.pack(side=tk.RIGHT, padx=(5, 0))
                    # Update value label in the command
                    scale['command'] = lambda val, n=name, v=value_var: (
                        v.set(round(float(val), 2)), # Update label var
                        self.update_parameter(n, float(val)) # Update node param
                    )
                    self.widgets[name + "_value_label"] = value_label


                elif widget_type == 'button':
                    # Use ttk.Button
                    button = ttk.Button(
                        param_frame,
                        text=info.get('text', name.title()),
                        command=info['command']
                    )
                    button.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.widgets[name] = button

                elif widget_type == 'label':
                     # Use ttk.Label
                    val_str = str(info.get('value', 'N/A'))
                    value_label = ttk.Label(param_frame, text=val_str, font=APP_FONT, anchor='w')
                    value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.widgets[name] = value_label

                # Add more parameter types (e.g., ttk.Combobox, ttk.Checkbutton) here if needed

        else:
             no_params_label = ttk.Label(self.frame, text="No configurable parameters.", font=APP_FONT, foreground="grey")
             no_params_label.pack(pady=10)
             self.widgets["no_params"] = no_params_label


    def update_parameter(self, param_name, value):
        if self.current_node:
            # Check if the attribute exists and update it
            if hasattr(self.current_node, param_name):
                setattr(self.current_node, param_name, value)
                # print(f"[PARAM] Updated {self.current_node.node_type}.{param_name} to {value}") # Reduce spam
                if self.graph:
                    self.graph.request_update() # Signal graph needs re-processing
            else:
                print(f"[WARN] Parameter '{param_name}' not found on node {self.current_node.node_type}")


class PreviewWindow:
    def __init__(self, master):
        # Use ttk Frame, adjust background if needed (or let theme handle it)
        self.frame = ttk.Frame(master, relief=tk.FLAT, borderwidth=0)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Use ttk Label, font
        self.label = ttk.Label(self.frame, text="Output Preview", font=APP_FONT_BOLD)
        self.label.pack(pady=(5, 2))

        # Canvas for image display - standard tk Canvas is fine here
        # Use a slightly lighter background than node graph?
        self.canvas_bg = '#555555' # Dark gray background for preview
        self.canvas = tk.Canvas(self.frame, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.image_on_canvas = None
        self.tk_image = None # Keep a reference

    def update_image(self, pil_image):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Clear previous content first
        self.canvas.delete("all")
        # Set background color again in case it was cleared
        self.canvas.config(bg=self.canvas_bg)
        self.image_on_canvas = None
        self.tk_image = None


        if pil_image is None:
            self.canvas.after(10, self._draw_no_output_text)
            return

        if canvas_width <= 1 or canvas_height <= 1:
            self.canvas.after(100, lambda: self.update_image(pil_image))
            return

        try:
            img_copy = pil_image.copy()
            # --- Increase Resolution/Quality ---
            # Use full canvas width/height for thumbnail bounds
            # LANCZOS is already a high-quality filter
            img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            # --- End Resolution/Quality Change ---

            self.tk_image = ImageTk.PhotoImage(img_copy)

            # self.canvas.delete("all") # Moved deletion to start of function
            self.image_on_canvas = self.canvas.create_image(
                canvas_width / 2, canvas_height / 2,
                anchor=tk.CENTER,
                image=self.tk_image
            )
        except Exception as e:
             print(f"[ERROR] Failed to update preview image: {e}")
             # self.canvas.delete("all") # Moved deletion to start of function
             self.canvas.after(10, self._draw_error_text)

    def _draw_no_output_text(self):
        if self.image_on_canvas is None:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                self.canvas.create_text(canvas_width/2, canvas_height/2, text="No Output", fill="white", anchor=tk.CENTER, font=APP_FONT)

    def _draw_error_text(self):
        if self.image_on_canvas is None:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                 self.canvas.create_text(canvas_width/2, canvas_height/2, text="Preview Error", fill="#FF8888", anchor=tk.CENTER, font=APP_FONT) # Light red text