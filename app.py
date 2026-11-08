import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title='ReMat | Digital Twin V2', page_icon='💧', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.3rem}.stMetric{background:#edf7fa;padding:12px;border-radius:12px}h1,h2,h3{color:#123451}</style>''',unsafe_allow_html=True)
st.title('💧 ReMat Digital Twin | V2')
st.caption('Interactive process visualization + transparent, exploratory chemistry/electrochemistry models. Not a validated process simulator.')
with st.sidebar:
 st.header('⚙️ Operating conditions')
 volume=st.slider('Batch volume (L)',1.,20.,5.,.5)
 ca=st.slider('Ca²⁺ (mg/L)',100,2500,800,50)
 mg=st.slider('Mg²⁺ (mg/L)',100,4000,1500,50)
 ph=st.slider('Precipitation pH',7.,12.,9.5,.1)
 dose=st.slider('Na₂CO₃ dose (g/L)',0.,5.,2.2,.1)
 st.divider()
 st.header('⚡ Electrochemical cell')
 voltage=st.slider('Applied cell voltage (V)',0.,15.,5.,.5)
 resistance=st.slider('Effective cell resistance (Ω)',0.5,20.,4.,.5)
 duration=st.slider('Electrolysis time (min)',5,240,60,5)
 efficiency=st.slider('Faradaic efficiency (assumed, %)',10,100,75,5)/100
 cell_ph=st.slider('Cathode-region pH (assumed)',8.,13.,11.,.1)
 st.divider()
 st.info('All reaction efficiency relationships are illustrative. Calibrate using experiments and PHREEQC before predictive use.')

# Explicit simplified screening model, NOT a thermodynamic equilibrium solver.
ca_mol=ca/1000*volume/40.078
mg_mol=mg/1000*volume/24.305
carbonate_mol=dose*volume/105.99
# assumed carbonate availability increases with pH (pKa2 ~10.33), with HCO3 contribution via dosing
alpha_co3=1/(1+10**(10.33-ph))
# scenario kinetic/availability factor, intentionally not an equilibrium calculation
ca_potential=np.clip((ph-7.4)/1.7,0,1)
ca_removed_mol=min(ca_mol*0.98*ca_potential,carbonate_mol*(0.35+0.65*alpha_co3))
# Mg(OH)2 can precipitate at high pH, illustrative smooth transition; independent of carbonate complexation
mg_loss_fraction=0.32/(1+np.exp(-(ph-10.6)*3.0))
mg_lost_mol=mg_mol*mg_loss_fraction
mg_available_mol=max(mg_mol-mg_lost_mol,0)
# Lumped electrical model: onset voltage and ohmic resistance; actual electrolysis requires measured I-V
current=max(voltage-1.8,0)/resistance
charge=current*duration*60
F=96485.33212
# 2 e- -> 2 OH- for 1 Mg(OH)2 equivalent; pH adjustment factor is empirical placeholder
ph_factor=1/(1+np.exp(-(cell_ph-9.8)*2.8))
mg_converted_mol=min(mg_available_mol,charge*efficiency/(2*F)*ph_factor)
ca_removal=100*ca_removed_mol/ca_mol if ca_mol else 0
mg_loss=100*mg_lost_mol/mg_mol if mg_mol else 0
mg_recovery=100*mg_converted_mol/mg_mol if mg_mol else 0
caco3=ca_removed_mol*100.087
mgh2=mg_converted_mol*58.3197
energy_kwh=voltage*current*duration/60/1000

st.subheader('🏭 Animated process line')
svg=f'''<html><style>body{{margin:0;background:#071b30;font-family:Arial;color:#eef8ff}}svg{{width:100%;height:auto}}.water{{animation:rise 3s ease-in-out infinite alternate}}@keyframes rise{{from{{transform:translateY(5px)}}to{{transform:translateY(-4px)}}}}.flow{{stroke-dasharray:10 9;animation:move 1s linear infinite}}@keyframes move{{to{{stroke-dashoffset:-38}}}}.bubble{{animation:float 2s ease-in-out infinite alternate}}@keyframes float{{to{{transform:translateY(-14px);opacity:.25}}}}text{{font-family:Arial}}</style><svg viewBox="0 0 1100 400" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="tank" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#153a5b"/><stop offset="1" stop-color="#0d263d"/></linearGradient><linearGradient id="liquid" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#32c6db"/><stop offset="1" stop-color="#096f9e"/></linearGradient></defs><text x="25" y="30" font-size="19" font-weight="bold">ReMat • Integrated brine-to-magnesium process</text>
<g stroke="#65d6e9" stroke-width="15" fill="none" opacity=".55"><path d="M210 210H282"/><path d="M470 210H550"/><path d="M748 210H826"/></g><g stroke="#4de8e5" stroke-width="6" fill="none" class="flow"><path d="M210 210H282"/><path d="M470 210H550"/><path d="M748 210H826"/></g>
<g fill="url(#tank)" stroke="#6bbed4" stroke-width="4"><rect x="22" y="86" width="190" height="240" rx="18"/><rect x="282" y="86" width="190" height="240" rx="18"/><rect x="550" y="86" width="198" height="240" rx="18"/><rect x="826" y="86" width="240" height="240" rx="18"/></g>
<g fill="url(#liquid)" opacity=".8" class="water"><path d="M27 206H207V310Q207 320 197 320H37Q27 320 27 310Z"/><path d="M287 206H467V310Q467 320 457 320H297Q287 320 287 310Z"/><path d="M555 206H743V310Q743 320 733 320H565Q555 320 555 310Z"/><path d="M831 206H1061V310Q1061 320 1051 320H841Q831 320 831 310Z"/></g>
<g fill="#fff" font-size="16" text-anchor="middle" font-weight="bold"><text x="117" y="116">1 • Pre-filter</text><text x="377" y="116">2 • Ca precipitation</text><text x="649" y="116">3 • Electrochemical</text><text x="946" y="116">4 • Recovery</text></g>
<g fill="#d4f5fc" font-size="13" text-anchor="middle"><text x="117" y="140">5 µm filter</text><text x="377" y="140">Na₂CO₃ dosing</text><text x="649" y="140">{voltage:.1f} V • {current:.2f} A</text><text x="946" y="140">Mg(OH)₂ collection</text></g>
<g stroke="#c8eaf3" stroke-width="6"><path d="M90 175V295M105 175V295M120 175V295M135 175V295"/><path d="M607 170V285" stroke="#f8a75b" stroke-width="11"/><path d="M685 170V285" stroke="#b9e5ff" stroke-width="11"/></g>
<g fill="#e9f4c3" opacity=".9"><circle class="bubble" cx="355" cy="260" r="6"/><circle class="bubble" cx="387" cy="284" r="8"/><circle class="bubble" cx="420" cy="265" r="5"/><circle class="bubble" cx="633" cy="270" r="6"/><circle class="bubble" cx="667" cy="250" r="4"/><circle cx="923" cy="282" r="10"/><circle cx="956" cy="292" r="7"/><circle cx="981" cy="275" r="8"/></g>
<g fill="#b4eaf2" font-size="13" text-anchor="middle"><text x="117" y="356">Feed: {volume:g} L</text><text x="377" y="356">CaCO₃: {caco3:.2f} g</text><text x="649" y="356">Mg recovery: {mg_recovery:.1f}%</text><text x="946" y="356">Mg(OH)₂: {mgh2:.2f} g</text></g></svg></html>'''
components.html(svg,height=340,scrolling=False)
a,b,c,d=st.columns(4)
a.metric('Ca removal (scenario)',f'{ca_removal:.1f}%')
b.metric('Mg lost in Ca stage (scenario)',f'{mg_loss:.1f}%')
c.metric('Mg recovered (scenario)',f'{mg_recovery:.1f}%')
d.metric('Energy (electrical)',f'{energy_kwh:.4f} kWh')
if mg_loss>5:st.warning('⚠️ Significant magnesium co-precipitation is possible in the Ca-removal stage at this pH (illustrative estimate).')
if carbonate_mol<ca_removed_mol:st.warning('Carbonate dosing is below modeled Ca precipitation demand.')
st.caption('The process animation is schematic; flow, solids and bubbles are not physically simulated. pH response is a screening heuristic, not PHREEQC equilibrium. Voltage response uses an assumed onset voltage and resistance.')
left,right=st.columns(2)
with left:
 st.subheader('Mass balance')
 df=pd.DataFrame({'Quantity':['Ca in feed','Ca removed','Ca remaining','Mg in feed','Mg lost during Ca stage','Mg recovered as Mg(OH)₂','CaCO₃ solids','Mg(OH)₂ solids'],'Mass (g)':[ca_mol*40.078,ca_removed_mol*40.078,(ca_mol-ca_removed_mol)*40.078,mg_mol*24.305,mg_lost_mol*24.305,mg_converted_mol*24.305,caco3,mgh2]})
 st.dataframe(df,hide_index=True,use_container_width=True)
with right:
 st.subheader('Electrical model')
 st.write(f'Estimated current: **{current:.2f} A** · Charge: **{charge:.0f} C** · Energy: **{energy_kwh:.4f} kWh**')
 st.write('Faraday-limited Mg(OH)₂ formation: 2 mol electrons per mol Mg(OH)₂. This assumes sufficient Mg²⁺ and does not predict real electrode selectivity, mass transfer or electrode overpotentials.')
 st.write('For experimental calibration, measure: actual current vs. voltage, conductivity, electrode area, cathode pH, Mg/Ca after each stage, product purity and energy.')

st.subheader('Sensitivity analyses (same assumptions)')
phs=np.linspace(7,12,101)
ca_curve=[];loss_curve=[]
for p in phs:
 a=1/(1+10**(10.33-p)); ca_curve.append(100*min(ca_mol*0.98*np.clip((p-7.4)/1.7,0,1),carbonate_mol*(0.35+0.65*a))/ca_mol)
 loss_curve.append(100*.32/(1+np.exp(-(p-10.6)*3)))
fig=go.Figure();fig.add_trace(go.Scatter(x=phs,y=ca_curve,name='Ca removal (scenario)'));fig.add_trace(go.Scatter(x=phs,y=loss_curve,name='Mg loss (scenario)'));fig.add_vline(x=ph,line_dash='dash');fig.update_layout(xaxis_title='Precipitation pH',yaxis_title='Fraction (%)',height=350,margin=dict(t=15,b=30));st.plotly_chart(fig,use_container_width=True)
volts=np.linspace(0,15,100); recovered=[]
for v in volts:
 q=max(v-1.8,0)/resistance*duration*60
 recovered.append(100*min(mg_available_mol,q*efficiency/(2*F)*ph_factor)/mg_mol)
fig2=go.Figure(go.Scatter(x=volts,y=recovered,name='Mg recovery (scenario)'));fig2.add_vline(x=voltage,line_dash='dash');fig2.update_layout(xaxis_title='Applied cell voltage (V)',yaxis_title='Mg recovery (%)',height=320,margin=dict(t=15,b=30));st.plotly_chart(fig2,use_container_width=True)
st.download_button('⬇️ Download current mass balance CSV',df.to_csv(index=False).encode(),file_name='remat_v2_mass_balance.csv',mime='text/csv')
with st.expander('Scientific limitations and next calibration steps'):
 st.markdown('''**This is an exploratory model, not a validated digital twin.** The calcium and magnesium precipitation curves are assumed functions for demonstration; real brine chemistry depends on alkalinity, ionic strength, carbonate speciation, activity coefficients, salinity, temperature, competing ions, mixing and precipitation kinetics. A PHREEQC/Pitzer model is recommended for brine equilibrium. The cell current uses I = max(V − 1.8 V, 0)/R, a placeholder electrical model. Electrolysis results require experimentally measured polarization curves, Faradaic efficiency, electrode area, cathode pH and mass-transfer effects. **Do not use these outputs as measured recovery or purity.**''')
