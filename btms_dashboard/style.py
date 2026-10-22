"""Shared native dark theme; optional fonts fall back to installed system fonts."""
import tkinter as tk
from tkinter import ttk
from config import ACCENT, BAD, BG, BORDER, CARD, FONT, GOOD, MUTED, TEXT, HEADING_FONT


def setup_style(root):
    st = ttk.Style(root)
    st.theme_use("clam")
    root.configure(bg=BG)
    root.option_add("*TCombobox*Listbox.background", CARD)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", "#703016")
    st.configure(".", font=(FONT, 10), background=BG, foreground=TEXT)
    for name, bg in [("TFrame", BG), ("Card.TFrame", CARD)]:
        st.configure(name, background=bg)
    st.configure("TLabel", background=BG, foreground=TEXT)
    st.configure("Card.TLabel", background=CARD)
    st.configure("Muted.TLabel", foreground=MUTED)
    st.configure("Title.TLabel", font=(HEADING_FONT, 19, "bold"))
    st.configure("TLabelframe", background=CARD, bordercolor=BORDER, relief="solid", borderwidth=1)
    st.configure("TLabelframe.Label", background=CARD, foreground=ACCENT, font=(FONT, 10, "bold"))
    st.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 6, 0, 12))
    st.configure("TNotebook.Tab", padding=(12, 12), font=(FONT, 9, "bold"),
                 background=BG, foreground=MUTED, borderwidth=0)
    st.map("TNotebook.Tab", background=[("selected", "#24160f"), ("active", CARD)],
           foreground=[("selected", ACCENT), ("active", TEXT)])
    st.configure("Treeview", rowheight=30, background=CARD, fieldbackground=CARD,
                 foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
    st.configure("Treeview.Heading", font=(FONT, 9, "bold"), background="#202023",
                 foreground=MUTED, padding=(6, 10), bordercolor=BORDER, relief="flat")
    st.map("Treeview.Heading", background=[("active", "#343036")])
    st.map("Treeview", background=[("selected", "#77351c")], foreground=[("selected", "#ffffff")])
    for name, col, hover, fg in [("Accent", ACCENT, "#d94200", "#ffffff"),
                                ("Good", ACCENT, "#d94200", "#ffffff"),
                                ("Danger", "#3a1e20", "#59272a", BAD),
                                ("Soft", "#222225", "#333338", TEXT)]:
        st.configure(f"{name}.TButton", background=col, foreground=fg, padding=(12, 9),
                     font=(FONT, 9, "bold"), borderwidth=1, bordercolor=col, focusthickness=1)
        st.map(f"{name}.TButton", background=[("disabled", CARD), ("active", hover)],
               foreground=[("disabled", MUTED)], bordercolor=[("focus", TEXT)])
    for name in ("TEntry", "TCombobox"):
        st.configure(name, padding=7, fieldbackground="#19191c", foreground=TEXT,
                     bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, insertcolor=TEXT,
                     arrowcolor=ACCENT)
        st.map(name, fieldbackground=[("readonly", "#19191c")],
               foreground=[("readonly", TEXT)], bordercolor=[("focus", ACCENT)])
    st.configure("Horizontal.TScale", background=CARD, troughcolor="#303036", bordercolor=CARD)
    st.configure("TScrollbar", background="#333338", troughcolor=CARD, arrowcolor=MUTED,
                 bordercolor=CARD)
