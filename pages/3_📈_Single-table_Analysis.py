import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re
from utils import *
from llm_chains import *
from pythonREPL import *

st.set_page_config(
    page_title="EDA",
    page_icon="📊",
)

st.markdown("# Single-table Analysis")

if 'uploaded_file' in st.session_state :
    db_name=st.session_state['uploaded_file'].name
    st.write("You uploaded:", db_name)

    tables_names=load_tables_names(db_name)
    table_name = st.selectbox("Select a table", tables_names,index=None)
    if 'table_name' not in st.session_state :
        st.session_state['table_name'] = table_name
    
    if 'py_sections_single' in st.session_state :
        if table_name!=None :
            st.session_state['table_name']=table_name
        else :
            table_name=st.session_state['table_name']
            visualizations_seq = st.session_state['py_sections_single'] 
            table_description= st.session_state['table_description']
            st.write(f"### Table Summary for {table_name}:")
            st.write(table_description)
            debug_and_display_single(visualizations_seq,db_name,table_name)
            table_name=None
        
    if table_name!=None:           

        visualizer = TableVisualizer()
            
        with st.spinner("Generating table summary..."):
            table_schema = extract_table_schema(db_name, table_name)
            table_description = visualizer.execute_prompt1(db_name, table_name, table_schema)
        st.session_state['table_description'] = table_description
        st.write(f"### Table Summary for {table_name}:")
        st.write(table_description)
    
        

        with st.spinner("Generating table visualizations..."):
            visualizations_ideas = visualizer.execute_prompt2(table_description)
        
            visualizations_seq=visualizer.execute_prompt3(db_name,table_name,visualizations_ideas)

        
        st.session_state['py_sections_single'] = visualizations_seq

        debug_and_display_single(visualizations_seq,db_name,table_name)

    
else : 
    st.write("Move first to the Home page to download your database")
