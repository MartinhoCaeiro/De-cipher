"""Helpers to apply a cohesive dark theme to the Tkinter application.

This module exposes a single function, :func:`apply_dark_theme`, which
applies consistent colors and ttk style mappings to make the UI look
dark and modern. It is intentionally small and safe to call at any
point during UI initialization.
"""

from tkinter import ttk


def apply_dark_theme(root):
    """Apply a compact dark theme to the given Tk root.

    Args:
        root: A :class:`tk.Tk` or :class:`tk.Toplevel` instance. The
            function will set the root background and configure ttk style
            options so widgets share a consistent dark appearance.

    The function is best-effort: it uses `try/except` around style
    operations that may not be supported on all platforms/themes.
    """

    root.configure(bg="#1e1e1e")

    style = ttk.Style()
    style.theme_use("clam")

    bg_main = "#1e1e1e"
    bg_entry = "#2d2d2d"
    bg_button = "#3a3a3a"
    bg_tab = "#2b2b2b"
    bg_tab_active = "#3a3a3a"
    fg_text = "#ffffff"

    style.configure(".", background=bg_main, foreground=fg_text, fieldbackground=bg_entry)
    style.configure("TLabel", background=bg_main, foreground=fg_text)
    style.configure("TButton", background=bg_button, foreground=fg_text, padding=6)
    style.map("TButton", background=[("active", "#505050")])
    style.configure("TEntry", fieldbackground=bg_entry, foreground=fg_text)
    style.configure("TRadiobutton", background=bg_main, foreground=fg_text)
    try:
        style.configure("TRadiobutton", selectcolor=bg_main)
    except Exception:
        pass
    try:
        style.map(
            "TRadiobutton",
            background=[("active", bg_main), ("selected", bg_tab_active)],
            foreground=[("active", fg_text), ("selected", fg_text)],
        )
    except Exception:
        pass

    style.configure("TFrame", background=bg_main)
    style.configure("TNotebook", background=bg_main, borderwidth=0)
    style.configure("TNotebook.Tab", background=bg_tab, foreground=fg_text, padding=[10, 5])
    style.map("TNotebook.Tab", background=[("selected", bg_tab_active)])
