from fastapi import APIRouter, Depends
from typing import Optional
import sqlite3

router = APIRouter()

# Stub router for log — implement endpoints per api-spec.md

def get_db():
    conn = sqlite3.connect("foundation.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@router.get("")
def list_log(db=Depends(get_db)):
    rows = db.execute("SELECT * FROM log").fetchall()
    return {"success": True, "data": [dict(r) for r in rows], "total": len(rows)}
