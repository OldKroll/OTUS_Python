from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("user"),
        "email": "user@user.user",
        "age": 25,
    }
}


class User(BaseModel):
    username: str
    email: str
    age: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def __verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def __authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not __verify_password(password, user["hashed_password"]):
        return False
    return user


def __create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = __authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = __create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.get("/user", response_model=User)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@app.post("/user", response_model=User)
def create_user(user: User):
    """Создание нового пользователя"""
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash("secret")
    user_data = user.__dict__()
    user_data["hashed_password"] = hashed_password
    fake_users_db[user.username] = user_data
    return user


class ModelInference(BaseModel):
    count: int
    price: int
    label: str


def __some_very_smart_model(model_inf: ModelInference) -> dict:
    """Некая очень усмная модель"""
    return {
        "predict": f"{model_inf.count * model_inf.price + len(model_inf.label)} усп/м"
    }


@app.post(
    "/inference_model", response_model=dict, dependencies=[Depends(get_current_user)]
)
def inference_model(model_inf: ModelInference):
    """
    Метод предсказания успешности товара на рынке,
    на основе его названия, цены и количества.
    Успех измеряется в "успешнсти на метр" (усп/м).
    """
    return __some_very_smart_model(model_inf)
