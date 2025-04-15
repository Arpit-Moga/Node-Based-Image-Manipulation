import tkinter as tk
from tkinter import ttk 
from nodes.base_node import BaseNode
from PIL import Image

class SplitterNode(BaseNode):
    MODES = ["Red", "Green", "Blue", "Alpha", "Gray (R)", "Gray (G)", "Gray (B)", "Gray (A)"]
    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Color Splitter", x, y)
        self.output_mode = SplitterNode.MODES[0] 
        self.height = 130 

    def draw_controls(self):
        super().draw_controls()
        control_y = self.get_control_area_start_y()
        widget_x = self.x + 10
        widget_width = self.width - 20
        label_height_estimate = 20
        
        label = tk.Label(self.node_graph.canvas, text="Output Channel:", bg="#e0e0e0", font=("Arial", 8), anchor='w')
        self.ui_elements['mode_label_widget'] = label
        label_window_id = self.node_graph.canvas.create_window(widget_x, control_y, width=widget_width, anchor=tk.NW, window=label,tags=(self.node_tag,))
        self.widget_windows['mode_label'] = label_window_id

        dropdown_y = control_y + label_height_estimate + 5
        self.mode_var = tk.StringVar(value=self.output_mode)
        dropdown = ttk.Combobox(self.node_graph.canvas,textvariable=self.mode_var,values=SplitterNode.MODES,state="readonly", width=int(widget_width / 7) )
        dropdown.bind("<<ComboboxSelected>>", self._update_mode)
        self.ui_elements['mode_dropdown_widget'] = dropdown
        dropdown_window_id = self.node_graph.canvas.create_window(widget_x, dropdown_y, width=widget_width, anchor=tk.NW, window=dropdown,tags=(self.node_tag,))
        self.widget_windows['mode_dropdown'] = dropdown_window_id

    def _update_mode(self, event=None):
        new_mode = self.mode_var.get()
        if self.output_mode != new_mode:
            self.output_mode = new_mode
            print(f"[PARAM] Splitter mode changed to: {self.output_mode}")
            self.node_graph.request_update()

    def process(self):
        super().process() 
        self.output_data = None 
        if self.input_data and isinstance(self.input_data, Image.Image):
            try:
                bands = self.input_data.split()
                num_bands = len(bands)
                mode_parts = self.output_mode.split() 
                target_channel = mode_parts[-1].replace('(', '').replace(')', '') 
                make_grayscale = "Gray" in mode_parts

                channel_index = -1
                if target_channel == 'R' and num_bands >= 1: channel_index = 0
                elif target_channel == 'G' and num_bands >= 2: channel_index = 1
                elif target_channel == 'B' and num_bands >= 3: channel_index = 2
                elif target_channel == 'A' and num_bands == 4: channel_index = 3
                elif target_channel == 'A' and num_bands < 4:
                    self.output_data = Image.new('L', self.input_data.size, 0)
                    return 
                elif channel_index == -1:
                     self.output_data = Image.new('L', self.input_data.size, 0) 
                     return 
                selected_band = bands[channel_index]
                if make_grayscale:self.output_data = selected_band
                else: self.output_data = selected_band 

            except Exception as e: self.output_data = None
        else: self.output_data = None