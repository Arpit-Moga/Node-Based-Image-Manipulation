import tkinter as tk
from tkinter import ttk
from node_graph import NodeGraph
from ui import Toolbar, PropertiesPanel, PreviewWindow

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Node Editor")
    root.geometry("1400x900")

    style = ttk.Style(root)
    try: style.theme_use('clam')
    except tk.TclError: print("Theme 'clam' not available, using default.")

    main_paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
    main_paned_window.pack(fill=tk.BOTH, expand=True)

    left_pane_frame = ttk.Frame(main_paned_window, width=250)
    main_paned_window.add(left_pane_frame) 
    left_pane_frame.pack_propagate(False) 
    
    right_pane_frame = ttk.Frame(main_paned_window) 
    main_paned_window.add(right_pane_frame) 
    
    toolbar = Toolbar(left_pane_frame)
    toolbar.frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    
    props_panel = PropertiesPanel(left_pane_frame)
    props_panel.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    right_paned_window = tk.PanedWindow(right_pane_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED)
    right_paned_window.pack(fill=tk.BOTH, expand=True)
    
    graph_frame = ttk.Frame(right_paned_window)     
    right_paned_window.add(graph_frame)
    
    preview_frame = ttk.Frame(right_paned_window, height=250) 
    preview_frame.pack_propagate(False) 
    right_paned_window.add(preview_frame) 
    
    preview_window = PreviewWindow(preview_frame)
    graph = NodeGraph(graph_frame, preview_window)
    
    toolbar.set_node_graph(graph)
    root.mainloop()