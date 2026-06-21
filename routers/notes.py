from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from dependencies import get_current_user

from services.embedding_service import (
    delete_source_embedding,
    is_auto_embed_enabled,
    upsert_note_embedding,
)

router = APIRouter(
    tags=["Notes"],
)


@router.post("/problems/{problem_id}/notes", response_model=schemas.NoteResponse)
def create_note(
    problem_id: int,
    note: schemas.NoteCreate,
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

    new_note = models.ProblemNote(
        user_id=current_user.id,
        problem_id=problem_id,
        content=note.content,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    if is_auto_embed_enabled():
        try:
            upsert_note_embedding(
                db=db,
                note=new_note,
                problem=problem,
                user_id=current_user.id,
            )
        except Exception as exc:
            print(f"Auto-embedding failed for note {new_note.id}: {exc}")

    return new_note


@router.get("/problems/{problem_id}/notes", response_model=list[schemas.NoteResponse])
def get_notes(
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

    notes = db.query(models.ProblemNote).filter(
        models.ProblemNote.problem_id == problem_id,
        models.ProblemNote.user_id == current_user.id,
    ).all()

    return notes


@router.put("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    note = db.query(models.ProblemNote).filter(
        models.ProblemNote.id == note_id,
        models.ProblemNote.user_id == current_user.id,
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    update_data = note_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    if is_auto_embed_enabled():
        try:
            upsert_note_embedding(
                db=db,
                note=note,
                problem=note.problem,
                user_id=current_user.id,
            )
        except Exception as exc:
            print(f"Auto-embedding failed for note {note.id}: {exc}")

    return note


@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    note = db.query(models.ProblemNote).filter(
        models.ProblemNote.id == note_id,
        models.ProblemNote.user_id == current_user.id,
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    delete_source_embedding(
        db=db,
        user_id=current_user.id,
        source_type="note",
        source_id=note.id,
    )

    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted successfully"
    }