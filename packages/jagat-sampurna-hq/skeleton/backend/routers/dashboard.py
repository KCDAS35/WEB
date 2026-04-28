from fastapi import APIRouter, Depends
from datetime import date
import sqlite3

router = APIRouter()


def get_db():
    conn = sqlite3.connect("foundation.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@router.get("")
def dashboard_summary(db=Depends(get_db)):
    today = str(date.today())

    personnel_active = db.execute("SELECT COUNT(*) FROM personnel WHERE status='active'").fetchone()[0]
    agents_running   = db.execute("SELECT COUNT(*) FROM ai_agents WHERE status='running'").fetchone()[0]
    assets_issues    = db.execute("SELECT COUNT(*) FROM assets WHERE condition!='good'").fetchone()[0]
    low_stock        = db.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= low_threshold").fetchone()[0]
    visitors_today   = db.execute("SELECT COUNT(*) FROM visitors WHERE DATE(arrival)=?", [today]).fetchone()[0]
    tasks_overdue    = db.execute("SELECT COUNT(*) FROM tasks WHERE status!='completed' AND due_date < ?", [today]).fetchone()[0]
    renewals_soon    = db.execute("SELECT COUNT(*) FROM subscriptions WHERE renewal_date BETWEEN ? AND DATE(?, '+7 days') AND status='active'", [today, today]).fetchone()[0]

    alerts = []
    if assets_issues:  alerts.append({"module": "assets",    "level": "yellow", "message": f"{assets_issues} asset(s) need attention"})
    if low_stock:      alerts.append({"module": "inventory", "level": "red",    "message": f"{low_stock} inventory item(s) below threshold"})
    if tasks_overdue:  alerts.append({"module": "tasks",     "level": "red",    "message": f"{tasks_overdue} overdue task(s)"})
    if renewals_soon:  alerts.append({"module": "subscriptions", "level": "yellow", "message": f"{renewals_soon} subscription(s) renewing within 7 days"})

    return {
        "success": True,
        "data": {
            "personnel_active": personnel_active,
            "agents_running":   agents_running,
            "assets_issues":    assets_issues,
            "low_stock_items":  low_stock,
            "visitors_today":   visitors_today,
            "tasks_overdue":    tasks_overdue,
            "renewals_soon":    renewals_soon,
            "alerts":           alerts
        }
    }


@router.get("/alerts")
def get_alerts(db=Depends(get_db)):
    today = str(date.today())
    alerts = []

    low = db.execute("SELECT name FROM inventory WHERE quantity <= low_threshold").fetchall()
    for r in low:
        alerts.append({"module": "inventory", "level": "red", "item": r["name"]})

    overdue = db.execute("SELECT title FROM tasks WHERE status!='completed' AND due_date < ?", [today]).fetchall()
    for r in overdue:
        alerts.append({"module": "tasks", "level": "red", "item": r["title"]})

    return {"success": True, "data": alerts, "total": len(alerts)}
