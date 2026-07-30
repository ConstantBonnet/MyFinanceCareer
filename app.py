from __future__ import annotations

import base64
import html
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


APP_TITLE = "My Finance Career"
DB_PATH = Path("mfc_data.sqlite3")
LOGO_PATH = Path("static/logo.png")

FIELDS = [
    "Investment Banking",
    "Private Equity",
    "Asset Management",
    "Markets",
    "Corporate Finance",
    "Audit & Transaction Services",
    "Financial Advisory",
]
STATUSES = ["Entreprise cible", "A preparer", "Envoyee", "Tests", "Entretien", "Offre", "Cloturee"]
STATUS_LABELS = {
    "Entreprise cible": "Cible",
    "A preparer": "A preparer",
    "Envoyee": "Envoyee",
    "Tests": "Tests",
    "Entretien": "Entretien",
    "Offre": "Offre",
    "Cloturee": "Cloturee",
}
STATUS_FLOW = {
    "Entreprise cible": 0,
    "A preparer": 1,
    "Envoyee": 2,
    "Tests": 3,
    "Entretien": 4,
    "Offre": 5,
    "Cloturee": 6,
}
PRIORITIES = ["Haute", "Moyenne", "Basse"]
PRIORITY_WEIGHT = {"Haute": 3, "Moyenne": 2, "Basse": 1}
CONTRACTS = ["Stage", "Alternance", "Graduate program", "CDI", "VIE"]
RESOURCE_CATEGORIES = ["CV", "Lettre", "Modele", "Guide", "Cours", "Preparation entretien", "Site utile"]
EVENT_TYPES = ["Deadline", "Entretien", "Test", "Networking", "Relance", "Tache"]
GOAL_STATUSES = ["En cours", "En pause", "Termine"]
TABLES = ["applications", "resources", "events", "goals", "contacts"]
PAGES = ["Accueil", "Pipeline", "Agenda", "Contacts", "Ressources", "Objectifs", "Analyse", "Donnees"]


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


def init_db() -> None:
    with closing(connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                field TEXT NOT NULL,
                location TEXT,
                contract_type TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                deadline TEXT,
                sent_date TEXT,
                next_action TEXT,
                follow_up_date TEXT,
                offer_link TEXT,
                cv_link TEXT,
                cover_letter_link TEXT,
                contacts TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            );
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
                relation_type TEXT,
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
        conn.commit()


def table_is_empty(table: str) -> bool:
    with closing(connect()) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


