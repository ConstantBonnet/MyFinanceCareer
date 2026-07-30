from __future__ import annotations

import base64
import calendar
import html
import sqlite3
import unicodedata
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pandas as pd
import streamlit as st


APP_TITLE = "My Finance Career"
DB_PATH = Path("mfc_data.sqlite3")
LOGO_PATH = Path("static/logo_mark.png")

FIELDS = [
    "Investment Banking",
    "Private Equity",
    "Asset Management",
    "Markets",
    "Corporate Finance",
    "Audit & Transaction Services",
    "Financial Advisory",
]
PRIORITIES = ["Haute", "Moyenne", "Basse"]
PRIORITY_WEIGHT = {"Haute": 3, "Moyenne": 2, "Basse": 1}
RESOURCE_CATEGORIES = ["CV", "Lettre de motivation", "Modele", "Preparation technique", "Cours", "Document Drive", "Site utile"]
EVENT_TYPES = ["Deadline", "Entretien", "Test", "Networking", "Relance", "Tache"]
GOAL_STATUSES = ["En cours", "En pause", "Termine"]
NETWORK_PROFESSIONS = [
    "M&A / Investment Banking",
    "Private Equity",
    "Transaction Services",
    "Valuation",
    "Audit",
    "Asset Management",
    "Markets",
    "Corporate Finance",
    "Financial Advisory",
    "Recruitment / HR",
    "Alumni / School",
    "Other",
]
NETWORK_STATUSES = ["A contacter", "Contacte", "A relancer", "Echange planifie", "Rencontre", "A remercier", "Dormant"]
NETWORK_CHANNELS = ["LinkedIn", "Email", "Call", "Coffee chat", "Event", "Alumni platform", "Referral", "Other"]
SENIORITY_LEVELS = ["Student", "Intern", "Analyst", "Associate", "Manager", "VP", "Director", "Partner", "Recruiter", "Other"]
TABLES = ["resources", "events", "goals", "contacts"]
PAGES = ["Objectifs", "Calendrier", "Bibliotheque", "Reseau"]
NAV_LABELS = {
    "Objectifs": "Objectifs",
    "Calendrier": "Calendrier",
    "Bibliotheque": "Bibliotheque",
    "Reseau": "Reseau",
}
MONTH_NAMES = [
    "",
    "Janvier",
    "Fevrier",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Aout",
    "Septembre",
    "Octobre",
    "Novembre",
    "Decembre",
]
WEEKDAY_LABELS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_sql(sql: str, values: tuple[Any, ...] = ()) -> None:
    with closing(connect()) as conn:
        conn.execute(sql, values)
        conn.commit()


