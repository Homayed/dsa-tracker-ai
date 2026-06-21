from pydantic import BaseModel, EmailStr, Field , field_validator, ConfigDict

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