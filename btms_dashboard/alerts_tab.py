# Warnings tab: lists every reading outside the safe temperature range

from tkinter import ttk
from config import SOURCE_NAMES, TEMP_MAX


class AlertsTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        ttk.Label(self, text='05  /  WARNINGS', style="Title.TLabel").pack(anchor="w", padx=14, pady=(18, 8))
        self.app = app
        self.head = ttk.Label(self, text="", style="Title.TLabel")
        self.head.pack(anchor="w", padx=14, pady=(14, 2))
        ttk.Label(self, text="Batteries that get too hot lose life and can become unsafe (thermal runaway). "
                             "Anything outside 15–45 °C is listed here.",
                  style="Muted.TLabel", wraplength=980, justify="left").pack(fill="x", padx=14)
        cols = ("id", "ts", "cell_id", "battery_temp", "reason", "source")
        names = ("No.", "Date & time", "Cell", "Temperature °C", "What's wrong", "Data source")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, n, w in zip(cols, names, (60, 170, 80, 120, 230, 130)):
            self.tree.heading(c, text=n)
            self.tree.column(c, width=w, anchor="center")
        self.tree.tag_configure("hot", background="#361b1c")
        self.tree.tag_configure("cold", background="#152a39")
        self.tree.pack(fill="both", expand=True, padx=14, pady=12)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        al = self.app.db.alerts()
        self.head.config(text="No warnings. All good ✔" if not al else f"{len(al)} warning(s)")
        for r in al:
            hot = r["battery_temp"] > TEMP_MAX
            self.tree.insert("", "end", tags=("hot" if hot else "cold",), values=(
                r["id"], r["ts"], r["cell_id"], r["battery_temp"],
                "Too hot (above 45 °C)" if hot else "Too cold (below 15 °C)",
                SOURCE_NAMES.get(r["source"], r["source"])))
