from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
p=Path(__file__).resolve().parent/'site'
st.set_page_config(page_title='Visualization gallery',layout='wide')
st.title('Local Streamlit companion')
if not (p/'reports.json').exists():
    st.error('Run python build.py first. See README.');st.stop()
df=pd.DataFrame(json.loads((p/'reports.json').read_text()))
st.caption('All data are synthetic.')
st.plotly_chart(px.scatter(df,x='age_hours',y='estimate',color='source',hover_data=['report','verification']),use_container_width=True)
for name in ['uncertainty.png','missingness.png']:
    if (p/name).exists():st.image(str(p/name))
selected=st.selectbox('Inspect report',df.report)
st.dataframe(df[df.report==selected])
st.caption('The complete D3 and Cytoscape gallery is available on the static page. Serve site/ locally as described in README.')
