# Battery Cooling Monitor

Python / Tkinter / SQLite mini project, case study KJS-CES-02.

## Run

From the repository root:

```sh
python btms_dashboard/main.py
```

Use Python 3 with Tkinter installed (included with the standard Windows Python installer). No pip dependencies are required. Run from the repository root to use the existing `btms.db`.

## Space-inspired interface

All six original tabs remain: Home, Temperature Readings, Cooling Simulations, Predict Temperature, Warnings, and Help. The numbered rail provides an additional way to select the same tabs.

The interface uses space black, Mars orange, dark bordered panels, matching charts and tables, and a 56px status bar. Home includes a decorative sphere with an eight-second orbit and mouse parallax. The illustration is not a battery model or data visualization. On shorter windows it hides automatically to keep the actual charts and controls accessible.

Install **Satoshi** and **Cabinet Grotesk** locally for the reference typography; Tk substitutes an available font otherwise. This remains a native Tkinter application: translucent browser glass, CSS blur, and actual 3D rendering are approximated with opaque layered colors and Canvas shapes.

Existing database operations, CSV import/export, sample data, search, sorting, prediction calculations, thresholds, and Help content are retained. No database migration is required.
