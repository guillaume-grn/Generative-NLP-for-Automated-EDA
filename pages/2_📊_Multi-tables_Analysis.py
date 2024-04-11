import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re
import utils as ut
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
        ut.debug_and_display_multi(py_sections,db_name)

    
    if launch_button:
        #clear the page
        st.session_state['py_sections_multi'] = None

        visualizer = MultiTableVisualizer()
        
        with st.spinner("Generating database visualizations..."):
            table_schema = str(ut.extract_table_attributes(db_name))
            joins_info = str(ut.extract_joins(db_name))
        
            #claude_ideas = visualizer.execute_prompt_suggest_ideas('claude', table_schema, joins_info)
            gpt_ideas = visualizer.execute_prompt_suggest_ideas('gpt', table_schema, joins_info)
            mistral_ideas = visualizer.execute_prompt_suggest_ideas('mistral', table_schema, joins_info)
            #visualizations_ideas = gpt_ideas + '\n' + '\n'+ claude_ideas + '\n' + '\n'+ mistral_ideas
            visualizations_ideas = gpt_ideas + '\n' + '\n'+  mistral_ideas
            
            filtered_ideas = visualizer.execute_prompt_filter('gpt', visualizations_ideas)
            evaluated_ideas = visualizer.execute_prompt_evaluate('gpt', filtered_ideas)
            
            sql_queries = visualizer.execute_prompt_sql('gpt', evaluated_ideas, table_schema)
        
            #sql_queries est une longue str, on veut la couper autour des queries sql en utilisant re en splittant autour de '''sql
            queries_with_header = re.findall(r'(\d+\..*?```sql.*?```)', sql_queries, re.DOTALL)
            # py_sections = visualizer.execute_prompt_code('gpt', db_name, sql_queries)
        py_sections = ""
        for i,query_with_header in enumerate(queries_with_header,start=1): 
            with st.spinner(f"Generating code for visualisation {i}..."):           
                py_sections += visualizer.execute_prompt_code('gpt', db_name, query_with_header.strip())
        st.session_state['py_sections_multi'] = py_sections

        ut.debug_and_display_multi(py_sections,db_name)

    user_question = st.text_input("If you have a question, enter it below:")
    
    # Bouton "Submit" pour soumettre la question
    if st.button("Submit your question"):
        # Si une question a été saisie, ...
        if user_question:
 
            # ... on crée un agent Python pour traiter la question
            general_agent = GeneralAgent(db_name)
            
            # On exécute le code de l'agent Python
            agent_response = general_agent.answer_user(user_question)

            ut.debug_and_display_general_agent(agent_response,db_name)   
    
else : 
    st.write("Move first to the Home page to download your database")
