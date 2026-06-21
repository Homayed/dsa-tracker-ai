from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from dependencies import get_current_user

from services.embedding_service import (
    delete_source_embedding,
    is_auto_embed_enabled,
    upsert_review_log_embedding,
)

router = APIRouter(
    tags=["Reviews"],
)


@router.post("/problems/{problem_id}/reviews", response_model=schemas.ReviewLogResponse)
def create_review_log(
    problem_id: int,
    review: schemas.ReviewLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    problem = db.query(models.DSAProblem).filter(
        models.DSAProblem.id == problem_id,
        models.DSAProblem.user_id == current_user.id,
    ).first()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    new_review = models.ReviewLog(
        user_id=current_user.id,
        problem_id=problem_id,
        confidence_before=review.confidence_before,
        confidence_after=review.confidence_after,
        was_solved_again=review.was_solved_again,
        time_taken_minutes=review.time_taken_minutes,
        notes=review.notes,
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    if is_auto_embed_enabled():
        try:
            upsert_review_log_embedding(
                db=db,
                review_log=new_review,
                problem=problem,
                user_id=current_user.id,
            )
        except Exception as exc:
            print(f"Auto-embedding failed for review log {new_review.id}: {exc}")

    return new_review


@router.get("/problems/{problem_id}/reviews", response_model=list[schemas.ReviewLogResponse])
def get_review_logs(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    problem = db.query(models.DSAProblem).filter(
        models.DSAProblem.id == problem_id,
        models.DSAProblem.user_id == current_user.id,
    ).first()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    review_logs = db.query(models.ReviewLog).filter(
        models.ReviewLog.problem_id == problem_id,
        models.ReviewLog.user_id == current_user.id,
    ).all()

    return review_logs


@router.put("/reviews/{review_id}", response_model=schemas.ReviewLogResponse)
def update_review_log(
    review_id: int,
    review_update: schemas.ReviewLogUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    review = db.query(models.ReviewLog).filter(
        models.ReviewLog.id == review_id,
        models.ReviewLog.user_id == current_user.id,
    ).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review log not found",
        )

    update_data = review_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    if is_auto_embed_enabled():
        try:
            upsert_review_log_embedding(
                db=db,
                review_log=review,
                problem=review.problem,
                user_id=current_user.id,
            )
        except Exception as exc:
            print(f"Auto-embedding failed for review log {review.id}: {exc}")

    return review


@router.delete("/reviews/{review_id}")
def delete_review_log(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    review = db.query(models.ReviewLog).filter(
        models.ReviewLog.id == review_id,
        models.ReviewLog.user_id == current_user.id,
    ).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review log not found",
        )

    delete_source_embedding(
        db=db,
        user_id=current_user.id,
        source_type="review_log",
        source_id=review.id,
    )
    db.delete(review)
    db.commit()

    return {
        "message": "Review log deleted successfully"
    }