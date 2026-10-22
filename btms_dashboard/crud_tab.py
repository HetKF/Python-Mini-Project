# Reusable tab with a form and a table for adding, editing, deleting, searching and CSV import/export

from datetime import datetime
import csv
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from config import ACCENT, FONT, MAX_DELTA_T, MAX_ROWS, MUTED, SOURCE_NAMES, TEMP_MAX, TEMP_MIN


class CrudTab(ttk.Frame):

    def __init__(self, master, app, table, columns, fields, labels, defaults, intro, noun):
        super().__init__(master)
        ttk.Label(self, text=("02  /  TEMPERATURE READINGS" if table == "sensor_readings" else "03  /  COOLING SIMULATIONS"), style="Title.TLabel").pack(anchor="w", padx=14, pady=(18, 8))
        self.app, self.table, self.columns, self.fields = app, table, columns, fields
        self.labels, self.defaults, self.noun = labels, defaults, noun
        self.selected_id = None
        self.vars = {f: tk.StringVar(value=defaults.get(f, "")) for f in fields}

        ttk.Label(self, text=intro, style="Muted.TLabel", wraplength=980, justify="left").pack(
            fill="x", padx=14, pady=(12, 4))

        form = ttk.LabelFrame(self, text="  Add or edit a record  ")
        form.pack(fill="x", padx=14, pady=6)
        self.mode = tk.StringVar()
        ttk.Label(form, textvariable=self.mode, style="Card.TLabel", foreground=ACCENT,
                  font=(FONT, 10, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(6, 2))
        for i, f in enumerate(fields):
            r, c = 1 + i // 4 * 2, i % 4
            ttk.Label(form, text=labels[f], style="Card.TLabel", foreground=MUTED).grid(
                row=r, column=c, sticky="w", padx=10, pady=(6, 0))
            if f == "cell_id":
                w = ttk.Combobox(form, textvariable=self.vars[f], values=[f"C{n}" for n in range(1, 11)],
                                 width=18, state="readonly")
            else:
                w = ttk.Entry(form, textvariable=self.vars[f], width=22)
            w.grid(row=r + 1, column=c, padx=10, pady=(2, 6), sticky="we")
        for c in range(4):
            form.columnconfigure(c, weight=1)

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=14, pady=4)
        ttk.Button(bar, text=f"＋ Add {noun}", style="Good.TButton", command=self.add).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎ Save changes", style="Accent.TButton", command=self.edit).pack(side="left", padx=3)
        ttk.Button(bar, text="🗑 Delete", style="Danger.TButton", command=self.remove).pack(side="left", padx=3)
        ttk.Button(bar, text="Clear form", style="Soft.TButton", command=self.clear).pack(side="left", padx=3)
        ttk.Button(bar, text="Export to CSV", style="Soft.TButton", command=self.export_csv).pack(side="right", padx=3)
        ttk.Button(bar, text="Import from CSV", style="Soft.TButton", command=self.import_csv).pack(side="right", padx=3)

        sbar = ttk.Frame(self)
        sbar.pack(fill="x", padx=14, pady=(8, 0))
        ttk.Label(sbar, text="🔍 Search:").pack(side="left")
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(sbar, textvariable=self.search, width=28).pack(side="left", padx=6)
        self.count_var = tk.StringVar()
        ttk.Label(sbar, textvariable=self.count_var, style="Muted.TLabel").pack(side="left", padx=10)
        ttk.Label(sbar, text="Tip: click a column title to sort", style="Muted.TLabel").pack(side="right")

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=14, pady=8)
        self.tree = ttk.Treeview(wrap, columns=[c[0] for c in columns], show="headings")
        for key, title, w in columns:
            self.tree.heading(key, text=title, command=lambda k=key: self.sort_by(k))
            self.tree.column(key, width=w, anchor="center")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        horizontal = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=horizontal.set)
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.tag_configure("bad", background="#361b1c")
        self.tree.tag_configure("alt", background="#19191c")
        self._sort_rev = False
        self.clear()


    def read_form(self):
        return {f: v.get().strip() for f, v in self.vars.items()}

    def validate(self, data):
        optional = ("voltage", "current", "flow_rate", "pressure_drop", "htc")
        for f in [f for f in data if f not in ("ts", "cell_id", "notes")]:
            if data[f] in ("", None):
                if f in optional:
                    data[f] = None
                    continue
                raise ValueError(f"Please fill in:  {self.labels.get(f, f)}")
            try:
                data[f] = float(data[f])
            except ValueError:
                raise ValueError(f"'{self.labels.get(f, f)}' must be a number (for example 31.5)")
        if self.table == "sensor_readings":
            if not data["cell_id"]:
                raise ValueError("Please choose a battery cell (C1 to C10)")
            if not (-40 <= data["battery_temp"] <= 150):
                raise ValueError("That battery temperature doesn't look realistic. Please double-check it.")
            if not data["ts"]:
                data["ts"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            if not (400 <= data["reynolds"] <= 700):
                raise ValueError("Flow strength (Reynolds number) must be between 400 and 700, "
                                 "the range studied in this project.")
            data["reynolds"] = int(data["reynolds"])
        return data


    def add(self):
        try:
            data = self.validate(self.read_form())
        except ValueError as e:
            return messagebox.showwarning("Please check the form", str(e))
        self.app.db.insert(self.table, data)
        self.app.say(f"✔ {self.noun.capitalize()} added.")
        self.app.refresh_all()

    def edit(self):
        if self.selected_id is None:
            return messagebox.showinfo("Nothing selected", "Click a row in the table first, then change the form and press Save changes.")
        try:
            data = self.validate(self.read_form())
        except ValueError as e:
            return messagebox.showwarning("Please check the form", str(e))
        self.app.db.update(self.table, self.selected_id, data)
        self.app.say(f"✔ Record {self.selected_id} updated.")
        self.app.refresh_all()

    def remove(self):
        if self.selected_id is None:
            return messagebox.showinfo("Nothing selected", "Click the row you want to delete first.")
        if messagebox.askyesno("Delete record", f"Delete record {self.selected_id}? This cannot be undone."):
            self.app.db.delete(self.table, self.selected_id)
            self.app.say(f"✔ Record {self.selected_id} deleted.")
            self.clear()
            self.app.refresh_all()

    def clear(self):
        for f, v in self.vars.items():
            v.set(self.defaults.get(f, ""))
        self.selected_id = None
        self.mode.set(f"Adding a new {self.noun}")

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        row = dict(zip([c[0] for c in self.columns], self.tree.item(sel[0])["values"]))
        self.selected_id = row["id"]
        for f in self.fields:
            v = row.get(f, "")
            self.vars[f].set("" if v in ("None", None) else str(v))
        self.mode.set(f"Editing record {self.selected_id}  (press Save changes, or Clear form to start a new one)")

    def sort_by(self, key):
        idx = [c[0] for c in self.columns].index(key)
        rows = [(self.tree.set(i, key), i) for i in self.tree.get_children("")]
        try:
            rows.sort(key=lambda r: float(r[0]), reverse=self._sort_rev)
        except ValueError:
            rows.sort(key=lambda r: r[0], reverse=self._sort_rev)
        for pos, (_, iid) in enumerate(rows):
            self.tree.move(iid, "", pos)
        self._sort_rev = not self._sort_rev

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        term = self.search.get().strip().lower()
        matches = 0
        shown = 0
        for r in self.app.db.fetch(self.table):
            row = dict(r)
            row["source"] = SOURCE_NAMES.get(row["source"], row["source"])
            if term and term not in " ".join(str(v).lower() for v in row.values()):
                continue
            matches += 1
            if shown >= MAX_ROWS:
                continue
            tag = ("alt",) if shown % 2 else ()
            if self.table == "sensor_readings" and not (TEMP_MIN <= row["battery_temp"] <= TEMP_MAX):
                tag = ("bad",)
            if self.table == "cfd_runs" and row["delta_t"] >= MAX_DELTA_T:
                tag = ("bad",)
            self.tree.insert("", "end", values=[row[c[0]] if row[c[0]] is not None else "" for c in self.columns],
                             tags=tag)
            shown += 1
        total = self.app.db.count(self.table)
        text = f"Showing {shown} of {matches} matching records ({total} in total)"
        if matches > shown:
            text += ".  Use Search to narrow it down."
        self.count_var.set(text)

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"{self.table}.csv",
                                            title="Save data as a spreadsheet file")
        if not path:
            return
        rows = self.app.db.fetch(self.table)
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(rows[0].keys() if rows else [c[0] for c in self.columns])
            for r in rows:
                w.writerow(list(r))
        messagebox.showinfo("Export finished", f"Saved {len(rows)} rows. You can open the file in Excel.")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV / Excel text file", "*.csv")],
                                          title="Choose a CSV file to import")
        if not path:
            return
        ok = bad = 0
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                try:
                    data = self.validate({k: row.get(k, "") for k in self.fields})
                    data["source"] = "imported"
                    self.app.db.insert(self.table, data)
                    ok += 1
                except Exception:
                    bad += 1
        self.app.refresh_all()
        messagebox.showinfo("Import finished", f"Imported {ok} rows. Skipped {bad} rows that had problems.")
