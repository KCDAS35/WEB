# Data Models — Jagat Sampurna HQ Mission Control

All entities stored in relational database (SQLite dev / PostgreSQL prod).

---

## Personnel

```sql
personnel (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  role        TEXT,                  -- e.g. "Director", "Cook", "Volunteer"
  type        TEXT,                  -- "staff" | "volunteer" | "resident" | "intern"
  email       TEXT,
  phone       TEXT,
  assigned_to TEXT,                  -- department or space
  status      TEXT DEFAULT "active", -- "active" | "inactive" | "away"
  notes       TEXT,
  joined_on   DATE,
  photo_url   TEXT
)
```

---

## AI Agents

```sql
ai_agents (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,        -- e.g. "MediaAgent-Gemini-1"
  provider      TEXT,                 -- "Claude" | "Gemini" | "OpenAI" | "Other"
  model         TEXT,                 -- e.g. "gemini-2.0-flash"
  role          TEXT,                 -- e.g. "Media Manager", "Comms Agent"
  assigned_to   TEXT,                 -- department or task
  status        TEXT DEFAULT "idle",  -- "idle" | "running" | "paused" | "error"
  api_key_ref   TEXT,                 -- reference to secrets manager, never raw key
  capabilities  TEXT,                 -- JSON array: ["plex", "email", "scheduling"]
  last_active   DATETIME,
  notes         TEXT
)
```

---

## Assets (Hardware & Equipment)

```sql
assets (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,        -- e.g. "Main Recording Drone"
  category      TEXT,                 -- "computer" | "drone" | "camera" | "furniture" | "instrument"
  brand         TEXT,
  model         TEXT,
  serial_number TEXT,
  location      TEXT,                 -- links to spaces.id
  assigned_to   INTEGER,              -- links to personnel.id (nullable)
  condition     TEXT DEFAULT "good",  -- "good" | "fair" | "needs_repair" | "retired"
  purchase_date DATE,
  purchase_cost REAL,
  notes         TEXT
)
```

---

## Spaces (Rooms & Zones)

```sql
spaces (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,          -- e.g. "Meditation Hall A"
  type        TEXT,                   -- "meditation" | "rest" | "library" | "kitchen" | "office" | "screening" | "interview" | "common"
  capacity    INTEGER,
  status      TEXT DEFAULT "open",    -- "open" | "occupied" | "reserved" | "maintenance"
  notes       TEXT
)
```

---

## Living Beings (Pets & Animals)

```sql
living_beings (
  id            INTEGER PRIMARY KEY,
  name          TEXT,                 -- e.g. "Luna"
  species       TEXT,                 -- "cat" | "goldfish" | "bird" | "other"
  breed         TEXT,
  caretaker_id  INTEGER,              -- links to personnel.id
  location      TEXT,                 -- links to spaces.id
  health_status TEXT DEFAULT "good",
  last_vet_date DATE,
  notes         TEXT,
  photo_url     TEXT
)
```

---

## Inventory (Consumables)

```sql
inventory (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,        -- e.g. "Brown Rice"
  category      TEXT,                 -- "food" | "medicine" | "cleaning" | "office" | "other"
  quantity      REAL,
  unit          TEXT,                 -- "kg" | "liters" | "units" | "boxes"
  low_threshold REAL,                 -- alert when quantity drops below this
  location      TEXT,                 -- links to spaces.id
  expiry_date   DATE,
  supplier      TEXT,
  notes         TEXT
)
```

---

## Visitors

```sql
visitors (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  purpose     TEXT,                   -- "retreat" | "interview" | "screening" | "consultation" | "other"
  arrival     DATETIME,
  departure   DATETIME,
  host_id     INTEGER,                -- links to personnel.id
  status      TEXT DEFAULT "pending",-- "pending" | "arrived" | "departed" | "cancelled"
  notes       TEXT,
  contact     TEXT
)
```

---

## Clients

```sql
clients (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL,
  email           TEXT,
  phone           TEXT,
  services        TEXT,               -- JSON array of services received
  subscription_id INTEGER,            -- links to subscriptions.id
  assigned_to_id  INTEGER,            -- links to personnel.id
  status          TEXT DEFAULT "active",
  joined_on       DATE,
  notes           TEXT
)
```

---

## Subscriptions

```sql
subscriptions (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL,      -- e.g. "Plex Pass", "Anthropic API", "Google Workspace"
  provider        TEXT,
  cost            REAL,
  billing_cycle   TEXT,               -- "monthly" | "annual" | "one-time"
  renewal_date    DATE,
  assigned_to_id  INTEGER,            -- links to personnel or ai_agents
  status          TEXT DEFAULT "active",
  notes           TEXT
)
```

---

## Financial Accounts

```sql
financial_accounts (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,        -- e.g. "Foundation Main Account"
  institution   TEXT,                 -- bank or payment processor name
  account_type  TEXT,                 -- "checking" | "savings" | "paypal" | "crypto" | "other"
  currency      TEXT DEFAULT "USD",
  balance       REAL,
  last_updated  DATETIME,
  notes         TEXT
)
```

---

## Communications

```sql
communications (
  id          INTEGER PRIMARY KEY,
  type        TEXT,                   -- "email" | "webpage" | "social" | "phone"
  label       TEXT,                   -- e.g. "Foundation Main Email"
  address     TEXT,                   -- email address, URL, handle, or phone number
  platform    TEXT,                   -- "Gmail" | "GitHub Pages" | "Instagram" | etc.
  managed_by  INTEGER,                -- links to personnel.id or ai_agents.id
  status      TEXT DEFAULT "active",
  notes       TEXT
)
```

---

## Media Library

```sql
media (
  id            INTEGER PRIMARY KEY,
  title         TEXT NOT NULL,
  type          TEXT,                 -- "recording" | "interview" | "presentation" | "screening" | "film"
  format        TEXT,                 -- "video" | "audio" | "pdf" | "image"
  file_path     TEXT,                 -- local path or URL
  plex_id       TEXT,                 -- Plex library ID if applicable
  recorded_on   DATE,
  produced_by   INTEGER,              -- links to personnel.id
  participants  TEXT,                 -- JSON array of names
  status        TEXT DEFAULT "draft", -- "draft" | "published" | "archived"
  tags          TEXT,                 -- comma-separated tags
  notes         TEXT
)
```

---

## Library (Books & Resources)

```sql
library (
  id          INTEGER PRIMARY KEY,
  title       TEXT NOT NULL,
  author      TEXT,
  category    TEXT,                   -- "spiritual" | "technical" | "medical" | "art" | "general"
  format      TEXT,                   -- "physical" | "ebook" | "audio" | "course" | "video"
  location    TEXT,                   -- shelf reference or URL
  checked_out_by INTEGER,             -- links to personnel.id
  notes       TEXT
)
```

---

## Tasks

```sql
tasks (
  id            INTEGER PRIMARY KEY,
  title         TEXT NOT NULL,
  description   TEXT,
  assigned_to   TEXT,                 -- "human:<personnel.id>" or "agent:<ai_agents.id>"
  priority      TEXT DEFAULT "normal",-- "low" | "normal" | "high" | "urgent"
  status        TEXT DEFAULT "pending",-- "pending" | "in_progress" | "completed" | "cancelled"
  due_date      DATE,
  created_on    DATETIME,
  completed_on  DATETIME,
  notes         TEXT
)
```

---

## Operations Log

```sql
operations_log (
  id          INTEGER PRIMARY KEY,
  timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
  logged_by   TEXT,                   -- name or "system"
  module      TEXT,                   -- which module this log entry relates to
  action      TEXT,
  details     TEXT
)
```
