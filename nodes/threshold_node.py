# New/nodes/threshold_node.py
import tkinter as tk
from tkinter import ttk
from nodes.base_node import BaseNode
from PIL import Image, ImageOps, ImageFilter
import numpy as np

class ThresholdNode(BaseNode):
    # Note: Otsu and Adaptive methods are typically done with OpenCV.
    # This implementation uses simple binary thresholding via Pillow.
    METHODS = ["Binary"] # Add "Otsu (cv2)", "Adaptive (cv2)" if OpenCV is integrated later

    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Threshold", x, y)
        self.threshold_value = 128
        self.method = ThresholdNode.METHODS[0]
        self.height = 160 # Increased height for controls

    def draw_controls(self):
        super().draw_controls()
        control_y = self.get_control_area_start_y()
        widget_x = self.x + 10
        widget_width = self.width - 20
        label_h = 20
        widget_y = control_y

        # --- Method Selector ---
        method_label = tk.Label(self.node_graph.canvas, text="Method:", bg="#e0e0e0", font=("Arial", 8), anchor='w')
        self.ui_elements['method_label_widget'] = method_label
        method_label_window_id = self.node_graph.canvas.create_window(
            widget_x, widget_y, width=widget_width, anchor=tk.NW, window=method_label,
            tags=(self.node_tag,)
        )
        self.widget_windows['method_label'] = method_label_window_id
        widget_y += label_h + 5

        self.method_var = tk.StringVar(value=self.method)
        method_dropdown = ttk.Combobox(
            self.node_graph.canvas, textvariable=self.method_var, values=ThresholdNode.METHODS,
            state="readonly", width=int(widget_width / 7)
        )
        method_dropdown.bind("<<ComboboxSelected>>", self._update_method)
        self.ui_elements['method_dropdown_widget'] = method_dropdown
        method_dropdown_window_id = self.node_graph.canvas.create_window(
            widget_x, widget_y, width=widget_width, anchor=tk.NW, window=method_dropdown,
            tags=(self.node_tag,)
        )
        self.widget_windows['method_dropdown'] = method_dropdown_window_id
        widget_y += label_h + 10 # More space after dropdown

        # --- Threshold Value Slider ---
        thresh_label = tk.Label(self.node_graph.canvas, text="Threshold Value:", bg="#e0e0e0", font=("Arial", 8), anchor='w')
        self.ui_elements['thresh_label_widget'] = thresh_label
        thresh_label_window_id = self.node_graph.canvas.create_window(
            widget_x, widget_y, width=widget_width, anchor=tk.NW, window=thresh_label,
            tags=(self.node_tag,)
        )
        self.widget_windows['thresh_label'] = thresh_label_window_id
        widget_y += label_h

        slider = tk.Scale(
            self.node_graph.canvas, from_=0, to=255, resolution=1,
            orient=tk.HORIZONTAL, length=widget_width, sliderlength=15, width=10,
            command=self._update_threshold, bg="#e0e0e0", troughcolor="#cccccc",
            highlightthickness=0, showvalue=False
        )
        slider.set(self.threshold_value)
        self.ui_elements['thresh_slider_widget'] = slider
        slider_window_id = self.node_graph.canvas.create_window(
            widget_x, widget_y, width=widget_width, anchor=tk.NW, window=slider,
            tags=(self.node_tag,)
        )
        self.widget_windows['thresh_slider'] = slider_window_id
        widget_y += 30 # Space for slider

        # Value Label
        self.thresh_value_var = tk.StringVar(value=f"{self.threshold_value}")
        value_label = tk.Label(
             self.node_graph.canvas, textvariable=self.thresh_value_var,
             bg="#e0e0e0", font=("Arial", 8), anchor='center'
        )
        self.ui_elements['thresh_value_label_widget'] = value_label
        value_label_window_id = self.node_graph.canvas.create_window(
             widget_x + widget_width/2, widget_y, anchor=tk.N, window=value_label,
             tags=(self.node_tag,)
        )
        self.widget_windows['thresh_value_label'] = value_label_window_id

        # Note: Histogram display omitted due to complexity

    def _update_method(self, event=None):
        new_method = self.method_var.get()
        if self.method != new_method:
            self.method = new_method
            print(f"[PARAM] Threshold method changed to: {self.method}")
            # Hide/show relevant controls if needed in future
            self.node_graph.request_update()

    def _update_threshold(self, value_str):
        try:
            new_value = int(float(value_str))
            if self.threshold_value != new_value:
                self.threshold_value = new_value
                if hasattr(self, 'thresh_value_var'):
                    self.thresh_value_var.set(f"{self.threshold_value}")
                self.node_graph.request_update()
        except ValueError:
            print(f"[ERROR] Invalid threshold slider value: {value_str}")

    def process(self):
        super().process() # Gets self.input_data
        self.output_data = None

        if self.input_data and isinstance(self.input_data, Image.Image):
            try:
                # Convert to grayscale first, as thresholding usually operates on luminance
                img_gray = ImageOps.grayscale(self.input_data)

                if self.method == "Binary":
                    # Use point transformation for binary thresholding
                    # Pixels > threshold become 255 (white), others 0 (black)
                    self.output_data = img_gray.point(lambda p: 255 if p > self.threshold_value else 0, mode='1') # Output binary image
                    # Convert back to 'L' mode if needed for compatibility, though '1' is correct
                    self.output_data = self.output_data.convert('L')

                # elif self.method == "Otsu (cv2)":
                #     # Requires OpenCV:
                #     # import cv2
                #     # img_np = np.array(img_gray)
                #     # thresh_val, img_otsu = cv2.threshold(img_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                #     # print(f"[PROC] Otsu Threshold calculated: {thresh_val}")
                #     # self.output_data = Image.fromarray(img_otsu)
                #     print("[WARN] Otsu thresholding requires OpenCV (cv2) - Not implemented.")
                #     self.output_data = img_gray # Pass through original gray

                # elif self.method == "Adaptive (cv2)":
                #     # Requires OpenCV:
                #     # import cv2
                #     # img_np = np.array(img_gray)
                #     # img_adaptive = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                #     #                                      cv2.THRESH_BINARY, blockSize=11, C=2) # Example parameters
                #     # self.output_data = Image.fromarray(img_adaptive)
                #     print("[WARN] Adaptive thresholding requires OpenCV (cv2) - Not implemented.")
                #     self.output_data = img_gray # Pass through original gray

                else:
                     print(f"[WARN] Unknown threshold method: {self.method}")
                     self.output_data = img_gray # Pass through

            except Exception as e:
                print(f"[ERROR] Threshold processing failed: {e}")
                self.output_data = None
        else:
            self.output_data = None