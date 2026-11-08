# ReMat Digital Twin V1

An interactive proof-of-concept dashboard for brine calcium precipitation and magnesium recovery.

## Run
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. `pip install -r requirements.txt`
4. `streamlit run app.py`

The browser opens automatically, typically at http://localhost:8501.

## Important
This version provides mass-balance calculations and explicitly adjustable hypothetical efficiencies, not calibrated chemical predictions. The pH slider is display-only. The sodium carbonate dose is checked for theoretical stoichiometric sufficiency but does not determine calcium removal. Do not present numerical outputs as validated experimental results.
