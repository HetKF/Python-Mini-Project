# Entry point: builds the window, joins all the tabs together and starts the program (python main.py)

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from alerts_tab import AlertsTab
from config import ACCENT, BG, BORDER, CARD, GOOD, MUTED, HEADING_FONT, CFD_COLS, CFD_INTRO, CFD_LABELS, FONT, NAVY, SENSOR_COLS, SENSOR_INTRO, SENSOR_LABELS, TEXT
from crud_tab import CrudTab
from dashboard_tab import DashboardTab
from database import Database
from help_tab import HelpTab
from predict_tab import PredictTab
from style import setup_style


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Battery Cooling Monitor - KJS-CES-02")
        self.geometry(f"{min(1440, self.winfo_screenwidth()-40)}x{min(960, self.winfo_screenheight()-80)}")
        self.minsize(1200, 720)
        setup_style(self)
        self.db = Database()

        rail = tk.Frame(self, bg="#0b0b0d", width=96, highlightthickness=1,
                        highlightbackground=BORDER)
        rail.pack(side="left", fill="y")
        rail.pack_propagate(False)
        tk.Label(rail, text="◉", bg="#0b0b0d", fg=ACCENT,
                 font=(FONT, 32)).pack(pady=(24, 8))
        tk.Label(rail, text="B T M S", bg="#0b0b0d", fg=MUTED,
                 font=(FONT, 8, "bold")).pack(pady=(0, 46))
        self.nav_buttons = []
        for i in range(6):
            button = tk.Button(rail, text=f"{i+1:02d}  ━", bg="#0b0b0d", fg=MUTED,
                               activebackground=CARD, activeforeground=ACCENT,
                               relief="flat", bd=0, cursor="hand2", pady=18,
                               font=(FONT, 11, "bold"), command=lambda n=i: nb.select(n))
            button.pack(fill="x", padx=8, pady=2)
            self.nav_buttons.append(button)
        tk.Label(rail, text="KJS\nCES–02", bg="#0b0b0d", fg=MUTED,
                 font=(FONT, 8), pady=22).pack(side="bottom")

        content = tk.Frame(self, bg=BG)
        content.pack(side="left", fill="both", expand=True)
        head = tk.Frame(content, bg=BG)
        head.pack(fill="x", padx=28, pady=(24, 12))
        tk.Label(head, text="E V   /   T H E R M A L   M A N A G E M E N T", bg=BG,
                 fg=ACCENT, font=(FONT, 9, "bold")).pack(anchor="w")
        tk.Label(head, text="BATTERY COOLING MONITOR", bg=BG, fg=TEXT,
                 font=(HEADING_FONT, 28, "bold")).pack(anchor="w", pady=(8, 0))

        self.status = tk.StringVar(value="Welcome! Start on the Home tab.")
        status_bar = tk.Frame(content, bg="#0d0d0f", height=56,
                              highlightthickness=1, highlightbackground=BORDER)
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)
        tk.Label(status_bar, text="●  LOCAL DATABASE", bg="#0d0d0f", fg=GOOD,
                 font=(FONT, 8, "bold")).pack(side="left", padx=20)
        tk.Label(status_bar, textvariable=self.status, anchor="w", bg="#0d0d0f", fg=MUTED,
                 font=(FONT, 9)).pack(side="left", padx=12)

        nb = ttk.Notebook(content)
        self.notebook = nb
        nb.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        self.dash = DashboardTab(nb, self)
        self.sensor = CrudTab(nb, self, "sensor_readings", SENSOR_COLS,
                              ["ts", "cell_id", "battery_temp", "coolant_in", "coolant_out",
                               "voltage", "current", "flow_rate", "notes"],
                              SENSOR_LABELS, {"cell_id": "C1"}, SENSOR_INTRO, "reading")
        self.cfd = CrudTab(nb, self, "cfd_runs", CFD_COLS,
                           ["reynolds", "concentration", "inlet_temp", "max_temp", "delta_t",
                            "pressure_drop", "htc", "notes"],
                           CFD_LABELS, {}, CFD_INTRO, "simulation")
        self.predict = PredictTab(nb, self)
        self.alerts = AlertsTab(nb, self)
        for tab, name in [(self.dash, "  🏠 Home  "), (self.sensor, "  🌡 Temperature Readings  "),
                          (self.cfd, "  💧 Cooling Simulations  "), (self.predict, "  🔮 Predict Temperature  "),
                          (self.alerts, "  ⚠ Warnings  "), (HelpTab(nb), "  ❔ Help  ")]:
            nb.add(tab, text=name)

        def sync_navigation(_event=None):
            active = nb.index(nb.select())
            for index, button in enumerate(self.nav_buttons):
                button.configure(fg=ACCENT if index == active else MUTED,
                                 bg="#24160f" if index == active else "#0b0b0d")
        nb.bind("<<NotebookTabChanged>>", sync_navigation)
        sync_navigation()

        menu = tk.Menu(self, bg=CARD, fg=TEXT, activebackground=ACCENT, activeforeground="white")
        m = tk.Menu(menu, tearoff=0, bg=CARD, fg=TEXT, activebackground=ACCENT, activeforeground="white")
        m.add_command(label="Load sample data (real + synthetic)", command=self.load_sample)
        m.add_command(label="Delete ALL data", command=self.clear_all)
        m.add_separator()
        m.add_command(label="Exit", command=self.destroy)
        menu.add_cascade(label="Data", menu=m)
        self.config(menu=menu)

        if self.db.count("sensor_readings") == 0 and self.db.count("cfd_runs") == 0:
            if messagebox.askyesno("Welcome", "The database is empty.\n\nLoad the sample data so you can "
                                              "explore the program?\n\nIt mixes real lab data with synthetic "
                                              "data, and every row is labelled."):
                self.db.seed()
        self.refresh_all()

    def say(self, msg):
        self.status.set(msg)

    def load_sample(self):
        added = self.db.seed()
        if any(added.values()):
            self.say(f"✔ Loaded {added['real']:,} real readings, {added['synthetic_sensors']:,} synthetic readings "
                     f"and {added['synthetic_cfd']:,} synthetic simulations.")
        else:
            self.say("Sample data is already loaded.")
        self.refresh_all()

    def clear_all(self):
        if messagebox.askyesno("Delete everything", "Delete ALL readings and simulations?\nThis cannot be undone."):
            self.db.conn.executescript("DELETE FROM sensor_readings; DELETE FROM cfd_runs;")
            self.db.conn.commit()
            self.say("All data deleted.")
            self.refresh_all()

    def refresh_all(self):
        self.dash.refresh()
        self.sensor.refresh()
        self.cfd.refresh()
        self.alerts.refresh()
        self.predict.retrain()


if __name__ == "__main__":
    App().mainloop()
