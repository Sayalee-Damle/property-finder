from pathlib import Path
import html2text
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
import markdownify
from tabulate import tabulate

### .sv-details__address1--truncate > span > span


def html_loader(path: Path):
    loader = BSHTMLLoader(path)
    data = loader.load()
    return data


def find_realtor(soup):
    
    realtor_name_list = []
    for realtors in soup.find_all("h6", ("sv-details__contacts-name")):
        realtor_name_list.append(realtors.string)
    return realtor_name_list


def find_name_property(soup):
    
    property_name_list = []
    address_tags = soup.select(".sv-details__address1")
    for property in address_tags:
        # logger.info(i.text)
        property_name_list.append(property.text)
    return property_name_list


def find_property_details(soup):
    
    property_details_list = []
    property_details = soup.select(".sv-details__features")
    for details in property_details:
        # logger.info(i.text)
        property_details_list.append(details.text)
    return property_details_list

def find_property_link(soup):
    
    property_links_list = []
    for a in soup.find_all('a', class_="sv-details__link"):
    #print("Found the URL:", a['href']) 
        #logger.info(a['href'])
        property_links_list.append("https://search.savills.com/" + a['href'])
    return property_links_list

def create_soup(html):
    content_html = html.content
    soup = BeautifulSoup(content_html, "html.parser")
    return soup


def zip_details(property_name, property_details, realtor_name, property_link):
    mapped = zip(property_name, property_details, realtor_name, property_link)
    return mapped

def property_size(soup):
    property_size_list = []
    property_size = soup.select("div .sv-property-attribute sv--size")
    for size in property_size:
        logger.info(size.text)
        #property_size_list.append(size.text)
    #return property_size_list

    

def create_markdown(input_list):
    # Convert the list to a list of lists (each item is a separate list)
    table_data = []
    
    for item in input_list:
        data = {}
        data["property name"] = item[0]
        data['property details'] = item[1]
        data['realtor name'] = item[2]
        data['property link'] = item[3]
        table_data.append(data)
    logger.info(table_data)

    markdown = ""
    for item in table_data:
        markdown += "#### Property\n"
        for key, value in item.items():
            markdown += f"- **{key}**: {value}\n"
        markdown += "\n"

    with open(
        cfg.save_html_path / "savills_markdown.md", mode="wt", encoding="utf-8"
    ) as f:
        f.write(markdown)



if __name__ == "__main__":
    url_property = requests.get(
        f"https://search.savills.com/in/en/list?SearchList=Id_1243+Category_RegionCountyCountry&Tenure=GRS_T_B&SortOrder=SO_PCDD&Currency=INR&&Bedrooms=GRS_B_1&Bathrooms=-1&CarSpaces=-1&Receptions=-1&ResidentialSizeUnit=SquareFeet&LandAreaUnit=Acre&Category=GRS_CAT_RES&Shapes=W10"
    )
    # logger.info(find_realtor(url_property))
    # html_loader("C:/tmp/html_savills/savills.txt")
    soup = create_soup(url_property)
    property_name = find_name_property(soup)
    property_details = find_property_details(soup)
    realtor_name = find_realtor(soup)
    property_link = find_property_link(soup)
    #property_sizes = property_size(soup)
    #logger.info(property_sizes)
    list_properties = (list(zip_details(property_name, property_details, realtor_name, property_link)))
    #html_loader("C:/tmp/html_savills/savills.txt")
    create_markdown(list_properties)
