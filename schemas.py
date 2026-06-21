from pydantic import BaseModel, EmailStr, Field , field_validator, ConfigDict
from typing import Optional

from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one number")

        special_characters = "!@#$%^&*()-_=+[]{};:'\",.<>?/\\|`~"

        if not any(char in special_characters for char in password):
            raise ValueError("Password must contain at least one special character")

        return password

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes= True)

class Token(BaseModel):
    access_token: str
    token_type: str


class ProblemCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    platform: str = "LeetCode"
    difficulty: str
    pattern: str = Field(..., min_length=2, max_length=100)
    status: str = "Solved"
    confidence_level: Optional[int] = Field(default=None, ge=1, le=5,description=(
        "Confidence level from 1 to 5. "
        "1 = Not confident, 2 = Weak, 3 = Okay, "
        "4 = Good, 5 = Strong."
    ),)
    time_taken_minutes: Optional[int] = Field(default=None, ge=0)

    solution_code: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    solved_at: Optional[datetime] = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, difficulty: str):
        allowed = ["Easy", "Medium", "Hard"]

        if difficulty not in allowed:
            raise ValueError("Difficulty must be Easy, Medium, or Hard")

        return difficulty

    @field_validator("status")
    @classmethod
    def validate_status(cls, status: str):
        allowed = ["Solved", "Review Again", "Struggling"]

        if status not in allowed:
            raise ValueError("Status must be Solved, Review Again, or Struggling")

        return status


class ProblemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    platform: Optional[str] = None
    difficulty: Optional[str] = None
    pattern: Optional[str] = None
    status: Optional[str] = None
    confidence_level: Optional[int] = Field(default=None, ge=1, le=5,description=(
        "Confidence level from 1 to 5. "
        "1 = Not confident, 2 = Weak, 3 = Okay, "
        "4 = Good, 5 = Strong."
    ),)
    time_taken_minutes: Optional[int] = Field(default=None, ge=0)

    solution_code: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    solved_at: Optional[datetime] = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, difficulty: Optional[str]):
        if difficulty is None:
            return difficulty

        allowed = ["Easy", "Medium", "Hard"]

        if difficulty not in allowed:
            raise ValueError("Difficulty must be Easy, Medium, or Hard")

        return difficulty

    @field_validator("status")
    @classmethod
    def validate_status(cls, status: Optional[str]):
        if status is None:
            return status

        allowed = ["Solved", "Review Again", "Struggling"]

        if status not in allowed:
            raise ValueError("Status must be Solved, Review Again, or Struggling")

        return status


class ProblemResponse(BaseModel):
    id: int
    user_id: int
    title: str
    platform: str
    difficulty: str
    pattern: str
    status: str
    confidence_level: Optional[int]
    time_taken_minutes: Optional[int]
    solution_code: Optional[str]
    time_complexity: Optional[str]
    space_complexity: Optional[str]
    solved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=2)


class NoteUpdate(BaseModel):
    content: Optional[str] = Field(default=None, min_length=2)


class NoteResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MistakeCreate(BaseModel):
    mistake_category: Optional[str] = None
    description: str = Field(..., min_length=2)
    lesson_learned: Optional[str] = None


class MistakeUpdate(BaseModel):
    mistake_category: Optional[str] = None
    description: Optional[str] = Field(default=None, min_length=2)
    lesson_learned: Optional[str] = None


class MistakeResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    mistake_category: Optional[str]
    description: str
    lesson_learned: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)