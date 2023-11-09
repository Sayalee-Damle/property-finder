## Description

This tool uses autogen to create agents. It accesses a LinkedIn page and gives the summary of the page.

## Installation instructions


```
conda create -n linkedin_summarizer python=3.11
conda activate linkedin_summarizer
pip install poetry
poetry install
```
This creates a specific environment with all the libraries in need!



## to start the project
```chainlit run .\linkedin_summary\backend\execution.py```




## Configuration
configure the .env file might like this:
To specify configurations use .env file

```
OPENAI_API_KEY= openai key
OPENAI_MODEL = gpt-3.5-turbo-16k
CHUNK_SIZE = 1000
TERMINATE_TOKEN =  TERMINATE
REQUEST_TIMEOUT = 300
SEED = 42
TEMPERATURE = 0
MAX_AUTO_REPLY = 4
CODE_DIR = /tmp/linkedin_summarizer
SAVE_HTML = /tmp/html_savills
LLM_CACHE = False
LANGCHAIN_DEBUG = True
PROJECT_ROOT =  the root of your project
```
## Flow of the project function wise
get_key --->  tool is used to find the keyword ---> create_get_message ---> find_houses

### steps in tool
find_keywords ---> match_properties ---> return keyword

Problems faced: 
The value returned is in a sentence format/None from the Autogen 'find_keywords' method, have to extract the key from it. 
Tried the same in langchain but gave a similar result
