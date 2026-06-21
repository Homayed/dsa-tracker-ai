from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from dependencies import get_current_user

from services.embedding_service import (
    delete_source_embedding,
    is_auto_embed_enabled,
    upsert_mistake_embedding,
)

router = APIRouter(
    tags=["Mistakes"],
)


@router.post("/problems/{problem_id}/mistakes", response_model=schemas.MistakeResponse)
def create_mistake(
    problem_id: int,
    mistake: schemas.MistakeCreate,
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

    new_mistake = models.Mistake(
        user_id=current_user.id,
        problem_id=problem_id,
        mistake_category=mistake.mistake_category,
        description=mistake.description,
        lesson_learned=mistake.lesson_learned,
    )

    db.add(new_mistake)
    db.commit()
    db.refresh(new_mistake)
    if is_auto_embed_enabled():
        try:
            upsert_mistake_embedding(
                db=db,
                mistake=new_mistake,
                problem=problem,
                user_id=current_user.id,
            )
        except Exception as exc:
            print(f"Auto-embedding failed for mistake {new_mistake.id}: {exc}")

    return new_mistake


@router.get("/problems/{problem_id}/mistakes", response_model=list[schemas.MistakeResponse])
def get_mistakes(
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

    mistakes = db.query(models.Mistake).filter(
        models.Mistake.problem_id == problem_id,
        models.Mistake.user_id == current_user.id,
    ).all()

    return mistakes


@router.put("/mistakes/{mistake_id}", response_model=schemas.MistakeResponse)
def update_mistake(
    mistake_id: int,
    mistake_update: schemas.MistakeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    mistake = db.query(models.Mistake).filter(
        models.Mistake.id == mistake_id,
        models.Mistake.user_id == current_user.id,
    ).first()

    if not mistake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mistake not found",
        )

    update_data = mistake_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(mistake, key, value)

    db.commit()
    db.refresh(mistake)

    if is_auto_embed_enabled():
        try:
            upsert_mistake_embedding(
                db=db,
                mistake=mistake,
                problem=mistake.problem,
                user_id=current_user.id,
            )
        except Exception as exc:
            print(f"Auto-embedding failed for mistake {mistake.id}: {exc}")

    return mistake


@router.delete("/mistakes/{mistake_id}")
def delete_mistake(
    mistake_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    mistake = db.query(models.Mistake).filter(
        models.Mistake.id == mistake_id,
        models.Mistake.user_id == current_user.id,
    ).first()

    if not mistake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mistake not found",
        )
    delete_source_embedding(
        db=db,
        user_id=current_user.id,
        source_type="mistake",
        source_id=mistake.id,
    )
    db.delete(mistake)
    db.commit()

    return {
        "message": "Mistake deleted successfully"
    }