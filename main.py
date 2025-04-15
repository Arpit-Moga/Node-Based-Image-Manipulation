import tkinter as tk
from tkinter import ttk # Import themed widgets
from node_graph import NodeGraph
from ui import Toolbar, PropertiesPanel, PreviewWindow # Assuming PropertiesPanel might be used later

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Node Editor")
    root.geometry("1400x900") # Slightly larger default size

    # --- Apply a TTK Theme ---
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
        print("Using 'clam' theme.")
    except tk.TclError:
        print("Theme 'clam' not available, using default.")

    # Use TTK Frames for better theme integration
    # PanedWindow itself doesn't directly take ttk style via 'style='
    # Its background might be influenced by the root window's theme settings
    main_paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
    main_paned_window.pack(fill=tk.BOTH, expand=True)

    # Left Pane (Toolbar & Properties) - Give it a fixed initial width
    left_pane_frame = ttk.Frame(main_paned_window, width=250) # Use ttk.Frame
    # --- Corrected add call ---
    main_paned_window.add(left_pane_frame) # Remove weight option
    left_pane_frame.pack_propagate(False) # Prevent frame from shrinking to content

    # Right Pane (Graph & Preview)
    right_pane_frame = ttk.Frame(main_paned_window) # Use ttk.Frame
    # --- Corrected add call ---
    main_paned_window.add(right_pane_frame) # Remove weight option


    # Toolbar setup within left pane
    toolbar = Toolbar(left_pane_frame)
    toolbar.frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    # Placeholder for Properties Panel (using ttk.Frame)
    props_panel = PropertiesPanel(left_pane_frame)
    props_panel.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))


    # Right pane split vertically for Graph and Preview
    right_paned_window = tk.PanedWindow(right_pane_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED)
    right_paned_window.pack(fill=tk.BOTH, expand=True)

    # Graph Frame (allow expansion)
    graph_frame = ttk.Frame(right_paned_window) # Use ttk.Frame
    # --- Corrected add call ---
    right_paned_window.add(graph_frame) # Remove weight option

    # Preview Frame (fixed initial height, but can be resized)
    preview_frame = ttk.Frame(right_paned_window, height=250) # Use ttk.Frame, fixed initial height
    preview_frame.pack_propagate(False) # Prevent shrinking
    # --- Corrected add call ---
    right_paned_window.add(preview_frame) # Remove weight option

    # Instantiate PreviewWindow and NodeGraph
    preview_window = PreviewWindow(preview_frame)
    graph = NodeGraph(graph_frame, preview_window)

    # Link components
    toolbar.set_node_graph(graph)
    # props_panel.set_node_graph(graph)
    # graph.set_properties_panel(props_panel) # If needed


    root.mainloop()