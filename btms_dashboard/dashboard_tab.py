# Home tab: summary cards, safety banner and the two charts

import tkinter as tk
from tkinter import ttk
from charts import BarChart, LineChart
from space_visual import OrbitalVisual
from config import BG, HEADING_FONT, ACCENT, BAD, CARD, FONT, GOOD, MUTED, REAL_CREDIT, TEMP_MAX, TEMP_MIN, TEXT, WARN


class KpiCard(tk.Frame):
    def __init__(self, master, title, caption, color=ACCENT):
        super().__init__(master, bg=CARD, highlightthickness=1, highlightbackground="#29292d")
        self.bind("<Enter>", lambda _: self.configure(highlightbackground=ACCENT))
        self.bind("<Leave>", lambda _: self.configure(highlightbackground="#29292d"))
        tk.Frame(self, bg=color, width=2).pack(side="left", fill="y")
        body = tk.Frame(self, bg=CARD)
        body.pack(side="left", fill="both", expand=True, padx=12, pady=8)
        tk.Label(body, text=title, bg=CARD, fg=MUTED, font=(FONT, 9, "bold")).pack(anchor="w")
        self.value = tk.Label(body, text="-", bg=CARD, fg=TEXT, font=(FONT, 19, "bold"))
        self.value.pack(anchor="w")
        tk.Label(body, text=caption, bg=CARD, fg=MUTED, font=(FONT, 8)).pack(anchor="w")

    def set(self, text, color=TEXT):
        self.value.config(text=text, fg=color)


class DashboardTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        hero = ttk.Frame(self)
        hero.pack(fill="x", padx=14, pady=(8, 0))
        hero.columnconfigure(0, weight=5)
        hero.columnconfigure(1, weight=7)
        intro = ttk.Frame(hero)
        intro.grid(row=0, column=0, sticky="nsew", padx=(8, 20), pady=24)
        ttk.Label(intro, text="01  /  SYSTEM OVERVIEW", foreground=ACCENT,
                  font=(FONT, 9, "bold")).pack(anchor="w")
        ttk.Label(intro, text="KEEP COOL.\nGO FURTHER.", font=(HEADING_FONT, 36, "bold")).pack(
            anchor="w", pady=(12, 8))
        ttk.Label(intro, text="Ten cells. One clear view.\nExplore battery temperatures, cooling simulations\nand predictions from your saved data.",
                  style="Muted.TLabel", font=(FONT, 10), justify="left").pack(anchor="w")
        self.orbit = OrbitalVisual(hero, height=245, width=400)
        self.orbit.grid(row=0, column=1, sticky="nsew")
        self.banner = tk.Label(self, text="", font=(FONT, 10, "bold"), fg=TEXT, pady=11)
        self.banner.pack(fill="x", padx=14, pady=(12, 8))

        def resize_hero(event):
            if event.widget is not self:
                return
            if event.height < 730:
                hero.pack_forget()
            elif not hero.winfo_manager():
                hero.pack(fill="x", padx=14, pady=(8, 0), before=self.banner)
        self.bind("<Configure>", resize_hero)


        row = ttk.Frame(self)
        row.pack(fill="x", padx=10)
        specs = [("n", "READINGS", "temperature readings stored", ACCENT),
                 ("avg", "AVERAGE TEMP", "across all battery cells", ACCENT),
                 ("max", "HOTTEST READING", "should stay under 45 °C", WARN),
                 ("alerts", "WARNINGS", "readings outside safe range", BAD),
                 ("cfd", "SIMULATIONS", "cooling runs in the database", "#b29bde"),
                 ("best", "BEST COOLING SETUP", "lowest temp with even spread", GOOD)]
        self.cards = {}
        for index, (key, title, cap, col) in enumerate(specs):
            card = KpiCard(row, title, cap, col)
            card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=4, pady=4)
            row.columnconfigure(index % 3, weight=1)
            self.cards[key] = card

        charts = ttk.Frame(self)
        charts.pack(fill="both", expand=True, padx=10, pady=10)
        charts.columnconfigure(0, weight=1)
        charts.columnconfigure(1, weight=1)
        charts.rowconfigure(0, weight=1)
        self.bar = BarChart(charts, height=250)
        self.bar.grid(row=0, column=0, sticky="nsew", padx=4)
        self.line = LineChart(charts, height=250)
        self.line.grid(row=0, column=1, sticky="nsew", padx=4)
        foot = ttk.Frame(self)
        foot.pack(fill="x", padx=14)
        ttk.Label(foot, text="Time chart shows:").pack(side="left")
        self.pick = tk.StringVar(value="All cells")
        self.combo = ttk.Combobox(foot, textvariable=self.pick, width=14, state="readonly", values=["All cells"])
        self.combo.pack(side="left", padx=6)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_line())
        ttk.Label(foot, text="Colour guide:  green = safe   |   amber = close to the limit   |   red = too hot",
                  style="Muted.TLabel").pack(side="right")
        self.sources = ttk.Label(self, text="", style="Muted.TLabel", wraplength=1040, justify="left")
        self.sources.pack(fill="x", padx=14, pady=(4, 8))

    def refresh_line(self):
        cell = self.pick.get()
        title = "Average battery temperature over time (°C)"
        self.line.show(self.app.db.trend(None if cell == "All cells" else cell),
                       title if cell == "All cells" else f"{title}  -  {cell}", limit=TEMP_MAX)

    def describe_sources(self):
        db = self.app.db
        s, c = db.source_counts("sensor_readings"), db.source_counts("cfd_runs")
        parts = []
        if s.get("real"):
            parts.append(f"{s['real']:,} real lab readings (cells C1 to C7 are test runs of one cell: {REAL_CREDIT})")
        if s.get("synthetic"):
            parts.append(f"{s['synthetic']:,} synthetic readings (C8 to C10)")
        if c.get("synthetic"):
            parts.append(f"{c['synthetic']:,} synthetic cooling simulations")
        mine = sum(v for k, v in s.items() if k in ("user", "imported")) + sum(
            v for k, v in c.items() if k in ("user", "imported"))
        if mine:
            parts.append(f"{mine:,} rows entered or imported by you")
        return "Data in use:  " + "   ·   ".join(parts) if parts else ""

    def refresh(self):
        db = self.app.db
        s, al = db.summary(), db.alerts()
        c = self.cards
        c["n"].set(s["n"])
        c["avg"].set(f"{s['avg_t']:.1f} °C" if s["avg_t"] else "-")
        mx = s["max_t"]
        c["max"].set(f"{mx:.1f} °C" if mx else "-", BAD if mx and mx > TEMP_MAX else TEXT)
        c["alerts"].set(len(al), BAD if al else GOOD)
        c["cfd"].set(db.count("cfd_runs"))
        b = db.best_cfd()
        c["best"].set(f"Flow {b['reynolds']} · {b['concentration']:g}%" if b else "-", GOOD if b else TEXT)
        cs = db.cell_stats()
        self.bar.show([r["cell_id"] for r in cs], [r["max_t"] for r in cs],
                      "Hottest reading for each battery cell (°C)", limit=TEMP_MAX)
        self.combo.configure(values=["All cells"] + [r["cell_id"] for r in cs])
        if self.pick.get() not in ["All cells"] + [r["cell_id"] for r in cs]:
            self.pick.set("All cells")
        self.refresh_line()
        self.sources.config(text=self.describe_sources())
        if not s["n"]:
            self.banner.config(text="No readings yet. Add some on the 'Temperature Readings' tab "
                                    "or use  Data ▸ Load sample data.", bg="#252528", fg=MUTED)
        elif al:
            self.banner.config(text=f"⚠  {len(al)} reading(s) went outside the safe range "
                                    f"({TEMP_MIN:g}–{TEMP_MAX:g} °C). See the Warnings tab.", bg="#361b1c", fg=BAD)
        else:
            self.banner.config(text="✔  All batteries are within the safe temperature range.", bg="#13281f", fg=GOOD)
