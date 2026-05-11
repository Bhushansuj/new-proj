from fastapi import APIRouter
from database import get_db
from backend.auth import create_token
from passlib.context import CryptContext

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"])

@router.post("/login")
def login(data: dict):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s", (data["username"],))
    user = cursor.fetchone()

    if not user:
        return {"error": "User not found"}

    if not pwd.verify(data["password"], user["password"]):
        return {"error": "Wrong password"}

    token = create_token({"sub": user["username"]})

    return {"access_token": token}