def seed_demo() -> None:
    if not table_is_empty("applications"):
        return
    today = date.today()
    now = datetime.utcnow().isoformat(timespec="seconds")
    applications = [
        ("Rothschild & Co", "M&A Intern - Paris", "Investment Banking", "Paris", "Stage", "Entretien", "Haute", 12, -8, "Preparer les questions techniques et relire les deals recents", 2, "Claire Martin"),
        ("Ardian", "Private Equity Analyst Intern", "Private Equity", "Paris", "Stage", "A preparer", "Haute", 7, None, "Adapter la lettre et trouver deux alumni", 1, ""),
        ("Amundi", "Portfolio Assistant", "Asset Management", "Paris", "Stage", "Envoyee", "Moyenne", 20, -3, "Relancer si pas de reponse", 6, ""),
        ("BNP Paribas CIB", "Global Markets Summer Intern", "Markets", "London", "Stage", "Tests", "Moyenne", 3, -5, "Finaliser le test numerique", 0, ""),
        ("PwC", "Transaction Services Intern", "Audit & Transaction Services", "Paris", "Stage", "Offre", "Basse", -4, -25, "Comparer avec les autres opportunites", 4, "Marc Dubois"),
    ]
    with closing(connect()) as conn:
        conn.executemany(
            """
            INSERT INTO applications (
                company, role, field, location, contract_type, status, priority,
                deadline, sent_date, next_action, follow_up_date, offer_link,
                cv_link, cover_letter_link, contacts, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    company,
                    role,
                    field,
                    location,
                    contract,
                    status,
                    priority,
                    (today + timedelta(days=deadline)).isoformat(),
                    (today + timedelta(days=sent)).isoformat() if sent is not None else None,
                    action,
                    (today + timedelta(days=follow)).isoformat(),
                    "https://example.com",
                    "https://drive.google.com/",
                    "https://drive.google.com/",
                    linked_contacts,
                    "Donnee de demonstration orientee finance.",
                    now,
                )
                for company, role, field, location, contract, status, priority, deadline, sent, action, follow, linked_contacts in applications
            ],
        )
        conn.executemany(
            "INSERT INTO resources (title, category, field, tags, link, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("CV Finance - version M&A", "CV", "Investment Banking", "cv, m&a, paris", "https://drive.google.com/", "Version orientee transaction, valorisation et experience deal.", now),
                ("Questions techniques finance", "Preparation entretien", "Investment Banking", "valuation, accounting, technicals", "https://www.wallstreetprep.com/", "Support de revision pour entretiens M&A et PE.", now),
                ("Liste alumni finance", "Site utile", "Financial Advisory", "networking, alumni", "https://www.linkedin.com/", "Base de travail pour les prises de contact ciblees.", now),
                ("Modele de lettre PE", "Modele", "Private Equity", "cover letter, pe", "https://drive.google.com/", "Structure courte pour candidatures private equity.", now),
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
            "INSERT INTO goals (title, field, due_date, progress, status, next_step, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Obtenir un stage M&A a Paris", "Investment Banking", (today + timedelta(days=60)).isoformat(), 45, "En cours", "Envoyer 5 candidatures ciblees", "Priorite aux boutiques et banques avec fort dealflow.", now),
                ("Contacter 10 alumni en finance", "Financial Advisory", (today + timedelta(days=21)).isoformat(), 30, "En cours", "Identifier 3 anciens en PE", "Suivre les reponses dans Contacts.", now),
            ],
        )
        conn.executemany(
            """
            INSERT INTO contacts (
                name, company, role, relation_type, linkedin, email, last_interaction,
                next_follow_up, associated_company, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("Claire Martin", "Rothschild & Co", "Associate", "Alumni", "https://www.linkedin.com/", "", (today - timedelta(days=2)).isoformat(), (today + timedelta(days=5)).isoformat(), "Rothschild & Co", "Conseils sur les entretiens techniques.", now),
                ("Marc Dubois", "PwC", "Manager TS", "Recruteur", "https://www.linkedin.com/", "", (today - timedelta(days=6)).isoformat(), (today + timedelta(days=4)).isoformat(), "PwC", "Contact principal pour l'offre TS.", now),
            ],
        )
        conn.commit()


def applications_df() -> pd.DataFrame:
    return enrich_applications(read_df("SELECT * FROM applications ORDER BY created_at DESC, id DESC"))


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
    return read_df("SELECT * FROM goals ORDER BY due_date ASC, id DESC")


def contacts_df() -> pd.DataFrame:
    data = read_df("SELECT * FROM contacts ORDER BY next_follow_up ASC, id DESC")
    if data.empty:
        return data
    data["follow_day"] = data["next_follow_up"].apply(parse_day)
    data["days_left"] = data["follow_day"].apply(lambda item: (item - date.today()).days if item else None)
    return data


def parse_day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def format_day(value: Any) -> str:
    parsed = parse_day(value)
    return parsed.strftime("%d/%m/%Y") if parsed else "-"


def escape(value: Any) -> str:
    return html.escape(str(value or ""))


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


