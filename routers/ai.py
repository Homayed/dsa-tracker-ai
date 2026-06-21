from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import DSAProblem, ProblemEmbedding, User
from services.embedding_service import EMBEDDING_MODEL, create_embedding

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


def build_problem_embedding_text(problem: DSAProblem) -> str:
    return f"""
Title: {problem.title}
Difficulty: {problem.difficulty}
Pattern: {problem.pattern}
Status: {problem.status}
Confidence Level: {problem.confidence_level}
""".strip()


@router.post("/problems/{problem_id}/embed")
def embed_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    problem = (
        db.query(DSAProblem)
        .filter(
            DSAProblem.id == problem_id,
            DSAProblem.user_id == current_user.id,
        )
        .first()
    )

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    content = build_problem_embedding_text(problem)
    embedding = create_embedding(content)

    existing_embedding = (
        db.query(ProblemEmbedding)
        .filter(
            ProblemEmbedding.user_id == current_user.id,
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

        return {
            "message": "Problem embedding updated successfully",
            "embedding_id": existing_embedding.id,
            "problem_id": problem.id,
            "vector_dimensions": len(embedding),
            "embedding_model": EMBEDDING_MODEL,
        }

    new_embedding = ProblemEmbedding(
        user_id=current_user.id,
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

    return {
        "message": "Problem embedding created successfully",
        "embedding_id": new_embedding.id,
        "problem_id": problem.id,
        "vector_dimensions": len(embedding),
        "embedding_model": EMBEDDING_MODEL,
    }