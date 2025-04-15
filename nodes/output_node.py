###### THIS IS WORKING!!!
# nodes/output_node.py
import tkinter as tk
from tkinter import filedialog, messagebox
from nodes.base_node import BaseNode
from PIL import Image

class OutputNode(BaseNode):
    # __init__, draw, draw_controls, get_output_pos, connect_output, output_hit, save_image
    # remain the same as previous version

    def __init__(self, node_graph, x, y):
         super().__init__(node_graph, "Output", x, y)
         self.height = 100 # Adjusted height for button space
         # No output_data initialization needed, base class handles it

    def draw(self):
        super().draw()
        self.node_graph.canvas.itemconfig(self.id, fill="#d0f0d0")
        self.node_graph.canvas.itemconfig(self.text_id, text="Final Output")

    def draw_controls(self):
        """Add Save button"""
        super().draw_controls()
        control_y = self.get_control_area_start_y()
        widget_x = self.x + 10
        widget_width = self.width - 20

        save_button = tk.Button(
            self.node_graph.canvas,
            text="Save Image...",
            command=self.save_image
        )
        self.ui_elements['save_button_widget'] = save_button
        button_window_id = self.node_graph.canvas.create_window(
            widget_x, control_y, width=widget_width, anchor=tk.NW, window=save_button,
            tags=(self.node_tag,)
        )
        self.widget_windows['save_button'] = button_window_id

    def process(self):
        # --- MODIFIED ---
        super().process() # Call base class to populate self.input_data_list

        image_to_output = None
        # Default: use the first valid input image if available
        if self.input_data_list:
             for data in self.input_data_list:
                 if isinstance(data, Image.Image):
                      image_to_output = data
                      print(f"[PROC] OutputNode using input image type: {type(image_to_output)}") # Debug
                      break # Use the first valid image found

        # The OutputNode's job is just to hold the final data.
        # The base process method already sets self.output_data based on the first input (by default).
        # We just need to ensure it's set correctly based on our check.
        self.output_data = image_to_output

        if self.output_data is None:
             print("[PROC] OutputNode: No valid input image received.")
        # --- END MODIFIED ---

        # The actual preview update is handled by the update_loop in main.py

    def get_output_pos(self):
         return None

    def connect_output(self, target_node):
         print("[WARN] Output node cannot be connected outwards.")
         pass

    def output_hit(self, x, y):
         return False

    def save_image(self):
        print("[SAVE] Forcing graph process before saving...")
        self.node_graph.process_graph()

        image_to_save = self.output_data # Use the data set by the process method

        if image_to_save is None or not isinstance(image_to_save, Image.Image):
            print("[SAVE] No valid image data in Output node to save.")
            messagebox.showwarning("Save Error", "No image data available to save.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Processed Image As...",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg;*.jpeg"),
                ("BMP Image", "*.bmp"),
                ("TIFF Image", "*.tiff"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            print("[SAVE] Save cancelled.")
            return

        try:
            print(f"[SAVE] Saving image to: {file_path}")
            save_img = image_to_save
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                 if save_img.mode == 'RGBA':
                      print("[SAVE] Converting RGBA to RGB for JPEG.")
                      bg = Image.new("RGB", save_img.size, (255, 255, 255))
                      bg.paste(save_img, mask=save_img.split()[3])
                      save_img = bg
                 elif save_img.mode == 'P' and 'transparency' in save_img.info:
                     print("[SAVE] Converting transparent Palette image to RGB for JPEG.")
                     save_img = save_img.convert('RGB')

            save_img.save(file_path)
            print("[SAVE] Image saved successfully.")
            messagebox.showinfo("Save Successful", f"Image saved to:\n{file_path}")

        except Exception as e:
            print(f"[ERROR] Failed to save image: {e}")
            messagebox.showerror("Save Error", f"Failed to save image:\n{e}")

    # get_params method remains removed