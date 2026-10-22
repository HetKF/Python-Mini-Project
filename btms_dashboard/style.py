# One place that sets the colours, fonts and button styles for the whole window

import tkinter as tk
from tkinter import ttk
from config import ACCENT, BAD, BG, CARD, FONT, GOOD, MUTED, NAVY, TEXT


def setup_style(root):
    st = ttk.Style(root)
    try:
        st.theme_use("clam")
    except tk.TclError:
        pass
    root.configure(bg=BG)
    st.configure(".", font=(FONT, 10), background=BG, foreground=TEXT)
    st.configure("TFrame", background=BG)
    st.configure("Card.TFrame", background=CARD)
    st.configure("TLabel", background=BG, foreground=TEXT)
    st.configure("Card.TLabel", background=CARD)
    st.configure("Muted.TLabel", background=BG, foreground=MUTED)
    st.configure("Title.TLabel", font=(FONT, 13, "bold"), background=BG)
    st.configure("TLabelframe", background=CARD, bordercolor="#dbe0ea")
    st.configure("TLabelframe.Label", background=CARD, foreground=NAVY, font=(FONT, 10, "bold"))
    st.configure("TNotebook", background=BG, borderwidth=0)
    st.configure("TNotebook.Tab", padding=(18, 9), font=(FONT, 10, "bold"),
                 background="#dfe5f0", foreground=MUTED)
    st.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", ACCENT)])
    st.configure("Treeview", rowheight=27, background=CARD, fieldbackground=CARD,
                 bordercolor="#dbe0ea", font=(FONT, 10))
    st.configure("Treeview.Heading", font=(FONT, 10, "bold"), background="#e8edf6",
                 foreground=NAVY, padding=6)
    st.map("Treeview", background=[("selected", "#cfe2fa")], foreground=[("selected", TEXT)])
    for name, col, hover in [("Accent", ACCENT, "#2568b0"), ("Good", GOOD, "#25834b"),
                             ("Danger", BAD, "#b53636"), ("Soft", "#e3e8f2", "#d3dbea")]:
        fg = TEXT if name == "Soft" else "white"
        st.configure(f"{name}.TButton", background=col, foreground=fg, padding=(14, 7),
                     font=(FONT, 10, "bold"), borderwidth=0, focusthickness=0)
        st.map(f"{name}.TButton", background=[("active", hover)])
    st.configure("TEntry", padding=5, fieldbackground="white")
    st.configure("TCombobox", padding=5)
    st.configure("Horizontal.TScale", background=CARD)
