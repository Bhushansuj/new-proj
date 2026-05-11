from fastapi import APIRouter, Depends
from database import get_db
from backend.dependencies import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/update")
def update(data: dict):
    db = get_db()
    cursor = db.cursor()

    query = """
    INSERT INTO clients (hostname, ip_address)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE last_seen=%s
    """

    cursor.execute(query, (
        data["hostname"],
        data["ip"],
        datetime.now()
    ))

    db.commit()
    return {"ok": True}


@router.get("/clients")
def get_clients(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clients")
    return cursor.fetchall()