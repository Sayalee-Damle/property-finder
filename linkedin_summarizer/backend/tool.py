
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Union, Type
from bs4 import BeautifulSoup
import html2text
from langchain.chains import create_extraction_chain
from langchain.prompts.chat import SystemMessage
import requests
from langchain.agents import AgentType, initialize_agent


import linkedin_summarizer.backend.execution as exec
import linkedin_summarizer.langchain_agent.extract_properties as ep
from linkedin_summarizer.configuration.log_factory import logger
from linkedin_summarizer.configuration.config import cfg
import linkedin_summarizer.langchain_agent.extract_properties as ep
import linkedin_summarizer.langchain_agent.data_read as data_read


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

MIN_BATHROOMS = {
    0:-1,
    1: "GRS_BT_1",
    2: "GRS_BT_2",
    3: "GRS_BT_3",
    4: "GRS_BT_4",
    5: "GRS_BT_5",
    6: "GRS_BT_6",
}

FEATURES = {
    "balcony":"GRS_FTR_B" ,
    "children's facility":"GRS_FTR_CHF",
    "club facilities": "GRS_FTR_CF" ,
    "concierge": "GRS_FTR_CON" ,
    "garden":"GRS_FTR_GDN",
    "gym": "GRS_FTR_G" ,
    "staff accomodation":"GRS_FTR_HLPQ",
    "jacuzzi": "GRS_FTR_JKZI",
    "lift":"GRS_FTR_L",
    "roof terrace":"GRS_FTR_RT",
    "swimming pool":"GRS_FTR_SP",
    "tennis court":"GRS_FTR_TC",
    "spa":"GRS_FTR_SPA",
    "fireplace":"GRS_FTR_FP"
}

## GRS_BT_4
##features: Union[str, None] = Field(
 ##       ..., description="The name of the index for which the data is to be retrieved"
    ##)

class HouseFinderToolInput(BaseModel):
    type_of_property: Union[str, None] = Field(
        ..., description="The name of the index for which the data is to be retrieved"
    )
    no_of_bedrooms: Union[int, None] = Field(
        ..., description="The number of bedrooms in the property"
    )

    no_of_bathrooms: Union[int, None] = Field(
        ..., description="The number of bathrooms in the property"
    )

    features: Union[list, None] = Field(
      ..., description="Extract features in the property"
    )


class HouseFinderTool(BaseTool):
    name = "house_finder"
    description = "Use this tool when you need to find a house"
    args_schema: Type[BaseModel] = HouseFinderToolInput

    def _run(
        self, type_of_property: Union[str, None], features: Union[list, None], no_of_bedrooms: Union[int, None] = -1, no_of_bathrooms: Union[int, None] = -1
    ):
        property_code =  PROPERTY_TYPES.get(type_of_property.lower())
        if no_of_bedrooms != -1:
            bedroom_code = MIN_BEDROOMS.get(no_of_bedrooms)
        if no_of_bathrooms != -1:
            bathroom_code = MIN_BATHROOMS.get(no_of_bathrooms)
        if features != []:
            feature_code: str = "&Features="
            if len(features) == 1:
                for feature in features:
                    feature_code: str = feature_code + FEATURES.get(feature.lower())
            else:
                for feature in features:
                    feature_code: str = feature_code + ',' + FEATURES.get(feature.lower())
        else:
            feature_code = ""
        logger.info(feature_code)
        if property_code != None:
            property_code = '&PropertyTypes=' + property_code
        else:
            property_code =""
        url_site = f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR{property_code}&Bedrooms={bedroom_code}&Bathrooms={bathroom_code}{feature_code}&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"

        url_for_properties = requests.get( url_site
        )
        logger.info(url_site)
        if url_for_properties.status_code == 200:
            content_html = url_for_properties.content
            with open(cfg.save_html_path / "savills.txt", "wb") as f:
                f.write(content_html)
            list_properties_markdown = data_read.create_zip(url_for_properties)
            return list_properties_markdown

        elif url_for_properties.status_code >= 500:
            return "Server Error"
        elif url_for_properties.status_code >= 400:
            return "Bad Request"
        else:
            return f"{url_for_properties.status_code},Unkown Error"

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




system_message =SystemMessage(content = """
# Main Purpose
-You are a polite real estate agent who helps customers to find properties

# Dialect
- Utilize polite American English with expressions prevalent in the property market

# Personality
- Portray a warm, approachable female property agent

# Interaction
- Response to inquiries about property but not about other subject. If someone asks about topics unrelated to the real estate market, please tell them that you do not know about it
- Reply to the queries using markdown dialect
- Please do not ask follow up questions like eg:Please let me know if you need more information about any of these properties""")

agent_kwargs = {"system_message": system_message}

house_finder_tool = HouseFinderTool()
agent = initialize_agent(
    [HouseFinderTool()], cfg.llm,
    agent=AgentType.OPENAI_FUNCTIONS, verbose=True, agent_kwargs=agent_kwargs
)

if __name__ == "__main__":
    import webbrowser

    list_of_properties = agent.run("I want to buy a bangalow of 4 bedrooms with a lift and a balcony")
    #logger.info(list_of_properties)
    # content = html.content
    # with open("/tmp/savills.txt", "wb") as f:
    # f.write(content)

    #webbrowser.open(url)
