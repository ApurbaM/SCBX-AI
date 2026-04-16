-- SCBx CXO dashboard backing store (SQLite)
-- Personas + twin state, catalog datasets, and ontology graph (catalog + CXO journey layer).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS persona (
  persona_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  short_desc TEXT,
  avatar_url TEXT,
  customer_ref TEXT,
  full_name TEXT,
  line_of_work TEXT,
  product_holdings_json TEXT,
  journey_metrics_json TEXT,
  defaults_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS persona_twin (
  persona_id TEXT PRIMARY KEY REFERENCES persona(persona_id) ON DELETE CASCADE,
  state_json TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS catalog_dataset (
  dataset_name TEXT PRIMARY KEY,
  full_name TEXT,
  description TEXT,
  update_frequency TEXT,
  subject_area TEXT
);

CREATE TABLE IF NOT EXISTS ontology_node (
  uri TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  label TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS ontology_edge (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_uri TEXT NOT NULL,
  to_uri TEXT NOT NULL,
  rel TEXT NOT NULL,
  UNIQUE (from_uri, to_uri, rel)
);

CREATE INDEX IF NOT EXISTS idx_edge_from ON ontology_edge(from_uri);
CREATE INDEX IF NOT EXISTS idx_edge_to ON ontology_edge(to_uri);
CREATE INDEX IF NOT EXISTS idx_catalog_subject ON catalog_dataset(subject_area);
