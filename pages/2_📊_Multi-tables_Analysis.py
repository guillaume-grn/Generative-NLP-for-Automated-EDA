import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re
from utils import *
from llm_chains import *
from llm_agents import *

st.set_page_config(
    page_title="EDA",
    page_icon="📊",
)

st.markdown("# Multi-tables Analysis")

if 'uploaded_file' in st.session_state :
    db_name=st.session_state['uploaded_file'].name

    st.write("You uploaded:", db_name)

    # Add a button "Run Analysis"
    launch_button = st.button("Run Analysis")

    if 'py_sections_multi' in st.session_state and launch_button==False:
        py_sections = st.session_state['py_sections_multi'] 
        debug_and_display_multi(py_sections,db_name)

    
    if launch_button:
        #clear the page
        st.session_state['py_sections_multi'] = None

        visualizer = MultiTableVisualizer()
        
        with st.spinner("Generating database visualizations..."):
            table_schema = str(extract_table_attributes(db_name))
            joins_info = str(extract_joins(db_name))
            

            visualizations_ideas = visualizer.execute_prompt1(table_schema,joins_info)
            sql_queries = visualizer.execute_prompt2(visualizations_ideas,table_schema)
            
            py_sections = visualizer.execute_prompt3(db_name,sql_queries)

            st.session_state['py_sections_multi'] = py_sections

            debug_and_display_multi(py_sections,db_name)

    user_question = st.text_input("If you have a question, enter it below:")
    
    # Bouton "Submit" pour soumettre la question
    if st.button("Submit your question"):
        # Si une question a été saisie, ...
        if user_question:
 
            # ... on crée un agent Python pour traiter la question
            general_agent = GeneralAgent(db_name)
            
            # On exécute le code de l'agent Python
            agent_response = general_agent.answer_user(user_question)

            debug_and_display_general_agent(agent_response,db_name)   
    
else : 
    st.write("Move first to the Home page to download your database")
