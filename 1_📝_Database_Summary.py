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

st.markdown("# Database Summary")

if 'uploaded_file' in st.session_state :
    db_name=st.session_state['uploaded_file'].name

    st.write("You uploaded:", db_name)

    launch_button = st.button("Run Analysis")

    if 'database_summary' in st.session_state and launch_button==False:
        database_summary = st.session_state['database_summary'] 
        st.write(database_summary)
    
    if launch_button:
        #clear the page
        st.session_state['database_summary'] = None
        with st.spinner("Generating database summary..."):
            db_schema=str(extract_database_schema(db_name))
            database_summary = DatabaseSummary().execute_prompt(db_name, db_schema)
        st.write(database_summary)
        st.session_state['database_summary'] = database_summary

else : 
    st.write("Move first to the Home page to download your database")
