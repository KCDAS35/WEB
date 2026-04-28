# HANDOFF: Jagat Sampurna International Yogi Foundation — HQ Mission Control

## Project Identity

**Full Name:** Jagat Sampurna International Yogi Foundation  
**Project Codename:** HQ Mission Control  
**System Type:** Foundation Operating System (FOS)  
**Owner/Director:** To be confirmed with Foundation director  
**Primary Agent Contact:** PlaceinTime AI (Claude / Gemini / OpenAI — Three of Pentacles collaboration)

---

## What This System Is

This is a **Foundation Operating System (FOS)** — an integrated management platform designed so that a person of average intelligence can sit down, open the dashboard, and competently manage every department, asset, living being, and operation of the Jagat Sampurna International Yogi Foundation.

In institutional management terms, this combines:
- **ERP** (Enterprise Resource Planning) — assets, inventory, finances
- **CRM** (Customer/Client Relationship Management) — visitors, clients, appointments
- **HRMS** (Human Resource Management) — personnel and AI agent assignment
- **FMS** (Facility Management System) — physical spaces and equipment
- **AMS** (Association Management System) — memberships and subscriptions
- **MAM** (Media Asset Management) — recordings, screenings, video productions

The closest real-world analogs are monastery/ashram management systems used by established spiritual communities. This system is custom-built for the unique scope of JSIYF.

---

## Vision Statement

The Foundation needs one place — one dashboard — where any trained operator (human or AI) can see the full status of the institution and take action. No department should be invisible. No asset should be untracked. No task should fall through the cracks.

The system must be simple enough for a non-technical person to use daily, and powerful enough that AI agents can be assigned to run entire departments autonomously.

---

## Inventory of Foundation Entities (All Must Be Tracked)

| Category | Items |
|---|---|
| **Personnel** | Staff, volunteers, residents, interns |
| **AI Agents** | Deployed agents, their roles, capabilities, and current tasks |
| **Hardware** | Computers, tablets, phones, printers |
| **Equipment** | Drones, recording equipment, cameras |
| **Furniture** | By room/space |
| **Spaces** | Meditation areas, rest areas, library, interview rooms, screening rooms |
| **Living Beings** | Cats, goldfish, other animals |
| **Consumables** | Foods, medicines, supplies |
| **Visitors** | Guest registry with dates and purpose |
| **Clients** | Active client profiles, history, services rendered |
| **Subscriptions** | Active subscriptions (software, services, platforms) |
| **Financial** | Bank accounts, income streams, expenses |
| **Communications** | Email accounts, web pages, social media handles |
| **Media** | Recordings, video presentations, screenings, interviews |
| **Library** | Books, digital resources, courses |

---

## Core Functional Modules

1. **Dashboard** — Real-time status overview of all modules
2. **Personnel Manager** — Staff roster, role assignment, schedules
3. **AI Agent Console** — Deploy, monitor, and assign tasks to AI agents (including Plex, media automation)
4. **Asset Registry** — Track all physical assets with location, condition, assigned user
5. **Living Beings Registry** — Pets and animals with care schedules
6. **Space Manager** — Rooms and zones, usage schedules, maintenance status
7. **Inventory Manager** — Foods, medicines, consumables with low-stock alerts
8. **Visitor & Client CRM** — Intake, history, appointments, follow-up
9. **Media Production Hub** — Schedule and log interviews, screenings, recordings
10. **Financial Ledger** — Bank accounts, subscriptions, expenses
11. **Communications Hub** — Email accounts, web pages, linked platforms
12. **Library Catalog** — Books, digital resources
13. **Operations Log** — Daily activity log, incident reports
14. **Task Assignment Engine** — Assign any task to any human or AI agent

---

## AI Agent Task Assignments (Agentic Layer)

The following categories of work can be fully delegated to AI agents:

| Agent Role | Capabilities |
|---|---|
| **Media Agent** | Manage Plex library, schedule screenings, tag recordings |
| **Comms Agent** | Monitor email, draft responses, maintain web pages |
| **Inventory Agent** | Track stock levels, generate purchase orders |
| **Scheduling Agent** | Calendar management, visitor appointments |
| **Finance Agent** | Expense tracking, subscription renewal alerts |
| **Research Agent** | Library curation, resource discovery |

---

## Technical Architecture (Recommended)

- **Backend:** Python / FastAPI — REST API, JSON responses
- **Database:** SQLite (development) → PostgreSQL (production)
- **Frontend:** HTML5 + Vanilla JS dashboard (no framework dependency, easy for any agent to modify)
- **Auth:** Simple role-based access (Admin, Operator, Viewer, Agent)
- **API:** RESTful with OpenAPI/Swagger docs auto-generated
- **Deployment:** Local-first (runs on Foundation hardware), optionally exposed via ngrok or Cloudflare Tunnel

---

## Current Status

- [ ] System designed (specs complete — see /specs/)
- [ ] Skeleton backend created (see /skeleton/backend/)
- [ ] Skeleton frontend created (see /skeleton/frontend/)
- [ ] Database schema implemented
- [ ] API endpoints implemented
- [ ] Frontend dashboard implemented
- [ ] AI agent console implemented
- [ ] Deployed on Foundation hardware

---

## Handoff Instructions for Incoming Agents

1. Read this HANDOFF.md completely
2. Read `/specs/functional-spec.md` for full module detail
3. Read `/specs/data-models.md` for all database entities
4. Read `/specs/api-spec.md` for all API endpoints
5. Review `/skeleton/` for the starter code structure
6. Begin implementation starting with the **Asset Registry** and **Personnel Manager** — these are the foundation for all other modules
7. Use FastAPI + SQLite for rapid prototyping; schema is in data-models.md
8. The frontend must remain simple HTML/JS — no React, no npm required

---

## Operator's Manual Philosophy

Every screen must answer: **"What is the status of X, and what do I need to do about it?"**

The operator should never need to search. The system surfaces what needs attention. Color coding: Green = good, Yellow = needs attention, Red = urgent action required.
