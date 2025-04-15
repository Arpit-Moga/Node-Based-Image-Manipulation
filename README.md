# ✨ NodeFusion Image Editor ✨

Unleash your creativity with NodeFusion! 🎨🔗 A simple, node-based image editor built with Python and Tkinter. Connect nodes visually to build complex image processing pipelines right on your desktop. Perfect for learning, experimenting, and basic image manipulation tasks!

## 🚀 Features

* **Visual Node Graph:** Drag, drop, and connect nodes to create your image processing workflow. ⛓️
* **Real-time Preview:** See the results of your node graph instantly in the preview pane! 👁️‍🗨️ (Updates automatically after processing)
* **Interactive UI:** Built with Python's native Tkinter library (using modern `ttk` widgets and themes). 🖼️
* **Core Image Operations:** Includes essential nodes for loading, adjusting, filtering, and saving images.
* **Extensible:** Add new nodes easily by extending the `BaseNode` class. 🔧

## 🧩 Available Nodes

NodeFusion comes packed with these built-in nodes:

* **Input:** Load your starting image (PNG, JPG, BMP, etc.). 📂
* **Output:** Save the final processed image or view the result. 💾
* **Brightness:** Adjust the overall brightness of the image. ☀️
* **Contrast:** Modify the image contrast for more pop! ⚫⚪
* **Blur:** Apply a Gaussian blur with configurable radius (0.1 - 20px). 💧
* **Color Splitter:** Isolate Red, Green, Blue, or Alpha channels (outputs as grayscale). 🌈
* **Threshold:** Convert the image to binary (black & white) based on a threshold value. 🌓
* **Edge Detect:** Find edges using the Sobel operator. Option to overlay edges (in red) on the original image. 📉

## ⚙️ Setup & Running

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <repository-folder-name>
    ```
2.  **Install Dependencies:**
    NodeFusion relies on Python 3 and a few libraries. Make sure you have Python 3 installed. Then, install the required libraries (Pillow for image processing, NumPy might be needed by some nodes):
    ```bash
    pip install Pillow numpy
    ```
    *(**Note:** Some planned nodes like Canny edge detection or advanced thresholding might require OpenCV (`opencv-python`) in the future, but it's not needed for the current nodes).*
3.  **Run the Application:**
    ```bash
    python New/main.py
    ```
    *(Adjust the path `New/main.py` if your main script is located differently).*

4.  **Start Editing!**
    * Right-click on the dark gray graph area to add nodes.
    * Click and drag nodes to rearrange them.
    * Click and drag from a node's output (right side, red circle) to another node's input (left side, blue circle) to connect them.
    * Click a node to select it (press Delete/Backspace to remove).
    * Adjust parameters using the sliders/controls within the nodes.
    * Load an image using the `Input` node's button.
    * Use the `Output` node's "Save Image..." button to save your result.

## 🔮 Future Ideas

* Implementing advanced Thresholding (Otsu, Adaptive) & Edge Detection (Canny) methods (likely requires OpenCV).
* Adding more complex nodes (e.g., Color Balance, Sharpen, Transformations, Masking).
* Histogram display within the Threshold node UI.
* Saving and loading node graph layouts.
* Properties Panel integration to show/edit selected node parameters externally.
* Performance optimizations for larger images or complex graphs.

---

Enjoy experimenting with NodeFusion! Feel free to contribute or suggest features. ⭐
