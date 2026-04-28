from fastapi import APIRouter, Depends
from typing import Optional
import sqlite3

router = APIRouter()

# Stub router for comms — implement endpoints per api-spec.md

def get_db():
    conn = sqlite3.connect("foundation.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@router.get("")
def list_comms(db=Depends(get_db)):
    rows = db.execute("SELECT * FROM comms").fetchall()
    return {"success": True, "data": [dict(r) for r in rows], "total": len(rows)}
