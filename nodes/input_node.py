import tkinter as tk
from tkinter import filedialog
from nodes.base_node import BaseNode
from PIL import Image, ImageTk 

class InputNode(BaseNode):
    def __init__(self, node_graph, x, y):
        super().__init__(node_graph, "Input", x, y)
        self.image_path = None
        self.pil_image = None 
        self.tk_image = None 
        self.preview_size = (self.width - 20, self.height - 50) 

    def draw(self):
        super().draw() 
        button_y = self.y + self.title_height + 5
        button_height = 25
        self.ui_elements['button_rect'] = self.node_graph.canvas.create_rectangle(self.x + 10, button_y, self.x + self.width - 10, button_y + button_height,fill="#ddd", outline="black", width=1, tags=(f"node_{id(self)}", "input_button"))
        self.ui_elements['button_text'] = self.node_graph.canvas.create_text(self.x + self.width / 2, button_y + button_height / 2,text="Load Image", anchor=tk.CENTER, tags=(f"node_{id(self)}", "input_button"))

        preview_y = button_y + button_height + 5
        self.ui_elements['preview_rect'] = self.node_graph.canvas.create_rectangle(self.x + 10, preview_y, self.x + self.width - 10, self.y + self.height - 5,fill="#bbb", outline="#999", width=1, tags=(f"node_{id(self)}", "preview_area"))
        self.ui_elements['preview_image'] = None
        self.node_graph.canvas.tag_bind("input_button", "<Button-1>", lambda e: self.ask_load_image())

    def ask_load_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image",filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff"), ("All Files", "*.*")])
        if file_path:self.load_image(file_path)

    def load_image(self, file_path):
        try:
            self.image_path = file_path
            self.pil_image = Image.open(file_path)
            
            preview_img = self.pil_image.copy()
            preview_img.thumbnail(self.preview_size, Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(preview_img) 

            self.output_data = self.pil_image 
            self.node_graph.needs_update = True 

        except Exception as e:
            self.image_path = None
            self.pil_image = None
            self.tk_image = None
            self.output_data = None
             
            if self.ui_elements.get('preview_image'):
                self.node_graph.canvas.delete(self.ui_elements['preview_image'])
                self.ui_elements['preview_image'] = None
            self.node_graph.needs_update = True 

    def process(self):
        if self.pil_image and not self.output_data: self.output_data = self.pil_image
        elif not self.pil_image:self.output_data = None

    def update_ui_element_positions(self):
        button_y = self.y + self.title_height + 5
        button_height = 25
        self.node_graph.canvas.coords(self.ui_elements['button_rect'],self.x + 10, button_y, self.x + self.width - 10, button_y + button_height)
        self.node_graph.canvas.coords(self.ui_elements['button_text'],self.x + self.width / 2, button_y + button_height / 2)
        preview_y = button_y + button_height + 5
        self.node_graph.canvas.coords(self.ui_elements['preview_rect'],self.x + 10, preview_y, self.x + self.width - 10, self.y + self.height - 5)

        if self.ui_elements.get('preview_image'):
            preview_bg_coords = self.node_graph.canvas.coords(self.ui_elements['preview_rect'])
            preview_center_x = (preview_bg_coords[0] + preview_bg_coords[2]) / 2
            preview_center_y = (preview_bg_coords[1] + preview_bg_coords[3]) / 2
            self.node_graph.canvas.coords(self.ui_elements['preview_image'], preview_center_x, preview_center_y)

    def get_params(self):
        params = super().get_params()
        params['load_image'] = {'type': 'button','text': 'Load New Image', 'command': self.ask_load_image}
        return params