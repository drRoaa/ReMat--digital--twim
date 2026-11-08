import math
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='ReMat Virtual Laboratory V3',page_icon='🧪',layout='wide')
STAGES=['Pre-filtration','Calcium precipitation','Electrochemical cell','Product recovery']
for k,v in {'stage':0,'running':False,'progress':0}.items():
    if k not in st.session_state: st.session_state[k]=v
st.title('🧪 ReMat | Virtual Laboratory V3')
st.caption('5-L bench-scale visual experiment · interactive stage controls · exploratory scenario calculations, NOT validated laboratory predictions')
with st.sidebar:
    st.header('⚙️ Laboratory inputs')
    volume=st.slider('Batch volume (L)',1.0,5.0,5.0,0.5)
    ca=st.number_input('Feed Ca²⁺ (mg/L)',100.,5000.,800.,50.)
    mg=st.number_input('Feed Mg²⁺ (mg/L)',100.,5000.,1500.,50.)
    ph=st.slider('Precipitation pH',7.,12.,9.5,.1)
    soda=st.slider('Na₂CO₃ dose (g/L)',0.,5.,2.2,.1)
    st.header('⚡ Cell controls')
    volts=st.slider('Applied voltage (V)',0.,15.,5.,.5)
    resistance=st.slider('Assumed effective resistance (Ω)',1.,30.,4.,.5)
    hours=st.slider('Electrolysis duration (min)',5,180,60,5)
    faraday_eff=st.slider('Assumed Faradaic efficiency (%)',10,100,70,5)
    st.info('pH response is illustrative, not PHREEQC. Voltage-to-current uses an assumed circuit, not measured electrode behavior.')

# Illustrative precipitation response, explicitly not equilibrium chemistry.
ca_feed=ca*volume/1000
mg_feed=mg*volume/1000
ca_fraction=max(0,min(.98, .38+ .6/(1+math.exp(-2*(ph-10.25)))))
mg_loss_fraction=max(0,min(.5, .32/(1+math.exp(-2.4*(ph-10.5)))))
# Na2CO3 stoichiometry: 1 mol per mol Ca; dose limits calcium removal.
soda_moles=soda*volume/105.99
ca_removed=min(ca_feed*ca_fraction, soda_moles*40.078)
ca_remaining=ca_feed-ca_removed
mg_lost=mg_feed*mg_loss_fraction
mg_available=mg_feed-mg_lost
caco3=ca_removed*100.087/40.078
current=max(0,(volts-1.8)/resistance)
charge=current*hours*60
# 2 e- generate 2 OH-, enough for one Mg(OH)2 formula unit.
mg_recovered=min(mg_available,charge*faraday_eff/100/(2*96485.33212)*24.305)
mgoh2=mg_recovered*58.319/24.305
energy=volts*current*hours/60/1000
ca_pct=100*ca_removed/ca_feed if ca_feed else 0
mg_loss_pct=100*mg_lost/mg_feed if mg_feed else 0
mg_rec_pct=100*mg_recovered/mg_feed if mg_feed else 0

st.subheader('1. Run the laboratory sequence')
c1,c2,c3,c4=st.columns(4)
with c1:
    if st.button('▶ Start' if not st.session_state.running else '⏸ Pause',use_container_width=True): st.session_state.running=not st.session_state.running
with c2:
    if st.button('⏭ Next stage',use_container_width=True):
        st.session_state.stage=min(3,st.session_state.stage+1);st.session_state.progress=0
with c3:
    if st.button('⏮ Previous',use_container_width=True):
        st.session_state.stage=max(0,st.session_state.stage-1);st.session_state.progress=0
with c4:
    if st.button('↺ Reset',use_container_width=True):
        st.session_state.stage=0;st.session_state.running=False;st.session_state.progress=0
