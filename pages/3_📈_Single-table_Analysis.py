import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re
from utils import *
from llm_chains import *
#from llm_agents import *

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
    if 'single_page_memory' not in st.session_state:
        st.session_state['single_page_memory'] = {}

    if table_name not in st.session_state['single_page_memory']:  
        st.session_state['single_page_memory'][table_name] = {}
        
    if table_name!=None:
        
        if 'table_description' in st.session_state['single_page_memory'][table_name] :
            visualizations_seq = st.session_state['single_page_memory'][table_name]['py_sections_single'] 
            table_description= st.session_state['single_page_memory'][table_name]['table_description']
            st.write(f"### Table Summary for {table_name}:")
            st.write(table_description)
            debug_and_display_single(visualizations_seq,db_name,table_name)
            if st.button(f"Relaunch a new analysis on the table {table_name}"):
                st.session_state['single_page_memory'][table_name] = {}
            

        else :
            visualizer = TableVisualizer()
                
            with st.spinner("Generating table summary..."):
                table_schema = extract_table_schema(db_name, table_name)
                table_description = visualizer.execute_prompt1(db_name, table_name, table_schema)
            st.session_state['single_page_memory'][table_name]['table_description'] = table_description
            st.write(f"### Table Summary for {table_name}:")
            st.write(table_description)
        
            

            with st.spinner("Generating table visualizations..."):
                visualizations_ideas = visualizer.execute_prompt2(table_description)
            
                visualizations_seq=visualizer.execute_prompt3(db_name,table_name,visualizations_ideas)

            
            st.session_state['single_page_memory'][table_name]['py_sections_single'] = visualizations_seq

            debug_and_display_single(visualizations_seq,db_name,table_name)
            
    
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