from random import random
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "john_doe": {
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


def __authentificate_user(credentials: HTTPBasicCredentials):
    """Метод аутентифиакиции пользователя"""
    user = fake_users_db.get(credentials.username)
    if user is None or not pwd_context.verify(
        credentials.password, user["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@app.get("/user", response_model=User)
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Получение информации о текущем пользователе"""
    return __authentificate_user(credentials)


@app.post("/user", response_model=User)
def create_user(user: User):
    """Создание нового пользователя"""
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


@app.post("/inference_model", response_model=dict, dependencies=[Depends(security)])
def inference_model(model_inf: ModelInference):
    """
    Метод предсказания успешности товара на рынке,
    на основе его названия, цены и количества.
    Успех измеряется в "успешнсти на метр" (усп/м).
    """
    return __some_very_smart_model(model_inf)
