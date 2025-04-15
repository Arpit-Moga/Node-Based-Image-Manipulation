###### THIS IS WORKING!!!
import tkinter as tk
from tkinter import filedialog
from nodes.base_node import BaseNode
from PIL import Image, ImageTk # Import Pillow

class InputNode(BaseNode):
    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Input", x, y)
        self.image_path = None
        self.pil_image = None # Store the loaded PIL image
        self.tk_image = None # Store Tkinter-compatible image for preview
        self.preview_size = (self.width - 20, self.height - 50) # Area for preview inside node

    def draw(self):
        super().draw() # Draw base node elements (rect, title, connectors)

        # --- Add specific UI for Input Node ---
        # Button Frame
        button_y = self.y + self.title_height + 5
        button_height = 25
        self.ui_elements['button_rect'] = self.node_graph.canvas.create_rectangle(
            self.x + 10, button_y, self.x + self.width - 10, button_y + button_height,
            fill="#ddd", outline="black", width=1, tags=(f"node_{id(self)}", "input_button")
        )
        self.ui_elements['button_text'] = self.node_graph.canvas.create_text(
            self.x + self.width / 2, button_y + button_height / 2,
            text="Load Image", anchor=tk.CENTER, tags=(f"node_{id(self)}", "input_button")
        )

        # Image Preview Area
        preview_y = button_y + button_height + 5
        self.ui_elements['preview_rect'] = self.node_graph.canvas.create_rectangle(
            self.x + 10, preview_y, self.x + self.width - 10, self.y + self.height - 5,
            fill="#bbb", outline="#999", width=1, tags=(f"node_{id(self)}", "preview_area")
        )
        # Placeholder for the image itself (created/updated in load_image)
        self.ui_elements['preview_image'] = None

        # Bind button click
        self.node_graph.canvas.tag_bind("input_button", "<Button-1>", lambda e: self.ask_load_image())

    def ask_load_image(self):
        # Important: This runs in the main thread, might block UI for large images
        # For production, consider running image loading in a separate thread
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_image(file_path)


    def load_image(self, file_path):
        try:
            print(f"[INFO] Loading image: {file_path}")
            self.image_path = file_path
            self.pil_image = Image.open(file_path)
            # Keep the original orientation info if available (for JPEGs)
            # self.pil_image = ImageOps.exif_transpose(self.pil_image) # Requires ImageOps

            # --- Update Node Preview ---
            # Create a thumbnail for the node preview
            preview_img = self.pil_image.copy()
            preview_img.thumbnail(self.preview_size, Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(preview_img) # Keep reference!

            # Delete old preview image if it exists
            # if self.ui_elements.get('preview_image'):
            #     self.node_graph.canvas.delete(self.ui_elements['preview_image'])

            # Calculate position to center the preview image
            preview_bg_coords = self.node_graph.canvas.coords(self.ui_elements['preview_rect'])
            preview_center_x = (preview_bg_coords[0] + preview_bg_coords[2]) / 2
            preview_center_y = (preview_bg_coords[1] + preview_bg_coords[3]) / 2

            # Create the new preview image on the canvas
            # self.ui_elements['preview_image'] = self.node_graph.canvas.create_image(
            #     preview_center_x, preview_center_y,
            #     anchor=tk.CENTER,
            #     image=self.tk_image,
            #     text = "Image Loaded",
            #     tags=(f"node_{id(self)}", "preview_display")
            # )

            print(f"[INFO] Image loaded successfully: {self.pil_image.format} {self.pil_image.size}")
            self.output_data = self.pil_image # Set output data for downstream nodes
            self.node_graph.needs_update = True # Signal graph needs re-processing

        except Exception as e:
            print(f"[ERROR] Failed to load image: {e}")
            self.image_path = None
            self.pil_image = None
            self.tk_image = None
            self.output_data = None
             # Clear preview if loading failed
            if self.ui_elements.get('preview_image'):
                self.node_graph.canvas.delete(self.ui_elements['preview_image'])
                self.ui_elements['preview_image'] = None
            self.node_graph.needs_update = True # Still trigger update


    def process(self):
        # Input node's job is to load data, so processing means ensuring output_data is set.
        if self.pil_image and not self.output_data:
             self.output_data = self.pil_image
        elif not self.pil_image:
             self.output_data = None
        # No actual image processing happens here, just provides the loaded image
        print(f"[PROC] InputNode providing data: {type(self.output_data)}")


    def update_ui_element_positions(self):
        # Recalculate positions based on self.x, self.y
        button_y = self.y + self.title_height + 5
        button_height = 25
        self.node_graph.canvas.coords(
            self.ui_elements['button_rect'],
            self.x + 10, button_y, self.x + self.width - 10, button_y + button_height
        )
        self.node_graph.canvas.coords(
            self.ui_elements['button_text'],
            self.x + self.width / 2, button_y + button_height / 2
        )

        preview_y = button_y + button_height + 5
        self.node_graph.canvas.coords(
             self.ui_elements['preview_rect'],
            self.x + 10, preview_y, self.x + self.width - 10, self.y + self.height - 5
        )

        if self.ui_elements.get('preview_image'):
            preview_bg_coords = self.node_graph.canvas.coords(self.ui_elements['preview_rect'])
            preview_center_x = (preview_bg_coords[0] + preview_bg_coords[2]) / 2
            preview_center_y = (preview_bg_coords[1] + preview_bg_coords[3]) / 2
            self.node_graph.canvas.coords(self.ui_elements['preview_image'], preview_center_x, preview_center_y)


    # Add get_params if you want to show the file path in properties
    def get_params(self):
        params = super().get_params()
        params['load_image'] = {
            'type': 'button',
            'text': 'Load New Image',
            'command': self.ask_load_image
        }
        # Could add a non-editable text field for the path if desired
        # params['image_path'] = {'type': 'label', 'value': self.image_path or "None"}
        return params