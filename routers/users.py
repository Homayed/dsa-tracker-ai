from fastapi import APIRouter, Depends

import models
import schemas
from dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(get_current_user),
):
    return current_user