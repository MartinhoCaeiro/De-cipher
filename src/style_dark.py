import tkinter as tk
from tkinter import ttk

def apply_dark_theme(root):
    """Aplica um tema escuro elegante à interface."""
    root.configure(bg="#1e1e1e")

    style = ttk.Style()
    style.theme_use("clam")

    # Cores principais
    bg_main = "#1e1e1e"
    bg_entry = "#2d2d2d"
    bg_button = "#3a3a3a"
    bg_tab = "#2b2b2b"
    bg_tab_active = "#3a3a3a"
    fg_text = "#ffffff"

    # Estilo base
    style.configure(".", background=bg_main, foreground=fg_text, fieldbackground=bg_entry)
    style.configure("TLabel", background=bg_main, foreground=fg_text)
    style.configure("TButton", background=bg_button, foreground=fg_text, padding=6)
    style.map("TButton", background=[("active", "#505050")])
    style.configure("TEntry", fieldbackground=bg_entry, foreground=fg_text)
    style.configure("TRadiobutton", background=bg_main, foreground=fg_text)
    style.configure("TNotebook", background=bg_main, borderwidth=0)
    style.configure("TNotebook.Tab", background=bg_tab, foreground=fg_text, padding=[10, 5])
    style.map("TNotebook.Tab", background=[("selected", bg_tab_active)])
