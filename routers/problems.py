from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from typing import Optional

import models
import schemas
from database import get_db
from dependencies import get_current_user

router = APIRouter(
    prefix="/problems",
    tags=["Problems"],
)


@router.post("/", response_model=schemas.ProblemResponse)
def create_problem(
    problem: schemas.ProblemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_problem = models.DSAProblem(
        user_id=current_user.id,
        title=problem.title,
        platform=problem.platform,
        difficulty=problem.difficulty,
        pattern=problem.pattern,
        status=problem.status,
        confidence_level=problem.confidence_level,
        time_taken_minutes=problem.time_taken_minutes,
        solution_code=problem.solution_code,
        time_complexity=problem.time_complexity,
        space_complexity=problem.space_complexity,
        solved_at=problem.solved_at,
    )

    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)

    return new_problem


@router.get("/", response_model=list[schemas.ProblemResponse])
def get_problems(
    difficulty: Optional[str] = None,
    pattern: Optional[str] = None,
    problem_status: Optional[str] = Query(default=None, alias="status"),
    confidence_level: Optional[int] = Query(default=None, ge=1, le=5),
    search: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id
    )

    if difficulty:
        query = query.filter(models.DSAProblem.difficulty == difficulty)

    if pattern:
        query = query.filter(models.DSAProblem.pattern.ilike(f"%{pattern}%"))

    if problem_status:
        query = query.filter(models.DSAProblem.status == problem_status)

    if confidence_level is not None:
        query = query.filter(models.DSAProblem.confidence_level == confidence_level)

    if search:
        search_value = f"%{search}%"

        query = query.filter(
            or_(
                models.DSAProblem.title.ilike(search_value),
                models.DSAProblem.pattern.ilike(search_value),
                models.DSAProblem.platform.ilike(search_value),
            )
        )

    problems = query.order_by(
        models.DSAProblem.created_at.desc()
    ).offset(skip).limit(limit).all()

    return problems


@router.get("/{problem_id}", response_model=schemas.ProblemResponse)
def get_problem(
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

    return problem


@router.put("/{problem_id}", response_model=schemas.ProblemResponse)
def update_problem(
    problem_id: int,
    problem_update: schemas.ProblemUpdate,
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

    update_data = problem_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(problem, key, value)

    db.commit()
    db.refresh(problem)

    return problem


@router.delete("/{problem_id}")
def delete_problem(
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

    db.delete(problem)
    db.commit()

    return {
        "message": "Problem deleted successfully"
    }