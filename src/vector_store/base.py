from langchain_chroma  import Chroma
from langchain_core.documents import Document
from src.config.env import BASE_URL1, MY_GITHUB_TOKEN
from src.test.example_captions import EXAMPLE_CAPTIONS
from langchain_openai import OpenAIEmbeddings

PERSIST_DIR = "chroma_db"

embeddings = OpenAIEmbeddings(
    model= "openai/text-embedding-3-small",
    base_url=BASE_URL1,
    api_key=MY_GITHUB_TOKEN
)

def build_vector_store():
    """
    Embeds all example captions and persists them to disk. Run once (or whenever you update examples)
    """

    docs = [
        Document(
            page_content=ex["description"],
            metadata={"caption": ex['caption']}
        )
        for ex in EXAMPLE_CAPTIONS
    ]

    store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )

    print(f"Vector store built with {len(docs)} examples at {PERSIST_DIR}")
    return store


def get_vector_store():
    """Loads the existing persisited vector store (used at query time)."""

    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )


def retrieve_similar_examples(query_description: str, k: int =3):
    """Given a new image description, returns the k most similar example captions"""
    store = get_vector_store()
    result = store.similarity_search(query_description, k=k)

    return [
        {
            "description": doc.page_content, "caption": doc.metadata["caption"]} for doc in result
        
    ]