def read_df(sql: str, values: tuple[Any, ...] = ()) -> pd.DataFrame:
    with closing(connect()) as conn:
        return pd.read_sql_query(sql, conn, params=values)


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db() -> None:
    with closing(connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                field TEXT,
                tags TEXT,
                link TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_date TEXT NOT NULL,
                related_company TEXT,
                priority TEXT NOT NULL,
                notes TEXT,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                field TEXT,
                due_date TEXT,
                priority TEXT DEFAULT 'Moyenne',
                progress INTEGER NOT NULL,
                status TEXT NOT NULL,
                next_step TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                role TEXT,
                profession_group TEXT DEFAULT 'Other',
                seniority TEXT,
                target_role TEXT,
                relation_type TEXT,
                status TEXT DEFAULT 'A contacter',
                source TEXT,
                contact_channel TEXT,
                city TEXT,
                priority TEXT DEFAULT 'Moyenne',
                linkedin TEXT,
                email TEXT,
                last_interaction TEXT,
                next_follow_up TEXT,
                associated_company TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        ensure_column(conn, "contacts", "profession_group", "TEXT DEFAULT 'Other'")
        ensure_column(conn, "contacts", "seniority", "TEXT")
        ensure_column(conn, "contacts", "target_role", "TEXT")
        ensure_column(conn, "contacts", "status", "TEXT DEFAULT 'A contacter'")
        ensure_column(conn, "contacts", "source", "TEXT")
        ensure_column(conn, "contacts", "contact_channel", "TEXT")
        ensure_column(conn, "contacts", "city", "TEXT")
        ensure_column(conn, "contacts", "priority", "TEXT DEFAULT 'Moyenne'")
        ensure_column(conn, "goals", "priority", "TEXT DEFAULT 'Moyenne'")
        conn.execute(
            """
            UPDATE goals
            SET title = 'Finaliser le dossier M&A',
                next_step = 'Relire CV, lettre et fiche technique'
            WHERE title = 'Obtenir un stage M&A a Paris'
              AND next_step = 'Envoyer 5 candidatures ciblees'
            """
        )
        conn.execute(
            """
            UPDATE contacts
            SET notes = 'Conseils utiles sur les messages courts, le one pager et les prises de contact ciblees.'
            WHERE name = 'Luigi Cazalis'
              AND notes = 'Conseils utiles sur les messages courts, le one pager et les candidatures spontanees.'
            """
        )
        conn.commit()


def table_is_empty(table: str) -> bool:
    with closing(connect()) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


def seed_demo() -> None:
    if not table_is_empty("goals"):
        return
    today = date.today()
    now = datetime.utcnow().isoformat(timespec="seconds")
    with closing(connect()) as conn:
        conn.executemany(
            "INSERT INTO resources (title, category, field, tags, link, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("CV Finance - version M&A", "CV", "Investment Banking", "cv, m&a, paris", "https://drive.google.com/", "Version orientee transaction, valorisation et experience deal.", now),
                ("Questions techniques finance", "Preparation technique", "Investment Banking", "valuation, accounting, technicals", "https://www.wallstreetprep.com/", "Support de revision pour entretiens M&A et PE.", now),
                ("Liste alumni finance", "Site utile", "Financial Advisory", "networking, alumni", "https://www.linkedin.com/", "Base de travail pour les prises de contact ciblees.", now),
                ("Modele de lettre PE", "Lettre de motivation", "Private Equity", "cover letter, pe", "https://drive.google.com/", "Structure courte pour dossiers private equity.", now),
            ],
        )
        conn.executemany(
            "INSERT INTO events (title, event_type, event_date, related_company, priority, notes, done, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Entretien Rothschild", "Entretien", (today + timedelta(days=3)).isoformat(), "Rothschild & Co", "Haute", "Reviser DCF, comparables et deals recents.", 0, now),
                ("Relance Amundi", "Relance", (today + timedelta(days=6)).isoformat(), "Amundi", "Moyenne", "Message court et professionnel.", 0, now),
                ("Deadline Ardian", "Deadline", (today + timedelta(days=7)).isoformat(), "Ardian", "Haute", "Envoyer CV et lettre adaptee.", 0, now),
            ],
        )
        conn.executemany(
            "INSERT INTO goals (title, field, due_date, priority, progress, status, next_step, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Finaliser le dossier M&A", "Investment Banking", (today + timedelta(days=10)).isoformat(), "Haute", 45, "En cours", "Relire CV, lettre et fiche technique", "Priorite aux boutiques et banques avec fort dealflow.", now),
                ("Contacter 10 alumni en finance", "Financial Advisory", (today + timedelta(days=21)).isoformat(), "Moyenne", 30, "En cours", "Identifier 3 anciens en PE", "Suivre les reponses dans Reseau.", now),
            ],
        )
        conn.executemany(
            """
            INSERT INTO contacts (
                name, company, role, profession_group, seniority, target_role, relation_type,
                status, source, contact_channel, city, priority, linkedin, email, last_interaction,
                next_follow_up, associated_company, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("Claire Martin", "Rothschild & Co", "Associate", "M&A / Investment Banking", "Associate", "M&A Intern", "Alumni", "A relancer", "Alumni school", "LinkedIn", "Paris", "Haute", "https://www.linkedin.com/", "", (today - timedelta(days=2)).isoformat(), (today + timedelta(days=5)).isoformat(), "Rothschild & Co", "Conseils sur les entretiens techniques.", now),
                ("Marc Dubois", "PwC", "Manager TS", "Transaction Services", "Manager", "TS Intern", "Recruteur", "Echange planifie", "Event", "Coffee chat", "Paris", "Moyenne", "https://www.linkedin.com/", "", (today - timedelta(days=6)).isoformat(), (today + timedelta(days=4)).isoformat(), "PwC", "Contact principal pour l'offre TS.", now),
                ("Luigi Cazalis", "Clairfield", "M&A Intern", "M&A / Investment Banking", "Intern", "Boutique M&A", "Contact LinkedIn", "Contacte", "LinkedIn search", "Call", "Paris", "Haute", "https://www.linkedin.com/", "", (today - timedelta(days=8)).isoformat(), (today + timedelta(days=9)).isoformat(), "Clairfield", "Conseils utiles sur les messages courts, le one pager et les prises de contact ciblees.", now),
            ],
        )
        conn.commit()


def resources_df() -> pd.DataFrame:
    return read_df("SELECT * FROM resources ORDER BY created_at DESC, id DESC")


def events_df() -> pd.DataFrame:
    data = read_df("SELECT * FROM events ORDER BY event_date ASC, id DESC")
    if data.empty:
        return data
    data["event_day"] = data["event_date"].apply(parse_day)
    data["days_left"] = data["event_day"].apply(lambda item: (item - date.today()).days if item else None)
    return data


def goals_df() -> pd.DataFrame:
    data = read_df("SELECT * FROM goals ORDER BY due_date ASC, id DESC")
    if data.empty:
        return data
    data = data.copy()
    if "priority" not in data.columns:
        data["priority"] = "Moyenne"
    data["priority"] = data["priority"].fillna("Moyenne").replace("", "Moyenne")
    data["due_day"] = data["due_date"].apply(parse_day)
    data["days_left"] = data["due_day"].apply(lambda item: (item - date.today()).days if item else None)
    data["priority_score"] = data["priority"].map(PRIORITY_WEIGHT).fillna(2).astype(int)
    data["status_score"] = data["status"].map({"En cours": 0, "En pause": 1, "Termine": 2}).fillna(1).astype(int)
    return data.sort_values(["status_score", "priority_score", "days_left", "id"], ascending=[True, False, True, False])


def contacts_df() -> pd.DataFrame:
    data = read_df("SELECT * FROM contacts ORDER BY next_follow_up ASC, id DESC")
    if data.empty:
        return data
    data = data.copy()
    for column, default in {
        "profession_group": "Other",
        "status": "A contacter",
        "priority": "Moyenne",
        "contact_channel": "Other",
        "seniority": "",
        "target_role": "",
        "source": "",
        "city": "",
    }.items():
        if column not in data.columns:
            data[column] = default
        data[column] = data[column].fillna(default).replace("", default if column in {"profession_group", "status", "priority", "contact_channel"} else "")
    data["follow_day"] = data["next_follow_up"].apply(parse_day)
    data["days_left"] = data["follow_day"].apply(lambda item: (item - date.today()).days if item else None)
    data["network_score"] = data.apply(contact_score, axis=1)
    return data.sort_values(["network_score", "days_left", "id"], ascending=[False, True, False])


def contact_score(row: pd.Series) -> int:
    score = PRIORITY_WEIGHT.get(row.get("priority"), 2) * 20
    days_left = row.get("days_left")
    if pd.notna(days_left):
        if days_left < 0:
            score += 45
        elif days_left <= 3:
            score += 30
        elif days_left <= 7:
            score += 18
        elif days_left <= 14:
            score += 8
    if row.get("status") in {"A relancer", "A remercier"}:
        score += 25
    elif row.get("status") == "Echange planifie":
        score += 12
    elif row.get("status") == "Dormant":
        score -= 20
    return score


def strip_accents(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower().strip()


def infer_profession_group(*values: Any) -> str:
    text = " ".join(strip_accents(value) for value in values)
    if any(token in text for token in ["m&a", "mergers", "acquisition", "investment banking", "ibd"]):
        return "M&A / Investment Banking"
    if "private equity" in text or "pe " in f"{text} ":
        return "Private Equity"
    if "transaction" in text or " ts" in f" {text}" or "financial due diligence" in text:
        return "Transaction Services"
    if "valuation" in text or "valo" in text:
        return "Valuation"
    if "audit" in text:
        return "Audit"
    if "asset management" in text or "portfolio" in text or "gestion d'actifs" in text:
        return "Asset Management"
    if "markets" in text or "trading" in text or "sales" in text:
        return "Markets"
    if "corporate finance" in text:
        return "Corporate Finance"
    if "recruit" in text or "hr" in text or "talent" in text:
        return "Recruitment / HR"
    if "alumni" in text or "ecole" in text:
        return "Alumni / School"
    if "advisory" in text or "conseil" in text:
        return "Financial Advisory"
    return "Other"


def normalize_import_columns(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data
    raw = data.dropna(how="all").copy()
    header_index = None
    for idx, row in raw.iterrows():
        row_text = " ".join(strip_accents(value) for value in row.tolist())
        if ("prenom" in row_text or "name" in row_text) and ("entreprise" in row_text or "company" in row_text):
            header_index = idx
            break
    if header_index is not None:
        headers = [strip_accents(value).replace(" ", "_") or f"column_{i}" for i, value in enumerate(raw.loc[header_index].tolist())]
        raw = raw.loc[header_index + 1 :].copy()
        raw.columns = headers
    else:
        raw.columns = [strip_accents(column).replace(" ", "_") for column in raw.columns]
    aliases = {
        "first_name": ["prenom", "first_name", "firstname"],
        "last_name": ["nom", "last_name", "lastname"],
        "name": ["name", "personne"],
        "role": ["position", "poste", "role", "titre"],
        "company": ["entreprise", "company", "societe"],
        "linkedin": ["lien", "linkedin", "link", "url"],
        "notes": ["note", "notes", "commentaire"],
        "email": ["contact", "email", "telephone", "phone"],
    }
    normalized = pd.DataFrame()
    for target, names in aliases.items():
        match = next((name for name in names if name in raw.columns), None)
        normalized[target] = raw[match] if match else ""
    normalized = normalized.fillna("")
    normalized["name"] = normalized.apply(lambda row: " ".join(part for part in [str(row["first_name"]).strip(), str(row["last_name"]).strip()] if part) or str(row["name"]).strip(), axis=1)
    normalized["profession_group"] = normalized.apply(lambda row: infer_profession_group(row["role"], row["company"], row["notes"]), axis=1)
    return normalized[normalized["name"].astype(str).str.strip() != ""]


def parse_day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def format_day(value: Any) -> str:
    parsed = parse_day(value)
    return parsed.strftime("%d/%m/%Y") if parsed else "-"


def escape(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def days_text(value: Any) -> str:
    parsed = parse_day(value)
    if not parsed:
        return "Date a definir"
    delta = (parsed - date.today()).days
    if delta < 0:
        return f"En retard de {abs(delta)} j"
    if delta == 0:
        return "Aujourd'hui"
    if delta == 1:
        return "Demain"
    return f"Dans {delta} j"


def filter_rows(data: pd.DataFrame, query: str) -> pd.DataFrame:
    if data.empty or not query:
        return data
    needle = query.lower()
    return data[data.apply(lambda row: needle in " ".join(row.astype(str)).lower(), axis=1)]


def logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def setup_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":chart_with_upwards_trend:", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(
        """
        <style>
        :root {
            --ink: #141817;
            --muted: #687370;
            --soft: #f5f7f4;
            --paper: #ffffff;
            --line: #dce5df;
            --line-strong: #b9c9c1;
            --emerald: #12b886;
            --emerald-dark: #05735f;
            --night: #101817;
            --aqua: #e6fff6;
            --amber: #a86518;
            --red: #b34040;
        }
        .stApp {
            background:
                linear-gradient(180deg, rgba(230,255,246,.9), rgba(245,247,244,.55) 260px),
                var(--soft);
            color: var(--ink);
        }
        .block-container {
            max-width: 1220px;
            padding: .45rem 1.6rem 2.5rem;
        }
        section[data-testid="stSidebar"], div[data-testid="collapsedControl"] {
            display: none !important;
        }
        #MainMenu, footer, div[data-testid="stToolbar"], div[data-testid="stDecoration"] {
            visibility: hidden !important;
            height: 0 !important;
        }
        header[data-testid="stHeader"] {
            background: transparent;
        }
        h1, h2, h3, p {
            letter-spacing: 0;
        }
        h1 {
            font-size: clamp(2.1rem, 4vw, 4.2rem);
            line-height: .98;
            margin: 0 0 .7rem;
            font-weight: 850;
        }
        h2 {
            font-size: 1.45rem;
            margin: 0 0 .75rem;
        }
        h3 {
            font-size: 1.05rem;
            margin: 0 0 .55rem;
        }
        div.st-key-app_topbar {
            padding: 6px 0 8px;
            position: sticky;
            top: 0;
            z-index: 999;
            background: rgba(239,249,244,.88);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(16,24,23,.12);
            margin-bottom: 2px;
        }
        .appbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            min-height: 42px;
        }
        .appbar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
            flex: 0 0 auto;
        }
        .appbar-brand img {
            width: 60px;
            height: 36px;
            object-fit: contain;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
        }
        .appbar-title {
            font-size: 1.02rem;
            font-weight: 820;
            color: var(--ink);
            white-space: nowrap;
        }
        .topnav-links {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            flex: 1 1 auto;
            min-width: 0;
            overflow-x: auto;
            scrollbar-width: none;
        }
        .topnav-links::-webkit-scrollbar {
            display: none;
        }
        .nav-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 38px;
            padding: 0 14px;
            white-space: nowrap;
            border-radius: 8px;
            border: 1px solid var(--line-strong);
            background: rgba(255,255,255,.72);
            color: var(--muted) !important;
            font-size: .92rem;
            font-weight: 760;
            text-decoration: none !important;
            position: relative;
            box-sizing: border-box;
            flex: 0 0 auto;
            min-width: 112px;
            line-height: 38px;
            cursor: pointer;
        }
        .nav-pill::after {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: inherit;
        }
        .nav-pill:hover {
            border-color: var(--emerald-dark);
            color: var(--emerald-dark) !important;
            background: #ffffff;
        }
        .nav-pill.is-active {
            border-color: var(--emerald-dark);
            background: var(--emerald-dark);
            color: #ffffff !important;
        }
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border-radius: 8px !important;
            border-color: var(--line-strong) !important;
            background: rgba(255,255,255,.9) !important;
            min-height: 36px;
        }
        div[data-testid="stSelectbox"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stDateInput"] input {
            border-radius: 8px !important;
            border: 1px solid var(--line) !important;
            background: rgba(255,255,255,.96) !important;
            box-shadow: none !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stDateInput"] input:focus,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
            border-color: var(--emerald-dark) !important;
            box-shadow: 0 0 0 3px rgba(18,184,134,.12) !important;
        }
        div[data-testid="stForm"] {
            border: 0 !important;
            padding: 0 !important;
            background: transparent !important;
        }
        div[data-testid="stForm"] label p {
            color: #202826;
            font-size: .82rem;
            font-weight: 760;
        }
        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button {
            min-height: 44px;
            background: var(--night) !important;
            border-color: var(--night) !important;
            color: #ffffff !important;
            font-weight: 780 !important;
        }
        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button:hover {
            background: var(--emerald-dark) !important;
            border-color: var(--emerald-dark) !important;
            color: #ffffff !important;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(300px, .65fr);
            gap: 22px;
            align-items: stretch;
            margin-bottom: 22px;
        }
        .hero-copy {
            padding: 14px 0 16px;
            border-bottom: 1px solid rgba(16,24,23,.1);
            margin-bottom: 16px;
        }
        .eyebrow {
            color: var(--emerald-dark);
            font-size: .76rem;
            font-weight: 830;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        .lead {
            color: #45504d;
            max-width: 680px;
            font-size: 1rem;
            line-height: 1.55;
        }
        .form-intro {
            border: 1px solid var(--line);
            background: linear-gradient(180deg, rgba(255,255,255,.92), rgba(247,251,248,.92));
            border-radius: 8px;
            padding: 14px 16px;
            margin: 2px 0 14px;
        }
        .form-title {
            color: var(--ink);
            font-size: 1rem;
            font-weight: 830;
            line-height: 1.25;
        }
        .form-subtitle {
            color: var(--muted);
            font-size: .88rem;
            line-height: 1.45;
            margin-top: 4px;
        }
        .form-section-title {
            color: var(--emerald-dark);
            font-size: .76rem;
            font-weight: 830;
            letter-spacing: 0;
            text-transform: uppercase;
            margin: 14px 0 6px;
        }
        .form-note {
            color: var(--muted);
            font-size: .82rem;
            line-height: 1.4;
            margin: -2px 0 10px;
        }
        .focus-panel {
            border: 1px solid rgba(18,184,134,.28);
            background: linear-gradient(180deg, #101817 0%, #162622 100%);
            color: #effff9;
            border-radius: 8px;
            padding: 14px;
            min-height: 0;
            box-shadow: 0 12px 28px rgba(5,40,34,.14);
        }
        .focus-panel h2 {
            font-size: 1.05rem;
            margin-bottom: .25rem;
        }
        .focus-panel .muted {
            color: rgba(239,255,249,.72);
            font-size: .82rem;
        }
        .dashboard-band {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(320px, .9fr);
            gap: 18px;
            align-items: start;
            margin: 18px 0 4px;
        }
        .panel {
            background: rgba(255,255,255,.88);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 12px 26px rgba(20,24,23,.045);
        }
        .todo-row {
            display: grid;
            grid-template-columns: 102px minmax(0, 1fr) auto;
            gap: 12px;
            align-items: start;
            border-bottom: 1px solid var(--line);
            padding: 11px 0;
        }
        .todo-row:last-child {
            border-bottom: 0;
            padding-bottom: 0;
        }
        .todo-type {
            color: var(--emerald-dark);
            font-size: .74rem;
            font-weight: 830;
            text-transform: uppercase;
        }
        .todo-main {
            font-weight: 760;
            line-height: 1.35;
        }
        .todo-sub {
            color: var(--muted);
            font-size: .84rem;
            line-height: 1.35;
            margin-top: 3px;
        }
        .todo-date {
            color: var(--muted);
            font-size: .8rem;
            white-space: nowrap;
        }
        .goal-row {
            margin-bottom: 12px;
        }
        .goal-top {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            font-weight: 760;
            line-height: 1.35;
        }
        .goal-track {
            height: 9px;
            border-radius: 999px;
            background: #e9f0ed;
            overflow: hidden;
            margin: 8px 0 5px;
        }
        .goal-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--emerald-dark), var(--emerald));
        }
        .stat-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
        }
        .mini-stat {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px;
            background: #fbfdfb;
        }
        .mini-stat-value {
            font-size: 1.35rem;
            font-weight: 850;
        }
        .mini-stat-label {
            color: var(--muted);
            font-size: .8rem;
            margin-top: 2px;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 6px 0 18px;
        }
        .metric-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,.86);
            padding: 15px 16px;
            min-height: 110px;
            box-shadow: 0 12px 28px rgba(20,24,23,.05);
        }
        .metric-label {
            color: var(--muted);
            font-size: .78rem;
            font-weight: 760;
            text-transform: uppercase;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 840;
            margin-top: 10px;
        }
        .metric-help {
            color: var(--muted);
            font-size: .84rem;
            margin-top: 4px;
        }
        .section-label {
            color: var(--muted);
            font-size: .77rem;
            font-weight: 820;
            text-transform: uppercase;
            margin: 22px 0 9px;
        }
        .surface {
            border-top: 1px solid var(--line);
            padding-top: 16px;
            margin-top: 6px;
        }
        .item-card {
            background: rgba(255,255,255,.88);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px 15px;
            margin-bottom: 10px;
            box-shadow: 0 10px 24px rgba(20,24,23,.045);
        }
        .item-title {
            font-weight: 790;
            color: var(--ink);
            line-height: 1.35;
        }
        .muted {
            color: var(--muted);
            font-size: .9rem;
            line-height: 1.45;
            white-space: pre-line;
        }
        .chips {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
        }
        .chip {
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 3px 8px;
            font-size: .74rem;
            color: #30403b;
            background: #f7fbf8;
        }
        .chip-hot {
            border-color: rgba(179,64,64,.28);
            color: var(--red);
            background: #fff5f4;
        }
        .chip-good {
            border-color: rgba(18,184,134,.35);
            color: var(--emerald-dark);
            background: #f0fff8;
        }
        .stage-row {
            display: grid;
            grid-template-columns: 132px minmax(0, 1fr) 48px;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
        }
        .stage-track {
            height: 9px;
            border-radius: 999px;
            background: #e9f0ed;
            overflow: hidden;
        }
        .stage-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--emerald), #73f0cf);
        }
        .brief-row {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 12px;
            border-bottom: 1px solid rgba(255,255,255,.1);
            padding: 7px 0;
        }
        .brief-row:last-child {
            border-bottom: 0;
        }
        .brief-kicker {
            color: rgba(239,255,249,.58);
            font-size: .76rem;
            text-transform: uppercase;
        }
        .brief-date {
            font-size: .78rem;
            color: #9ff5dd;
            white-space: nowrap;
        }
        .calendar-shell {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            background: rgba(255,255,255,.88);
            box-shadow: 0 12px 26px rgba(20,24,23,.045);
        }
        .calendar-head,
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
        }
        .calendar-head div {
            padding: 10px;
            border-right: 1px solid var(--line);
            background: #f7fbf8;
            color: var(--muted);
            font-size: .76rem;
            font-weight: 830;
            text-transform: uppercase;
        }
        .calendar-head div:last-child {
            border-right: 0;
        }
        .calendar-day {
            min-height: 132px;
            border-top: 1px solid var(--line);
            border-right: 1px solid var(--line);
            padding: 9px;
            background: #fff;
        }
        .calendar-day:nth-child(7n) {
            border-right: 0;
        }
        .calendar-muted {
            background: #f6f8f6;
            color: #a0aaa6;
        }
        .calendar-today {
            box-shadow: inset 0 0 0 2px rgba(18,184,134,.55);
        }
        .calendar-number {
            font-weight: 830;
            font-size: .86rem;
            margin-bottom: 7px;
        }
        .calendar-event {
            border: 1px solid var(--line);
            border-left: 3px solid var(--emerald-dark);
            border-radius: 6px;
            padding: 5px 6px;
            margin-bottom: 5px;
            background: #f7fbf8;
            font-size: .75rem;
            line-height: 1.25;
        }
        .calendar-event-hot {
            border-left-color: var(--red);
            background: #fff7f6;
        }
        .calendar-event-done {
            opacity: .55;
            text-decoration: line-through;
        }
        div[data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,.78);
            box-shadow: 0 10px 22px rgba(20,24,23,.035);
        }
        div[data-testid="stExpander"] details summary p {
            font-weight: 790;
        }
        div[data-testid="stDataFrame"], div[data-testid="stTable"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }
        div.stButton > button,
        div.stDownloadButton > button,
        div.stLinkButton > a {
            border-radius: 8px !important;
            border: 1px solid var(--line-strong) !important;
            background: #ffffff !important;
            color: var(--ink) !important;
            font-weight: 720 !important;
        }
        div.stButton > button:hover,
        div.stDownloadButton > button:hover,
        div.stLinkButton > a:hover {
            border-color: var(--emerald-dark) !important;
            color: var(--emerald-dark) !important;
        }
        @media (max-width: 880px) {
            .block-container {
                padding: .75rem .85rem 1.8rem;
            }
            div.st-key-app_topbar {
                position: static;
            }
            .appbar {
                flex-direction: row;
                align-items: center;
                gap: 12px;
            }
            .appbar-brand img {
                width: 48px;
                height: 30px;
            }
            .appbar-title {
                font-size: .92rem;
            }
            .topnav-links {
                width: auto;
                justify-content: flex-start;
            }
            .nav-pill {
                min-width: 96px;
                min-height: 36px;
                line-height: 36px;
                padding: 0 10px;
                font-size: .84rem;
            }
            .hero-grid {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            .hero-copy {
                padding: 10px 0 4px;
            }
            .metric-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .dashboard-band {
                grid-template-columns: 1fr;
            }
            .stat-strip {
                grid-template-columns: 1fr;
            }
            .todo-row {
                grid-template-columns: 82px minmax(0, 1fr);
            }
            .todo-date {
                grid-column: 2;
            }
            .stage-row {
                grid-template-columns: 102px minmax(0, 1fr) 38px;
            }
            h1 {
                font-size: 2.25rem;
            }
        }
        @media (max-width: 520px) {
            .metric-grid {
                grid-template-columns: 1fr;
            }
            .appbar-brand {
                min-width: 0;
            }
            .appbar-brand img {
                width: 44px;
                height: 28px;
            }
            .appbar-title {
                display: none;
            }
            .nav-pill {
                min-width: 100px;
                min-height: 36px;
                line-height: 36px;
                padding: 0 12px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> str:
    logo = logo_data_uri()
    logo_html = f'<img src="{logo}" alt="My Finance Career logo">' if logo else ""
    requested_page = st.query_params.get("page", PAGES[0])
    if requested_page not in PAGES:
        requested_page = PAGES[0]
        st.query_params["page"] = requested_page

    if "current_page" not in st.session_state or st.session_state["current_page"] not in PAGES or st.session_state.get("_url_page") != requested_page:
        st.session_state["current_page"] = requested_page
        st.session_state["_url_page"] = requested_page

    current_page = st.session_state["current_page"]
    nav_html = "".join(
        f'<a class="nav-pill {"is-active" if page_key == current_page else ""}" href="?page={quote(page_key)}" target="_self">{escape(NAV_LABELS[page_key])}</a>'
        for page_key in PAGES
    )
    with st.container(key="app_topbar"):
        st.markdown(
            f"""
            <div class="appbar">
                <div class="appbar-brand">
                    {logo_html}
                    <div class="appbar-title">My Finance Career</div>
                </div>
                <nav class="topnav-links" aria-label="Navigation My Finance Career">
                    {nav_html}
                </nav>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state["current_page"]


def page_intro(title: str, subtitle: str, eyebrow: str) -> None:
    st.markdown(
        f"""
        <div class="hero-copy">
            <div class="eyebrow">{escape(eyebrow)}</div>
            <div class="lead">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{escape(text)}</div>', unsafe_allow_html=True)


def form_intro(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="form-intro">
            <div class="form-title">{escape(title)}</div>
            <div class="form-subtitle">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def form_section(title: str, note: str = "") -> None:
    note_html = f'<div class="form-note">{escape(note)}</div>' if note else ""
    st.markdown(
        f"""
        <div class="form-section-title">{escape(title)}</div>
        {note_html}
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: Any, help_text: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
            <div class="metric-help">{escape(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chips_html(chips: list[Any] | None = None, hot: bool = False) -> str:
    chip_class = "chip chip-hot" if hot else "chip"
    return "".join(f'<span class="{chip_class}">{escape(item)}</span>' for item in chips or [] if item)


def item_card(title: str, body: str, chips: list[Any] | None = None, hot: bool = False) -> None:
    st.markdown(
        f"""
        <div class="item-card">
            <div class="item-title">{escape(title)}</div>
            <div class="muted">{escape(body)}</div>
            <div class="chips">{chips_html(chips, hot=hot)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def next_month(month_start: date, offset: int) -> date:
    month = month_start.month - 1 + offset
    year = month_start.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


def agenda_items(events: pd.DataFrame, contacts: pd.DataFrame, goals: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not events.empty:
        for _, row in events.iterrows():
            parsed = parse_day(row["event_date"])
            if parsed:
                rows.append(
                    {
                        "day": parsed,
                        "title": row["title"],
                        "kind": row["event_type"],
                        "priority": row["priority"],
                        "notes": row["notes"] or row["related_company"] or "",
                        "done": bool(row["done"]),
                        "source": "Agenda",
                    }
                )
    if not contacts.empty:
        active_contacts = contacts[contacts["status"] != "Dormant"] if "status" in contacts.columns else contacts
        for _, row in active_contacts.iterrows():
            follow = parse_day(row["next_follow_up"])
            if follow:
                rows.append(
                    {
                        "day": follow,
                        "title": f"{row['name']} - relance",
                        "kind": "Reseau",
                        "priority": row.get("priority", "Moyenne"),
                        "notes": row["company"] or row.get("profession_group", ""),
                        "done": False,
                        "source": "Reseau",
                    }
                )
    if not goals.empty:
        active_goals = goals[goals["status"] != "Termine"] if "status" in goals.columns else goals
        for _, row in active_goals.iterrows():
            due = parse_day(row["due_date"])
            if due:
                rows.append(
                    {
                        "day": due,
                        "title": row["title"],
                        "kind": "Objectif",
                        "priority": row.get("priority", "Moyenne"),
                        "notes": row["next_step"] or row["notes"] or "Objectif a suivre",
                        "done": False,
                        "source": "Objectifs",
                    }
                )
    return sorted(rows, key=lambda item: (item["day"], PRIORITY_WEIGHT.get(item["priority"], 2)), reverse=False)


def render_calendar(month_start: date, items: list[dict[str, Any]]) -> None:
    by_day: dict[date, list[dict[str, Any]]] = {}
    for item in items:
        by_day.setdefault(item["day"], []).append(item)
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(month_start.year, month_start.month)
    header = "".join(f"<div>{escape(day)}</div>" for day in WEEKDAY_LABELS)
    cells = []
    for week in weeks:
        for day in week:
            classes = ["calendar-day"]
            if day.month != month_start.month:
                classes.append("calendar-muted")
            if day == date.today():
                classes.append("calendar-today")
            day_items = by_day.get(day, [])
            events_html = ""
            for item in day_items[:3]:
                event_classes = ["calendar-event"]
                if item["priority"] == "Haute" or item["day"] <= date.today():
                    event_classes.append("calendar-event-hot")
                if item["done"]:
                    event_classes.append("calendar-event-done")
                events_html += (
                    f'<div class="{" ".join(event_classes)}">'
                    f'<strong>{escape(item["kind"])}</strong><br>{escape(item["title"])}'
                    f'</div>'
                )
            if len(day_items) > 3:
                events_html += f'<div class="todo-sub">+{len(day_items) - 3} autre(s)</div>'
            cells.append(
                f'<div class="{" ".join(classes)}">'
                f'<div class="calendar-number">{day.day}</div>'
                f'{events_html}'
                f'</div>'
            )
    st.markdown(
        f"""
        <div class="calendar-shell">
            <div class="calendar-head">{header}</div>
            <div class="calendar-grid">{"".join(cells)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def resource_form(prefix: str = "resource") -> None:
    with st.form(f"{prefix}_form", clear_on_submit=True, border=False):
        form_intro("Nouvelle ressource", "Ajoute un lien utile et classe-le directement pour le retrouver sans fouiller.")
        form_section("Essentiel", "Le titre et le lien suffisent pour enregistrer la ressource.")
        left, right = st.columns([1.15, .85])
        with left:
            title = st.text_input("Nom de la ressource", placeholder="Ex: Template CV finance")
            link = st.text_input("Lien externe", placeholder="https://drive.google.com/...")
        with right:
            category = st.selectbox("Categorie", RESOURCE_CATEGORIES)
            field = st.selectbox("Domaine associe", [""] + FIELDS, placeholder="Choisir un domaine")
        form_section("Contexte")
        tags = st.text_input("Tags", placeholder="Ex: CV, IB, entretien")
        description = st.text_area("Pourquoi c'est utile", placeholder="Ce que cette ressource aide a preparer, quand l'utiliser, points importants...", height=96)
        submitted = st.form_submit_button("Enregistrer la ressource", width="stretch")
    if submitted:
        if not title or not link:
            st.error("Ajoute au minimum un titre et un lien.")
            return
        run_sql(
            "INSERT INTO resources (title, category, field, tags, link, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, category, field, tags, link, description, datetime.utcnow().isoformat(timespec="seconds")),
        )
        st.success("Ressource ajoutee.")
        st.rerun()


def event_form(prefix: str = "event") -> None:
    with st.form(f"{prefix}_form", clear_on_submit=True, border=False):
        form_intro("Nouvel evenement", "Ajoute une echeance, une relance, un entretien ou une tache au calendrier.")
        form_section("Details")
        left, right = st.columns([1.15, .85])
        with left:
            title = st.text_input("Titre", placeholder="Ex: Relancer alumni Lazard")
            related_company = st.text_input("Entreprise associee", placeholder="Ex: Lazard")
        with right:
            event_type = st.selectbox("Type", EVENT_TYPES)
            event_date = st.date_input("Date", value=date.today() + timedelta(days=7))
            priority = st.selectbox("Priorite", PRIORITIES)
        form_section("Suivi")
        done = st.checkbox("Deja termine")
        notes = st.text_area("Notes", placeholder="Objectif de l'evenement, preparation a faire, message a envoyer...", height=96)
        submitted = st.form_submit_button("Ajouter a l'agenda", width="stretch")
    if submitted:
        if not title:
            st.error("Ajoute un titre.")
            return
        run_sql(
            "INSERT INTO events (title, event_type, event_date, related_company, priority, notes, done, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, event_type, event_date.isoformat(), related_company, priority, notes, int(done), datetime.utcnow().isoformat(timespec="seconds")),
        )
        st.success("Evenement ajoute.")
        st.rerun()


def agenda_page() -> None:
    page_intro("Calendrier", "Un vrai calendrier mensuel pour ajouter et suivre les echeances, entretiens, relances et objectifs a venir.", "Planning")
    events, contacts, goals = events_df(), contacts_df(), goals_df()
    items = agenda_items(events, contacts, goals)
    if "agenda_month" not in st.session_state:
        st.session_state["agenda_month"] = date.today().replace(day=1)
    month_start = st.session_state["agenda_month"]

    prev_col, title_col, next_col, today_col = st.columns([.75, 1.8, .75, .9])
    if prev_col.button("Mois precedent", width="stretch"):
        st.session_state["agenda_month"] = next_month(month_start, -1)
        st.rerun()
    title_col.markdown(f"### {MONTH_NAMES[month_start.month]} {month_start.year}")
    if next_col.button("Mois suivant", width="stretch"):
        st.session_state["agenda_month"] = next_month(month_start, 1)
        st.rerun()
    if today_col.button("Aujourd'hui", width="stretch"):
        st.session_state["agenda_month"] = date.today().replace(day=1)
        st.rerun()

    with st.expander("Ajouter un evenement", expanded=False):
        event_form("main_event")

    overdue = [item for item in items if not item["done"] and item["day"] < date.today()]
    month_items = [item for item in items if item["day"].year == month_start.year and item["day"].month == month_start.month]
    upcoming = [item for item in items if not item["done"] and item["day"] >= date.today()]
    done = [item for item in items if item["done"]]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("En retard", len(overdue), "a replanifier")
    with col2:
        metric_card("Ce mois-ci", len(month_items), "elements au calendrier")
    with col3:
        metric_card("A venir", len(upcoming), "non termines")
    with col4:
        metric_card("Termines", len(done), "archives dans l'agenda")

    section_label("Calendrier")
    if not items:
        st.info("Aucun element date pour le moment. Ajoute un evenement, une relance reseau ou une echeance d'objectif.")
    render_calendar(month_start, items)

    left, right = st.columns([1.1, .9])
    with left:
        section_label("Prochains jalons")
        for item in upcoming[:8]:
            item_card(item["title"], item["notes"], [item["kind"], format_day(item["day"]), item["priority"], item["source"]], hot=item["day"] <= date.today() + timedelta(days=3))
        if not upcoming:
            st.caption("Aucun jalon a venir.")
    with right:
        section_label("Evenements ajoutes")
        manual_events = events[events["done"] == 0].head(8) if not events.empty else events
        if manual_events.empty:
            st.caption("Aucun evenement manuel actif.")
        for _, row in manual_events.iterrows():
            item_card(row["title"], row["notes"] or row["related_company"] or "", [row["event_type"], format_day(row["event_date"]), row["priority"]])

    with st.expander("Marquer un evenement comme termine"):
        options = {f"{row['event_date']} - {row['title']}": int(row["id"]) for _, row in events[events["done"] == 0].iterrows()}
        if options:
            selected = st.selectbox("Evenement", list(options))
            if st.button("Marquer termine", width="stretch"):
                run_sql("UPDATE events SET done = 1 WHERE id = ?", (options[selected],))
                st.success("Evenement termine.")
                st.rerun()
        else:
            st.caption("Tout est termine.")


def contacts_page() -> None:
    page_intro("Reseau", "Une bibliotheque de contacts classee par metier, avec les relances et les conversations a piloter.", "Network")

    contacts = contacts_df()
    active_contacts = contacts[contacts["status"] != "Dormant"] if not contacts.empty else contacts
    due_contacts = contacts[contacts["days_left"].fillna(99) <= 7] if not contacts.empty else contacts
    profession_count = int(contacts["profession_group"].nunique()) if not contacts.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Contacts", len(contacts), "dans la bibliotheque")
    with c2:
        metric_card("Metiers", profession_count, "categories couvertes")
    with c3:
        metric_card("Relances", len(due_contacts), "a faire sous 7 jours")
    with c4:
        metric_card("Actifs", len(active_contacts), "hors contacts dormants")

    with st.expander("Ajouter un contact reseau", expanded=contacts.empty):
        with st.form("contact_form", clear_on_submit=True, border=False):
            form_intro("Nouveau contact reseau", "Enregistre la personne, son contexte et la prochaine action a faire.")
            form_section("Identite")
            left, right = st.columns(2)
            with left:
                first_name = st.text_input("Prenom", placeholder="Ex: Camille")
                company = st.text_input("Entreprise", placeholder="Ex: Rothschild & Co")
                role = st.text_input("Poste actuel", placeholder="Ex: Analyst M&A")
            with right:
                last_name = st.text_input("Nom", placeholder="Ex: Martin")
                city = st.text_input("Ville", placeholder="Ex: Paris")
                seniority = st.selectbox("Seniorite", SENIORITY_LEVELS)

            form_section("Classification", "Ces champs servent a filtrer ton reseau et a prioriser les relances.")
            left, mid, right = st.columns(3)
            with left:
                profession = st.selectbox("Metier", NETWORK_PROFESSIONS)
                target_role = st.text_input("Cible / poste vise", placeholder="Ex: Stage M&A")
            with mid:
                relation = st.text_input("Type de relation", placeholder="Alumni, recruteur, LinkedIn...")
                status = st.selectbox("Statut", NETWORK_STATUSES, index=1)
            with right:
                channel = st.selectbox("Canal", NETWORK_CHANNELS)
                priority = st.selectbox("Priorite", PRIORITIES)

            form_section("Coordonnees et relance")
            left, mid, right = st.columns(3)
            with left:
                linkedin = st.text_input("LinkedIn", placeholder="https://linkedin.com/in/...")
                source = st.text_input("Source", placeholder="Excel, event, alumni...")
            with mid:
                email = st.text_input("Email / telephone", placeholder="email ou numero")
                associated = st.text_input("Opportunite associee", placeholder="Ex: Summer internship")
            with right:
                last = st.date_input("Derniere interaction", value=date.today())
                follow = st.date_input("Prochaine relance", value=date.today() + timedelta(days=14))
            notes = st.text_area("Notes", placeholder="Contexte de l'echange, sujet a aborder, prochaine phrase de relance...", height=104)
            submitted = st.form_submit_button("Enregistrer le contact", width="stretch")
        if submitted:
            name = " ".join(part.strip() for part in [first_name, last_name] if part.strip())
            if not name:
                st.error("Ajoute au moins un prenom ou un nom.")
                return
            run_sql(
                """
                INSERT INTO contacts (
                    name, company, role, profession_group, seniority, target_role, relation_type,
                    status, source, contact_channel, city, priority, linkedin, email, last_interaction,
                    next_follow_up, associated_company, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    company,
                    role,
                    profession,
                    seniority,
                    target_role,
                    relation,
                    status,
                    source,
                    channel,
                    city,
                    priority,
                    linkedin,
                    email,
                    last.isoformat(),
                    follow.isoformat(),
                    associated,
                    notes,
                    datetime.utcnow().isoformat(timespec="seconds"),
                ),
            )
            st.success("Contact ajoute au reseau.")
            st.rerun()

    with st.expander("Importer une fiche Excel ou CSV", expanded=False):
        uploaded = st.file_uploader("Fichier de networking", type=["xlsx", "xls", "csv"])
        fallback_profession = st.selectbox("Metier par defaut si non reconnu", ["Auto"] + NETWORK_PROFESSIONS)
        if uploaded is not None:
            try:
                if uploaded.name.lower().endswith(".csv"):
                    imported_raw = pd.read_csv(uploaded)
                else:
                    imported_raw = pd.read_excel(uploaded, header=None)
                imported = normalize_import_columns(imported_raw)
                if fallback_profession != "Auto":
                    imported.loc[imported["profession_group"] == "Other", "profession_group"] = fallback_profession
                preview = imported[["name", "profession_group", "company", "role", "linkedin", "email", "notes"]].copy()
                preview.columns = ["Contact", "Metier", "Entreprise", "Poste", "Lien", "Contact direct", "Notes"]
                st.dataframe(preview.head(25), width="stretch", hide_index=True)
                if st.button("Importer ces contacts", width="stretch"):
                    now = datetime.utcnow().isoformat(timespec="seconds")
                    today_iso = date.today().isoformat()
                    follow_iso = (date.today() + timedelta(days=14)).isoformat()
                    rows = [
                        (
                            row["name"],
                            row["company"],
                            row["role"],
                            row["profession_group"],
                            "",
                            row["role"],
                            "Import fichier",
                            "Contacte",
                            uploaded.name,
                            "LinkedIn" if row["linkedin"] else "Other",
                            "",
                            "Moyenne",
                            row["linkedin"],
                            row["email"],
                            today_iso,
                            follow_iso,
                            row["company"],
                            row["notes"],
                            now,
                        )
                        for _, row in imported.iterrows()
                    ]
                    with closing(connect()) as conn:
                        conn.executemany(
                            """
                            INSERT INTO contacts (
                                name, company, role, profession_group, seniority, target_role, relation_type,
                                status, source, contact_channel, city, priority, linkedin, email, last_interaction,
                                next_follow_up, associated_company, notes, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            rows,
                        )
                        conn.commit()
                    st.success(f"{len(rows)} contacts importes.")
                    st.rerun()
            except Exception as exc:
                st.error(f"Import impossible: {exc}")

    if contacts.empty:
        st.info("Aucun contact sauvegarde. Ajoute ton premier contact pour construire ta bibliotheque reseau.")
        return

    query_col, profession_col, status_col, priority_col = st.columns([1.4, 1, 1, 1])
    filtered = filter_rows(contacts, query_col.text_input("Recherche reseau"))
    profession_filter = profession_col.selectbox("Metier", ["Tous"] + NETWORK_PROFESSIONS)
    status_filter = status_col.selectbox("Statut", ["Tous"] + NETWORK_STATUSES)
    priority_filter = priority_col.selectbox("Priorite", ["Toutes"] + PRIORITIES)
    if profession_filter != "Tous":
        filtered = filtered[filtered["profession_group"] == profession_filter]
    if status_filter != "Tous":
        filtered = filtered[filtered["status"] == status_filter]
    if priority_filter != "Toutes":
        filtered = filtered[filtered["priority"] == priority_filter]

    overview_tab, follow_tab, library_tab = st.tabs(["Vue metier", "Relances", "Bibliotheque"])
    with overview_tab:
        section_label("Contacts par metier")
        for profession in NETWORK_PROFESSIONS:
            group = filtered[filtered["profession_group"] == profession]
            if group.empty:
                continue
            st.write(f"**{profession}**")
            cols = st.columns(2)
            for index, (_, row) in enumerate(group.head(6).iterrows()):
                with cols[index % 2]:
                    subtitle = f"{row['company'] or '-'} - {row['role'] or row['seniority'] or 'Role a completer'}"
                    details = row["notes"] or row["target_role"] or row["relation_type"] or ""
                    item_card(row["name"], f"{subtitle}\n{details}", [row["status"], row["priority"], days_text(row["next_follow_up"])])
                    if row["linkedin"]:
                        st.link_button("LinkedIn", row["linkedin"], width="stretch")

    with follow_tab:
        section_label("Prochaines actions reseau")
        upcoming = filtered[filtered["days_left"].fillna(99) <= 30].head(12)
        if upcoming.empty:
            st.caption("Aucune relance dans les 30 prochains jours avec ces filtres.")
        cols = st.columns(2)
        for index, (_, row) in enumerate(upcoming.iterrows()):
            with cols[index % 2]:
                item_card(
                    row["name"],
                    f"{row['company'] or '-'} - {row['profession_group']}\n{row['notes'] or 'Preparer un message court et personnalise.'}",
                    [days_text(row["next_follow_up"]), row["status"], row["contact_channel"]],
                    hot=row["days_left"] <= 3 if pd.notna(row["days_left"]) else False,
                )

    with library_tab:
        section_label("Bibliotheque de contacts")
        table = filtered.copy()
        table["Relance"] = table["next_follow_up"].apply(format_day)
        table["Dernier contact"] = table["last_interaction"].apply(format_day)
        table = table[
            [
                "name",
                "profession_group",
                "company",
                "role",
                "seniority",
                "status",
                "priority",
                "contact_channel",
                "Relance",
                "Dernier contact",
                "associated_company",
                "linkedin",
                "notes",
            ]
        ]
        table.columns = [
            "Contact",
            "Metier",
            "Entreprise",
            "Poste",
            "Seniorite",
            "Statut",
            "Priorite",
            "Canal",
            "Relance",
            "Dernier contact",
            "Opportunite",
            "LinkedIn",
            "Notes",
        ]
        st.dataframe(table, width="stretch", hide_index=True)

    with st.expander("Mettre a jour un contact"):
        options = {f"{row['name']} - {row['company'] or 'Contact'}": int(row["id"]) for _, row in contacts.iterrows()}
        selected = st.selectbox("Contact", list(options))
        selected_row = contacts[contacts["id"] == options[selected]].iloc[0]
        col1, col2, col3 = st.columns(3)
        new_profession = col1.selectbox("Metier", NETWORK_PROFESSIONS, index=NETWORK_PROFESSIONS.index(selected_row["profession_group"]) if selected_row["profession_group"] in NETWORK_PROFESSIONS else len(NETWORK_PROFESSIONS) - 1)
        new_status = col2.selectbox("Statut", NETWORK_STATUSES, index=NETWORK_STATUSES.index(selected_row["status"]) if selected_row["status"] in NETWORK_STATUSES else 0)
        new_priority = col3.selectbox("Priorite", PRIORITIES, index=PRIORITIES.index(selected_row["priority"]) if selected_row["priority"] in PRIORITIES else 1)
        col4, col5 = st.columns(2)
        new_last = col4.date_input("Derniere interaction", value=parse_day(selected_row["last_interaction"]) or date.today())
        next_follow = col5.date_input("Nouvelle relance", value=parse_day(selected_row["next_follow_up"]) or date.today() + timedelta(days=14))
        new_notes = st.text_area("Notes", value=selected_row["notes"] or "")
        if st.button("Mettre a jour le contact", width="stretch"):
            run_sql(
                """
                UPDATE contacts
                SET profession_group = ?, status = ?, priority = ?, last_interaction = ?, next_follow_up = ?, notes = ?
                WHERE id = ?
                """,
                (new_profession, new_status, new_priority, new_last.isoformat(), next_follow.isoformat(), new_notes, options[selected]),
            )
            st.success("Contact mis a jour.")
            st.rerun()


def resources_page() -> None:
    page_intro("Bibliotheque", "CV, lettres de motivation, preparations techniques, cours et documents Drive centralises sous forme de liens.", "Ressources externes")
    with st.expander("Ajouter une ressource", expanded=False):
        resource_form("main_resource")

    items = resources_df()
    query, category_choice, field_choice = st.columns([1.3, 1, 1])
    filtered = filter_rows(items, query.text_input("Recherche"))
    category = category_choice.selectbox("Categorie", ["Toutes"] + RESOURCE_CATEGORIES)
    field = field_choice.selectbox("Domaine", ["Tous"] + FIELDS)
    if category != "Toutes":
        filtered = filtered[filtered["category"] == category]
    if field != "Tous":
        filtered = filtered[filtered["field"] == field]

    section_label("Documents et liens")
    cols = st.columns(3)
    for index, (_, row) in enumerate(filtered.iterrows()):
        with cols[index % 3]:
            item_card(row["title"], row["description"] or "", [row["category"], row["field"], row["tags"]])
            st.link_button("Ouvrir", row["link"], width="stretch")


def goals_page() -> None:
    page_intro("Objectifs", "Une liste d'actions concretes pour suivre ce que tu dois faire, quand le faire, et ce qui avance vraiment.", "To-do")
    goals = goals_df()
    active_goals = goals[goals["status"] != "Termine"] if not goals.empty else goals
    late_goals = active_goals[active_goals["days_left"].fillna(99) < 0] if not active_goals.empty else active_goals
    high_goals = active_goals[active_goals["priority"] == "Haute"] if not active_goals.empty else active_goals

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("A faire", len(active_goals), "objectifs ouverts")
    with c2:
        metric_card("Priorite haute", len(high_goals), "a traiter en premier")
    with c3:
        metric_card("En retard", len(late_goals), "echeances depassees")

    with st.expander("Ajouter une action", expanded=goals.empty):
        with st.form("goal_form", clear_on_submit=True, border=False):
            form_intro("Nouvelle action", "Transforme une intention en prochaine etape concrete, datee et priorisee.")
            form_section("Action")
            left, right = st.columns([1.15, .85])
            with left:
                title = st.text_input("Action / objectif", placeholder="Ex: Envoyer 5 candidatures en M&A")
                next_step = st.text_input("Prochaine etape", placeholder="Ex: finaliser le CV avant vendredi")
            with right:
                due = st.date_input("Echeance", value=date.today() + timedelta(days=7))
                priority = st.selectbox("Priorite", PRIORITIES)
                field = st.selectbox("Domaine", [""] + FIELDS)
            form_section("Etat")
            left, right = st.columns([.85, 1.15])
            with left:
                status = st.selectbox("Statut", GOAL_STATUSES)
            with right:
                notes = st.text_area("Notes", placeholder="Pourquoi c'est important, criteres de reussite, ressources associees...", height=96)
            submitted = st.form_submit_button("Ajouter a ma to-do", width="stretch")
    if submitted:
        if not title:
            st.error("Ajoute au minimum une action ou un objectif.")
            return
        run_sql(
            "INSERT INTO goals (title, field, due_date, priority, progress, status, next_step, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (title, field, due.isoformat(), priority, 0 if status != "Termine" else 100, status, next_step, notes, datetime.utcnow().isoformat(timespec="seconds")),
        )
        st.success("Action ajoutee.")
        st.rerun()

    if goals.empty:
        st.info("Ajoute ta premiere action pour construire ton plan de travail.")
        return

    section_label("Actions ouvertes")
    for _, row in active_goals.iterrows():
        hot = row["priority"] == "Haute" or (pd.notna(row["days_left"]) and row["days_left"] <= 3)
        item_card(
            row["title"],
            row["next_step"] or row["notes"] or "Prochaine etape a definir.",
            [row["priority"], row["status"], days_text(row["due_date"]), row["field"] or "General"],
            hot=hot,
        )
        st.progress(max(0, min(100, int(row["progress"] or 0))) / 100)

    done_goals = goals[goals["status"] == "Termine"]
    if not done_goals.empty:
        with st.expander("Actions terminees", expanded=False):
            for _, row in done_goals.iterrows():
                item_card(row["title"], row["notes"] or row["next_step"] or "", [format_day(row["due_date"]), row["field"] or "General"], hot=False)

    with st.expander("Mettre a jour une action"):
        options = {f"{row['title']}": int(row["id"]) for _, row in goals.iterrows()}
        if options:
            selected = st.selectbox("Objectif", list(options))
            selected_row = goals[goals["id"] == options[selected]].iloc[0]
            col1, col2, col3 = st.columns(3)
            new_status = col1.selectbox("Statut", GOAL_STATUSES, index=GOAL_STATUSES.index(selected_row["status"]) if selected_row["status"] in GOAL_STATUSES else 0)
            new_priority = col2.selectbox("Priorite", PRIORITIES, index=PRIORITIES.index(selected_row["priority"]) if selected_row["priority"] in PRIORITIES else 1)
            new_due = col3.date_input("Echeance", value=parse_day(selected_row["due_date"]) or date.today())
            new_progress = st.slider("Progression", 0, 100, int(selected_row["progress"] or 0))
            new_step = st.text_input("Nouvelle prochaine etape")
            if st.button("Mettre a jour", width="stretch"):
                final_progress = 100 if new_status == "Termine" else new_progress
                run_sql(
                    "UPDATE goals SET status = ?, priority = ?, due_date = ?, progress = ?, next_step = ? WHERE id = ?",
                    (new_status, new_priority, new_due.isoformat(), final_progress, new_step, options[selected]),
                )
                st.success("Action mise a jour.")
                st.rerun()


def main() -> None:
    setup_page()
    init_db()
    seed_demo()
    page = render_header()
    pages = {
        "Objectifs": goals_page,
        "Calendrier": agenda_page,
        "Bibliotheque": resources_page,
        "Reseau": contacts_page,
    }
    pages[page]()


if __name__ == "__main__":
    main()
