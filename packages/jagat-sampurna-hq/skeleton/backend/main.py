"""
Jagat Sampurna International Yogi Foundation — HQ Mission Control
Foundation Operating System (FOS) — Backend API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

app = FastAPI(
    title="Jagat Sampurna HQ Mission Control",
    description="Foundation Operating System for Jagat Sampurna International Yogi Foundation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv("DB_PATH", "foundation.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open("schema.sql", "r") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()


# ── Routers ──────────────────────────────────────────────────────────────────
from routers import (
    personnel, agents, assets, spaces, beings,
    inventory, visitors, clients, subscriptions,
    finance, comms, media, library, tasks, dashboard, log
)

app.include_router(personnel.router, prefix="/api/v1/personnel", tags=["Personnel"])
app.include_router(agents.router,    prefix="/api/v1/agents",    tags=["AI Agents"])
app.include_router(assets.router,    prefix="/api/v1/assets",    tags=["Assets"])
app.include_router(spaces.router,    prefix="/api/v1/spaces",    tags=["Spaces"])
app.include_router(beings.router,    prefix="/api/v1/beings",    tags=["Living Beings"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(visitors.router,  prefix="/api/v1/visitors",  tags=["Visitors"])
app.include_router(clients.router,   prefix="/api/v1/clients",   tags=["Clients"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(finance.router,   prefix="/api/v1/finance",   tags=["Finance"])
app.include_router(comms.router,     prefix="/api/v1/comms",     tags=["Communications"])
app.include_router(media.router,     prefix="/api/v1/media",     tags=["Media"])
app.include_router(library.router,   prefix="/api/v1/library",   tags=["Library"])
app.include_router(tasks.router,     prefix="/api/v1/tasks",     tags=["Tasks"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(log.router,       prefix="/api/v1/log",       tags=["Operations Log"])


@app.on_event("startup")
def startup():
    if not os.path.exists(DB_PATH):
        init_db()


@app.get("/")
def root():
    return {"message": "Jagat Sampurna HQ Mission Control — API Online", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    webbrowser.open("http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