def enrich_applications(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data
    data = data.copy()
    data["deadline_day"] = data["deadline"].apply(parse_day)
    data["follow_day"] = data["follow_up_date"].apply(parse_day)
    data["days_to_follow"] = data["follow_day"].apply(lambda item: (item - date.today()).days if item else 99)
    data["days_to_deadline"] = data["deadline_day"].apply(lambda item: (item - date.today()).days if item else 99)
    data["stage_score"] = data["status"].map(STATUS_FLOW).fillna(0).astype(int)
    data["priority_score"] = data["priority"].map(PRIORITY_WEIGHT).fillna(1).astype(int)
    data["action_score"] = data.apply(application_score, axis=1)
    return data.sort_values(["action_score", "priority_score", "stage_score"], ascending=[False, False, False])


def application_score(row: pd.Series) -> int:
    score = int(row.get("priority_score", 1)) * 18 + int(row.get("stage_score", 0)) * 6
    follow = row.get("days_to_follow", 99)
    deadline = row.get("days_to_deadline", 99)
    if follow <= 0:
        score += 40
    elif follow <= 3:
        score += 25
    elif follow <= 7:
        score += 12
    if deadline <= 0:
        score += 35
    elif deadline <= 3:
        score += 22
    elif deadline <= 7:
        score += 10
    if row.get("status") in {"Offre", "Entretien", "Tests"}:
        score += 12
    if row.get("status") == "Cloturee":
        score = 0
    return score


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
            padding: 1.2rem 1.6rem 2.5rem;
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
        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            padding: 12px 0 14px;
            border-bottom: 1px solid rgba(16,24,23,.12);
            margin-bottom: 14px;
        }
        .brand {
            display: flex;
            align-items: center;
            min-width: 240px;
            gap: 12px;
        }
        .brand img {
            width: 54px;
            height: 54px;
            object-fit: cover;
            border-radius: 12px;
            background: #0b1714;
            box-shadow: 0 16px 34px rgba(5,115,95,.18);
        }
        .brand-title {
            font-size: 1.08rem;
            font-weight: 820;
            color: var(--ink);
        }
        .brand-subtitle {
            color: var(--muted);
            font-size: .83rem;
            margin-top: 2px;
        }
        .topbar-note {
            color: var(--muted);
            font-size: .86rem;
            text-align: right;
        }
        div[role="radiogroup"] {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 8px 0 24px;
        }
        div[role="radiogroup"] label {
            min-height: 38px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: rgba(255,255,255,.74);
            padding: 8px 13px;
            box-shadow: 0 6px 14px rgba(20,24,23,.035);
        }
        div[role="radiogroup"] label p {
            color: var(--ink) !important;
            font-weight: 720 !important;
        }
        div[role="radiogroup"] label:has(input:checked) {
            border-color: rgba(18,184,134,.72);
            background: #0f2b25;
            color: #f5fffb;
        }
        div[role="radiogroup"] label:has(input:checked) p {
            color: #f5fffb !important;
        }
        div[role="radiogroup"] label > div:first-child {
            display: none;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(300px, .65fr);
            gap: 22px;
            align-items: stretch;
            margin-bottom: 22px;
        }
        .hero-copy {
            padding: 30px 0 24px;
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
            font-size: 1.05rem;
            line-height: 1.65;
        }
        .focus-panel {
            border: 1px solid rgba(18,184,134,.28);
            background: linear-gradient(180deg, #101817 0%, #162622 100%);
            color: #effff9;
            border-radius: 8px;
            padding: 19px;
            min-height: 260px;
            box-shadow: 0 20px 50px rgba(5,40,34,.18);
        }
        .focus-panel .muted {
            color: rgba(239,255,249,.72);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 12px 0 22px;
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
            padding: 10px 0;
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
        div[data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,.78);
            box-shadow: 0 10px 22px rgba(20,24,23,.035);
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
            .topbar {
                align-items: flex-start;
                flex-direction: column;
            }
            .topbar-note {
                text-align: left;
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
            .brand {
                min-width: 0;
            }
            .brand img {
                width: 46px;
                height: 46px;
            }
            div[role="radiogroup"] {
                flex-wrap: nowrap;
                overflow-x: auto;
                padding-bottom: 6px;
            }
            div[role="radiogroup"] label {
                white-space: nowrap;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    logo = logo_data_uri()
    logo_html = f'<img src="{logo}" alt="My Finance Career logo">' if logo else ""
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand">
                {logo_html}
                <div>
                    <div class="brand-title">My Finance Career</div>
                    <div class="brand-subtitle">Career operating system for finance roles</div>
                </div>
            </div>
            <div class="topbar-note">Pipeline, relances, entretiens, contacts et ressources au meme endroit.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav() -> str:
    requested_page = st.query_params.get("page", "Accueil")
    default_index = PAGES.index(requested_page) if requested_page in PAGES else 0
    if "page_nav" not in st.session_state or st.session_state.get("_url_page") != requested_page:
        st.session_state["page_nav"] = PAGES[default_index]
        st.session_state["_url_page"] = requested_page
    page = st.radio(
        "Navigation",
        PAGES,
        horizontal=True,
        label_visibility="collapsed",
        key="page_nav",
    )
    if st.query_params.get("page") != page:
        st.query_params["page"] = page
        st.session_state["_url_page"] = page
    return page


def page_intro(title: str, subtitle: str, eyebrow: str) -> None:
    st.markdown(
        f"""
        <div class="hero-copy">
            <div class="eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <div class="lead">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{escape(text)}</div>', unsafe_allow_html=True)


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


def stage_rows(apps: pd.DataFrame) -> None:
    total = max(len(apps), 1)
    for status in STATUSES:
        count = int((apps["status"] == status).sum()) if not apps.empty else 0
        width = int((count / total) * 100)
        st.markdown(
            f"""
            <div class="stage-row">
                <div class="muted">{escape(STATUS_LABELS[status])}</div>
                <div class="stage-track"><div class="stage-fill" style="width:{width}%"></div></div>
                <div class="muted">{count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def brief_panel(apps: pd.DataFrame, events: pd.DataFrame, contacts: pd.DataFrame) -> None:
    focus_apps = apps[apps["status"] != "Cloturee"].head(3) if not apps.empty else apps
    focus_events = events[(events["done"] == 0) & (events["days_left"] <= 7)].head(2) if not events.empty else events
    due_contacts = contacts[contacts["days_left"] <= 7].head(2) if not contacts.empty else contacts
    rows: list[tuple[str, str, str]] = []
    for _, row in focus_apps.iterrows():
        rows.append(("Candidature", f"{row['company']} - {row['next_action'] or 'Action a definir'}", days_text(row["follow_up_date"])))
    for _, row in focus_events.iterrows():
        rows.append((row["event_type"], f"{row['title']} - {row['related_company'] or 'Planning'}", days_text(row["event_date"])))
    for _, row in due_contacts.iterrows():
        rows.append(("Contact", f"{row['name']} - {row['company'] or 'Reseau'}", days_text(row["next_follow_up"])))
    if not rows:
        rows.append(("Focus", "Aucune action critique aujourd'hui. Tu peux avancer les opportunites de fond.", "OK"))
    rows_html = "".join(
        f"""
        <div class="brief-row">
            <div>
                <div class="brief-kicker">{escape(kind)}</div>
                <div>{escape(label)}</div>
            </div>
            <div class="brief-date">{escape(timing)}</div>
        </div>
        """
        for kind, label, timing in rows[:6]
    )
    st.markdown(
        f"""
        <div class="focus-panel">
            <div class="eyebrow" style="color:#9ff5dd;">Priorites</div>
            <h2>Ce qui merite ton attention</h2>
            <div class="muted">Une vue courte pour savoir quoi faire maintenant, pas un tableau de plus.</div>
            <div style="height:10px"></div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def application_form(prefix: str = "application") -> None:
    with st.form(f"{prefix}_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            company = st.text_input("Entreprise")
            role = st.text_input("Poste")
            field = st.selectbox("Domaine", FIELDS)
            location = st.text_input("Localisation", value="Paris")
            contract = st.selectbox("Contrat", CONTRACTS)
            priority = st.selectbox("Priorite", PRIORITIES)
        with right:
            status = st.selectbox("Statut", STATUSES, format_func=lambda item: STATUS_LABELS.get(item, item))
            deadline = st.date_input("Date limite", value=date.today() + timedelta(days=14))
            sent_enabled = st.checkbox("Candidature deja envoyee")
            sent_date = st.date_input("Date d'envoi", value=date.today(), disabled=not sent_enabled)
            follow_up = st.date_input("Prochaine action", value=date.today() + timedelta(days=7))
            offer_link = st.text_input("Lien vers l'offre")
        next_action = st.text_input("Action concrete a faire")
        cv_link = st.text_input("Lien CV utilise")
        cover_link = st.text_input("Lien lettre utilise")
        linked_contacts = st.text_input("Contacts associes")
        notes = st.text_area("Notes de preparation")
        submitted = st.form_submit_button("Ajouter au pipeline", width="stretch")
    if submitted:
        if not company or not role:
            st.error("Ajoute au minimum une entreprise et un poste.")
            return
        run_sql(
            """
            INSERT INTO applications (
                company, role, field, location, contract_type, status, priority,
                deadline, sent_date, next_action, follow_up_date, offer_link,
                cv_link, cover_letter_link, contacts, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company, role, field, location, contract, status, priority, deadline.isoformat(),
                sent_date.isoformat() if sent_enabled else None, next_action, follow_up.isoformat(),
                offer_link, cv_link, cover_link, linked_contacts, notes, datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )
        st.success("Candidature ajoutee au pipeline.")
        st.rerun()


def resource_form(prefix: str = "resource") -> None:
    with st.form(f"{prefix}_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            title = st.text_input("Titre")
            category = st.selectbox("Categorie", RESOURCE_CATEGORIES)
            field = st.selectbox("Domaine associe", [""] + FIELDS)
        with right:
            tags = st.text_input("Tags")
            link = st.text_input("Lien")
        description = st.text_area("Pourquoi c'est utile")
        submitted = st.form_submit_button("Ajouter la ressource", width="stretch")
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
    with st.form(f"{prefix}_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            title = st.text_input("Titre")
            event_type = st.selectbox("Type", EVENT_TYPES)
            event_date = st.date_input("Date", value=date.today() + timedelta(days=7))
        with right:
            related_company = st.text_input("Entreprise associee")
            priority = st.selectbox("Priorite", PRIORITIES)
            done = st.checkbox("Deja termine")
        notes = st.text_area("Notes")
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


def home_page() -> None:
    apps, events, goals, contacts = applications_df(), events_df(), goals_df(), contacts_df()
    active_apps = apps[apps["status"] != "Cloturee"] if not apps.empty else apps
    sent_base = active_apps[active_apps["status"] != "Entreprise cible"] if not active_apps.empty else active_apps
    interviews = int(active_apps["status"].isin(["Tests", "Entretien", "Offre"]).sum()) if not active_apps.empty else 0
    overdue = int((active_apps["days_to_follow"] < 0).sum()) if not active_apps.empty else 0
    upcoming_events = events[(events["done"] == 0) & (events["days_left"] >= 0) & (events["days_left"] <= 14)] if not events.empty else events
    conversion = f"{interviews / max(len(sent_base), 1):.0%}" if not active_apps.empty else "0%"

    left, right = st.columns([1.35, .75])
    with left:
        page_intro(
            "My Finance Career",
            "Un espace de pilotage pour transformer une recherche finance en systeme clair: priorites, relances, preparation et reseau.",
            "Workspace",
        )
    with right:
        brief_panel(active_apps, events, contacts)

    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Pipeline actif", len(active_apps), "hors candidatures cloturees")
    with c2:
        metric_card("Entretiens & tests", interviews, "opportunites chaudes")
    with c3:
        metric_card("Taux de traction", conversion, "tests + entretiens + offres")
    with c4:
        metric_card("Retards", overdue, "relances depassees")
    st.markdown("</div>", unsafe_allow_html=True)

    left, middle, right = st.columns([1.05, 1, .95])
    with left:
        section_label("Pipeline")
        stage_rows(active_apps)
    with middle:
        section_label("Opportunites a pousser")
        if active_apps.empty:
            st.info("Ajoute une premiere candidature pour construire ton cockpit.")
        for _, row in active_apps.head(4).iterrows():
            hot = row["days_to_follow"] <= 1 or row["days_to_deadline"] <= 3
            item_card(
                f"{row['company']} - {row['role']}",
                row["next_action"] or "Definir la prochaine action.",
                [STATUS_LABELS.get(row["status"], row["status"]), row["priority"], days_text(row["follow_up_date"])],
                hot=hot,
            )
    with right:
        section_label("Prochaines echeances")
        if upcoming_events.empty:
            st.info("Aucune echeance dans les 14 prochains jours.")
        for _, row in upcoming_events.head(4).iterrows():
            item_card(row["title"], row["notes"] or row["related_company"] or "", [row["event_type"], days_text(row["event_date"]), row["priority"]])

    section_label("Ajout rapide")
    a, b, c = st.columns(3)
    with a.expander("Nouvelle candidature"):
        application_form("home_application")
    with b.expander("Nouvel evenement"):
        event_form("home_event")
    with c.expander("Nouvelle ressource"):
        resource_form("home_resource")


def pipeline_page() -> None:
    page_intro("Pipeline", "Prioriser, filtrer et faire avancer chaque candidature avec une action suivante claire.", "Candidatures")
    with st.expander("Ajouter une candidature", expanded=False):
        application_form("main_application")

    apps = applications_df()
    if apps.empty:
        st.info("Aucune candidature pour le moment.")
        return

    search, field_choice, priority_choice, status_choice = st.columns([1.35, 1, .9, .9])
    query = search.text_input("Recherche")
    field = field_choice.selectbox("Domaine", ["Tous"] + FIELDS)
    priority = priority_choice.selectbox("Priorite", ["Toutes"] + PRIORITIES)
    status = status_choice.selectbox("Statut", ["Tous"] + STATUSES, format_func=lambda item: STATUS_LABELS.get(item, item))
    filtered = filter_rows(apps, query)
    if field != "Tous":
        filtered = filtered[filtered["field"] == field]
    if priority != "Toutes":
        filtered = filtered[filtered["priority"] == priority]
    if status != "Tous":
        filtered = filtered[filtered["status"] == status]

    left, right = st.columns([.85, 1.15])
    with left:
        section_label("Focus list")
        for _, row in filtered.head(6).iterrows():
            hot = row["days_to_follow"] <= 1 or row["days_to_deadline"] <= 3
            item_card(
                f"{row['company']}",
                f"{row['role']}\n{row['next_action'] or 'Action a definir'}",
                [STATUS_LABELS.get(row["status"], row["status"]), row["field"], days_text(row["follow_up_date"])],
                hot=hot,
            )
    with right:
        section_label("Vue exploitable")
        table = filtered.copy()
        table["Statut"] = table["status"].map(STATUS_LABELS)
        table["Relance"] = table["follow_up_date"].apply(format_day)
        table["Deadline"] = table["deadline"].apply(format_day)
        table = table[["company", "role", "field", "priority", "Statut", "Relance", "Deadline", "next_action"]]
        table.columns = ["Entreprise", "Poste", "Domaine", "Priorite", "Statut", "Relance", "Deadline", "Action"]
        st.dataframe(table, width="stretch", hide_index=True)

    with st.expander("Faire avancer une candidature", expanded=False):
        options = {f"{row['company']} - {row['role']}": int(row["id"]) for _, row in apps.iterrows()}
        selected = st.selectbox("Candidature", list(options))
        col1, col2, col3 = st.columns(3)
        new_status = col1.selectbox("Nouveau statut", STATUSES, format_func=lambda item: STATUS_LABELS.get(item, item))
        new_priority = col2.selectbox("Priorite", PRIORITIES)
        new_follow = col3.date_input("Prochaine action", value=date.today() + timedelta(days=7))
        new_action = st.text_input("Action suivante")
        if st.button("Mettre a jour", width="stretch"):
            run_sql(
                "UPDATE applications SET status = ?, priority = ?, next_action = ?, follow_up_date = ? WHERE id = ?",
                (new_status, new_priority, new_action, new_follow.isoformat(), options[selected]),
            )
            st.success("Candidature mise a jour.")
            st.rerun()


def agenda_page() -> None:
    page_intro("Agenda", "Voir les deadlines, entretiens, tests et relances sans fouiller dans tout le pipeline.", "Planning")
    with st.expander("Ajouter un evenement", expanded=False):
        event_form("main_event")
    events = events_df()
    if events.empty:
        st.info("Aucun evenement planifie.")
        return

    overdue = events[(events["done"] == 0) & (events["days_left"] < 0)]
    upcoming = events[(events["done"] == 0) & (events["days_left"] >= 0)]
    done = events[events["done"] == 1]
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("En retard", len(overdue), "a replanifier")
    with col2:
        metric_card("A venir", len(upcoming), "non termines")
    with col3:
        metric_card("Termines", len(done), "archives dans l'agenda")

    section_label("Prochains jalons")
    for _, row in upcoming.head(8).iterrows():
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
    page_intro("Contacts", "Un carnet relationnel oriente action: qui relancer, pourquoi, et pour quelle opportunite.", "Network")
    with st.form("contact_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            name = st.text_input("Nom")
            company = st.text_input("Entreprise")
            role = st.text_input("Poste")
            relation = st.text_input("Type de relation")
            linkedin = st.text_input("LinkedIn")
        with right:
            email = st.text_input("Email")
            last = st.date_input("Derniere interaction", value=date.today())
            follow = st.date_input("Prochaine relance", value=date.today() + timedelta(days=14))
            associated = st.text_input("Opportunite associee")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Ajouter le contact", width="stretch")
    if submitted:
        if not name:
            st.error("Ajoute un nom.")
            return
        run_sql(
            "INSERT INTO contacts (name, company, role, relation_type, linkedin, email, last_interaction, next_follow_up, associated_company, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, company, role, relation, linkedin, email, last.isoformat(), follow.isoformat(), associated, notes, datetime.utcnow().isoformat(timespec="seconds")),
        )
        st.success("Contact ajoute.")
        st.rerun()

    contacts = contacts_df()
    if contacts.empty:
        st.info("Aucun contact sauvegarde.")
        return
    section_label("Relances relationnelles")
    urgent = contacts[contacts["days_left"] <= 14].head(8)
    cols = st.columns(2)
    for index, (_, row) in enumerate(urgent.iterrows()):
        with cols[index % 2]:
            item_card(row["name"], f"{row['company'] or '-'} - {row['role'] or row['relation_type'] or ''}\n{row['notes'] or ''}", [days_text(row["next_follow_up"]), row["associated_company"]])
            if row["linkedin"]:
                st.link_button("LinkedIn", row["linkedin"], width="stretch")

    with st.expander("Replanifier une relance"):
        options = {f"{row['name']} - {row['company'] or 'Contact'}": int(row["id"]) for _, row in contacts.iterrows()}
        selected = st.selectbox("Contact", list(options))
        next_follow = st.date_input("Nouvelle relance", value=date.today() + timedelta(days=14))
        if st.button("Replanifier", width="stretch"):
            run_sql("UPDATE contacts SET next_follow_up = ? WHERE id = ?", (next_follow.isoformat(), options[selected]))
            st.success("Relance mise a jour.")
            st.rerun()


def resources_page() -> None:
    page_intro("Ressources", "CV, lettres, guides, preparation entretien et liens utiles classes pour retrouver vite le bon support.", "Bibliotheque")
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

    section_label("Ressources")
    cols = st.columns(3)
    for index, (_, row) in enumerate(filtered.iterrows()):
        with cols[index % 3]:
            item_card(row["title"], row["description"] or "", [row["category"], row["field"], row["tags"]])
            st.link_button("Ouvrir", row["link"], width="stretch")


def goals_page() -> None:
    page_intro("Objectifs", "Transformer une ambition vague en progression mesurable et prochaines etapes visibles.", "Progression")
    with st.form("goal_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            title = st.text_input("Objectif")
            field = st.selectbox("Domaine", [""] + FIELDS)
            due = st.date_input("Echeance", value=date.today() + timedelta(days=30))
        with right:
            progress = st.slider("Progression", 0, 100, 10)
            status = st.selectbox("Statut", GOAL_STATUSES)
            next_step = st.text_input("Prochaine etape")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Ajouter l'objectif", width="stretch")
    if submitted:
        if not title:
            st.error("Ajoute un objectif.")
            return
        run_sql(
            "INSERT INTO goals (title, field, due_date, progress, status, next_step, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, field, due.isoformat(), progress, status, next_step, notes, datetime.utcnow().isoformat(timespec="seconds")),
        )
        st.success("Objectif ajoute.")
        st.rerun()

    goals = goals_df()
    section_label("Objectifs actifs")
    for _, row in goals.iterrows():
        st.write(f"**{row['title']}**")
        st.progress(int(row["progress"]) / 100)
        st.caption(f"{row['status']} - {row['field'] or 'general'} - echeance {format_day(row['due_date'])} - {row['next_step'] or 'prochaine etape a definir'}")

    with st.expander("Mettre a jour une progression"):
        options = {f"{row['title']}": int(row["id"]) for _, row in goals.iterrows()}
        if options:
            selected = st.selectbox("Objectif", list(options))
            new_progress = st.slider("Nouvelle progression", 0, 100, 50)
            new_step = st.text_input("Nouvelle prochaine etape")
            if st.button("Mettre a jour l'objectif", width="stretch"):
                run_sql("UPDATE goals SET progress = ?, next_step = ? WHERE id = ?", (new_progress, new_step, options[selected]))
                st.success("Objectif mis a jour.")
                st.rerun()


def analytics_page() -> None:
    page_intro("Analyse", "Comprendre ou l'effort produit le plus de traction et ou le pipeline se bloque.", "Pilotage")
    apps, goals = applications_df(), goals_df()
    active = apps[apps["status"] != "Cloturee"] if not apps.empty else apps
    sent_base = active[active["status"] != "Entreprise cible"] if not active.empty else active
    traction = int(active["status"].isin(["Tests", "Entretien", "Offre"]).sum()) if not active.empty else 0
    offers = int((active["status"] == "Offre").sum()) if not active.empty else 0
    overdue = int((active["days_to_follow"] < 0).sum()) if not active.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Candidatures", len(active), "pipeline actif")
    with c2:
        metric_card("Traction", f"{traction / max(len(sent_base), 1):.0%}", "tests + entretiens + offres")
    with c3:
        metric_card("Offres", offers, "opportunites gagnees")
    with c4:
        metric_card("Relances en retard", overdue, "a traiter")

    left, right = st.columns(2)
    with left:
        section_label("Par statut")
        st.bar_chart(active["status"].value_counts().reindex(STATUSES, fill_value=0) if not active.empty else pd.Series(dtype=int))
    with right:
        section_label("Par domaine")
        st.bar_chart(active["field"].value_counts() if not active.empty else pd.Series(dtype=int))
    section_label("Objectifs")
    st.bar_chart(goals.set_index("title")["progress"] if not goals.empty else pd.Series(dtype=int))


def data_page() -> None:
    page_intro("Donnees", "Exporter, verifier et reinitialiser les donnees de demonstration quand tu veux repartir proprement.", "Systeme")
    tables = {"applications": applications_df(), "resources": resources_df(), "events": events_df(), "goals": goals_df(), "contacts": contacts_df()}
    export = pd.concat([table.assign(table=name) for name, table in tables.items()], ignore_index=True, sort=False)
    st.download_button("Telecharger toutes les donnees en CSV", export.to_csv(index=False).encode("utf-8"), f"my-finance-career-{date.today().isoformat()}.csv", "text/csv", width="stretch")
    st.info("L'app est compatible Streamlit Cloud. La base SQLite locale est ignoree par GitHub pour eviter de publier tes donnees personnelles.")
    if st.button("Recharger les donnees de demonstration", width="stretch"):
        with closing(connect()) as conn:
            for table in TABLES:
                conn.execute(f"DELETE FROM {table}")
            conn.commit()
        seed_demo()
        st.success("Donnees rechargees.")
        st.rerun()


def main() -> None:
    setup_page()
    init_db()
    seed_demo()
    render_header()
    page = nav()
    pages = {
        "Accueil": home_page,
        "Pipeline": pipeline_page,
        "Agenda": agenda_page,
        "Contacts": contacts_page,
        "Ressources": resources_page,
        "Objectifs": goals_page,
        "Analyse": analytics_page,
        "Donnees": data_page,
    }
    pages[page]()


if __name__ == "__main__":
    main()
