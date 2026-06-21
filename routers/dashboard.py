from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
from database import get_db
from dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    total_problems = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id
    ).count()

    easy_count = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id,
        models.DSAProblem.difficulty == "Easy",
    ).count()

    medium_count = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id,
        models.DSAProblem.difficulty == "Medium",
    ).count()

    hard_count = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id,
        models.DSAProblem.difficulty == "Hard",
    ).count()

    review_again_count = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id,
        models.DSAProblem.status == "Review Again",
    ).count()

    struggling_count = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id,
        models.DSAProblem.status == "Struggling",
    ).count()

    average_confidence = db.query(
        func.avg(models.DSAProblem.confidence_level)
    ).filter(
        models.DSAProblem.user_id == current_user.id,
        models.DSAProblem.confidence_level.isnot(None),
    ).scalar()

    total_notes = db.query(models.ProblemNote).filter(
        models.ProblemNote.user_id == current_user.id
    ).count()

    total_mistakes = db.query(models.Mistake).filter(
        models.Mistake.user_id == current_user.id
    ).count()

    total_reviews = db.query(models.ReviewLog).filter(
        models.ReviewLog.user_id == current_user.id
    ).count()

    return {
        "total_problems": total_problems,
        "easy_count": easy_count,
        "medium_count": medium_count,
        "hard_count": hard_count,
        "review_again_count": review_again_count,
        "struggling_count": struggling_count,
        "average_confidence": round(average_confidence, 2) if average_confidence else None,
        "total_notes": total_notes,
        "total_mistakes": total_mistakes,
        "total_reviews": total_reviews,
    }