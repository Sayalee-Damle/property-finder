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
import linkedin_summarizer.langchain_agent.templates as t

from langchain.document_loaders import BSHTMLLoader
from bs4 import BeautifulSoup

### .sv-details__address1--truncate > span > span

def html_loader(path: Path):
    loader = BSHTMLLoader(path)
    data = loader.load()
    return data

def find_name(html):
    
    content_html = html.content
    soup = BeautifulSoup(content_html, 'html.parser')
    return soup.find_all("<h6 class=\"sv-details__contacts-name\"><h6>")
        

if __name__ == "__main__":
    url_property = requests.get(
                f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&&Bedrooms=GRS_B_1&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"
            )
    logger.info(find_name(url_property))