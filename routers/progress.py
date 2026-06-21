from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

import models
from database import get_db
from dependencies import get_current_user

router = APIRouter(
    prefix="/progress",
    tags=["Progress"],
)

@router.get("/weak-patterns")
def get_weak_patterns(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    patterns = db.query(models.DSAProblem.pattern).filter(
        models.DSAProblem.user_id == current_user.id
    ).distinct().all()

    result = []

    for pattern_row in patterns:
        pattern = pattern_row[0]

        problem_count = db.query(models.DSAProblem).filter(
            models.DSAProblem.user_id == current_user.id,
            models.DSAProblem.pattern == pattern,
        ).count()

        average_confidence = db.query(
            func.avg(models.DSAProblem.confidence_level)
        ).filter(
            models.DSAProblem.user_id == current_user.id,
            models.DSAProblem.pattern == pattern,
            models.DSAProblem.confidence_level.isnot(None),
        ).scalar()

        low_confidence_count = db.query(models.DSAProblem).filter(
            models.DSAProblem.user_id == current_user.id,
            models.DSAProblem.pattern == pattern,
            models.DSAProblem.confidence_level <= 3,
        ).count()

        review_again_count = db.query(models.DSAProblem).filter(
            models.DSAProblem.user_id == current_user.id,
            models.DSAProblem.pattern == pattern,
            models.DSAProblem.status == "Review Again",
        ).count()

        struggling_count = db.query(models.DSAProblem).filter(
            models.DSAProblem.user_id == current_user.id,
            models.DSAProblem.pattern == pattern,
            models.DSAProblem.status == "Struggling",
        ).count()

        mistake_count = db.query(models.Mistake).join(
            models.DSAProblem,
            models.Mistake.problem_id == models.DSAProblem.id,
        ).filter(
            models.Mistake.user_id == current_user.id,
            models.DSAProblem.pattern == pattern,
        ).count()

        reasons = []

        if average_confidence is not None and average_confidence <= 3:
            reasons.append("Average confidence is 3 or below")

        if low_confidence_count > 0:
            reasons.append("Has low-confidence problems")

        if review_again_count > 0:
            reasons.append("Has problems marked Review Again")

        if struggling_count > 0:
            reasons.append("Has problems marked Struggling")

        if mistake_count > 0:
            reasons.append("Has recorded mistakes")

        if reasons:
            result.append(
                {
                    "pattern": pattern,
                    "problem_count": problem_count,
                    "average_confidence": round(average_confidence, 2) if average_confidence else None,
                    "low_confidence_count": low_confidence_count,
                    "review_again_count": review_again_count,
                    "struggling_count": struggling_count,
                    "mistake_count": mistake_count,
                    "reasons": reasons,
                }
            )

    return {
        "weak_patterns": result
    }

@router.get("/review-needed")
def get_review_needed_problems(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    problems = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id,
        or_(
            models.DSAProblem.confidence_level <= 3,
            models.DSAProblem.status == "Review Again",
            models.DSAProblem.status == "Struggling",
        )
    ).order_by(
        models.DSAProblem.created_at.desc()
    ).all()

    result = []

    for problem in problems:
        mistake_count = db.query(models.Mistake).filter(
            models.Mistake.user_id == current_user.id,
            models.Mistake.problem_id == problem.id,
        ).count()

        review_count = db.query(models.ReviewLog).filter(
            models.ReviewLog.user_id == current_user.id,
            models.ReviewLog.problem_id == problem.id,
        ).count()

        latest_review = db.query(models.ReviewLog).filter(
            models.ReviewLog.user_id == current_user.id,
            models.ReviewLog.problem_id == problem.id,
        ).order_by(
            models.ReviewLog.reviewed_at.desc()
        ).first()

        reasons = []

        if problem.confidence_level is not None and problem.confidence_level <= 3:
            reasons.append("Low confidence level")

        if problem.status == "Review Again":
            reasons.append("Marked as Review Again")

        if problem.status == "Struggling":
            reasons.append("Marked as Struggling")

        if mistake_count > 0:
            reasons.append("Has recorded mistakes")

        result.append(
            {
                "id": problem.id,
                "title": problem.title,
                "platform": problem.platform,
                "difficulty": problem.difficulty,
                "pattern": problem.pattern,
                "status": problem.status,
                "confidence_level": problem.confidence_level,
                "mistake_count": mistake_count,
                "review_count": review_count,
                "latest_review_at": latest_review.reviewed_at if latest_review else None,
                "reasons": reasons,
            }
        )

    return {
        "review_needed": result
    }