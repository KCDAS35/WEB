# Functional Specification — Jagat Sampurna HQ Mission Control

## System Purpose

A single-operator dashboard that allows one human (or AI agent) to maintain full situational awareness of the Jagat Sampurna International Yogi Foundation and take corrective action on any department without technical expertise.

Design principle: **If it exists in the Foundation, it exists in the system.**

---

## Module 1 — Dashboard (Home Screen)

**What it shows:**
- Total headcount (personnel online today)
- Number of active AI agents and their current tasks
- Assets needing maintenance (condition != "good")
- Inventory alerts (items below threshold)
- Visitors expected today
- Subscriptions renewing within 7 days
- Tasks overdue
- Media scheduled for today

**Behavior:**
- Auto-refreshes every 60 seconds
- Color-coded tiles: green/yellow/red
- Each tile is clickable — links to the relevant module
- No login required on local network; Bearer token required for remote access

---

## Module 2 — Personnel Manager

**What it shows:**
- Full roster with photos, roles, and current assignment
- Filter by: type (staff/volunteer/resident/intern), status, department

**Actions:**
- Add / edit / deactivate a person
- Assign to a space or department
- View their current tasks
- Log attendance or absence

**Operator use case:** "I need to know who is in the meditation hall right now and who is unassigned today."

---

## Module 3 — AI Agent Console

**What it shows:**
- All registered AI agents, their provider (Claude/Gemini/OpenAI), model, and status
- Current task and last active time
- Activity log per agent

**Actions:**
- Register a new agent (name, provider, role, capabilities)
- Assign agent to a task or department
- Pause / resume an agent
- View agent log

**Key capability:** The operator can type a task description and assign it to any available agent. The system logs the assignment and tracks completion.

**Plex integration:** The Media Agent can be assigned to manage the Plex library, schedule screenings, and organize recordings.

---

## Module 4 — Asset Registry

**What it shows:**
- All physical assets: computers, drones, cameras, furniture, instruments
- Filter by: category, location, condition, assigned person

**Actions:**
- Register new asset
- Update condition
- Assign/unassign to person or space
- Mark for repair or retirement
- Generate asset report (PDF-ready)

**Operator use case:** "Which drones are operational and who has them?"

---

## Module 5 — Living Beings Registry

**What it shows:**
- All animals (cats, goldfish, others) with photos, names, caretaker, and health status
- Care schedule reminders

**Actions:**
- Add / edit animal record
- Log care events (feeding, vet visit, medication)
- Assign caretaker

**Operator use case:** "When was Luna the cat last seen by the vet? Who feeds the goldfish?"

---

## Module 6 — Space Manager

**What it shows:**
- All rooms and zones with current status (open/occupied/reserved/maintenance)
- Who/what is in each space
- Upcoming reservations

**Actions:**
- Create / edit space
- Reserve a space for a time block
- Release reservation
- Mark for maintenance

**Operator use case:** "I need Meditation Hall B for a screening at 7pm. Is it free?"

---

## Module 7 — Inventory Manager

**What it shows:**
- All consumables: food, medicine, cleaning supplies, office supplies
- Quantity, unit, expiry, and low-stock status

**Actions:**
- Add item
- Adjust quantity (use or restock)
- Set low-threshold for alerts
- Log supplier

**Operator use case:** "We're low on rice and the medicine cabinet needs restocking."

---

## Module 8 — Visitor & Client CRM

**Visitors tab:**
- Guest registry with arrival/departure dates and purpose
- Check in / check out visitors
- Assign host from personnel

**Clients tab:**
- Full client profiles with service history
- Assign to staff member
- Link to active subscription

**Operator use case:** "A new visitor is arriving for a retreat. Log them and assign them to a staff member."

---

## Module 9 — Media Production Hub

**What it shows:**
- All recordings, interviews, video presentations, screenings
- Status: draft / published / archived
- Plex-linked items flagged separately

**Actions:**
- Register a new media item
- Schedule a screening (links to Space Manager)
- Assign production to staff or agent
- Mark published
- Sync with Plex

**Operator use case:** "We recorded an interview yesterday. Log it, tag it, and have the Media Agent add it to Plex."

---

## Module 10 — Financial Ledger

**What it shows:**
- All bank accounts and digital wallets with current balance
- Total foundation assets
- Active subscriptions and their costs
- Upcoming subscription renewals

**Actions:**
- Add / update account
- Update balance
- Add/cancel subscription
- View renewal calendar

**Operator use case:** "What's our total liquid balance across all accounts? What subscriptions are renewing this month?"

---

## Module 11 — Communications Hub

**What it shows:**
- All email accounts, websites, social media handles
- Which agent or person manages each channel

**Actions:**
- Register channel
- Assign to agent or person
- Mark inactive

**Operator use case:** "Assign the foundation email to the Comms Agent."

---

## Module 12 — Library Catalog

**What it shows:**
- All books and digital resources
- Filter by category, format, availability

**Actions:**
- Add resource
- Check out to a person
- Mark returned

---

## Module 13 — Task Assignment Engine

**What it shows:**
- All tasks with status, priority, assignee, due date

**Actions:**
- Create task
- Assign to any human or AI agent
- Track completion
- Set priority and due date

**Operator use case:** "Assign the weekly inventory check to the Inventory Agent. Set priority to high, due Friday."

---

## Module 14 — Operations Log

- Timestamped log of all actions taken in the system
- Filterable by module, date range, user
- Exportable as CSV

---

## Role-Based Access

| Role | Capabilities |
|---|---|
| **Admin** | Full access, can create/delete records, manage agents |
| **Operator** | Can view all, create and update most records |
| **Viewer** | Read-only dashboard access |
| **Agent** | API-only access scoped to assigned modules |

---

## Deployment

- Runs locally on Foundation hardware (no cloud dependency)
- Optional remote access via Cloudflare Tunnel or ngrok
- Single command startup: `python main.py`
- SQLite database — no separate database server required
- Data lives in `foundation.db` — back up regularly
