from db import Database
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from utils import verify_password

security = HTTPBasic()


def get_db():
    db = Database()

    try:
        db.open()
        yield db
    finally:
        db.close()


def validate_user(credentials: HTTPBasicCredentials = Depends(security), db: Database = Depends(get_db)):
    user = db.get_one("users", ["id", "password", "active"], where={"email": credentials.username})

    if user and user['active']:
        if verify_password(credentials.password, user.get('password')):
            return user.get('id')

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials or inactive account.",
                        headers={"WWW-Authenticate": "Basic"})