stage=st.session_state.stage
progress=st.slider('Stage progress (%) — scrub to inspect the experiment',0,100,key='progress',step=5)
st.write(f'**Active stage {stage+1}/4:** {STAGES[stage]} · **Visual playback:** {"Running" if st.session_state.running else "Paused"}')
# SVG shows physically recognizable equipment and piping, with animated liquid / precipitation / bubbles.
# Animation is illustrative only. No simulation clock or CFD solver.
active=stage
run='running' if st.session_state.running else 'paused'
fill=min(1,max(.06,progress/100))
svg=f'''<html><head><style>
body{{margin:0;background:#081b2d;color:#eef7ff;font-family:Arial,sans-serif}}
svg{{width:100%;height:auto;display:block}}
.particle{{animation:float 2.2s infinite alternate ease-in-out;animation-play-state:{run}}}
.flow{{stroke-dasharray:11 12;animation:dash 1.1s linear infinite;animation-play-state:{run}}}
.bubble{{animation:rise 2.4s infinite linear;animation-play-state:{run}}}
@keyframes dash{{to{{stroke-dashoffset:-46}}}}
@keyframes float{{to{{transform:translateY(13px)}}}}
@keyframes rise{{0%{{transform:translateY(28px);opacity:.1}}50%{{opacity:1}}100%{{transform:translateY(-35px);opacity:.1}}}}
</style></head><body><svg viewBox="0 0 1080 420" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#38d6e5"/><stop offset="1" stop-color="#086a9c"/></linearGradient><clipPath id="tank"><rect x="0" y="0" width="190" height="235" rx="17"/></clipPath></defs>
<text x="30" y="33" font-size="19" fill="#dff7ff">ReMat bench-scale train · schematic (not to scale)</text>
<path d="M216 167 H278 M486 167 H550 M758 167 H820" fill="none" stroke="#335b74" stroke-width="18"/>
<path d="M216 167 H278 M486 167 H550 M758 167 H820" fill="none" stroke="#42e5e2" stroke-width="7" class="flow"/>
<g fill="#153c54" stroke="#70cde3" stroke-width="4">
<rect x="20" y="90" width="196" height="242" rx="20"/><rect x="286" y="90" width="200" height="242" rx="20"/><rect x="558" y="90" width="200" height="242" rx="20"/><rect x="824" y="90" width="200" height="242" rx="20"/></g>
<g fill="url(#water)" opacity=".83"><path d="M25 185 H211 V311 Q211 327 193 327 H43 Q25 327 25 311Z"/><path d="M291 185 H481 V311 Q481 327 463 327 H309 Q291 327 291 311Z"/><path d="M563 185 H753 V311 Q753 327 735 327 H581 Q563 327 563 311Z"/><path d="M829 185 H1019 V311 Q1019 327 1001 327 H847 Q829 327 829 311Z"/></g>
<g fill="#f3f9ff" font-size="15" text-anchor="middle"><text x="118" y="70">1. 5 µm filter</text><text x="386" y="70">2. CaCO₃ precipitation</text><text x="658" y="70">3. Electrochemical cell</text><text x="924" y="70">4. Product collection</text></g>
<g stroke="#f2fbff" stroke-width="7"><path d="M88 125V288 M108 125V288 M128 125V288 M148 125V288"/></g>
<path d="M386 89 V140" stroke="#e9bc53" stroke-width="9"/><path d="M366 98 H406" stroke="#e9bc53" stroke-width="5"/><text x="395" y="116" fill="#fff1b9" font-size="11">dose</text>
<g stroke-width="11"><path d="M632 124 V279" stroke="#ff9f59"/><path d="M692 124 V279" stroke="#b6e8fa"/></g>
<g fill="#c7e5f5" font-size="14"><text x="621" y="115">+</text><text x="690" y="115">−</text></g>
<g fill="#e7e0a2"><circle cx="904" cy="284" r="9"/><circle cx="935" cy="292" r="7"/><circle cx="959" cy="274" r="10"/></g>
<g opacity="{1 if stage>=1 else .08}"><circle class="particle" cx="349" cy="258" r="7" fill="#efe8be"/><circle class="particle" cx="392" cy="290" r="9" fill="#efe8be"/><circle class="particle" cx="432" cy="270" r="6" fill="#efe8be"/></g>
<g opacity="{1 if stage>=2 else .08}"><circle class="bubble" cx="689" cy="247" r="6" fill="#dbf8ff"/><circle class="bubble" cx="700" cy="222" r="4" fill="#dbf8ff"/><circle class="bubble" cx="679" cy="260" r="5" fill="#dbf8ff"/></g>
<g fill="#8dd7e9" font-size="13" text-anchor="middle"><text x="118" y="359">Pre-filter</text><text x="386" y="359">Soda ash + stirring</text><text x="658" y="359">{volts:.1f} V · {current:.2f} A</text><text x="924" y="359">Mg(OH)₂ separation</text></g>
<rect x="22" y="384" width="1032" height="9" rx="4" fill="#315067"/><rect x="22" y="384" width="{(stage+fill)*1032/4:.1f}" height="9" rx="4" fill="#56e0bf"/>
</svg></body></html>'''
components.html(svg,height=385,scrolling=False)
st.caption('Visual animations play only when Start is selected. Next stage changes the active step; the progress slider is a visual scrubber, not elapsed real time.')

