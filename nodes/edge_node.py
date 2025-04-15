import tkinter as tk
from tkinter import ttk
from nodes.base_node import BaseNode
from PIL import Image, ImageFilter, ImageOps

class EdgeNode(BaseNode):
    METHODS = ["Sobel", "Canny (cv2)"]
    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Edge Detection", x, y)
        self.method = EdgeNode.METHODS[0]
        self.overlay = tk.BooleanVar(value=False) 
        
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150
        
        self.height = 160 

    def draw_controls(self):
        super().draw_controls()
        control_y = self.get_control_area_start_y()
        widget_x = self.x + 10
        widget_width = self.width - 20
        label_h = 20
        widget_y = control_y
        
        method_label = tk.Label(self.node_graph.canvas, text="Method:", bg="#e0e0e0", font=("Arial", 8), anchor='w')
        self.ui_elements['method_label_widget'] = method_label
        method_label_window_id = self.node_graph.canvas.create_window(widget_x, widget_y, width=widget_width, anchor=tk.NW, window=method_label,tags=(self.node_tag,))
        self.widget_windows['method_label'] = method_label_window_id
        widget_y += label_h + 5

        self.method_var = tk.StringVar(value=self.method)
        method_dropdown = ttk.Combobox(self.node_graph.canvas, textvariable=self.method_var, values=EdgeNode.METHODS,state="readonly", width=int(widget_width / 7))
        method_dropdown.bind("<<ComboboxSelected>>", self._update_method)
        self.ui_elements['method_dropdown_widget'] = method_dropdown
        method_dropdown_window_id = self.node_graph.canvas.create_window(widget_x, widget_y, width=widget_width, anchor=tk.NW, window=method_dropdown,tags=(self.node_tag,))
        self.widget_windows['method_dropdown'] = method_dropdown_window_id
        widget_y += label_h + 10
        
        overlay_check = tk.Checkbutton(self.node_graph.canvas, text="Overlay on Original", variable=self.overlay,command=self._update_overlay, bg="#e0e0e0", anchor='w',font=("Arial", 8))
        self.ui_elements['overlay_check_widget'] = overlay_check
        overlay_check_window_id = self.node_graph.canvas.create_window(widget_x, widget_y, width=widget_width, anchor=tk.NW, window=overlay_check,tags=(self.node_tag,))
        self.widget_windows['overlay_check'] = overlay_check_window_id
        widget_y += label_h + 5

    def _update_method(self, event=None):
        new_method = self.method_var.get()
        if self.method != new_method:
            self.method = new_method
            self.node_graph.request_update()

    def _update_overlay(self): self.node_graph.request_update()

    def process(self):
        super().process() 
        self.output_data = None
        edges_img = None
        if self.input_data and isinstance(self.input_data, Image.Image):
            try:
                img_gray = ImageOps.grayscale(self.input_data)
                if self.method == "Sobel":edges_img = img_gray.filter(ImageFilter.FIND_EDGES)
                elif self.method == "Canny (cv2)": edges_img = img_gray 
                else: edges_img = img_gray 

                if self.overlay.get() and edges_img:
                    if self.input_data.mode != 'RGB': original_rgb = self.input_data.convert('RGB')
                    else:original_rgb = self.input_data.copy()
                    if edges_img.mode != 'L':edges_l = edges_img.convert('L')
                    else:edges_l = edges_img

                    edges_white = edges_l.point(lambda p: 255 if p > 0 else 0)
                    red_edges = ImageOps.colorize(edges_white, black=(0,0,0), white=(255,0,0)).convert('RGB')
                    mask = edges_white.point(lambda p: 255 if p > 0 else 0, mode='1')
                    self.output_data = Image.composite(red_edges, original_rgb, mask)
                else: self.output_data = edges_img
            except Exception as e: self.output_data = None
        else: self.output_data = None