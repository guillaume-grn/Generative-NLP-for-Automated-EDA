from env import OPEN_AI_KEY

from langchain import hub
from langchain.agents import AgentExecutor
from langchain_experimental.tools import PythonREPLTool
tools = [PythonREPLTool()]
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI
import sqlite3
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import Tool
from langchain_experimental.utilities import PythonREPL

import re

base_prompt = hub.pull("langchain-ai/openai-functions-template")

def remove_show(output):
    if re.search(r'plt.show\(\)', output):
        return re.sub(r'plt.show\(\)', '', output)
    return output

def format_agent_output(output):
    sections = output.split('```')
    for section in sections:
        if re.search(r'\bpython\b', section, re.IGNORECASE) and re.search(r'\(', section, re.IGNORECASE):
            replaced_section = re.sub(r'\bpython\b', '', section, flags=re.IGNORECASE)
            return remove_show(replaced_section)
        
class PythonAgent():
    def __init__(self, db_name):
        self.instructions = f"""You are an agent designed to fix python code.
        You have access to a python REPL, which you must use to execute python code.
        EXECUTE your code proposal to ensure it works properly.
        If conn is not defined, use conn = sqlite3.connect({db_name})
        Output the code you used to generate the visualization.
        """
        
        prompt = base_prompt.partial(instructions=self.instructions)
        agent = create_openai_functions_agent(ChatOpenAI(temperature=0, openai_api_key=OPEN_AI_KEY), tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    def debug_code(self, code):
        cvb=self.agent_executor.invoke({"input": code})["output"]
        return format_agent_output(cvb)
        
@tool
def extract_database_schema(db_name: str) -> list:
    """
    Extracts the schema of all tables in a SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database.

    Returns:
        list: A list containing the schemas of all tables in the database.
    """
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

@tool
def extract_table_schema(db_name: str, table_name: str) -> str:
    """
    Extracts the schema of a specific table in a SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database.
        table_name (str): The name of the table.

    Returns:
        str: The schema of the specified table.
    """
    # Connexion à la base de données SQLite
    connexion = sqlite3.connect(db_name)

    # Obtention de l'objet curseur
    curseur = connexion.cursor()

    # Exécution d'une requête pour obtenir le schéma de la table
    curseur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")

    # Récupération du résultat
    resultat = curseur.fetchone()

    # Création d'une chaîne pour stocker le schéma de la table
    sql_table_schema = resultat[0] if resultat else ""

    # Fermeture de la connexion à la base de données
    connexion.close()

    return sql_table_schema

@tool
def load_tables_names(db_name: str) -> list:
    """
    Loads the names of all tables in a SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database.

    Returns:
        list: A list containing the names of all tables in the database.
    """
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

@tool
def extract_table_attributes(db_name: str) -> dict:
    """
    Extracts the attributes of all tables in a SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database.

    Returns:
        dict: A dictionary containing the tables and their attributes.
    """
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Dictionnaire pour stocker les tables et leurs attributs
    tables_attributes = {}

    X = load_tables_names(db_name)

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

@tool
def extract_joins(db_name: str) -> list:
    """
    Extracts possible joins between tables in a SQLite database based on foreign keys.

    Parameters:
        db_name (str): The name of the SQLite database.

    Returns:
        list: A list containing possible join information between tables.
    """
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


    
class GeneralAgent():
    def __init__(self, db_name):
        self.prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are a datascientist working on the database {db_name}. If you were asked to generate a visualization, do it and then output the code you used to do it.",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        )
        python_repl = PythonREPL()
        repl_tool = Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Can be useful to plot visualisations. It has access to several libraries such as matplotlib. Input should be a valid python command. ",
        func=python_repl.run,
        )
        tools = [repl_tool,extract_joins,extract_table_attributes,load_tables_names,extract_table_schema,extract_database_schema]
        llm = ChatOpenAI(model="gpt-4",api_key=OPEN_AI_KEY)
        llm_with_tools = llm.bind_tools(tools)
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | self.prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )

        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    def answer_user(self, demand):
        cvb=self.agent_executor.invoke({"input": demand})['output']
        print(cvb)
        return cvb
        #return format_agent_output(cvb)


class PythonAgent2():
    def __init__(self, db_name):
        self.instructions = f"""You are an agent designed to fix python code, or to write python code using a sql query provided.
        You have access to a python REPL, which you must use to execute python code.
        EXECUTE your code proposal to ensure it works properly.
        If conn is not defined, use conn = sqlite3.connect({db_name})
        Output the code you used to generate the visualization.
        """
        
        prompt = base_prompt.partial(instructions=self.instructions)
        agent = create_openai_functions_agent(ChatOpenAI(temperature=0, openai_api_key=OPEN_AI_KEY), tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    def debug_code(self, code):
        cvb=self.agent_executor.invoke({"input": code})["output"]
        return format_agent_output(cvb)




