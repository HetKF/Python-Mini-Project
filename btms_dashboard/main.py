# Entry point: builds the window, joins all the tabs together and starts the program (python main.py)

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from alerts_tab import AlertsTab
from config import CFD_COLS, CFD_INTRO, CFD_LABELS, FONT, NAVY, SENSOR_COLS, SENSOR_INTRO, SENSOR_LABELS, TEXT
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
        self.geometry("1120x720")
        self.minsize(960, 620)
        setup_style(self)
        self.db = Database()

        head = tk.Frame(self, bg=NAVY)
        head.pack(fill="x")
        tk.Label(head, text="🔋  Battery Cooling Monitor", bg=NAVY, fg="white",
                 font=(FONT, 17, "bold")).pack(side="left", padx=18, pady=(12, 12))
        tk.Label(head, text="EV battery thermal management  ·  Case study KJS-CES-02", bg=NAVY,
                 fg="#aab7d4", font=(FONT, 10)).pack(side="left", pady=(16, 0))

        self.status = tk.StringVar(value="Welcome! Start on the Home tab.")
        tk.Label(self, textvariable=self.status, anchor="w", bg="#e3e8f2", fg=TEXT,
                 font=(FONT, 9), padx=14, pady=5).pack(side="bottom", fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=(8, 0))
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

        menu = tk.Menu(self)
        m = tk.Menu(menu, tearoff=0)
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
