from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from env import OPEN_AI_KEY
from utils import *



class TableVisualizer:
    def __init__(self, model="gpt-4"):
        self.model = ChatOpenAI(model=model, api_key=OPEN_AI_KEY)
        self.output_parser = StrOutputParser()

        self.template1 = "You are a data scientist expert. Provided with a SQL database table schema, your task is to explain the table to a human, inferring the use of different attributes, primary and secondary keys.\n" \
                         "Start with a brief introduction to the table, outlining its purpose and context. Then, delve into the details.\n\n" \
                         "The schema for the {table_name} table in the {db_name} database is as follows: {table_schema}"

        self.template2 = "You are a data scientist expert. Provided with a SQL table description, your goal is to create insightful visualizations to better understand the provided dataset. \n" \
                          "Avoid suggesting ideas that would lead to cluttered charts due to an overwhelming number of categories. \n" \
                          "Give accurate description of the visualizations for future implementation using python, and also give the attributes to use for data retrieval. \n" \
                          "Take into account the type of the attributes, and focus on relevant visualizations as a data scientist working for the company that provided the database. \n" \
                          "Give a score out of 10 for the relevance of each visualization according to you. \n" \
                          "The description for the table is: {table_description}"

        self.template3 = """You are a data scientist expert tasked with visualizing data from the {table_name} table 
        in the {db_name} database. \n\n
        You have been provided with ideas for visualizations and their relative relevance scores out of 10. \n\n
        Your role is to write Python code including SQL queries to retrieve data necessary for these visualizations, 
        and to create the visualizations themselves, focusing on ideas with scores of 7 or above. \n\n
        Your response must contain for each visualization: \n
        1. A paragraph explaining the motivation for the visualization and how to interpret it. \n
        2. Python code for generating the visualization, queries included (with conn.close() and without the plt.show() line).\n\n
        Format instructions : paragraph for visualization 1 | code for visualization 1 | paragraph for visualization 2 | ... \n\n
        The ideas provided for the {table_name} table in the {db_name} database are: {ideas}\n
        """


    def execute_prompt1(self, db_name, table_name, table_schema):
        prompt = ChatPromptTemplate.from_template(self.template1)
        chain = prompt | self.model | self.output_parser
        return chain.invoke({"db_name": db_name, "table_name": table_name, "table_schema": table_schema})

    def execute_prompt2(self, table_description):
        prompt = ChatPromptTemplate.from_template(self.template2)
        chain = prompt | self.model | self.output_parser
        return chain.invoke({"table_description": table_description})

    def execute_prompt3(self, db_name, table_name, visualizations_ideas):
        prompt = ChatPromptTemplate.from_template(self.template3)
        chain = prompt | self.model | self.output_parser
        py_codes=chain.invoke({"db_name": db_name, "table_name": table_name, "ideas": visualizations_ideas})
        return py_codes

class MultiTableVisualizer:
    def __init__(self, model="gpt-4"):
        self.model = ChatOpenAI(model=model, api_key=OPEN_AI_KEY)
        self.output_parser = StrOutputParser()

        self.template1 = """ You are a data scientist expert working on a database. Provided the SQL database schema, and the list of possible joins, your role is to propose several visualization ideas requiring joins. 
        Do not suggest ideas that would lead to overloaded charts due to an overwhelming number of categories. For instance, avoid pie charts with too many categories, or line plots with too many lines, replace lots of bars by histogram. 
        Try to choose the best type of chart for each idea. 
        You can also propose to limit the number of categories for a better visualization (For instance suggest Top 10 or grouped by larger category).  
        Give also a score out of 10 for each visualization (score assessing the idea relevance as data scientist and ease of readability of the chart).
        - The schema for the database is as follows: {tables_and_attributes}
        - Here is relevant info for possible joins : {parent_child_joins}"""

        self.template2 = """You are a data scientist expert working on a database. Provided with visualisation ideas, your role is to write sql queries to retrieve data required for each visualization. 
        Do that only for those with score 7 and above. If the exact idea is not doable with the database tables and attributes, ignore it. Make sure to use all the tables suggested so you don't change the intent of the visualization. 
        Repeat the complete visualization idea (the one WITH type of chart) in your response before each query.
        - Here is the list of ideas : {first_output}
        - Here are also the attributes for each table : {tables_and_attributes}
        """

        self.template3 = """You are a data scientist expert working on the database {db_name}. Provided with visualisation ideas and sql queries to retrieve useful data for each, 
        you need to write python code to plot them, using the queries.
        Make sure your code covers all the visualisation ideas.
        Your response must contain for each visualization: 
        1. A paragraph explaining the motivation for the visualization and how to interpret it. 
        2. Python code for generating the visualization, queries included (with conn.close() and without plt.show()). You can use seaborn if needed. 
        Please ensure that your code is executable without modification. If you're unsure about certain details and can only provide a template that requires variable changes, please skip that visualization.
        Format instructions : paragraph for visualization 1 | code for visualization 1 | paragraph for visualization 2 | etc...   
        
        - Here are the ideas with sql queries: {second_output}
        """


    def execute_prompt1(self, tables_and_attributes, parent_child_joins):
        prompt = ChatPromptTemplate.from_template(self.template1)
        chain = prompt | self.model | self.output_parser
        return chain.invoke({"tables_and_attributes": tables_and_attributes, "parent_child_joins": parent_child_joins})

    def execute_prompt2(self, first_output,tables_and_attributes):
        prompt = ChatPromptTemplate.from_template(self.template2)
        chain = prompt | self.model | self.output_parser
        return chain.invoke({"first_output":first_output,"tables_and_attributes": tables_and_attributes})

    def execute_prompt3(self, db_name, second_output):
        prompt = ChatPromptTemplate.from_template(self.template3)
        chain = prompt | self.model | self.output_parser
        py_codes=chain.invoke({"db_name": db_name, "second_output": second_output})
        print(py_codes)
        return py_codes
    
class DatabaseSummary:
    def __init__(self, model="gpt-4"):
        self.model = ChatOpenAI(model=model, api_key=OPEN_AI_KEY)
        self.output_parser = StrOutputParser()

        self.template = """You are tasked with generating descriptions of a database's content in two parts. The first part involves providing a brief overview of the entire database, while the second part requires descriptions of each table individually based solely on the provided schema. Please ensure that your responses adhere to this structure. Use markdown to fromat your response.

        Part 1: Brief Overview of Database Content
    

You have access to the schema of our database named {db_name}. Please generate a concise summary of the contents of our database. The database encompasses various tables, each housing distinct types of data. The summary should provide an overarching understanding of the data stored within the database, touching upon key themes or categories.

Part 2: Table-by-Table Description

Based solely on the provided schema, we'd like you to describe the contents of each table individually. The schema includes the names of all tables along with their respective attributes and data types. For each table, please generate a description outlining its purpose, the types of data it contains, and any notable relationships or patterns within the data.
                        Here is the schema for the database: {table_schema}"""

    def execute_prompt(self, db_name, table_schema):
        prompt = ChatPromptTemplate.from_template(self.template)
        chain = prompt | self.model | self.output_parser
        return chain.invoke({"db_name": db_name, "table_schema": table_schema})
   






