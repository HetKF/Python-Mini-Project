# Hand-drawn canvas charts: bar chart, line chart and the temperature gauge

import tkinter as tk
from config import ACCENT, BAD, CARD, FONT, GOOD, MUTED, NAVY, TEMP_MAX, TEMP_MIN, TEXT, WARN


class Chart(tk.Canvas):

    def __init__(self, master, **kw):
        super().__init__(master, bg=CARD, highlightthickness=1, highlightbackground="#dbe0ea", **kw)
        self._args = None
        self.bind("<Configure>", lambda e: self._redraw())

    def show(self, *args, **kw):
        self._args = (args, kw)
        self._redraw()

    def _redraw(self):
        if self._args:
            self.delete("all")
            self.render(self.winfo_width(), self.winfo_height(), *self._args[0], **self._args[1])

    def empty(self, w, h, msg="No data yet"):
        self.create_text(w / 2, h / 2, text=msg, fill=MUTED, font=(FONT, 11))


class BarChart(Chart):
    def render(self, w, h, labels, values, title, limit=None):
        self.create_text(14, 16, text=title, anchor="w", font=(FONT, 11, "bold"), fill=NAVY)
        if not values:
            return self.empty(w, h)
        top = max(max(values), limit or 0) * 1.15
        left, bottom = 46, h - 30
        bw = (w - left - 14) / len(values)
        for i, (lab, v) in enumerate(zip(labels, values)):
            x0 = left + i * bw + 6
            y0 = bottom - (v / top) * (bottom - 44)
            color = BAD if limit and v > limit else (WARN if limit and v > limit - 5 else GOOD)
            self.create_rectangle(x0, y0, x0 + bw - 12, bottom, fill=color, outline="")
            self.create_text(x0 + (bw - 12) / 2, y0 - 9, text=f"{v:.1f}", font=(FONT, 8), fill=TEXT)
            self.create_text(x0 + (bw - 12) / 2, bottom + 14, text=lab, font=(FONT, 9), fill=MUTED)
        if limit:
            y = bottom - (limit / top) * (bottom - 44)
            self.create_line(left, y, w - 10, y, fill=BAD, dash=(5, 4))
            self.create_text(left - 6, y, text=f"{limit:g}", anchor="e", fill=BAD, font=(FONT, 8, "bold"))
            self.create_text(w - 12, y - 9, text="safe limit", anchor="e", fill=BAD, font=(FONT, 8))
        self.create_line(left, bottom, w - 10, bottom, fill="#c5ccd9")


class LineChart(Chart):
    def render(self, w, h, values, title, limit=None):
        self.create_text(14, 16, text=title, anchor="w", font=(FONT, 11, "bold"), fill=NAVY)
        if len(values) < 2:
            return self.empty(w, h)
        lo = min(min(values), TEMP_MIN)
        hi = max(max(values), limit or 0) + 3
        left, right, top, bottom = 46, w - 14, 40, h - 24

        def X(i): return left + i * (right - left) / (len(values) - 1)
        def Y(v): return bottom - (v - lo) / (hi - lo) * (bottom - top)
        for t in range(int(lo // 5 * 5), int(hi) + 1, 5):
            if lo <= t <= hi:
                self.create_line(left, Y(t), right, Y(t), fill="#edf0f5")
                self.create_text(left - 6, Y(t), text=str(t), anchor="e", font=(FONT, 8), fill=MUTED)
        if limit:
            self.create_line(left, Y(limit), right, Y(limit), fill=BAD, dash=(5, 4))
            self.create_text(right, Y(limit) - 9, text=f"safe limit {limit:g} °C", anchor="e",
                             font=(FONT, 8), fill=BAD)
        pts = [c for i, v in enumerate(values) for c in (X(i), Y(v))]
        self.create_line(*pts, fill=ACCENT, width=2.5, smooth=True)
        self.create_text(right, bottom + 12, text="time  →", anchor="e", font=(FONT, 8), fill=MUTED)


class Gauge(Chart):

    def render(self, w, h, value=None):
        lo, hi = 10.0, 60.0
        x0, x1, y0, y1 = 20, w - 20, 28, 52

        def X(v): return x0 + (min(max(v, lo), hi) - lo) / (hi - lo) * (x1 - x0)
        self.create_rectangle(X(lo), y0, X(TEMP_MIN), y1, fill="#9ec5ee", outline="")
        self.create_rectangle(X(TEMP_MIN), y0, X(TEMP_MAX - 5), y1, fill=GOOD, outline="")
        self.create_rectangle(X(TEMP_MAX - 5), y0, X(TEMP_MAX), y1, fill=WARN, outline="")
        self.create_rectangle(X(TEMP_MAX), y0, X(hi), y1, fill=BAD, outline="")
        for t in (10, 15, 30, 45, 60):
            self.create_text(X(t), y1 + 12, text=f"{t}°", font=(FONT, 8), fill=MUTED)
        if value is not None:
            x = X(value)
            self.create_polygon(x, y0 - 2, x - 7, y0 - 14, x + 7, y0 - 14, fill=NAVY, outline="")
            self.create_line(x, y0, x, y1, fill=NAVY, width=3)
