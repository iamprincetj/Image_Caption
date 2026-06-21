import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.config.env import BASE_URL, get_api_key


# Langchain client pointed at Github Models' OpenAI-compatible endpoint

vision_llm = ChatOpenAI(
    model="gpt-4o",
    base_url=BASE_URL,
    api_key=get_api_key(),
    temperature=0.4
)

def encode_image_to_base64(image_path: str) -> str:
    """
    Reads an image file and returns a base64-encoded string.

    ARGS:
        - image_path (str): The image file
    
    RETURNS:
        - (str): The base64-encoded string
    """

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    

def describe_image(image_path: str) -> str:
    """
    Sends an image to GPT-4o and returns a rich, structured description
    covering subjects, setting, mood, colors, and notable details.
    This description is the raw material the caption stage will use.
    """
    base64_image = encode_image_to_base64(image_path)

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Describe this image in detail for someone who cannot see it. "
                    "Cover: main subject(s), setting/background, colors, mood/atmosphere, "
                    "any action happening, and notable details (text, objects, expressions). "
                    "Be specific and vivid, not generic. Write 3-5 sentences."     
                )
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
        ]
    )

    response = vision_llm.invoke([message])
    return response.content



