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
```chainlit run .\transcriber\frontend\main.py```




## Configuration
configure the .env file might like this:
To specify configurations use .env file

```
OPENAI_API_KEY = openaikey
OPENAI_MODEL = gpt-3.5-turbo-16k-0613
CHUNK_SIZE = 1000
TEXT_PATH_DISC = /TranscribedText/
PROJECT_ROOT =  (mention the root folder)/transcriber
REQUEST_TIMEOUT = 300
LLM_CACHE = False
VERBOSE_LLM = True
TOKEN_LIMIT = 13000
TEXT_FILES_PATH = /tmp/transcribe/
AUDIO_FILE = /tmp/audio/

```

