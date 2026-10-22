# Data used by the Battery Cooling Monitor

## Real lab data: `real/*.csv` (5,616 rows)

Source: https://github.com/aloisiohks/A123_26650_m1b_LAB_Dataset
Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)
Cite as (as given by the author):
Kawakita de Souza, Aloisio (2021), "Lithium-ion Battery OCV and Dynamic Test Data of a LiFePO4 cylindrical cell",
Mendeley Data, V1, doi: 10.17632/p8kf893yv3.1

A commercial A123 26650 2.5 Ah LiFePO4 cell was cycled with an Arbin BT2000 cycler inside a Cincinnati Sub-Zero thermal
chamber at the High-Voltage Battery Research Lab, University of Colorado Colorado Springs.

Changes we made (we are not the data authors):
- Converted seven MATLAB `.mat` files to CSV: CCCV charging at 1C, 2C, 3C and 4C (25 C chamber), UDDS drive-cycle
  discharge at 25 C and 35 C, and the periodic pulse test.
- Kept every 10th sample (the originals record about once per second).
- Renamed columns to the app's fields. `ts` is elapsed time since the run started (HH:MM:SS).
  `battery_temp` is the cell surface temperature. `coolant_in` and `coolant_out` hold the chamber AIR temperature,
  because this experiment has no liquid coolant. `cell_id` C1 to C7 labels the seven test runs of ONE cell.

## Synthetic data (generated in `database.py`, not stored as files)

- Readings for cells C8 to C10 (60 time steps each) and three overheating events, so the Warnings tab has something to show.
- 105 cooling simulations (7 flow strengths x 5 nanoparticle amounts x 3 inlet temperatures).

These are made up with simple formulas plus random noise. They are NOT measurements or real ANSYS Fluent output.
Every row carries a "Data source" label so real and synthetic data are never mixed up.
