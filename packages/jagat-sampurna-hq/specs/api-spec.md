# API Specification — Jagat Sampurna HQ Mission Control

Base URL: `http://localhost:8000/api/v1`  
Format: JSON  
Auth: Bearer token (role-based: admin | operator | viewer | agent)

Auto-generated Swagger docs available at: `http://localhost:8000/docs`

---

## Standard Response Envelope

```json
{
  "success": true,
  "data": { ... },
  "message": "Human-readable status",
  "total": 42
}
```

---

## Endpoints by Module

### Personnel

| Method | Endpoint | Description |
|---|---|---|
| GET | `/personnel` | List all personnel (filter: ?status=active&type=staff) |
| GET | `/personnel/{id}` | Get one person with full details |
| POST | `/personnel` | Create personnel record |
| PUT | `/personnel/{id}` | Update personnel record |
| DELETE | `/personnel/{id}` | Deactivate (soft delete) |
| POST | `/personnel/{id}/assign` | Assign to department or space |

### AI Agents

| Method | Endpoint | Description |
|---|---|---|
| GET | `/agents` | List all AI agents and their status |
| GET | `/agents/{id}` | Get agent details and current task |
| POST | `/agents` | Register a new AI agent |
| PUT | `/agents/{id}` | Update agent record |
| POST | `/agents/{id}/assign` | Assign agent to a task or department |
| POST | `/agents/{id}/pause` | Pause agent |
| POST | `/agents/{id}/resume` | Resume agent |
| GET | `/agents/{id}/log` | Get agent activity log |

### Assets

| Method | Endpoint | Description |
|---|---|---|
| GET | `/assets` | List all assets (filter: ?category=drone&condition=good) |
| GET | `/assets/{id}` | Get asset details |
| POST | `/assets` | Register new asset |
| PUT | `/assets/{id}` | Update asset |
| POST | `/assets/{id}/assign` | Assign asset to person or space |
| GET | `/assets/report` | Full asset report |

### Spaces

| Method | Endpoint | Description |
|---|---|---|
| GET | `/spaces` | List all spaces with current status |
| GET | `/spaces/{id}` | Get space details and occupants |
| POST | `/spaces` | Create space |
| PUT | `/spaces/{id}` | Update space |
| POST | `/spaces/{id}/reserve` | Reserve a space |
| POST | `/spaces/{id}/release` | Release a reservation |

### Living Beings

| Method | Endpoint | Description |
|---|---|---|
| GET | `/beings` | List all animals and pets |
| GET | `/beings/{id}` | Get animal details |
| POST | `/beings` | Register animal |
| PUT | `/beings/{id}` | Update record |
| POST | `/beings/{id}/care` | Log a care event (feeding, vet visit) |

### Inventory

| Method | Endpoint | Description |
|---|---|---|
| GET | `/inventory` | List all inventory (filter: ?category=food&low_stock=true) |
| GET | `/inventory/{id}` | Get item details |
| POST | `/inventory` | Add inventory item |
| PUT | `/inventory/{id}` | Update item |
| POST | `/inventory/{id}/adjust` | Adjust quantity (use/restock) |
| GET | `/inventory/alerts` | Items below low_threshold |

### Visitors

| Method | Endpoint | Description |
|---|---|---|
| GET | `/visitors` | List visitors (filter: ?status=arrived) |
| GET | `/visitors/{id}` | Get visitor details |
| POST | `/visitors` | Register visitor |
| PUT | `/visitors/{id}` | Update visitor record |
| POST | `/visitors/{id}/check-in` | Mark as arrived |
| POST | `/visitors/{id}/check-out` | Mark as departed |

### Clients

| Method | Endpoint | Description |
|---|---|---|
| GET | `/clients` | List all clients |
| GET | `/clients/{id}` | Get client profile and history |
| POST | `/clients` | Create client record |
| PUT | `/clients/{id}` | Update client |
| POST | `/clients/{id}/assign` | Assign to staff member |
| GET | `/clients/{id}/history` | Full service history |

### Subscriptions

| Method | Endpoint | Description |
|---|---|---|
| GET | `/subscriptions` | List all subscriptions |
| POST | `/subscriptions` | Add subscription |
| PUT | `/subscriptions/{id}` | Update subscription |
| DELETE | `/subscriptions/{id}` | Cancel subscription |
| GET | `/subscriptions/renewals` | Subscriptions due within 30 days |

### Financial

| Method | Endpoint | Description |
|---|---|---|
| GET | `/finance/accounts` | List all financial accounts |
| GET | `/finance/accounts/{id}` | Account details |
| POST | `/finance/accounts` | Add account |
| PUT | `/finance/accounts/{id}` | Update balance and details |
| GET | `/finance/summary` | Total assets across all accounts |

### Communications

| Method | Endpoint | Description |
|---|---|---|
| GET | `/comms` | List all communication channels |
| POST | `/comms` | Register email/page/social |
| PUT | `/comms/{id}` | Update channel |
| POST | `/comms/{id}/assign` | Assign channel to agent or person |

### Media

| Method | Endpoint | Description |
|---|---|---|
| GET | `/media` | List media library (filter: ?type=recording) |
| GET | `/media/{id}` | Get media details |
| POST | `/media` | Register media item |
| PUT | `/media/{id}` | Update metadata |
| POST | `/media/{id}/publish` | Mark as published |
| GET | `/media/plex` | List Plex-linked media |

### Library

| Method | Endpoint | Description |
|---|---|---|
| GET | `/library` | List all library resources |
| POST | `/library` | Add resource |
| PUT | `/library/{id}` | Update resource |
| POST | `/library/{id}/checkout` | Check out to a person |
| POST | `/library/{id}/return` | Return resource |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tasks` | List all tasks (filter: ?status=pending&assigned_to=agent) |
| GET | `/tasks/{id}` | Get task details |
| POST | `/tasks` | Create task |
| PUT | `/tasks/{id}` | Update task |
| POST | `/tasks/{id}/complete` | Mark task complete |
| POST | `/tasks/{id}/assign` | Reassign task |

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard` | Full status summary across all modules |
| GET | `/dashboard/alerts` | All red/yellow status items |
| GET | `/dashboard/today` | Today's visitors, tasks, and events |

### Operations Log

| Method | Endpoint | Description |
|---|---|---|
| GET | `/log` | Paginated operations log |
| POST | `/log` | Add log entry |

---

## Plex Integration (via Agent)

The Media Agent connects to Plex using the Plex API:

```
POST /agents/plex/scan     — Trigger library scan
GET  /agents/plex/library  — List all Plex content synced to HQ
POST /agents/plex/schedule — Schedule a screening
```

Plex API base: `http://<plex-server>:32400`  
Auth: `X-Plex-Token` header (stored in environment, never in code)
