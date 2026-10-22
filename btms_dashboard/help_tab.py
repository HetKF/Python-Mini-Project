# Help tab: plain-language guide and glossary

import tkinter as tk
from tkinter import ttk
from config import CARD, FONT, HELP_TEXT, NAVY, TEXT


class HelpTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        box = tk.Text(self, wrap="word", bg=CARD, fg=TEXT, font=(FONT, 10), relief="flat", padx=22, pady=16,
                      spacing1=2, spacing3=4, highlightthickness=1, highlightbackground="#dbe0ea")
        box.pack(fill="both", expand=True, padx=14, pady=14)
        box.tag_configure("h", font=(FONT, 11, "bold"), foreground=NAVY, spacing1=10)
        for para in HELP_TEXT.split("\n\n"):
            first, _, rest = para.partition("\n")
            if first.isupper() or first.startswith(("HOW TO", "SAVING", "WORDS", "WHAT IS", "ABOUT")):
                box.insert("end", first + "\n", "h")
                box.insert("end", rest + "\n\n")
            else:
                box.insert("end", para + "\n\n")
        box.config(state="disabled")
