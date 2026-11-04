from pydantic import BaseModel, EmailStr, Field, SecretStr

from app.schemas.users import UserOut


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: SecretStr = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    user: UserOut


class CsrfResponse(BaseModel):
    csrf_token: str


class MessageResponse(BaseModel):
    message: str
