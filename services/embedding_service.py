import os

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from models import DSAProblem, ProblemEmbedding

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.4-mini")


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing.")

    return OpenAI(api_key=api_key)


def is_auto_embed_enabled() -> bool:
    return os.getenv("AI_AUTO_EMBED", "false").lower() == "true"


def create_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty for embedding.")

    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def build_problem_embedding_text(problem: DSAProblem) -> str:
    return f"""
Title: {problem.title}
Platform: {problem.platform}
Difficulty: {problem.difficulty}
Pattern: {problem.pattern}
Status: {problem.status}
Confidence Level: {problem.confidence_level}
Time Taken Minutes: {problem.time_taken_minutes}
Time Complexity: {problem.time_complexity}
Space Complexity: {problem.space_complexity}
Solution Code:
{problem.solution_code}
""".strip()


def upsert_problem_embedding(
    db: Session,
    problem: DSAProblem,
    user_id: int,
) -> ProblemEmbedding:
    content = build_problem_embedding_text(problem)
    embedding = create_embedding(content)

    existing_embedding = (
        db.query(ProblemEmbedding)
        .filter(
            ProblemEmbedding.user_id == user_id,
            ProblemEmbedding.problem_id == problem.id,
            ProblemEmbedding.source_type == "problem",
            ProblemEmbedding.source_id == problem.id,
        )
        .first()
    )

    if existing_embedding:
        existing_embedding.content = content
        existing_embedding.embedding = embedding
        existing_embedding.embedding_model = EMBEDDING_MODEL

        db.commit()
        db.refresh(existing_embedding)

        return existing_embedding

    new_embedding = ProblemEmbedding(
        user_id=user_id,
        problem_id=problem.id,
        source_type="problem",
        source_id=problem.id,
        content=content,
        embedding=embedding,
        embedding_model=EMBEDDING_MODEL,
    )

    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)

    return new_embedding


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