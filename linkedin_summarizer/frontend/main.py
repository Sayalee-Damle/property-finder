import chainlit as cl
from chainlit.types import AskFileResponse
from pathlib import Path
from langchain.schema import Document
from asyncer import asyncify


import linkedin_summarizer.backend.execution as exec
from linkedin_summarizer.configuration.log_factory import logger
from linkedin_summarizer.configuration.config import cfg
from linkedin_summarizer.backend.tool import agent
import linkedin_summarizer.backend.tagging_service as ts
from linkedin_summarizer.backend.model import ResponseTags


def answer(input_msg: str):
    response_tags: ResponseTags = ts.sentiment_chain_factory().run(
        ts.prepare_sentiment_input(input_msg)
    )
    logger.info(response_tags)
    if response_tags.is_positive:
        return "positive"
    elif response_tags.is_negative:
        return "negative"
    elif response_tags.sounds_confused:
        return "confused"
    else:
        return "did not understand"

async def ask_user_msg(question):
    ans = None
    while ans == None:
        ans = await cl.AskUserMessage(
            content=f"{question}", timeout=cfg.ui_timeout, raise_on_timeout= True
        ).send()
    return ans

@cl.on_chat_start
async def start() -> cl.Message:
    await cl.Message(content="Welcome To The Property Finder").send()
    
    requirements = await ask_user_msg("What are the requirements for your house?")
    requirements_list = requirements['content']
    while True:
        #logger.info(requirements['content'])
        list_of_houses = await cl.make_async(agent.run)(requirements_list)
        await cl.Message(content=list_of_houses).send()

        requirements_more = await ask_user_msg("What else can you describe?")
        if answer(requirements_more['content']) == "negative":
            break
            
        requirements_list = requirements_list + " " + requirements_more['content']
        
        