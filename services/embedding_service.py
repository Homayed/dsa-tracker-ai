import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.4-mini")


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing.")

    return OpenAI(api_key=api_key)


def create_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty for embedding.")

    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def generate_rag_answer(question: str, context: str) -> str:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not context or not context.strip():
        return "I could not find enough saved DSA data to answer this question yet."

    client = get_openai_client()

    response = client.responses.create(
        model=CHAT_MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You are an AI DSA study assistant. "
                    "Answer only using the user's saved DSA tracker context. "
                    "Be practical, concise, and beginner-friendly. "
                    "If the context is not enough, say what data is missing."
                ),
            },
            {
                "role": "user",
                "content": f"""
Question:
{question}

Saved DSA tracker context:
{context}
""".strip(),
            },
        ],
    )

    return response.output_text