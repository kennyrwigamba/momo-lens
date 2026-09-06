# MoMo Lens

**Team:** Web Artisans

## Project Description

MoMo Lens is a full-stack application that processes Mobile Money (MoMo) SMS
transaction data provided in XML format. It cleans and categorizes the raw
data, loads it into a relational (SQLite) database, and exposes it through a
frontend dashboard for analysis and visualization, showing volumes, totals,
and trends across transaction types.

**Pipeline:** XML SMS export → parse → clean/normalize → categorize → load into SQLite → aggregate → visualize on dashboard.

## Team Members

| Name | GitHub |
|---|---|
| Ishimwe Rwigamba Kenny Louange | [@kennyrwigamba](https://github.com/kennyrwigamba) |
| Kevin Ishimwe | [@kevinishimwe2](https://github.com/kevinishimwe2) |
| Maunice Akaliza | [@Akaliza-ux](https://github.com/Akaliza-ux) |

## System Architecture

High-level architecture diagram: 
[@Link to the architecture diagram](https://app.diagrams.net/#G1VeovJ0P1I-WPy2vZ1r9kVdFE0xaAaCHP#%7B%22pageId%22%3A%22-w0HEG6bdLZIW8pZsZ7u%22%7D)

<img width="334" height="920" alt="MoMo Analytics architecture" src="https://github.com/user-attachments/assets/ac3c7495-b4e6-4dd2-81a7-3778178275a3" />



## Scrum Board

Task board (To Do / In Progress / Done): 

## Project Structure

```
.
├── README.md                         # Setup, run, overview
├── .env.example                      # DATABASE_URL or path to SQLite
├── requirements.txt                  # lxml/ElementTree, dateutil, (FastAPI optional)
├── index.html                        # Dashboard entry (static)
├── web/
│   ├── styles.css                    # Dashboard styling
│   ├── chart_handler.js              # Fetch + render charts/tables
│   └── assets/                       # Images/icons (optional)
├── data/
│   ├── raw/                          # Provided XML input (git-ignored)
│   │   └── momo.xml
│   ├── processed/                    # Cleaned/derived outputs for frontend
│   │   └── dashboard.json            # Aggregates the dashboard reads
│   ├── db.sqlite3                    # SQLite DB file
│   └── logs/
│       ├── etl.log                   # Structured ETL logs
│       └── dead_letter/              # Unparsed/ignored XML snippets
├── etl/
│   ├── __init__.py
│   ├── config.py                     # File paths, thresholds, categories
│   ├── parse_xml.py                  # XML parsing (ElementTree/lxml)
│   ├── clean_normalize.py            # Amounts, dates, phone normalization
│   ├── categorize.py                 # Simple rules for transaction types
│   ├── load_db.py                    # Create tables + upsert to SQLite
│   └── run.py                        # CLI: parse -> clean -> categorize -> load -> export JSON
├── api/                               # Optional (bonus)
│   ├── __init__.py
│   ├── app.py                        # Minimal FastAPI with /transactions, /analytics
│   ├── db.py                         # SQLite connection helpers
│   └── schemas.py                    # Pydantic response models
├── scripts/
│   ├── run_etl.sh                    # python etl/run.py --xml data/raw/momo.xml
│   ├── export_json.sh                # Rebuild data/processed/dashboard.json
│   └── serve_frontend.sh             # python -m http.server 8000 (or Flask static)
└── tests/
    ├── test_parse_xml.py             # Small unit tests
    ├── test_clean_normalize.py
    └── test_categorize.py
```
