"""Decorative orbital illustration. It never represents battery measurements."""
import math
import random
import time
import tkinter as tk
from config import ACCENT, BG, FONT, MUTED


class OrbitalVisual(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG, highlightthickness=0, **kwargs)
        rng = random.Random(42)
        self.stars = [(rng.random(), rng.random(), rng.choice((1, 1, 2))) for _ in range(70)]
        self.offset = (0, 0)
        self.started = time.monotonic()
        self.timer = None
        self.bind("<Motion>", self.track)
        self.bind("<Leave>", lambda _: setattr(self, "offset", (0, 0)))
        self.bind("<Destroy>", self.stop)
        self.animate()

    def track(self, event):
        self.offset = ((event.x / max(self.winfo_width(), 1) - .5) * 12,
                       (event.y / max(self.winfo_height(), 1) - .5) * 8)

    def stop(self, event):
        if event.widget is self and self.timer:
            self.after_cancel(self.timer)
            self.timer = None

    def animate(self):
        if self.winfo_ismapped():
            self.draw()
        self.timer = self.after(50, self.animate)

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        for x, y, r in self.stars:
            self.create_oval(x*w, y*h, x*w+r, y*h+r, fill="#555050", outline="")
        phase = (time.monotonic() - self.started) * math.tau / 8
        cx, cy = w*.52 + self.offset[0], h*.48 + math.sin(phase)*7 + self.offset[1]
        r = min(h*.36, w*.29)
        for scale in (1.3, 1.65):
            self.create_oval(cx-r*scale, cy-r*scale, cx+r*scale, cy+r*scale,
                             outline="#242021")
        for i in range(18, 0, -1):
            d = r + i*2
            self.create_oval(cx-d, cy-d, cx+d, cy+d, outline=f'#{max(8, 35-i):02x}0c08')
        self.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#2b0c06", outline="#863515")
        # Nested offset discs approximate a lit sphere without external images.
        for i in range(50):
            t = i / 50
            radius = r * (1 - t*.78)
            x, y = cx-r*t*.39, cy-r*t*.38
            color = '#%02x%02x%02x' % (int(61+154*t), int(19+65*t), int(9+20*t))
            self.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")
        for i in range(7):
            y = cy-r*.65+i*r*.21
            half = math.sqrt(max(0, r*r-(y-cy)**2))
            self.create_arc(cx-half, y-14, cx+half, y+18, start=185, extent=160,
                            style="arc", outline="#a64924")
        self.create_oval(cx-r*1.55, cy-r*.38, cx+r*1.55, cy+r*.38,
                         outline="#9c492b", width=1)
        ox, oy = cx+math.cos(phase)*r*1.55, cy+math.sin(phase)*r*.38
        self.create_oval(ox-3, oy-3, ox+3, oy+3, fill=ACCENT, outline="")
        self.create_text(16, h-14, text="THERMAL ORBIT  /  DECORATIVE VISUAL", anchor="w",
                         fill=MUTED, font=(FONT, 8))
