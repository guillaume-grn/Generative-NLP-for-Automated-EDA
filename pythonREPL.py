from env import OPEN_AI_KEY

from langchain import hub
from langchain.agents import AgentExecutor
from langchain_experimental.tools import PythonREPLTool
tools = [PythonREPLTool()]
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI

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
        
