from pathlib import Path
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

import linkedin_summarizer.backend.agents as agents
from linkedin_summarizer.configuration.config import cfg
from linkedin_summarizer.configuration.log_factory import logger
from linkedin_summarizer.backend.tool import house_finder_tool

def find_keywords_extract(keyword_sentence: str):
    property_types = ["bungalow", "condominium","duplex", "apartment", "flat", "house", "penthouse", "service apartments", "studio", "triplex", "villa"]
    sentence = keyword_sentence.split(" ")
    for word in sentence:
        logger.info("in for")
        logger.info(word)
        if word.lower() in property_types:
            return word

def find_keywords(specifications: str):
    property_types = ["bungalow", "condominium","duplex", "apartment", "flat", "house", "penthouse", "service apartments", "studio", "triplex", "villa"]
        
    task = f"""
        Give me the keyword for this type of property: {specifications}
        It should be from the list {property_types}
        """    
    agents.user_proxy.initiate_chat(agents.assistant, message=task)

    message_before_terminate = None
    for message in agents.user_proxy.chat_messages[agents.assistant]:
        content = message["content"]
        if content == cfg.terminate_token:
            break
        message_before_terminate = content
    return message_before_terminate
    
def get_key(user_msg):
    agents.user_proxy.register_function(
    function_map={
        house_finder_tool.name: house_finder_tool._run,
    }
    )

    key = agents.user_proxy.initiate_chat(
            agents.chatbot,
            message=f"could you give me the property code for {user_msg}", 
            llm_config=cfg.llm_config,
        )

    return key

def find_houses(key: str):
    website = create_get_message(key)
    logger.info(website)

    task = f"""
    give a list of properties with these specifications mentioned on the website: {website}. Use the data on the website
    """

    agents.user_proxy.initiate_chat(agents.assistant, message=task)

    message_before_terminate = None
    for message in agents.user_proxy.chat_messages[agents.assistant]:
        content = message["content"]
        if content == cfg.terminate_token:
            break
        message_before_terminate = content
    return message_before_terminate

def match_properties(type_of_property: str):
    property_types = {"GRS_PT_B" : "bungalow", 
        "GRS_PT_CONDO" : "condominium",
        "GRS_PT_D" : "duplex",
        "GRS_PT_APT" : ("apartment", "flat"),
        "GRS_PT_H" : "house",
        "GRS_PT_PENT" : "penthouse",
        "GRS_PT_SAPT" : "service apartments",
        "GRS_PT_STU" : "studio",
        "GRS_PT_T" : "triplex",
        "GRS_PT_V" : "villa"
        }
    for i in (property_types):
        if property_types[i] == type_of_property.lower():
            return i
        
def create_get_message(key: str):
    url = f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&PropertyTypes={key}&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"
    return url




if __name__ == "__main__":
    import sys

    #arg_length = len(sys.argv)
    #url = f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&PropertyTypes={key}&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"
    #website = "https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10&accept=true&_gl=1*2wlx6d*_ga*MTk0MjY5NjI2Mi4xNjY4NzQ3OTIz*_ga_CPY205VXSB*MTY5NTcxNDUxMS41NzEuMS4xNjk1NzE3MTYxLjAuMC4w"
    specifications = "I want a Villa"
    #if arg_length > 1:
        #website = sys.argv[1]

    #response = find_keywords(specifications)
    response = find_keywords_extract(specifications)
    #properties_list = find_properties(response, website)
    #key = agents.agent_chain.run('I want to buy a duplex')
    logger.info(response)
    #key = get_key(response)
    #logger.info(key)
    property_code = match_properties(response)
    logger.info(property_code)
    #properties_list = find_houses(property_code)
    #logger.info(properties_list)
    url = create_get_message(property_code)
    logger.info(url)
    data = requests.get(url)
    data.json()
    