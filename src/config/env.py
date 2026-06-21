import os
from dotenv import load_dotenv

# Loads the .env
load_dotenv()
from contextvars import ContextVar

# This will hold the API key dynamically for the lifetime of a single request
API_KEY_VAR: ContextVar[str] = ContextVar("api_key", default="")

def get_api_key() -> str:
    """Call this anywhere in your project to get the current request's API key."""
    return API_KEY_VAR.get()


BASE_URL =  os.environ["BASE_URL"]
BASE_URL1 =  os.environ["BASE_URL1"]
GITHUB_TOKEN = get_api_key()
MY_GITHUB_TOKEN = os.environ['MY_GITHUB_TOKEN']

print('here',GITHUB_TOKEN)
print('there',MY_GITHUB_TOKEN)