st.subheader('2. Scenario outputs at selected settings')
a,b,c,d=st.columns(4)
a.metric('Ca removal (illustrative)',f'{ca_pct:.1f}%')
b.metric('Mg lost in Ca stage (illustrative)',f'{mg_loss_pct:.1f}%')
c.metric('Mg recovered (Faraday-limited)',f'{mg_rec_pct:.1f}%')
d.metric('Electrical energy (estimated)',f'{energy:.4f} kWh')
rows=[('Ca²⁺ in feed',ca_feed),('Ca²⁺ removed',ca_removed),('Ca²⁺ remaining',ca_remaining),('Mg²⁺ in feed',mg_feed),('Mg²⁺ lost in Ca stage',mg_lost),('Mg²⁺ recovered in cell',mg_recovered),('CaCO₃ solid (ideal mass)',caco3),('Mg(OH)₂ solid (ideal mass)',mgoh2)]
df=pd.DataFrame(rows,columns=['Quantity','Mass (g)'])
left,right=st.columns([1,1])
with left:
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button('⬇ Download scenario mass balance CSV',df.to_csv(index=False).encode('utf-8'),file_name='ReMat_V3_scenario.csv',mime='text/csv')
with right:
    st.write(f'**Cell:** {current:.2f} A · {charge:.0f} C · {energy:.4f} kWh')
    st.write(f'**Soda ash:** {soda*volume:.2f} g added · theoretical minimum for calculated Ca removal: {ca_removed/40.078*105.99:.2f} g')
    st.write('**Important:** pH response is an assumed screening curve. The cell model uses I = max(V − 1.8, 0) / R and Faraday’s law with assumed efficiency. It does not predict electrode selectivity, measured current, or product purity.')

st.subheader('3. Explore pH and voltage effects')
phs=[7+i*.1 for i in range(51)]
ca_curve=[]; mg_curve=[]
for x in phs:
    cf=max(0,min(.98,.38+.6/(1+math.exp(-2*(x-10.25)))))
    ml=max(0,min(.5,.32/(1+math.exp(-2.4*(x-10.5)))))
    ca_curve.append(100*min(ca_feed*cf,soda_moles*40.078)/ca_feed)
    mg_curve.append(100*ml)
fig=go.Figure()
fig.add_trace(go.Scatter(x=phs,y=ca_curve,name='Ca removal (scenario)'))
fig.add_trace(go.Scatter(x=phs,y=mg_curve,name='Mg loss (scenario)'))
fig.add_vline(x=ph,line_dash='dash')
fig.update_layout(xaxis_title='Precipitation pH',yaxis_title='Fraction (%)',height=340,margin=dict(l=10,r=10,t=10,b=10))
st.plotly_chart(fig,use_container_width=True)
vs=[i*.5 for i in range(31)]
rec=[100*min(mg_available,max(0,(v-1.8)/resistance)*hours*60*faraday_eff/100/(2*96485.33212)*24.305)/mg_feed for v in vs]
fig2=go.Figure(go.Scatter(x=vs,y=rec,name='Faraday-limited Mg recovery'))
fig2.add_vline(x=volts,line_dash='dash')
fig2.update_layout(xaxis_title='Applied cell voltage (V)',yaxis_title='Mg recovery (% of initial Mg)',height=340,margin=dict(l=10,r=10,t=10,b=10))
st.plotly_chart(fig2,use_container_width=True)
with st.expander('Scientific limitations — read before interpreting results',expanded=True):
    st.warning('This is a virtual lab demonstrator, not a calibrated chemical process model. The tanks, bubbles and solids are illustrative animations; they do not reproduce fluid dynamics, mixing, reaction kinetics or precipitation time. The pH curves are assumed and are not equilibrium calculations. The voltage-current relationship is assumed; real electrochemical performance depends on measured polarization, conductivity, electrode area, local cathode pH and competing reactions. No purity is predicted. Validate against experiments and PHREEQC/Pitzer calculations before using results in scientific claims.')
