import tkinter as tk
from tkinter import ttk 
from PIL import Image, ImageTk


APP_FONT = ("Segoe UI", 9)
APP_FONT_BOLD = ("Segoe UI", 10, "bold")
APP_FONT_SMALL = ("Segoe UI", 8)

class Toolbar:
    def __init__(self, master):
        self.frame = ttk.Frame(master, relief=tk.FLAT, borderwidth=0)
        self.option_var = tk.StringVar(value="Input")
        node_types = ["Input", "Output", "Brightness", "Contrast", "Blur", "Splitter", "Threshold", "Edge Detect"]
        
        self.option_menu = ttk.OptionMenu(self.frame, self.option_var, node_types[0], *node_types)
        self.option_menu.pack(side=tk.LEFT, padx=(5, 2), pady=5)
        self.create_button = ttk.Button(self.frame, text="Create Node", command=self.create_node)
        self.create_button.pack(side=tk.LEFT, padx=(2, 5), pady=5)
        self.graph = None

    def set_node_graph(self, graph): self.graph = graph

    def create_node(self):
        node_type = self.option_var.get()
        if self.graph and node_type: self.graph.add_node(node_type)

class PropertiesPanel:
    def __init__(self, master):
        self.frame = ttk.Frame(master, relief=tk.GROOVE, borderwidth=1, padding=(5, 5))        
        self.graph = None
        self.current_node = None
        self.widgets = {}

        self.title_label = ttk.Label(self.frame, text="Properties", font=APP_FONT_BOLD)
        self.title_label.pack(pady=(0, 10)) 
        
        self.placeholder_label = ttk.Label(self.frame, text="Select a node to view properties.", font=APP_FONT, foreground="grey")
        self.placeholder_label.pack(pady=20)

    def set_node_graph(self, graph): self.graph = graph

    def show_properties(self, node):
        for widget in self.widgets.values(): widget.destroy()
        self.widgets = {}
        self.placeholder_label.pack_forget() 

        self.current_node = node
        if node is None:
            self.title_label.config(text="Properties")
            self.placeholder_label.pack(pady=20) 
            return
        
        self.title_label.config(text=f"{node.node_type} Node")
        
        if hasattr(node, 'get_params') and callable(node.get_params):
            params = node.get_params()
            for name, info in params.items():
                param_frame = ttk.Frame(self.frame) 
                param_frame.pack(fill=tk.X, pady=2)
                
                label_text = name.replace('_', ' ').title()
                label = ttk.Label(param_frame, text=f"{label_text}:", width=12, anchor='w', font=APP_FONT)
                label.pack(side=tk.LEFT, padx=(0, 5))
                widget_type = info.get('type', 'label')
                if widget_type == 'slider':
                    scale = ttk.Scale(param_frame, from_=info['range'][0], to=info['range'][1], orient=tk.HORIZONTAL, command=lambda val, n=name: self.update_parameter(n, float(val)) )
                    
                    scale.set(info['value']) 
                    scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.widgets[name] = scale
                    
                    value_var = tk.DoubleVar(value=info['value'])
                    value_label = ttk.Label(param_frame, textvariable=value_var, font=APP_FONT_SMALL, width=5)
                    value_label.pack(side=tk.RIGHT, padx=(5, 0))
                    
                    scale['command'] = lambda val, n=name, v=value_var: (v.set(round(float(val), 2)), self.update_parameter(n, float(val)))
                    self.widgets[name + "_value_label"] = value_label

                elif widget_type == 'button':
                    button = ttk.Button(param_frame, text=info.get('text', name.title()), command=info['command'])
                    button.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.widgets[name] = button

                elif widget_type == 'label':
                    val_str = str(info.get('value', 'N/A'))
                    value_label = ttk.Label(param_frame, text=val_str, font=APP_FONT, anchor='w')
                    value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    self.widgets[name] = value_label
        else:
             no_params_label = ttk.Label(self.frame, text="No configurable parameters.", font=APP_FONT, foreground="grey")
             no_params_label.pack(pady=10)
             self.widgets["no_params"] = no_params_label


    def update_parameter(self, param_name, value):
        if self.current_node:
            if hasattr(self.current_node, param_name):
                setattr(self.current_node, param_name, value)
                if self.graph: self.graph.request_update() 
            else: print(f"[WARN] Parameter '{param_name}' not found on node {self.current_node.node_type}")


class PreviewWindow:
    def __init__(self, master):
        self.frame = ttk.Frame(master, relief=tk.FLAT, borderwidth=0)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(self.frame, text="Output Preview", font=APP_FONT_BOLD)
        self.label.pack(pady=(5, 2))
        
        self.canvas_bg = '#555555' 
        self.canvas = tk.Canvas(self.frame, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.image_on_canvas = None
        self.tk_image = None 

    def update_image(self, pil_image):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        self.canvas.delete("all")
        
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
            img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img_copy)
            self.image_on_canvas = self.canvas.create_image(canvas_width / 2, canvas_height / 2, anchor=tk.CENTER, image=self.tk_image)

        except Exception as e: self.canvas.after(10, self._draw_error_text)

    def _draw_no_output_text(self):
        if self.image_on_canvas is None:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1: self.canvas.create_text(canvas_width/2, canvas_height/2, text="No Output", fill="white", anchor=tk.CENTER, font=APP_FONT)

    def _draw_error_text(self):
        if self.image_on_canvas is None:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1: self.canvas.create_text(canvas_width/2, canvas_height/2, text="Preview Error", fill="#FF8888", anchor=tk.CENTER, font=APP_FONT)