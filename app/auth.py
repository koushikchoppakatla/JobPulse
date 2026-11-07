from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from pwdlib import PasswordHash
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = "change-this-secret-key-before-deployment"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Temporary user storage
users = {}


class UserRegister(BaseModel):
    username: str
    password: str


def create_token(username):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
def register(user: UserRegister):

    if user.username in users:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    users[user.username] = password_hash.hash(user.password)

    return {"message": "User registered successfully"}


@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):

    hashed_password = users.get(form.username)

    if not hashed_password or not password_hash.verify(
        form.password, hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_token(form.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username not in users:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


@router.get("/me")
def profile(username: str = Depends(get_current_user)):

    return {
        "message": "Authentication successful",
        "username": username
    }