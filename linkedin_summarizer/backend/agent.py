import autogen
from linkedin_summarizer.configuration.config import cfg
from linkedin_summarizer.configuration.log_factory import logger
import linkedin_summarizer.backend.execution as exec

from langchain.agents import Tool, AgentExecutor, BaseSingleActionAgent,initialize_agent, AgentType
from linkedin_summarizer.backend.tool import house_finder_tool

import openai





assistant = autogen.AssistantAgent(
    name="assistant",
    system_message="You are an expert at making lists",
)

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="Give the keyword, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=cfg.llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode=cfg.terminate_token,
    max_consecutive_auto_reply=cfg.max_consecutive_auto_reply,
    is_termination_msg=lambda x: x.get("content", "")
    .rstrip()
    .endswith(cfg.terminate_token),
    code_execution_config={"work_dir": cfg.code_dir},
    llm_config=cfg.llm_config,
    system_message=f"""Reply {cfg.terminate_token} if the task has been solved at full satisfaction. Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""",
)






if __name__ == "__main__":
    llm_config=cfg.llm_config
    logger.info(llm_config)