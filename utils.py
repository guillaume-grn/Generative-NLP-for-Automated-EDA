import sqlite3
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re
from utils import *
from llm_chains import *
from llm_agents import *

def extract_table_schema(db_name,table_name):
  # Connexion à la base de données SQLite
  connexion = sqlite3.connect(db_name)

  # Obtention de l'objet curseur
  curseur = connexion.cursor()

  # Exécution d'une requête pour obtenir le schéma de la table
  curseur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")

  # Récupération du résultat
  resultat = curseur.fetchone()

  # Création d'une chaîne pour stocker le schéma de la table "Playlist"
  sql_table_schema = resultat[0] if resultat else ""

  # Fermeture de la connexion à la base de données
  connexion.close()

  return sql_table_schema

def load_tables_names(db_name):
    # Connexion à la base de données SQLite
    connexion = sqlite3.connect(db_name)

    # Obtention de l'objet curseur
    curseur = connexion.cursor()

    # Exécution d'une requête pour obtenir les noms des tables
    curseur.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Récupération des noms des tables
    tables_names = [row[0] for row in curseur.fetchall()]

    # Fermeture de la connexion à la base de données
    connexion.close()

    return tables_names

def extract_table_attributes(db_name):
  # Connexion à la base de données SQLite
  conn = sqlite3.connect(db_name)
  cursor = conn.cursor()

  # Dictionnaire pour stocker les tables et leurs attributs
  tables_attributes = {}

  X=load_tables_names(db_name)

  # Parcourir chaque table et extraire les attributs
  for table_name in X:

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    # Extraire les noms des colonnes de chaque table
    columns = [col_info[1] for col_info in columns_info]
    # Stocker les noms des colonnes dans le dictionnaire
    tables_attributes[table_name] = columns
  # Fermer la connexion à la base de données
  conn.close()

  return tables_attributes

def extract_joins(db_name):
  # List to store possible joins
  possible_joins = []
  tables = load_tables_names(db_name)

  # Connect to the SQLite database
  conn = sqlite3.connect(db_name)
  cursor = conn.cursor()

  # Traverse the tables to obtain foreign keys
  for table_name in tables:
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    foreign_keys = cursor.fetchall()

    # Traverse the foreign keys
    for foreign_key in foreign_keys:
      table_parent = foreign_key[2]  # Name of the parent table
      foreign_key_column_parent = foreign_key[3]  # Column of the parent table
      foreign_key_column_child = foreign_key[4]  # Column of the child table

      # Add join information to the list of possible joins
      possible_join = {
          'table_parent': table_parent,
          'table_child': table_name,
          'foreign_key_column_parent': foreign_key_column_parent,
          'foreign_key_column_child': foreign_key_column_child
      }
      possible_joins.append(possible_join)

  conn.close()
  return possible_joins

def debug_and_display_multi(py_code_sections,db_name):
  python_agent=PythonAgent(db_name)

  sections = py_code_sections.split('```')

  st.write(f"### Visualizations for {db_name}:")

  # Display sections
  for i in range(len(sections)-1):
      st.divider()
                  
      if re.search(r'\bpython\b', sections[i], re.IGNORECASE) and re.search(r'\(', sections[i], re.IGNORECASE):
          replaced_section = re.sub(r'\bpython\b', '', sections[i], flags=re.IGNORECASE)
          
          # Execute section code to create visualization
          try:
              exec(replaced_section, globals(), locals())
              st.code(replaced_section)
              st.pyplot(plt.gcf())
              plt.figure()
              
          except Exception as e:
              try:
                  st.write("After fix:")
                  
                  replaced_section2=python_agent.debug_code(replaced_section)
                            
                  st.code(replaced_section2)
                  exec(replaced_section2, globals(), locals())
                  st.pyplot(plt.gcf())
                  plt.figure()
              except Exception as e:
                  print("échec pour la visualisation ",i)
                  st.error(f"An error occurred: {e}")            
      else :
          st.write(sections[i])
def debug_and_display_single(py_code_sections,db_name,table_name):
  sections = py_code_sections.split('```')
  python_agent=PythonAgent(db_name)
  st.write(f"### Table Visualizations for {table_name}:")

  # Display sections
  for i in range(len(sections)-1):
      st.divider()
                      
      if re.search(r'\bpython\b', sections[i], re.IGNORECASE) and re.search(r'\(', sections[i], re.IGNORECASE):
          replaced_section = re.sub(r'\bpython\b', '', sections[i], flags=re.IGNORECASE)
          
          # Execute section code to create visualization
          try:
              exec(replaced_section, globals(), locals())
              st.code(replaced_section)
              st.pyplot(plt.gcf())
              plt.figure()
          except Exception as e:
              try:
                  st.write("After fix:")
                  replaced_section=python_agent.debug_code(replaced_section)
                  st.code(replaced_section)
                  exec(replaced_section, globals(), locals())
                  
                  st.pyplot(plt.gcf())
              except Exception as e:
                  print("échec pour la visualisation ",i)
                  st.error(f"An error occurred: {e}")            
      else :
          st.write(sections[i])

def extract_database_schema(db_name):
    # Connexion à la base de données SQLite
    connexion = sqlite3.connect(db_name)

    # Obtention de l'objet curseur
    curseur = connexion.cursor()

    # Exécution d'une requête pour obtenir les schémas de toutes les tables
    curseur.execute("SELECT sql FROM sqlite_master WHERE type='table';")

    # Récupération des résultats
    resultats = curseur.fetchall()

    # Création d'une liste pour stocker les schémas de toutes les tables
    table_schemas = [result[0] for result in resultats]

    # Fermeture de la connexion à la base de données
    connexion.close()

    return table_schemas

def debug_and_display_general_agent(agent_response,db_name):
  python_agent=PythonAgent2(db_name)

  sections = agent_response.split('```')

  # Display sections
  for i in range(len(sections)):
                        
      if re.search(r'\bpython\b', sections[i], re.IGNORECASE) and re.search(r'\(', sections[i], re.IGNORECASE):
          replaced_section = re.sub(r'\bpython\b', '', sections[i], flags=re.IGNORECASE)
          
          # Execute section code to create visualization
          try:
              exec(replaced_section, globals(), locals())
              st.code(replaced_section)
              st.pyplot(plt.gcf())
              plt.figure()
              
          except Exception as e:
              try:
                  st.write("After fix:")
                  
                  replaced_section2=python_agent.debug_code(replaced_section)
                            
                  st.code(replaced_section2)
                  exec(replaced_section2, globals(), locals())
                  st.pyplot(plt.gcf())
                  plt.figure()
              except Exception as e:
                  print("échec pour la visualisation ",i)
                  st.error(f"An error occurred: {e}")            
      else :
          st.write(sections[i])
