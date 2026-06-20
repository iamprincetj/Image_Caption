import os
from dotenv import load_dotenv

# Loads the .env
load_dotenv()

BASE_URL =  base_url=os.environ["BASE_URL"]
BASE_URL1 =  base_url=os.environ["BASE_URL1"]
GITHUB_TOKEN = api_key=os.environ['GITHUB_TOKEN']