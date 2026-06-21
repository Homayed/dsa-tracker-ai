from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    problems = db.query(models.DSAProblem).filter(
        models.DSAProblem.user_id == current_user.id
    ).all()

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