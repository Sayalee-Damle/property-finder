from linkedin_summarizer.configuration.config import cfg
from linkedin_summarizer.configuration.log_factory import logger
import linkedin_summarizer.backend.execution as exec
from linkedin_summarizer.backend.tool import agent


def test_type_property_exists():
    html = agent.run('villa')
    return html
    
