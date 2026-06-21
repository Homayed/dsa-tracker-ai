from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field

from database import get_db
from dependencies import get_current_user
from models import DSAProblem, ProblemEmbedding, User
from services.embedding_service import (
    CHAT_MODEL,
    EMBEDDING_MODEL,
    create_embedding,
    generate_rag_answer,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

class AskAIRequest(BaseModel):
    question: str = Field(..., min_length=2)
    limit: int = Field(3, ge=1, le=5)

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

@router.get("/search")
def semantic_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query_embedding = create_embedding(q)

    distance_expr = ProblemEmbedding.embedding.cosine_distance(query_embedding)

    results = (
        db.query(
            ProblemEmbedding,
            DSAProblem,
            distance_expr.label("distance"),
        )
        .join(DSAProblem, ProblemEmbedding.problem_id == DSAProblem.id)
        .filter(ProblemEmbedding.user_id == current_user.id)
        .order_by(distance_expr)
        .limit(limit)
        .all()
    )

    return {
        "query": q,
        "limit": limit,
        "results": [
            {
                "embedding_id": embedding.id,
                "problem_id": problem.id,
                "title": problem.title,
                "platform": problem.platform,
                "difficulty": problem.difficulty,
                "pattern": problem.pattern,
                "status": problem.status,
                "confidence_level": problem.confidence_level,
                "source_type": embedding.source_type,
                "content": embedding.content,
                "distance": float(distance),
                "similarity_score": round(1 - float(distance), 4),
            }
            for embedding, problem, distance in results
        ],
    }

@router.post("/ask")
def ask_ai(
    request: AskAIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query_embedding = create_embedding(request.question)

    distance_expr = ProblemEmbedding.embedding.cosine_distance(query_embedding)

    results = (
        db.query(
            ProblemEmbedding,
            DSAProblem,
            distance_expr.label("distance"),
        )
        .join(DSAProblem, ProblemEmbedding.problem_id == DSAProblem.id)
        .filter(ProblemEmbedding.user_id == current_user.id)
        .order_by(distance_expr)
        .limit(request.limit)
        .all()
    )

    if not results:
        return {
            "question": request.question,
            "answer": "I could not find any saved DSA tracker data to answer this yet. Add and embed some problems first.",
            "model": CHAT_MODEL,
            "sources": [],
        }

    context_blocks = []

    for index, (embedding, problem, distance) in enumerate(results, start=1):
        context_blocks.append(
            f"""
Source {index}
Problem ID: {problem.id}
Title: {problem.title}
Platform: {problem.platform}
Difficulty: {problem.difficulty}
Pattern: {problem.pattern}
Status: {problem.status}
Confidence Level: {problem.confidence_level}
Source Type: {embedding.source_type}
Content:
{embedding.content}
Similarity Score: {round(1 - float(distance), 4)}
""".strip()
        )

    context = "\n\n---\n\n".join(context_blocks)

    answer = generate_rag_answer(
        question=request.question,
        context=context,
    )

    return {
        "question": request.question,
        "answer": answer,
        "model": CHAT_MODEL,
        "sources": [
            {
                "embedding_id": embedding.id,
                "problem_id": problem.id,
                "title": problem.title,
                "pattern": problem.pattern,
                "difficulty": problem.difficulty,
                "status": problem.status,
                "similarity_score": round(1 - float(distance), 4),
            }
            for embedding, problem, distance in results
        ],
    }