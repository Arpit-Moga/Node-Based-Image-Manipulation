# New/nodes/edge_node.py
import tkinter as tk
from tkinter import ttk
from nodes.base_node import BaseNode
from PIL import Image, ImageFilter, ImageOps, ImageChops
import numpy as np

class EdgeNode(BaseNode):
    # Note: Canny edge detection is best done with OpenCV.
    # This implementation uses Sobel via Pillow's FIND_EDGES.
    METHODS = ["Sobel", "Canny (cv2)"]

    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Edge Detection", x, y)
        self.method = EdgeNode.METHODS[0]
        self.overlay = tk.BooleanVar(value=False) # Variable for overlay checkbox
        # Canny parameters (relevant if OpenCV is used)
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150
        # Sobel kernel size (Pillow's FIND_EDGES doesn't easily configure size)
        self.height = 160 # Adjust height for controls

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
            self.node_graph.canvas, textvariable=self.method_var, values=EdgeNode.METHODS,
            state="readonly", width=int(widget_width / 7)
        )
        method_dropdown.bind("<<ComboboxSelected>>", self._update_method)
        self.ui_elements['method_dropdown_widget'] = method_dropdown
        method_dropdown_window_id = self.node_graph.canvas.create_window(
            widget_x, widget_y, width=widget_width, anchor=tk.NW, window=method_dropdown,
            tags=(self.node_tag,)
        )
        self.widget_windows['method_dropdown'] = method_dropdown_window_id
        widget_y += label_h + 10

        # --- Overlay Checkbox ---
        overlay_check = tk.Checkbutton(
            self.node_graph.canvas, text="Overlay on Original", variable=self.overlay,
            command=self._update_overlay, bg="#e0e0e0", anchor='w',
            font=("Arial", 8)
        )
        self.ui_elements['overlay_check_widget'] = overlay_check
        overlay_check_window_id = self.node_graph.canvas.create_window(
            widget_x, widget_y, width=widget_width, anchor=tk.NW, window=overlay_check,
            tags=(self.node_tag,)
        )
        self.widget_windows['overlay_check'] = overlay_check_window_id
        widget_y += label_h + 5

        # --- Canny Parameters (add sliders if Canny is implemented) ---
        # Placeholder for where Canny threshold sliders would go
        # Need to adjust self.height if these are added

    def _update_method(self, event=None):
        new_method = self.method_var.get()
        if self.method != new_method:
            self.method = new_method
            print(f"[PARAM] Edge method changed to: {self.method}")
            # Hide/show Canny params if needed
            self.node_graph.request_update()

    def _update_overlay(self):
        print(f"[PARAM] Edge overlay set to: {self.overlay.get()}")
        self.node_graph.request_update()

    # Add _update_canny_thresh1, _update_canny_thresh2 if sliders are added

    def process(self):
        super().process() # Gets self.input_data
        self.output_data = None
        edges_img = None

        if self.input_data and isinstance(self.input_data, Image.Image):
            try:
                # Convert to grayscale for edge detection
                img_gray = ImageOps.grayscale(self.input_data)

                if self.method == "Sobel":
                    # Pillow's FIND_EDGES applies a Sobel operator
                    edges_img = img_gray.filter(ImageFilter.FIND_EDGES)

                elif self.method == "Canny (cv2)":
                    # Requires OpenCV:
                    # import cv2
                    # img_np = np.array(img_gray)
                    # # Apply Gaussian blur before Canny is often recommended
                    # img_blur = cv2.GaussianBlur(img_np, (5, 5), 0)
                    # edges_cv2 = cv2.Canny(img_blur, self.canny_threshold1, self.canny_threshold2)
                    # edges_img = Image.fromarray(edges_cv2)
                    print("[WARN] Canny edge detection requires OpenCV (cv2) - Not implemented.")
                    edges_img = img_gray # Pass through original gray

                else:
                     print(f"[WARN] Unknown edge method: {self.method}")
                     edges_img = img_gray # Pass through

                # Handle overlay
                if self.overlay.get() and edges_img:
                    if self.input_data.mode != 'RGB':
                        original_rgb = self.input_data.convert('RGB')
                    else:
                        original_rgb = self.input_data.copy()

                    # Ensure edges are L mode before converting to RGB for blending/masking
                    if edges_img.mode != 'L':
                        edges_l = edges_img.convert('L')
                    else:
                        edges_l = edges_img

                    # Make edges white on black for easier overlaying
                    edges_white = edges_l.point(lambda p: 255 if p > 0 else 0)
                    edges_rgb = ImageOps.colorize(edges_white, black="black", white="white").convert('RGB') # Convert edges to RGB

                    # Blend edges onto original - alternative: use edges as mask
                    # Create a red version of the edges to overlay
                    red_edges = ImageOps.colorize(edges_white, black=(0,0,0), white=(255,0,0)).convert('RGB')

                    # Composite red edges onto original using the edge mask
                    # Where edges_white is white (255), use red_edges, otherwise use original_rgb
                    mask = edges_white.point(lambda p: 255 if p > 0 else 0, mode='1')
                    self.output_data = Image.composite(red_edges, original_rgb, mask)

                    # Simpler blend (less distinct):
                    # self.output_data = ImageChops.add(original_rgb, edges_rgb) # Can saturate
                    # self.output_data = Image.blend(original_rgb, edges_rgb, alpha=0.5) # Washes out

                else:
                    # Output just the edges (usually black background, white/gray edges)
                    self.output_data = edges_img


            except Exception as e:
                print(f"[ERROR] Edge detection processing failed: {e}")
                self.output_data = None
        else:
            self.output_data = None