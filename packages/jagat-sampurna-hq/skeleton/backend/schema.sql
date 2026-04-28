-- Jagat Sampurna HQ Mission Control — Database Schema

CREATE TABLE IF NOT EXISTS personnel (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL,
  role        TEXT,
  type        TEXT DEFAULT 'staff',
  email       TEXT,
  phone       TEXT,
  assigned_to TEXT,
  status      TEXT DEFAULT 'active',
  notes       TEXT,
  joined_on   DATE,
  photo_url   TEXT
);

CREATE TABLE IF NOT EXISTS ai_agents (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  provider      TEXT,
  model         TEXT,
  role          TEXT,
  assigned_to   TEXT,
  status        TEXT DEFAULT 'idle',
  api_key_ref   TEXT,
  capabilities  TEXT,
  last_active   DATETIME,
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS assets (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  category      TEXT,
  brand         TEXT,
  model         TEXT,
  serial_number TEXT,
  location      TEXT,
  assigned_to   INTEGER REFERENCES personnel(id),
  condition     TEXT DEFAULT 'good',
  purchase_date DATE,
  purchase_cost REAL,
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS spaces (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  name     TEXT NOT NULL,
  type     TEXT,
  capacity INTEGER,
  status   TEXT DEFAULT 'open',
  notes    TEXT
);

CREATE TABLE IF NOT EXISTS living_beings (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT,
  species       TEXT,
  breed         TEXT,
  caretaker_id  INTEGER REFERENCES personnel(id),
  location      TEXT,
  health_status TEXT DEFAULT 'good',
  last_vet_date DATE,
  notes         TEXT,
  photo_url     TEXT
);

CREATE TABLE IF NOT EXISTS inventory (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  category      TEXT,
  quantity      REAL DEFAULT 0,
  unit          TEXT,
  low_threshold REAL DEFAULT 0,
  location      TEXT,
  expiry_date   DATE,
  supplier      TEXT,
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS visitors (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL,
  purpose     TEXT,
  arrival     DATETIME,
  departure   DATETIME,
  host_id     INTEGER REFERENCES personnel(id),
  status      TEXT DEFAULT 'pending',
  notes       TEXT,
  contact     TEXT
);

CREATE TABLE IF NOT EXISTS clients (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  name            TEXT NOT NULL,
  email           TEXT,
  phone           TEXT,
  services        TEXT,
  subscription_id INTEGER REFERENCES subscriptions(id),
  assigned_to_id  INTEGER REFERENCES personnel(id),
  status          TEXT DEFAULT 'active',
  joined_on       DATE,
  notes           TEXT
);

CREATE TABLE IF NOT EXISTS subscriptions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  provider      TEXT,
  cost          REAL,
  billing_cycle TEXT,
  renewal_date  DATE,
  assigned_to_id INTEGER,
  status        TEXT DEFAULT 'active',
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS financial_accounts (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT NOT NULL,
  institution  TEXT,
  account_type TEXT,
  currency     TEXT DEFAULT 'USD',
  balance      REAL DEFAULT 0,
  last_updated DATETIME,
  notes        TEXT
);

CREATE TABLE IF NOT EXISTS communications (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  type       TEXT,
  label      TEXT,
  address    TEXT,
  platform   TEXT,
  managed_by INTEGER,
  status     TEXT DEFAULT 'active',
  notes      TEXT
);

CREATE TABLE IF NOT EXISTS media (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  title         TEXT NOT NULL,
  type          TEXT,
  format        TEXT,
  file_path     TEXT,
  plex_id       TEXT,
  recorded_on   DATE,
  produced_by   INTEGER REFERENCES personnel(id),
  participants  TEXT,
  status        TEXT DEFAULT 'draft',
  tags          TEXT,
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS library (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  author         TEXT,
  category       TEXT,
  format         TEXT,
  location       TEXT,
  checked_out_by INTEGER REFERENCES personnel(id),
  notes          TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  description  TEXT,
  assigned_to  TEXT,
  priority     TEXT DEFAULT 'normal',
  status       TEXT DEFAULT 'pending',
  due_date     DATE,
  created_on   DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_on DATETIME,
  notes        TEXT
);

CREATE TABLE IF NOT EXISTS operations_log (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  logged_by TEXT,
  module    TEXT,
  action    TEXT,
  details   TEXT
);
