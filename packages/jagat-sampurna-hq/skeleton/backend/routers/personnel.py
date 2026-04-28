from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

router = APIRouter()


class PersonnelIn(BaseModel):
    name: str
    role: Optional[str] = None
    type: Optional[str] = "staff"
    email: Optional[str] = None
    phone: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None
    joined_on: Optional[str] = None
    photo_url: Optional[str] = None


def get_db():
    conn = sqlite3.connect("foundation.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@router.get("")
def list_personnel(status: Optional[str] = None, type: Optional[str] = None, db=Depends(get_db)):
    query = "SELECT * FROM personnel WHERE 1=1"
    params = []
    if status:
        query += " AND status=?"
        params.append(status)
    if type:
        query += " AND type=?"
        params.append(type)
    rows = db.execute(query, params).fetchall()
    return {"success": True, "data": [dict(r) for r in rows], "total": len(rows)}


@router.get("/{id}")
def get_person(id: int, db=Depends(get_db)):
    row = db.execute("SELECT * FROM personnel WHERE id=?", [id]).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"success": True, "data": dict(row)}


@router.post("")
def create_person(person: PersonnelIn, db=Depends(get_db)):
    cur = db.execute(
        "INSERT INTO personnel (name,role,type,email,phone,assigned_to,status,notes,joined_on,photo_url) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (person.name, person.role, person.type, person.email, person.phone,
         person.assigned_to, person.status, person.notes, person.joined_on, person.photo_url)
    )
    db.commit()
    return {"success": True, "data": {"id": cur.lastrowid}, "message": "Personnel record created"}


@router.put("/{id}")
def update_person(id: int, person: PersonnelIn, db=Depends(get_db)):
    db.execute(
        "UPDATE personnel SET name=?,role=?,type=?,email=?,phone=?,assigned_to=?,status=?,notes=?,joined_on=?,photo_url=? WHERE id=?",
        (person.name, person.role, person.type, person.email, person.phone,
         person.assigned_to, person.status, person.notes, person.joined_on, person.photo_url, id)
    )
    db.commit()
    return {"success": True, "message": "Updated"}


@router.delete("/{id}")
def deactivate_person(id: int, db=Depends(get_db)):
    db.execute("UPDATE personnel SET status='inactive' WHERE id=?", [id])
    db.commit()
    return {"success": True, "message": "Deactivated"}
