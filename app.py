import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title='ReMat Digital Twin V1', page_icon='💧', layout='wide')
st.title('💧 ReMat | Digital Twin V1')
st.caption('Interactive conceptual prototype • Mass balance + illustrative process assumptions • Not validated experimental predictions')

with st.sidebar:
    st.header('Feed & operating conditions')
    volume = st.slider('Batch volume (L)', 1., 100., 5., 1.)
    mg = st.slider('Mg²⁺ concentration (mg/L)', 100, 4000, 1500, 50)
    ca = st.slider('Ca²⁺ concentration (mg/L)', 50, 2500, 800, 50)
    ph = st.slider('Precipitation stage pH (illustrative)', 7.0, 12.0, 9.5, 0.1)
    soda = st.slider('Na₂CO₃ dose (g/L)', 0., 6., 2.2, 0.1)
    st.divider()
    st.subheader('Assumed efficiencies (adjustable)')
    ca_eff = st.slider('Ca precipitation efficiency (%)', 0, 100, 95)
    mg_recovery = st.slider('Mg recovery efficiency (%)', 0, 100, 60)
    conversion = st.slider('Recovered Mg → Mg(OH)₂ conversion (%)', 0, 100, 90)
    product_purity = st.slider('Assumed product purity (%)', 50, 100, 95)
    st.info('Efficiencies are scenario inputs, NOT predictions from pH or dose. For chemical speciation and precipitation equilibria, integrate PHREEQC after experimental calibration.')

M_CA, M_MG, M_NA2CO3, M_CACO3, M_MGOH2 = 40.078, 24.305, 105.99, 100.0869, 58.3197
ca_feed_g = ca * volume / 1000
mg_feed_g = mg * volume / 1000
ca_removed_g = ca_feed_g * ca_eff/100
mg_recovered_g = mg_feed_g * mg_recovery/100
mg_converted_g = mg_recovered_g * conversion/100
caco3_g = ca_removed_g * M_CACO3/M_CA
mgoh2_pure_g = mg_converted_g * M_MGOH2/M_MG
mgoh2_product_g = mgoh2_pure_g / (product_purity/100)
soda_stoich_g = ca_removed_g * M_NA2CO3/M_CA
soda_dosed_g = soda * volume
soda_shortfall = max(0., soda_stoich_g-soda_dosed_g)

st.warning('Scientific guardrail: soda-ash dose is checked against Ca removal stoichiometry; efficiency sliders are not calculated from dose or pH. If dose is insufficient, the selected Ca-removal scenario is infeasible.')
if soda_shortfall > 1e-9:
    st.error(f'⚠️ Insufficient Na₂CO₃ for the selected Ca removal: minimum {soda_stoich_g:.2f} g, supplied {soda_dosed_g:.2f} g (shortfall {soda_shortfall:.2f} g). Reduce assumed Ca removal or increase dose.')
else:
    st.success(f'✓ Soda ash dose meets the theoretical minimum for selected Ca removal ({soda_stoich_g:.2f} g). This does not guarantee actual precipitation.')

st.subheader('Animated process overview')
st.markdown('''<style>
@keyframes flow {from {background-position:0 0} to {background-position:80px 0}}
@keyframes bubble {0%{transform:translateY(0);opacity:.25}50%{opacity:1}100%{transform:translateY(-35px);opacity:0}}
.process {display:flex;align-items:center;gap:6px;justify-content:space-between;flex-wrap:wrap;padding:14px;background:#0b1830;border-radius:18px;color:white}
.unit {position:relative;min-width:145px;flex:1;text-align:center;border:2px solid #4a8eaf;border-radius:14px;padding:16px 8px;background:linear-gradient(to top,rgba(32,173,207,.55) 0 38%,#172c47 38% 100%);height:155px;overflow:hidden}
.unit strong{display:block;font-size:15px}.unit small{display:block;color:#d2e6f3;margin-top:12px}
.pipe{height:8px;min-width:20px;flex:.15;background:repeating-linear-gradient(90deg,#20d6c7 0 14px,#155a8e 14px 26px);animation:flow 1s linear infinite;border-radius:5px}
.bubble{position:absolute;bottom:15px;left:50%;width:10px;height:10px;background:#8df6ef;border-radius:50%;animation:bubble 2s infinite}
</style><div class="process">
<div class="unit"><strong>① Pre-filtration</strong><small>5 µm filter</small><div class="bubble"></div></div><div class="pipe"></div>
<div class="unit"><strong>② Ca precipitation</strong><small>Na₂CO₃ → CaCO₃ ↓</small><div class="bubble"></div></div><div class="pipe"></div>
<div class="unit"><strong>③ Electrochemical cell</strong><small>Mg²⁺ → Mg(OH)₂ ↓</small><div class="bubble"></div></div><div class="pipe"></div>
<div class="unit"><strong>④ Product recovery</strong><small>Solid-liquid separation</small><div class="bubble"></div></div></div>''', unsafe_allow_html=True)

cols = st.columns(4)
for c, label, val in zip(cols, ['Ca removal (assumed)','Mg recovery (assumed)','Pure Mg(OH)₂ (calculated)','CaCO₃ (calculated)'], [f'{ca_eff}%',f'{mg_recovery}%',f'{mgoh2_pure_g:.2f} g',f'{caco3_g:.2f} g']):
    c.metric(label,val)

left,right=st.columns(2)
with left:
    st.subheader('Material balance')
    st.dataframe({'Metric':['Feed Ca²⁺','Ca removed','Ca remaining','Feed Mg²⁺','Mg recovered','Mg converted','Pure Mg(OH)₂','Total product at assumed purity','Theoretical minimum Na₂CO₃','Na₂CO₃ added'], 'Mass (g)':[ca_feed_g,ca_removed_g,ca_feed_g-ca_removed_g,mg_feed_g,mg_recovered_g,mg_converted_g,mgoh2_pure_g,mgoh2_product_g,soda_stoich_g,soda_dosed_g]},hide_index=True,use_container_width=True)
with right:
    st.subheader('Ion mass flow')
    fig=go.Figure()
    fig.add_trace(go.Bar(name='Feed',x=['Ca²⁺','Mg²⁺'],y=[ca_feed_g,mg_feed_g]))
    fig.add_trace(go.Bar(name='Removed / recovered',x=['Ca²⁺','Mg²⁺'],y=[ca_removed_g,mg_recovered_g]))
    fig.update_layout(barmode='group',yaxis_title='Element mass (g)',height=350,margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig,use_container_width=True)

st.subheader('Sensitivity: magnesium product vs recovery')
rates=np.arange(0,101,5)
products=mg_feed_g*rates/100*conversion/100*M_MGOH2/M_MG
fig2=go.Figure(go.Scatter(x=rates,y=products,mode='lines+markers'))
fig2.update_layout(xaxis_title='Assumed Mg recovery (%)',yaxis_title='Pure Mg(OH)₂ (g)',height=300,margin=dict(l=10,r=10,t=20,b=10))
st.plotly_chart(fig2,use_container_width=True)

st.markdown('''**Model limitations:** No ion activity, ionic strength, Ca/Mg competing precipitation, carbonate speciation, electrode kinetics, current efficiency, Faradaic energy, crystallizer yield, or residence-time model is included. The pH control is displayed but does not drive the numerical predictions in V1. The 90% conversion is applied to recovered magnesium, not to all magnesium in the feed. Purity is an assumed input; no impurities are calculated. CaCO₃ mass assumes ideal carbonate precipitation. Actual brine experiments and PHREEQC modeling are required for validation.''')
