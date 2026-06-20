import os
from dotenv import load_dotenv
from openai import OpenAI
from src.config.env import BASE_URL, GITHUB_TOKEN

load_dotenv()

client = OpenAI(
    base_url=BASE_URL,
    api_key=GITHUB_TOKEN
)


response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "Say hello in 5 words"
    }]
)

print(response.choices[0])