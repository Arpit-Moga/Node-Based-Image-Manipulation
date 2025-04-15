# New/nodes/splitter_node.py
import tkinter as tk
from tkinter import ttk # For Combobox
from nodes.base_node import BaseNode
from PIL import Image, ImageOps
import numpy as np # For potential grayscale conversion if needed

class SplitterNode(BaseNode):
    MODES = ["Red", "Green", "Blue", "Alpha", "Gray (R)", "Gray (G)", "Gray (B)", "Gray (A)"]

    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Color Splitter", x, y)
        self.output_mode = SplitterNode.MODES[0] # Default to Red
        self.height = 130 # Increased height for dropdown

    def draw_controls(self):
        super().draw_controls()
        control_y = self.get_control_area_start_y()
        widget_x = self.x + 10
        widget_width = self.width - 20
        label_height_estimate = 20

        # --- Output Channel Selector ---
        label = tk.Label(self.node_graph.canvas, text="Output Channel:", bg="#e0e0e0", font=("Arial", 8), anchor='w')
        self.ui_elements['mode_label_widget'] = label
        label_window_id = self.node_graph.canvas.create_window(
            widget_x, control_y, width=widget_width, anchor=tk.NW, window=label,
            tags=(self.node_tag,)
        )
        self.widget_windows['mode_label'] = label_window_id

        dropdown_y = control_y + label_height_estimate + 5
        self.mode_var = tk.StringVar(value=self.output_mode)
        dropdown = ttk.Combobox(
            self.node_graph.canvas,
            textvariable=self.mode_var,
            values=SplitterNode.MODES,
            state="readonly", # Prevent typing custom values
            width=int(widget_width / 7) # Adjust width based on font/content
        )
        dropdown.bind("<<ComboboxSelected>>", self._update_mode)
        self.ui_elements['mode_dropdown_widget'] = dropdown
        dropdown_window_id = self.node_graph.canvas.create_window(
            widget_x, dropdown_y, width=widget_width, anchor=tk.NW, window=dropdown,
            tags=(self.node_tag,)
        )
        self.widget_windows['mode_dropdown'] = dropdown_window_id

    def _update_mode(self, event=None):
        new_mode = self.mode_var.get()
        if self.output_mode != new_mode:
            self.output_mode = new_mode
            print(f"[PARAM] Splitter mode changed to: {self.output_mode}")
            self.node_graph.request_update()

    def process(self):
        super().process() # Gets self.input_data
        self.output_data = None # Default to None

        if self.input_data and isinstance(self.input_data, Image.Image):
            try:
                bands = self.input_data.split()
                num_bands = len(bands)
                mode_parts = self.output_mode.split() # e.g., ["Gray", "(R)"] or ["Red"]
                target_channel = mode_parts[-1].replace('(', '').replace(')', '') # R, G, B, A
                make_grayscale = "Gray" in mode_parts

                channel_index = -1
                if target_channel == 'R' and num_bands >= 1: channel_index = 0
                elif target_channel == 'G' and num_bands >= 2: channel_index = 1
                elif target_channel == 'B' and num_bands >= 3: channel_index = 2
                elif target_channel == 'A' and num_bands == 4: channel_index = 3
                # Handle case where requested channel doesn't exist (e.g., Alpha on RGB)
                elif target_channel == 'A' and num_bands < 4:
                    print("[WARN] Splitter: Alpha channel requested but image is not RGBA. Outputting black.")
                    # Create a black image of the same size
                    self.output_data = Image.new('L', self.input_data.size, 0)
                    return # Exit early
                elif channel_index == -1:
                     print(f"[WARN] Splitter: Could not find channel {target_channel} in image with bands {self.input_data.getbands()}")
                     self.output_data = Image.new('L', self.input_data.size, 0) # Output black on error
                     return # Exit early


                selected_band = bands[channel_index]

                if make_grayscale:
                    # Output is already grayscale if we selected a single band
                    self.output_data = selected_band
                else:
                    # Recreate a color image with only the selected channel non-zero
                    # This might not be the typical expectation, usually splitter outputs grayscale.
                    # For direct color channel output, we output the grayscale band.
                    # To output "Red" as a *red* image requires creating a blank image
                    # and pasting the red channel data into the red channel of the blank.
                    # Let's stick to outputting the grayscale representation of the channel.
                    self.output_data = selected_band # Output the selected channel as grayscale

            except Exception as e:
                print(f"[ERROR] Splitter processing failed: {e}")
                self.output_data = None
        else:
            self.output_data = None