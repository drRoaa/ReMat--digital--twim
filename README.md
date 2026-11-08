# ReMat Digital Twin V2

Interactive animated process overview, mass balances, pH scenario curves, and illustrative electrochemical model.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Update an existing Streamlit Community Cloud app

On GitHub, replace the repository root `app.py` and `requirements.txt` with these V2 files, then commit. The existing Streamlit app should redeploy automatically. Keep the `main` branch and `app.py` entry point.

## Scientific caution

V2 uses **illustrative, uncalibrated** pH/precipitation response functions and a lumped electrical circuit. It is not a thermodynamic or validated electrochemical prediction. Calibrate with laboratory data and a PHREEQC model before treating outputs as forecasts.
