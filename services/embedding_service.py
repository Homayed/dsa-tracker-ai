import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, OpenAIError, RateLimitError
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

def is_ai_enabled() -> bool:
    return os.getenv("AI_ENABLED", "false").lower() == "true"


def raise_if_ai_disabled() -> None:
    if not is_ai_enabled():
        raise ValueError("AI features are currently disabled.")


def is_auto_embed_enabled() -> bool:
    return os.getenv("AI_AUTO_EMBED", "false").lower() == "true"


def create_embedding(text: str) -> list[float]:
    raise_if_ai_disabled()
    if not text or not text.strip():
        raise ValueError("Text cannot be empty for embedding.")

    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def get_value(obj: Any, field_name: str, default: str = "") -> str:
    value = getattr(obj, field_name, default)

    if value is None:
        return default

    return str(value)


def build_problem_embedding_text(problem: DSAProblem) -> str:
    return f"""
Source Type: problem
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


def build_note_embedding_text(note: Any, problem: DSAProblem) -> str:
    return f"""
Source Type: note
Problem Title: {problem.title}
Problem Pattern: {problem.pattern}
Problem Difficulty: {problem.difficulty}
Note Content:
{get_value(note, "content")}
""".strip()


def build_mistake_embedding_text(mistake: Any, problem: DSAProblem) -> str:
    return f"""
Source Type: mistake
Problem Title: {problem.title}
Problem Pattern: {problem.pattern}
Problem Difficulty: {problem.difficulty}
Mistake Category: {get_value(mistake, "mistake_category")}
Mistake Description:
{get_value(mistake, "description")}
Lesson Learned:
{get_value(mistake, "lesson_learned")}
""".strip()

def build_review_log_embedding_text(review_log: Any, problem: DSAProblem) -> str:
    return f"""
Source Type: review_log
Problem Title: {problem.title}
Problem Pattern: {problem.pattern}
Problem Difficulty: {problem.difficulty}
Confidence Before: {get_value(review_log, "confidence_before")}
Confidence After: {get_value(review_log, "confidence_after")}
Was Solved Again: {get_value(review_log, "was_solved_again")}
Time Taken Minutes: {get_value(review_log, "time_taken_minutes")}
Review Notes:
{get_value(review_log, "notes")}
""".strip()


def upsert_embedding(
    db: Session,
    user_id: int,
    problem_id: int,
    source_type: str,
    source_id: int,
    content: str,
) -> ProblemEmbedding:
    embedding = create_embedding(content)

    existing_embedding = (
        db.query(ProblemEmbedding)
        .filter(
            ProblemEmbedding.user_id == user_id,
            ProblemEmbedding.problem_id == problem_id,
            ProblemEmbedding.source_type == source_type,
            ProblemEmbedding.source_id == source_id,
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
        problem_id=problem_id,
        source_type=source_type,
        source_id=source_id,
        content=content,
        embedding=embedding,
        embedding_model=EMBEDDING_MODEL,
    )

    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)

    return new_embedding


def upsert_problem_embedding(
    db: Session,
    problem: DSAProblem,
    user_id: int,
) -> ProblemEmbedding:
    content = build_problem_embedding_text(problem)

    return upsert_embedding(
        db=db,
        user_id=user_id,
        problem_id=problem.id,
        source_type="problem",
        source_id=problem.id,
        content=content,
    )


def upsert_note_embedding(
    db: Session,
    note: Any,
    problem: DSAProblem,
    user_id: int,
) -> ProblemEmbedding:
    content = build_note_embedding_text(note, problem)

    return upsert_embedding(
        db=db,
        user_id=user_id,
        problem_id=problem.id,
        source_type="note",
        source_id=note.id,
        content=content,
    )


def upsert_mistake_embedding(
    db: Session,
    mistake: Any,
    problem: DSAProblem,
    user_id: int,
) -> ProblemEmbedding:
    content = build_mistake_embedding_text(mistake, problem)

    return upsert_embedding(
        db=db,
        user_id=user_id,
        problem_id=problem.id,
        source_type="mistake",
        source_id=mistake.id,
        content=content,
    )


def upsert_review_log_embedding(
    db: Session,
    review_log: Any,
    problem: DSAProblem,
    user_id: int,
) -> ProblemEmbedding:
    content = build_review_log_embedding_text(review_log, problem)

    return upsert_embedding(
        db=db,
        user_id=user_id,
        problem_id=problem.id,
        source_type="review_log",
        source_id=review_log.id,
        content=content,
    )


def delete_source_embedding(
    db: Session,
    user_id: int,
    source_type: str,
    source_id: int,
) -> None:
    existing_embedding = (
        db.query(ProblemEmbedding)
        .filter(
            ProblemEmbedding.user_id == user_id,
            ProblemEmbedding.source_type == source_type,
            ProblemEmbedding.source_id == source_id,
        )
        .first()
    )

    if existing_embedding:
        db.delete(existing_embedding)
        db.commit()


def generate_rag_answer(question: str, context: str) -> str:
    raise_if_ai_disabled()
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

def generate_study_recommendation(context: str, days: int) -> str:
    raise_if_ai_disabled()
    if not context or not context.strip():
        return "I could not find enough saved DSA tracker data to recommend a study plan yet."

    client = get_openai_client()

    response = client.responses.create(
        model=CHAT_MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You are an AI DSA study coach. "
                    "Use only the user's saved DSA tracker data. "
                    "Give practical, beginner-friendly study recommendations. "
                    "Focus on weak patterns, mistakes, confidence levels, and review history. "
                    "Do not invent problems that are not in the context unless you clearly mark them as suggestions."
                ),
            },
            {
                "role": "user",
                "content": f"""
Create a {days}-day DSA study recommendation plan.

Saved DSA tracker context:
{context}

Your answer should include:
1. Weak patterns
2. Problems to review first
3. Mistakes to focus on
4. A simple {days}-day plan
5. One motivational but realistic final note
""".strip(),
            },
        ],
    )

    return response.output_text