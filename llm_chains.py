from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
from utils import *
import os
import boto3
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.chat_models import BedrockChat
from langchain_mistralai.chat_models import ChatMistralAI

class TableVisualizer:
    def __init__(self):
        # self.model_mistral = ChatMistralAI(mistral_api_key=MISTRAL_API_KEY)
        self.model_gpt = ChatOpenAI(model="gpt-4", api_key=os.environ.get('OPEN_AI_KEY'))
        # bedrock_runtime = boto3.client(
        #     service_name="bedrock-runtime",
        #     region_name='us-west-2',
        #     aws_access_key_id=AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        # )

        # model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        # model_kwargs =  {
        #     "max_tokens": 5000,
        #     "temperature": 0.01,
        #     "top_k": 250,
        #     "top_p": 0.99,
        #     "stop_sequences": ["\n\nHuman"],
        # }

        # self.model_claude = BedrockChat(
        #     client=bedrock_runtime,
        #     model_id=model_id,
        #     model_kwargs=model_kwargs,
        # )
        self.output_parser = StrOutputParser()

        self.template1 = "You are a data scientist expert. Provided with a SQL database table schema, your task is to explain the table to a human, inferring the use of different attributes, primary and secondary keys.\n" \
                         "Start with a brief introduction to the table, outlining its purpose and context. Then, delve into the details.\n\n" \
                         "The schema for the {table_name} table in the {db_name} database is as follows: {table_schema}"

        self.template2 = """You are a data scientist expert. Provided with a SQL table description, your goal is to create insightful visualizations to better understand the provided dataset.
                          Do not suggest ideas that would lead to overloaded charts due to an overwhelming number of categories. For instance, avoid pie charts with too many categories, or line plots with too many lines, replace lots of bars by histogram.
                          Try to choose the best type of chart for each idea.
                          You can also propose to limit the number of categories for a better visualization (For instance suggest Top 10 or grouped by larger category).
                          Give accurate description of the visualizations for future implementation using python, and also give the attributes to use for data retrieval. 
                          Take into account the type of the attributes, and focus on relevant visualizations as a data scientist working for the company that provided the database. 
                          Give a score out of 10 for the relevance of each visualization according to you. 
                          The description for the table is: {table_description}"""

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
        chain = prompt | self.model_gpt | self.output_parser
        return chain.invoke({"db_name": db_name, "table_name": table_name, "table_schema": table_schema})

    def execute_prompt2(self, table_description):
        prompt = ChatPromptTemplate.from_template(self.template2)
        chain = prompt | self.model_gpt | self.output_parser
        return chain.invoke({"table_description": table_description})

    def execute_prompt3(self, db_name, table_name, visualizations_ideas):
        prompt = ChatPromptTemplate.from_template(self.template3)
        chain = prompt | self.model_gpt | self.output_parser
        py_codes=chain.invoke({"db_name": db_name, "table_name": table_name, "ideas": visualizations_ideas})
        print(py_codes)
        return py_codes

