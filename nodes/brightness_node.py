import tkinter as tk
from nodes.base_node import BaseNode
from PIL import ImageEnhance, Image

class BrightnessNode(BaseNode):
    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Brightness", x, y)
        self.brightness_factor = 1.0
        self.height = 130 

    def draw_controls(self):
        super().draw_controls()
        control_y = self.get_control_area_start_y()
        widget_x = self.x + 10
        widget_width = self.width - 20
        label_height_estimate = 20

        
        label = tk.Label(self.node_graph.canvas, text="Brightness:", bg="#e0e0e0", font=("Arial", 8), anchor='w')
        self.ui_elements['brightness_label_widget'] = label
        label_window_id = self.node_graph.canvas.create_window(widget_x, control_y, width=widget_width, anchor=tk.NW, window=label,tags=(self.node_tag,))
        self.widget_windows['brightness_label'] = label_window_id

        
        slider_y = control_y + label_height_estimate
        slider = tk.Scale(self.node_graph.canvas, from_=0.0, to=3.0, resolution=0.05,orient=tk.HORIZONTAL, length=widget_width, sliderlength=15, width=10,command=self._update_brightness, bg="#e0e0e0", troughcolor="#cccccc",highlightthickness=0, showvalue=False)
        slider.set(self.brightness_factor)
        self.ui_elements['brightness_slider_widget'] = slider
        slider_window_id = self.node_graph.canvas.create_window(widget_x, slider_y, width=widget_width, anchor=tk.NW, window=slider,tags=(self.node_tag,))
        self.widget_windows['brightness_slider'] = slider_window_id

        
        value_label_y = slider_y + 30 
        self.brightness_value_var = tk.StringVar(value=f"{self.brightness_factor:.2f}")
        value_label = tk.Label(self.node_graph.canvas, textvariable=self.brightness_value_var,bg="#e0e0e0", font=("Arial", 8), anchor='center')
        self.ui_elements['brightness_value_label_widget'] = value_label
        value_label_window_id = self.node_graph.canvas.create_window(widget_x + widget_width/2, value_label_y, anchor=tk.N, window=value_label,tags=(self.node_tag,))
        self.widget_windows['brightness_value_label'] = value_label_window_id

    def _update_brightness(self, value_str):
        try:
            new_factor = float(value_str)
            if abs(self.brightness_factor - new_factor) > 1e-6: 
                self.brightness_factor = new_factor
                if hasattr(self, 'brightness_value_var'): self.brightness_value_var.set(f"{self.brightness_factor:.2f}")
                self.node_graph.request_update()
        except ValueError:print(f"[ERROR] Invalid brightness slider value: {value_str}")

    def process(self):
        super().process() 
        if self.input_data and isinstance(self.input_data, Image.Image):
            try:
                image_copy = self.input_data.copy()
                enhancer = ImageEnhance.Brightness(image_copy)
                self.output_data = enhancer.enhance(self.brightness_factor)
                
            except Exception as e:self.output_data = self.input_data
        else: self.output_data = None