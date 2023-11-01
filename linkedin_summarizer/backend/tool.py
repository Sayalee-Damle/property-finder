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


### Tool for finding houses


# Savills property codes:

PROPERTY_TYPES = {
    "villa": "GRS_PT_V",
    "bungalow": "GRS_T_B",
    "comdominium": "GRS_PT_CONDO",
    "duplex": "GRS_PT_D",
    "appartment": "GRS_PT_APT",
    "house": "GRS_PT_H",
    "penthouse": "GRS_PT_PENT",
    "serviced appartment": "GRS_PT_SAPT",
    "studio": "GRS_PT_STU",
    "triplex": "GRS_PT_T",
}


class HouseFinderToolInput(BaseModel):
    type_of_property: str = Field()


class HouseFinderTool(BaseTool):
    name = "house_finder"
    description = "Use this tool when you need to find a house"
    args_schema: Type[BaseModel] = HouseFinderToolInput

    def _run(self, user_needs: str, type_of_property: str, key: str):
        property_code = PROPERTY_TYPES.get(type_of_property)
        if property_code is None:
            available_property_types = list(PROPERTY_TYPES.keys())
            return f"Could not find property type: {type_of_property}. Available property types: {available_property_types}"
        return requests.get(f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&PropertyTypes={property_code}&Bedrooms=-1&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10")


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
