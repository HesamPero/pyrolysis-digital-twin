# 🌿 Biomass Pyrolysis Digital Twin — Public Demo

An interactive dashboard modelling the **mass and energy balance** of a slow pyrolysis process, built as a portfolio demonstration.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

## What it does

Given a biomass biochemical composition and process temperature, the app computes and visualises:

- **Mass balance** — yields of biochar, tar, aqueous phase, and gas
- **Biochar sub-parameters** — carbon/hydrogen content, H/C molar ratio, ash content
- **Gas speciation** — H₂, CH₄, CO₂, CO, C₂H₄, C₂H₆ in both wt% and vol%
- **Energy balance** — chemical energy, sensible heat, condensation heat, and losses in MJ/kg

## Tech stack

| Layer | Tools |
|-------|-------|
| UI framework | Streamlit |
| Visualisation | Plotly (Sankey, Pie, Bar) |
| Physics engine | Python (NumPy, generalised correlations) |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Input parameters

| Parameter | Range |
|-----------|-------|
| Cellulose content | 20 – 60 % |
| Hemicellulose content | 5 – 35 % |
| Lignin content | 5 – 60 % |
| Ash content | 0 – 10 % |
| Highest Treatment Temperature (HTT) | 450 – 850 °C |

## Biomass presets

Wood (Pine) · Wheat Straw · Rice Husk · Corn Stover · Sugarcane Bagasse · Miscanthus

## Note on the physics model

This public demo uses **generalised literature correlations** (Neves et al. 2011; Antal & Grønli 2003) for illustrative purposes.  
The proprietary multivariate regression model derived from experimental PYREKA/PyFlex reactor data is **not included**.

## Deploy to Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py`
4. Deploy ✅

---

*Built with Python & Streamlit · Portfolio project*
