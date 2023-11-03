from pathlib import Path
import requests
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Optional, Type
import math
import autogen
import requests
from langchain.tools import tool
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

import linkedin_summarizer.backend.execution as exec
from linkedin_summarizer.configuration.log_factory import logger
from linkedin_summarizer.configuration.config import cfg
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI
import linkedin_summarizer.langchain_agent.extract_properties as ep

### Tool for finding houses


# Savills property codes:

PROPERTY_TYPES = {
    "villa": "GRS_PT_V",
    "bungalow": "GRS_PT_B",
    "comdominium": "GRS_PT_CONDO",
    "duplex": "GRS_PT_D",
    "apartment": "GRS_PT_APT",
    "house": "GRS_PT_H",
    "penthouse": "GRS_PT_PENT",
    "serviced appartment": "GRS_PT_SAPT",
    "studio": "GRS_PT_STU",
    "triplex": "GRS_PT_T",
}

MIN_BEDROOMS = {
    1: "GRS_B_1",
    2: "GRS_B_2",
    3: "GRS_B_3",
    4: "GRS_B_4",
    5: "GRS_B_5",
    6: "GRS_B_6"
}

class HouseFinderToolInput(BaseModel):
    type_of_property: str = Field()


class HouseFinderTool(BaseTool):
    name = "house_finder"
    description = "Use this tool when you need to find a house"
    args_schema: Type[BaseModel] = HouseFinderToolInput

    def _run(self, user_input: str):
        properties = ep.extract_properties(user_input)
        logger.info(properties)
        property_code = PROPERTY_TYPES.get(properties.get("property type").lower())
        logger.info(property_code)
        min_no_bedrooms = properties.get("minimum number of bedrooms")
        url_property  = requests.get(f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&PropertyTypes={property_code}&Bedrooms=GRS_B_{min_no_bedrooms}&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10")
        if url_property.status_code == 500:
            return f"Could not find property."
        content = url_property.content
        with open(cfg.save_html_path/"savills.txt", "wb") as f:
            f.write(content)
        return url_property

def generate_llm_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.lower().replace(" ", "_"),
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


house_finder_tool = HouseFinderTool()
agent = initialize_agent(
    [HouseFinderTool()], cfg.llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

if __name__ == "__main__":
    html = house_finder_tool.run('house with 2 bedrooms')
    logger.info(html)
    #content = html.content
    #with open("/tmp/savills.txt", "wb") as f:
        #f.write(content)
