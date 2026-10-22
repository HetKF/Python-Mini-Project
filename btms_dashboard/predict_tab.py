# Predict tab: sliders for cooling settings and the live temperature estimate

import tkinter as tk
from tkinter import ttk
from charts import Gauge
from config import ACCENT, BAD, CARD, FONT, GOOD, MUTED, TEMP_MAX, TEXT, WARN
from model import LinearModel


class PredictTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.model = LinearModel()
        self.syn_note = ""
        ttk.Label(self, text="Move the sliders to try different cooling settings. The program learns from the "
                             "saved simulations and estimates how hot the battery would get. "
                             "No button needed, it updates instantly.",
                  style="Muted.TLabel", wraplength=980, justify="left").pack(fill="x", padx=14, pady=(12, 4))

        panel = ttk.LabelFrame(self, text="  Cooling settings  ")
        panel.pack(fill="x", padx=14, pady=8)
        self.vars, self.val_lbl = {}, {}
        specs = [("reynolds", "Flow strength (Reynolds number)", 400, 700, 550, "{:.0f}", "Higher = coolant moves faster"),
                 ("concentration", "Nanoparticles in coolant (%)", 0, 2, 1.0, "{:.1f} %", "More particles = better heat transfer"),
                 ("inlet_temp", "Coolant inlet temperature (°C)", 15, 35, 25, "{:.0f} °C", "Colder coolant = cooler battery")]
        for i, (k, lab, lo, hi, init, fmt, hint) in enumerate(specs):
            ttk.Label(panel, text=lab, style="Card.TLabel", font=(FONT, 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=12, pady=8)
            var = tk.DoubleVar(value=init)
            self.vars[k] = var
            ttk.Scale(panel, from_=lo, to=hi, variable=var, length=360,
                      command=lambda _v, k=k, f=fmt: self.on_move(k, f)).grid(row=i, column=1, padx=10)
            self.val_lbl[k] = ttk.Label(panel, text=fmt.format(init), style="Card.TLabel",
                                        foreground=ACCENT, font=(FONT, 11, "bold"), width=8)
            self.val_lbl[k].grid(row=i, column=2)
            ttk.Label(panel, text=hint, style="Card.TLabel", foreground=MUTED).grid(
                row=i, column=3, sticky="w", padx=12)
        self.fmts = {k: s[5] for k, s in zip(self.vars, specs)}

        res = ttk.LabelFrame(self, text="  Estimated result  ")
        res.pack(fill="x", padx=14, pady=8)
        self.temp_lbl = tk.Label(res, text="-", bg=CARD, fg=TEXT, font=(FONT, 30, "bold"))
        self.temp_lbl.pack(pady=(10, 0))
        self.verdict = tk.Label(res, text="", bg=CARD, font=(FONT, 12, "bold"))
        self.verdict.pack()
        self.gauge = Gauge(res, height=84)
        self.gauge.pack(fill="x", padx=20, pady=6)
        self.info = tk.Label(res, text="", bg=CARD, fg=MUTED, font=(FONT, 9), justify="left")
        self.info.pack(pady=(0, 10))
        self.best = ttk.Label(self, text="", style="Muted.TLabel", wraplength=980, justify="left")
        self.best.pack(fill="x", padx=14)

    def retrain(self):
        try:
            self.model.fit(self.app.db.fetch("cfd_runs"))
        except ValueError:
            self.model = LinearModel()
        syn = self.app.db.source_counts("cfd_runs").get("synthetic", 0)
        self.syn_note = f" ({syn} of them synthetic sample data)" if syn else ""
        b = self.app.db.best_cfd()
        self.best.config(text=(f"Best setup recorded so far:  flow strength {b['reynolds']},  "
                               f"{b['concentration']:g}% nanoparticles,  inlet {b['inlet_temp']:g} °C  →  "
                               f"hottest {b['max_temp']} °C, spread {b['delta_t']} °C.") if b else "")
        self.update_result()

    def on_move(self, key, fmt):
        self.val_lbl[key].config(text=fmt.format(self.vars[key].get()))
        self.update_result()

    def update_result(self):
        if self.model.w is None:
            self.temp_lbl.config(text="-", fg=MUTED)
            self.verdict.config(text="Add at least 5 cooling simulations to enable predictions.", fg=MUTED)
            self.gauge.show(None)
            self.info.config(text="")
            return
        p = self.model.predict(round(self.vars["reynolds"].get()), self.vars["concentration"].get(),
                               self.vars["inlet_temp"].get())
        if p > TEMP_MAX:
            col, msg = BAD, "✖  Too hot: above the 45 °C safety limit"
        elif p > TEMP_MAX - 5:
            col, msg = WARN, "⚠  Close to the limit: be careful"
        else:
            col, msg = GOOD, "✔  Safe temperature"
        self.temp_lbl.config(text=f"{p:.1f} °C", fg=col)
        self.verdict.config(text=msg, fg=col)
        self.gauge.show(p)
        self.info.config(text=f"Learned from {self.model.n} simulations{self.syn_note}. Matches them about "
                              f"{self.model.r2 * 100:.0f}% of the time (an estimate, not a guarantee).")
