from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Optional, Type
import math
import autogen

from linkedin_summarizer.configuration.config import cfg


class CircumferenceToolInput(BaseModel):
    radius: float = Field()

class CircumferenceTool(BaseTool):
    name = "circumference_calculator"
    description = "Use this tool when you need to calculate a circumference using the radius of a circle"
    args_schema: Type[BaseModel] = CircumferenceToolInput

    def _run(self, radius: float):
        return float(radius) * 2.0 * math.pi
    
from langchain.tools.file_management.read import ReadFileTool

# Define a function to generate llm_config from a LangChain tool
def generate_llm_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.lower().replace (' ', '_'),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
      function_schema["parameters"]["properties"] = tool.args

    return function_schema

# Instantiate the ReadFileTool
read_file_tool = ReadFileTool()
custom_tool = CircumferenceTool()

# Construct the llm_config


user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
)

# Register the tool and start the conversation
user_proxy.register_function(
    function_map={
        custom_tool.name: custom_tool._run,
        read_file_tool.name: read_file_tool._run,
    }
)

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=cfg.llm_config,
)

user_proxy.initiate_chat(
    chatbot,
    message="Take the radius at 3 mm, then calculate the circumference of a circle.", #" 7.81mm" in the file
    llm_config=cfg.llm_config,
)

