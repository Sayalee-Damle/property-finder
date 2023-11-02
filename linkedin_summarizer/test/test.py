from linkedin_summarizer.configuration.config import cfg
from linkedin_summarizer.configuration.log_factory import logger
import linkedin_summarizer.backend.execution as exec
from linkedin_summarizer.backend.tool import house_finder_tool


def test_type_property_exists():
    html = house_finder_tool.run('villa')
    assert html.content, "Property exists"
    
