# ReMat Virtual Laboratory V3

Bench-scale 1–5 L interactive Streamlit demonstrator for Ca precipitation and electrochemical Mg recovery.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## On Streamlit Community Cloud

Replace `app.py`, `requirements.txt`, and `README.md` in the root of your existing GitHub repository. The deployment normally rebuilds automatically.

## Controls

Use **Start/Pause** to control decorative animation, **Next/Previous** to change stage, **Reset** to restart, and the progress slider to scrub through a visual stage. The visual progress is not a kinetic calculation or an automatic time-lapse. Adjust laboratory inputs to update scenario results and charts.

## Scientific caution

This is an exploratory scenario demonstrator, not a validated digital twin. pH response is a heuristic; calcium removal is additionally limited by carbonate stoichiometry. Cell current uses an assumed effective resistance and onset voltage, with idealized Faraday-limited production. No PHREEQC, Pitzer, CFD, measured polarization, or purity model is included. Do not report outputs as measured results.
