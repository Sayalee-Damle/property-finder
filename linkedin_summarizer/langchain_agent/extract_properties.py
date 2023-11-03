
import ast
from langchain.tools import tool
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.chains import create_extraction_chain

from linkedin_summarizer.configuration.config import cfg
from linkedin_summarizer.configuration.log_factory import logger
import linkedin_summarizer.backend.execution as exec

import linkedin_summarizer.langchain_agent.templates as t

def prompt_factory(system_template, human_template):
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        template=system_template
    )
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        template=human_template
    )
    messages = [system_message_prompt, human_message_prompt]
    chat_prompt = ChatPromptTemplate.from_messages(messages)
    return chat_prompt

def extract_properties(user_input):
    schema = {
    "properties": {
        "property type": {"type": "string", "examples": ["bungalow", "condominium","duplex", "apartment", "flat", "house", "penthouse", "service apartments", "studio", "triplex", "villa"]},
        "minimum number of bedrooms": {"type": "integer"},
        
    },
    "required": ["property type", "minimum number of bedrooms"],
    }
    #chain = LLMChain( llm=cfg.llm, prompt=prompt_factory(t.human_message, t.system_message))
    chain = create_extraction_chain(schema, cfg.llm)
    #properties_json = chain.run({"user_input": user_input})
    return chain.run(user_input)

def json_extract(keyword_sentence: str):
    list_keyword = list(keyword_sentence)
    logger.info(list_keyword[1])
    val = list_keyword[1]
    
    return val


if __name__ == "__main__":
    output = extract_properties("house with 2 bedrooms")
    logger.info(output)
    #value = json_extract()
    #logger.info(value)