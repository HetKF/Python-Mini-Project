# SQLite layer: creates tables, does add/edit/delete, runs the dashboard queries, loads real + synthetic sample data

import csv
import glob
import os
import random
import sqlite3
from config import DATA_DIR, MAX_DELTA_T, TEMP_MAX, TEMP_MIN, DB_FILE

SENSOR_INSERT = ("INSERT INTO sensor_readings (ts,cell_id,battery_temp,coolant_in,coolant_out,"
                 "voltage,current,flow_rate,notes,source) VALUES (?,?,?,?,?,?,?,?,?,?)")
CFD_INSERT = ("INSERT INTO cfd_runs (reynolds,concentration,inlet_temp,max_temp,delta_t,"
              "pressure_drop,htc,notes,source) VALUES (?,?,?,?,?,?,?,?,?)")


class Database:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            cell_id TEXT NOT NULL,
            battery_temp REAL NOT NULL,
            coolant_in REAL NOT NULL,
            coolant_out REAL NOT NULL,
            voltage REAL,
            current REAL,
            flow_rate REAL,
            notes TEXT,
            source TEXT NOT NULL DEFAULT 'user'
        );
        CREATE TABLE IF NOT EXISTS cfd_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reynolds INTEGER NOT NULL,
            concentration REAL NOT NULL,
            inlet_temp REAL NOT NULL,
            max_temp REAL NOT NULL,
            delta_t REAL NOT NULL,
            pressure_drop REAL,
            htc REAL,
            notes TEXT,
            source TEXT NOT NULL DEFAULT 'user'
        );
        """)
        for table in ("sensor_readings", "cfd_runs"):
            cols = [r["name"] for r in self.conn.execute(f"PRAGMA table_info({table})")]
            if "source" not in cols:
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN source TEXT NOT NULL DEFAULT 'user'")
        self.conn.commit()

    def fetch(self, table, where="", params=()):
        sql = f"SELECT * FROM {table} {where} ORDER BY id DESC"
        return self.conn.execute(sql, params).fetchall()

    def insert(self, table, data: dict):
        cols = ", ".join(data)
        q = ", ".join("?" * len(data))
        cur = self.conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({q})", tuple(data.values()))
        self.conn.commit()
        return cur.lastrowid

    def update(self, table, row_id, data: dict):
        sets = ", ".join(f"{k}=?" for k in data)
        self.conn.execute(f"UPDATE {table} SET {sets} WHERE id=?", (*data.values(), row_id))
        self.conn.commit()

    def delete(self, table, row_id):
        self.conn.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
        self.conn.commit()

    def count(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def source_counts(self, table):
        rows = self.conn.execute(f"SELECT source, COUNT(*) n FROM {table} GROUP BY source").fetchall()
        return {r["source"]: r["n"] for r in rows}

    def summary(self):
        r = self.conn.execute("""
            SELECT COUNT(*) n, AVG(battery_temp) avg_t, MAX(battery_temp) max_t,
                   MIN(battery_temp) min_t FROM sensor_readings""").fetchone()
        return dict(r)

    def alerts(self):
        return self.conn.execute(
            "SELECT * FROM sensor_readings WHERE battery_temp > ? OR battery_temp < ? "
            "ORDER BY id DESC", (TEMP_MAX, TEMP_MIN)).fetchall()

    def cell_stats(self):
        return self.conn.execute("""
            SELECT cell_id, COUNT(*) n, AVG(battery_temp) avg_t, MAX(battery_temp) max_t
            FROM sensor_readings GROUP BY cell_id ORDER BY CAST(SUBSTR(cell_id,2) AS INTEGER)
        """).fetchall()

    def trend(self, cell=None, points=60):
        sql = "SELECT ts, AVG(battery_temp) t FROM sensor_readings"
        sql += " WHERE cell_id=?" if cell else ""
        sql += " GROUP BY ts ORDER BY ts"
        values = [r["t"] for r in self.conn.execute(sql, (cell,) if cell else ())]
        if len(values) <= points:
            return values
        step = (len(values) - 1) / (points - 1)
        return [values[round(i * step)] for i in range(points)]

    def best_cfd(self):
        return self.conn.execute(
            "SELECT * FROM cfd_runs WHERE delta_t < ? ORDER BY max_temp ASC, pressure_drop ASC LIMIT 1",
            (MAX_DELTA_T,)).fetchone()

    def has_source(self, table, source):
        return self.conn.execute(f"SELECT 1 FROM {table} WHERE source=? LIMIT 1", (source,)).fetchone() is not None

    def load_real(self):
        rows = []
        for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.csv"))):
            with open(path, newline="") as f:
                for r in csv.DictReader(f):
                    rows.append((r["ts"], r["cell_id"], float(r["battery_temp"]), float(r["coolant_in"]),
                                 float(r["coolant_out"]), float(r["voltage"]), float(r["current"]),
                                 None, r["notes"], "real"))
        self.conn.executemany(SENSOR_INSERT, rows)
        self.conn.commit()
        return len(rows)

    def load_synthetic_sensors(self):
        random.seed(7)
        rows = []
        for step in range(60):
            for c in (8, 9, 10):
                s = 120 * step
                heating = 22 + 0.18 * step + random.uniform(-0.8, 0.8) + (c % 4) * 0.5
                cin = 20 + random.uniform(-0.3, 0.3)
                rows.append((f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}", f"C{c}", round(heating, 2),
                             round(cin, 2), round(cin + 0.25 * (heating - cin), 2),
                             round(4.2 - 0.003 * step + random.uniform(-0.01, 0.01), 3),
                             round(3.0 + random.uniform(-0.1, 0.1), 2),
                             random.choice([60.0, 80.0, 100.0]), "synthetic cell", "synthetic"))
        for cell, temp in (("C8", 46.8), ("C9", 48.2), ("C10", 45.6)):
            rows.append(("01:59:00", cell, temp, 20.1, 31.0, 3.9, 3.1, 60.0, "synthetic fast-charge spike", "synthetic"))
        self.conn.executemany(SENSOR_INSERT, rows)
        self.conn.commit()
        return len(rows)

    def load_synthetic_cfd(self):
        random.seed(7)
        rows = []
        for re_ in (400, 450, 500, 550, 600, 650, 700):
            for phi in (0.0, 0.5, 1.0, 1.5, 2.0):
                for tin in (20, 25, 30):
                    maxt = (tin + 16 - 0.012 * (re_ - 400) - 1.4 * phi
                            + 0.35 * phi ** 2 + random.uniform(-0.3, 0.3))
                    dt = max(1.0, 6.5 - 0.004 * (re_ - 400) - 0.6 * phi + random.uniform(-0.2, 0.2))
                    dp = 120 + 0.9 * (re_ - 400) * (1 + 0.15 * phi)
                    htc = 1800 + 3.2 * (re_ - 400) + 260 * phi - 40 * phi ** 2
                    rows.append((re_, phi, tin, round(maxt, 2), round(dt, 2), round(dp, 1), round(htc, 1),
                                 "synthetic (not real ANSYS output)", "synthetic"))
        self.conn.executemany(CFD_INSERT, rows)
        self.conn.commit()
        return len(rows)

    def seed(self):
        added = {"real": 0, "synthetic_sensors": 0, "synthetic_cfd": 0}
        if not self.has_source("sensor_readings", "real"):
            added["real"] = self.load_real()
        if not self.has_source("sensor_readings", "synthetic"):
            added["synthetic_sensors"] = self.load_synthetic_sensors()
        if not self.has_source("cfd_runs", "synthetic"):
            added["synthetic_cfd"] = self.load_synthetic_cfd()
        return added
