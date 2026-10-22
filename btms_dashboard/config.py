# Constants shared everywhere: file name, safe limits, colours, table columns, labels, help text

import os

DB_FILE = "btms.db"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "real")
TEMP_MIN, TEMP_MAX = 15.0, 45.0
MAX_DELTA_T = 5.0
MAX_ROWS = 1500

SOURCE_NAMES = {"real": "Real lab data", "synthetic": "Synthetic", "user": "Entered by you",
                "imported": "Imported"}
REAL_CREDIT = "A123 26650 cell lab tests, Kawakita de Souza (2021), CC BY 4.0"

BG = "#050505"
CARD = "#111113"
NAVY = "#f4f1ed"
ACCENT = "#ff4d00"
GOOD = "#72d5a3"
WARN = "#eab467"
BAD = "#ff7d78"
TEXT = "#f4f1ed"
MUTED = "#a2a2ab"
BORDER = "#29292d"
FONT = "Satoshi"
HEADING_FONT = "Cabinet Grotesk"

SENSOR_COLS = [("id", "No.", 50), ("ts", "Date & time", 150), ("cell_id", "Cell", 55),
               ("battery_temp", "Battery °C", 90), ("coolant_in", "Coolant in °C", 95),
               ("coolant_out", "Coolant out °C", 105), ("voltage", "Volts", 60),
               ("current", "Amps", 60), ("flow_rate", "Flow mL/min", 90), ("notes", "Notes", 150),
               ("source", "Data source", 115)]
CFD_COLS = [("id", "No.", 50), ("reynolds", "Flow strength", 95), ("concentration", "Nanoparticle %", 105),
            ("inlet_temp", "Inlet °C", 75), ("max_temp", "Hottest °C", 85),
            ("delta_t", "Spread °C", 80), ("pressure_drop", "Pressure Pa", 95),
            ("htc", "Heat transfer", 100), ("notes", "Notes", 130), ("source", "Data source", 115)]
SENSOR_LABELS = {
    "ts": "Date & time (leave blank = now)", "cell_id": "Battery cell",
    "battery_temp": "Battery temperature (°C)", "coolant_in": "Coolant going in (°C)",
    "coolant_out": "Coolant coming out (°C)", "voltage": "Voltage (V)  - optional",
    "current": "Current (A)  - optional", "flow_rate": "Coolant flow (mL/min)  - optional",
    "notes": "Notes  - optional"}
CFD_LABELS = {
    "reynolds": "Flow strength - Reynolds no. (400 to 700)", "concentration": "Nanoparticles in coolant (%)",
    "inlet_temp": "Coolant inlet temperature (°C)", "max_temp": "Hottest battery temperature (°C)",
    "delta_t": "Temperature spread across cells (°C)", "pressure_drop": "Pressure drop (Pa)  - optional",
    "htc": "Heat transfer (W/m²K)  - optional", "notes": "Notes  - optional"}
SENSOR_INTRO = ("Each row is one temperature reading taken from one battery cell. "
                "Fill in the form and press  Add reading.  Click a row to change or delete it. "
                "Rows shaded red are too hot or too cold. "
                "The last column tells you if a row is real lab data or synthetic sample data.")
CFD_INTRO = ("Each row is one computer simulation (ANSYS Fluent) of the cooling system. "
             "These runs are what the prediction page learns from. "
             "Rows shaded red have an uneven temperature spread (5 °C or more). "
             "The sample simulations are synthetic (made up for the demo), and are labelled that way.")

HELP_TEXT = """\
WHAT IS THIS PROGRAM?
It helps monitor the cooling of an electric-vehicle battery pack. The pack has 10 battery cells (C1 to C10) \
cooled by liquid flowing through tiny channels. Too much heat shortens battery life and can be dangerous, so \
we record temperatures, store cooling simulations, and predict how hot the battery will get.

HOW TO USE IT  (4 easy steps)
1.  Home: see the overall picture. A green banner means everything is safe.
2.  Temperature Readings: type in or import real measurements from the battery cells.
3.  Cooling Simulations: store results of computer simulations of different cooling settings.
4.  Predict Temperature: move the sliders to see how hot the battery would get with new settings.
The Warnings tab lists every reading that went outside the safe range.

SAVING AND SHARING DATA
Everything is saved automatically in a file called btms.db next to this program. Use 'Export to CSV' to open \
your data in Excel, and 'Import from CSV' to bring data in.

WORDS YOU MAY MEET
Battery cell     One cylindrical lithium-ion cell (21700 type). There are ten, named C1 to C10.
Coolant          The liquid that carries heat away from the cells.
Nanoparticles    Tiny particles (aluminium oxide, Al2O3) mixed into water so it removes heat better.
Reynolds number  A measure of how fast and turbulent the coolant flows. Studied range here: 400 to 700.
Spread (ΔT)      The temperature difference between the hottest and coolest cell. Target: under 5 °C.
Pressure drop    How hard the pump must work. Lower means less energy used.
Safe range       15 to 45 °C, as set in the case study.
CFD              Computer simulation of fluid flow and heat (done in ANSYS Fluent).

WHERE THE DATA COMES FROM
Real lab data: temperature, voltage and current of an A123 26650 lithium-ion cell tested in a thermal chamber \
(charging at 1C to 4C, drive-cycle discharge, pulse tests). Author: Aloisio Kawakita de Souza, University of \
Colorado Colorado Springs, 2021, CC BY 4.0 (github.com/aloisiohks/A123_26650_m1b_LAB_Dataset). In this program the \
cell labels C1 to C7 are seven test runs of that one cell, and the coolant columns hold the chamber air temperature.
Synthetic data: readings for cells C8 to C10 (including three overheating events) and all the cooling simulations \
were generated by the program for the demo. They are not real measurements, and every row says so in its Data source \
column.

ABOUT
Case study KJS-CES-02: AI-Enabled Micro-channel Battery Thermal Management System for Electric Vehicles \
(K J Somaiya School of Engineering). Built with Python, tkinter and SQLite.
"""
