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
import linkedin_summarizer.langchain_agent.extract_properties as ep
from linkedin_summarizer.configuration.log_factory import logger
from linkedin_summarizer.configuration.config import cfg
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI
import linkedin_summarizer.langchain_agent.extract_properties as ep
from typing import Optional, Union
from bs4 import BeautifulSoup
import html2text
from langchain.chains import create_extraction_chain

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
    6: "GRS_B_6",
}


class HouseFinderToolInput(BaseModel):
    type_of_property: Union[str, None] = Field(
        ..., description="The name of the index for which the data is to be retrieved"
    )
    no_of_bedrooms: Union[int, None] = Field(
        ..., description="The number of bedrooms in the property"
    )


class HouseFinderTool(BaseTool):
    name = "house_finder"
    description = "Use this tool when you need to find a house"
    args_schema: Type[BaseModel] = HouseFinderToolInput

    def _run(
        self, type_of_property: Union[str, None], no_of_bedrooms: Union[int, None] = -1
    ):
        property_code = PROPERTY_TYPES.get(type_of_property.lower())
        if no_of_bedrooms != -1:
            bedroom_code = MIN_BEDROOMS.get(no_of_bedrooms)
        logger.info(property_code)
        if property_code != None:
            url = f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&PropertyTypes={property_code}&Bedrooms={bedroom_code}&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"

            url_property = requests.get(
                f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&PropertyTypes={property_code}&Bedrooms={bedroom_code}&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"
            )
        else:
            url = f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&&Bedrooms={bedroom_code}&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"

            url_property = requests.get(
                f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&&Bedrooms={bedroom_code}&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"
            )
        if url_property.status_code == 200:
            content_html = url_property.content
            with open(cfg.save_html_path / "savills.txt", "wb") as f:
                f.write(content_html)
            return url

        elif url_property.status_code >= 500:
            return "Server Error"
        elif url_property.status_code >= 400:
            return "Bad Request"
        else:
            return f"{url_property.status_code},Unkown Error"


    def extract_text_html(self, content_html):
        html_text = BeautifulSoup(content_html, features="html.parser")

        with open(
            cfg.save_html_path / "savills_text.txt", mode="wt", encoding="utf-8"
        ) as f:
            f.write(html_text.get_text())


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
    [HouseFinderTool()], cfg.llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=False
)

if __name__ == "__main__":
    import webbrowser

    url = agent.run("I want to buy a bangalow of 4 bedrooms")
    url = agent.invoke({"input": "I want to buy a bangalow of 4 bedrooms"}, )
    logger.info(url)
    # content = html.content
    # with open("/tmp/savills.txt", "wb") as f:
    # f.write(content)

    webbrowser.open(url) 