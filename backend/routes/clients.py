from fastapi import APIRouter, Depends
from database import get_db
from dependencies import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/update")
def update(data: dict):
    db = get_db()
    cursor = db.cursor()

    query = """
    INSERT INTO inventory (hostname, mac_address, status, last_update)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE status=%s, last_update=%s
    """

    cursor.execute(query, (
        data.get("hostname"),
        data.get("mac_address", ""),
        data.get("status", "unknown"),
        datetime.now(),
        data.get("status", "unknown"),
        datetime.now()
    ))

    db.commit()
    return {"ok": True}


@router.get("/clients")
def get_clients(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM inventory")
    return cursor.fetchall()