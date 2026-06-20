from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config.env import BASE_URL, GITHUB_TOKEN
from src.vision import describe_image
from src.vector_store.base import retrieve_similar_examples

caption_llm = ChatOpenAI(
    model="gpt-4o",
    base_url=BASE_URL,
    api_key=GITHUB_TOKEN,
    temperature=0.9, # higher temperature: caption should feel creative, not deterministic
)


CAPTION_PROMPT = ChatPromptTemplate.from_template("""You are a social media caption writer. Given an image description and \
examples of high-engagement captions for similar images, write ONE new caption \
for this specific image.

Rules:
- Match the tone/mood of the example captions (don't force upbeat energy onto a somber image, or vice versa)
- Be specific to THIS image's details, not generic
- Include 2-4 relevant hashtags at the end
- Keep it short: 1-2 sentences plus hashtags
- Do not copy the example captions verbatim — use them only as style guidance

Image description:
{description}

Example captions for similar images (style reference only):
{examples}

Write the new caption now:""")

caption_chain = CAPTION_PROMPT | caption_llm | StrOutputParser()

def generate_caption(image_path: str) -> dict:
    """
    Full pipeline: image -> description -> retrieve similar examples -> generate caption.
    Returns a dict with all intermediate outputs for transparency/debugging.
    """

    description = describe_image(image_path)
    examples = retrieve_similar_examples(description, k=3)

    example_text = "\n".join(f"- {ex['caption']}" for ex in examples)

    caption = caption_chain.invoke({
        "description": description,
        "examples": example_text,
    })


    return {
        "description": description,
        "retrieved_examples": [ex["caption"] for ex in examples],
        "caption": caption
    }