class MultiTableVisualizer:
    def __init__(self):
        model_mistral = ChatMistralAI(mistral_api_key=os.environ.get('MISTRAL_API_KEY'))
        model_gpt = ChatOpenAI(model="gpt-4", api_key=os.environ.get('OPEN_AI_KEY'))
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name='us-west-2',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        )

        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        model_kwargs =  {
            "max_tokens": 5000,
            "temperature": 0.01,
            "top_k": 250,
            "top_p": 0.99,
            "stop_sequences": ["\n\nHuman"],
        }

        model_claude = BedrockChat(
            client=bedrock_runtime,
            model_id=model_id,
            #model_kwargs=model_kwargs,
        )
        self.models = {'gpt': model_gpt, 'mistral': model_mistral, 'claude': model_claude}
        self.output_parser = StrOutputParser()

        self.template_suggest_ideas = """ You are a data scientist expert working on a database. Provided the SQL database schema, and the list of possible joins, your role is to propose several visualization ideas requiring joins.
        Do not suggest ideas that would lead to overloaded charts due to an overwhelming number of categories. For instance, avoid pie charts with too many categories, or line plots with too many lines, replace lots of bars by histogram.
        Try to choose the best type of chart for each idea.
        You can also propose to limit the number of categories for a better visualization (For instance suggest Top 10 or grouped by larger category).
        - The schema for the database is as follows: {tables_and_attributes}
        - Here is relevant info for possible joins : {parent_child_joins}"""

        self.template_filter = """You are a data scientist expert working on a database. Among the provided visualization ideas, some may observe the same fact or data point but are presented differently. Your task is to:
        1. Identify these redundant ideas.
        2. Select the most effective one from these sets.
        4. Briefly explain why certain ideas were left out in favor of the chosen one.
        5. Compile a final list of visualization ideas that will be used going forward. This list should include the selected ideas from any redundant sets and ALL other non-redundant ideas that were originally provided.
        Please follow these format instructions for your response:
        - For redundant ideas: "1. [Redundant idea 1 removed] | Reason: [explanation]. 2. [Redundant idea 2 removed] | Reason: [explanation]. ..."
        - For the final list of ideas: "Final List: 1. [Chosen idea 1]. 2. [Chosen idea 2]. ..."

        List of visualization ideas provided: {first_output}

        """

        self.template_evaluate = """You are a data scientist expert working on a database. Following the identification and exclusion of redundant visualization ideas from the first step, you are now tasked with scoring the remaining non-redundant ideas.
        These ideas are unique and were not part of the sets of redundant ideas previously evaluated.
        Assuming you have a clear understanding of which ideas were deemed redundant, score each non-redundant visualization idea on a scale of 10, focusing on its relevance as a data scientist and ease of readability.
        For each non-redundant visualization idea:
        1. Describe the visualization idea.
        2. Provide a score out of 10, based on its relevance and readability.

        Format instructions:
        1. Non-redundant visualization idea 1 | Score/10 |
        2. Non-redundant visualization idea 2 | Score/10 |
        ...
        - You will find the ideas in the Final List  : {list_ideas}
        """

        self.template_write_sql = """You are a data scientist expert working on a database. Provided with visualisation ideas, your role is to write sql queries to retrieve data required for each visualization. 
                Do that only for those with score 7 and above. If the exact idea is not doable with the database tables and attributes, ignore it. Make sure to use all the tables suggested so you don't change the intent of the visualization. 
                Repeat the complete visualization idea (the one WITH type of chart) in your response before each query.
                - Here is the list of ideas : {evaluated_ideas}
                - Here are also the attributes for each table : {tables_and_attributes}
                """

        self.template_write_code = """You are a skillful python coder robot working on the database {db_name}. Provided with visualisation ideas and sql queries to retrieve useful data for each, 
        you need to write python code to plot them, using the queries.
        Your response must contain for each visualization: 
        1. A paragraph explaining the motivation for the visualization and how to interpret it. 
        2. Python code for generating the visualization, queries included. You can use seaborn if needed. 
        Please ensure that your code is executable without modification. If you're unsure about certain details and can only provide a template that requires variable changes, please skip that visualization.
        Do not delve into python's code details.
        Format instructions for each visualization idea : paragraph for visualization | code for visualization  
        
        - Here are the ideas with sql queries: {sql_queries}
        """


    def execute_prompt_suggest_ideas(self, model_name, tables_and_attributes, parent_child_joins):
        prompt = ChatPromptTemplate.from_template(self.template_suggest_ideas)
        chain = prompt | self.models[model_name] | self.output_parser
        return chain.invoke({"tables_and_attributes": tables_and_attributes, "parent_child_joins": parent_child_joins})

    def execute_prompt_filter(self, model_name, first_output):
        prompt = ChatPromptTemplate.from_template(self.template_filter)
        chain = prompt | self.models[model_name] | self.output_parser
        filtered = chain.invoke({"first_output": first_output})
        return filtered
    
    def execute_prompt_evaluate(self, model_name, filtered_ideas):
        prompt = ChatPromptTemplate.from_template(self.template_evaluate)
        chain = prompt | self.models[model_name] | self.output_parser
        evaluated_ideas = chain.invoke({"list_ideas": filtered_ideas})
        return evaluated_ideas
    
    def execute_prompt_sql(self, model_name, evaluated_ideas, tables_and_attributes):
        prompt = ChatPromptTemplate.from_template(self.template_write_sql)
        chain = prompt | self.models[model_name] | self.output_parser
        return chain.invoke({"evaluated_ideas": evaluated_ideas,"tables_and_attributes": tables_and_attributes})

    def execute_prompt_code(self, model_name, db_name, sql_queries):
        prompt = ChatPromptTemplate.from_template(self.template_write_code)
        chain = prompt | self.models[model_name] | self.output_parser
        py_codes=chain.invoke({"db_name": db_name, "sql_queries": sql_queries})
        print(py_codes)
        return py_codes


class DatabaseSummary:
    def __init__(self, model="gpt-4"):
        self.model = ChatOpenAI(model=model, api_key=os.environ.get('OPEN_AI_KEY'))
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
   






