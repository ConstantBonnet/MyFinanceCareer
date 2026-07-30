from __future__ import annotations

import html
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


APP_TITLE = "MFC - My Finance Career"
DB_PATH = Path("mfc_data.sqlite3")

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
PRIORITIES = ["Haute", "Moyenne", "Basse"]
CONTRACTS = ["Stage", "Alternance", "Graduate program", "CDI", "VIE"]
RESOURCE_CATEGORIES = ["CV", "Lettre", "Modele", "Guide", "Cours", "Preparation entretien", "Site utile"]
EVENT_TYPES = ["Deadline", "Entretien", "Test", "Networking", "Relance", "Tache"]
GOAL_STATUSES = ["En cours", "En pause", "Termine"]
TABLES = ["applications", "resources", "events", "goals", "contacts"]
PAGES = ["Tableau de bord", "Candidatures", "Bibliotheque", "Calendrier", "Objectifs", "Contacts", "Statistiques", "Parametres"]


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
    return read_df("SELECT * FROM applications ORDER BY created_at DESC, id DESC")


def resources_df() -> pd.DataFrame:
    return read_df("SELECT * FROM resources ORDER BY created_at DESC, id DESC")


def events_df() -> pd.DataFrame:
    return read_df("SELECT * FROM events ORDER BY event_date ASC, id DESC")


def goals_df() -> pd.DataFrame:
    return read_df("SELECT * FROM goals ORDER BY due_date ASC, id DESC")


def contacts_df() -> pd.DataFrame:
    return read_df("SELECT * FROM contacts ORDER BY next_follow_up ASC, id DESC")


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


def setup_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":briefcase:", layout="wide", initial_sidebar_state="expanded")
    st.markdown(
        """
        <style>
        :root {
            --ink: #192225;
            --muted: #66757a;
            --line: #dce4e3;
            --panel: #ffffff;
            --page: #f4f7f6;
            --jade: #0f6b5f;
            --plum: #45324f;
            --amber: #b76e2b;
            --rose: #b84a4a;
        }
        .stApp { background: var(--page); color: var(--ink); }
        .block-container { max-width: 1380px; padding-top: 1.35rem; padding-bottom: 2rem; }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #172026 0%, #213133 100%);
            border-right: 1px solid rgba(255,255,255,.08);
        }
        section[data-testid="stSidebar"] * { color: #f7fbfb; }
        h1, h2, h3 { letter-spacing: 0; }
        h1 { font-size: 2.35rem; margin-bottom: .3rem; }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 15px 17px;
            box-shadow: 0 10px 24px rgba(25,34,37,.045);
        }
        .hero {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: linear-gradient(120deg, #ffffff 0%, #eff5f3 58%, #f7efe8 100%);
            padding: 22px 24px;
            margin-bottom: 18px;
        }
        .hero .eyebrow {
            color: var(--jade);
            font-size: .78rem;
            font-weight: 760;
            text-transform: uppercase;
            letter-spacing: .08rem;
            margin-bottom: 8px;
        }
        .hero p { color: var(--muted); max-width: 780px; margin: 0; }
        .panel, .mfc-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 15px 16px;
            box-shadow: 0 8px 20px rgba(25,34,37,.035);
        }
        .mfc-card { margin-bottom: 10px; min-height: 118px; }
        .mfc-card strong { font-size: .98rem; }
        .muted { color: var(--muted); font-size: .9rem; white-space: pre-line; }
        .chips { margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap; }
        .chip {
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 3px 9px;
            background: #f8fbfa;
            color: #344348;
            font-size: .76rem;
        }
        .section-label {
            color: var(--muted);
            font-size: .78rem;
            font-weight: 760;
            text-transform: uppercase;
            letter-spacing: .07rem;
            margin: 18px 0 8px 0;
        }
        div.stButton > button, div.stDownloadButton > button, div.stLinkButton > a {
            border-radius: 8px !important;
            border: 1px solid #cbd7d6 !important;
            background: #ffffff !important;
            color: #172026 !important;
            font-weight: 650 !important;
        }
        div.stButton > button:hover, div.stDownloadButton > button:hover, div.stLinkButton > a:hover {
            border-color: var(--jade) !important;
            color: var(--jade) !important;
        }
        @media (max-width: 760px) {
            .block-container { padding: 1rem .85rem 1.8rem .85rem; }
            .hero { padding: 18px 16px; }
            h1 { font-size: 1.9rem; }
            .mfc-card { min-height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "MFC workspace") -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{escape(text)}</div>', unsafe_allow_html=True)


def card(title: str, body: str, chips: list[Any] | None = None) -> None:
    chip_html = "".join(f'<span class="chip">{escape(item)}</span>' for item in chips or [] if item)
    st.markdown(
        f"""
        <div class="mfc-card">
            <strong>{escape(title)}</strong>
            <div class="muted">{escape(body)}</div>
            <div class="chips">{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filter_rows(data: pd.DataFrame, query: str) -> pd.DataFrame:
    if data.empty or not query:
        return data
    return data[data.apply(lambda row: query.lower() in " ".join(row.astype(str)).lower(), axis=1)]


def nav() -> str:
    st.sidebar.title("MFC")
    st.sidebar.caption("My Finance Career")
    requested_page = st.query_params.get("page", "Tableau de bord")
    default_index = PAGES.index(requested_page) if requested_page in PAGES else 0
    page = st.sidebar.radio(
        "Navigation",
        PAGES,
        index=default_index,
    )
    if st.query_params.get("page") != page:
        st.query_params["page"] = page
    st.sidebar.divider()
    st.sidebar.caption("Organise les candidatures, contacts, ressources et echeances de ta carriere finance.")
    return page


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
            status = st.selectbox("Statut", STATUSES)
            deadline = st.date_input("Date limite", value=date.today() + timedelta(days=14))
            sent_enabled = st.checkbox("Candidature deja envoyee")
            sent_date = st.date_input("Date d'envoi", value=date.today(), disabled=not sent_enabled)
            follow_up = st.date_input("Prochaine relance/action", value=date.today() + timedelta(days=7))
            offer_link = st.text_input("Lien vers l'offre")
        next_action = st.text_input("Prochaine action")
        cv_link = st.text_input("Lien CV utilise")
        cover_link = st.text_input("Lien lettre utilise")
        linked_contacts = st.text_input("Contacts associes")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Ajouter la candidature", width="stretch")
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
        st.success("Candidature ajoutee.")
        st.rerun()


def resource_form(prefix: str = "resource") -> None:
    with st.form(f"{prefix}_form", clear_on_submit=True):
        title = st.text_input("Titre")
        category = st.selectbox("Categorie", RESOURCE_CATEGORIES)
        field = st.selectbox("Domaine associe", [""] + FIELDS)
        tags = st.text_input("Tags")
        link = st.text_input("Lien")
        description = st.text_area("Description")
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
        submitted = st.form_submit_button("Ajouter l'evenement", width="stretch")
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


def dashboard_page() -> None:
    hero("My Finance Career", "Le poste de pilotage sobre et structure pour transformer une recherche de stage finance en pipeline lisible.")
    apps, evs, gls = applications_df(), events_df(), goals_df()
    today = date.today()
    upcoming = evs[evs["event_date"].apply(lambda value: (parse_day(value) or date.min) >= today)] if not evs.empty else evs
    urgent = apps[apps["follow_up_date"].apply(lambda value: parse_day(value) is not None and parse_day(value) <= today + timedelta(days=3))] if not apps.empty else apps

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidatures", len(apps))
    m2.metric("Envoyees", int((apps["status"] == "Envoyee").sum()) if not apps.empty else 0)
    m3.metric("Entretiens", int((apps["status"] == "Entretien").sum()) if not apps.empty else 0)
    m4.metric("Echeances 14 jours", len(upcoming.head(14)))

    left, middle, right = st.columns([1.12, 1, 1])
    with left:
        section_label("Actions prioritaires")
        if urgent.empty:
            st.info("Aucune action urgente. Le pipeline est propre.")
        for _, row in urgent.head(4).iterrows():
            card(f"{row['company']} - {row['role']}", row["next_action"] or "Action a definir", [row["status"], row["priority"], f"Relance {format_day(row['follow_up_date'])}"])
    with middle:
        section_label("Prochaines echeances")
        if upcoming.empty:
            st.info("Aucune echeance planifiee.")
        for _, row in upcoming.head(5).iterrows():
            card(row["title"], row["notes"] or row["related_company"] or "", [row["event_type"], format_day(row["event_date"]), row["priority"]])
    with right:
        section_label("Objectifs actifs")
        if gls.empty:
            st.info("Ajoute ton premier objectif.")
        for _, row in gls.head(4).iterrows():
            st.write(f"**{row['title']}**")
            st.progress(int(row["progress"]) / 100)
            st.caption(f"{row['progress']}% - {row['next_step'] or 'prochaine etape a definir'}")

    section_label("Raccourcis")
    a, b, c = st.columns(3)
    with a.expander("Ajouter une candidature"):
        application_form("dash_application")
    with b.expander("Ajouter un evenement"):
        event_form("dash_event")
    with c.expander("Ajouter une ressource"):
        resource_form("dash_resource")


def applications_page() -> None:
    hero("Candidatures", "Un pipeline finance clair: priorite, statut, prochaine action et relance toujours visibles.", "Pipeline")
    with st.expander("Nouvelle candidature", expanded=False):
        application_form("main_application")
    apps = applications_df()
    section_label("Filtres")
    search, field_choice, priority_choice = st.columns([1.4, 1, 1])
    query = search.text_input("Recherche")
    field = field_choice.selectbox("Domaine", ["Tous"] + FIELDS)
    priority = priority_choice.selectbox("Priorite", ["Toutes"] + PRIORITIES)
    filtered = filter_rows(apps, query)
    if field != "Tous":
        filtered = filtered[filtered["field"] == field]
    if priority != "Toutes":
        filtered = filtered[filtered["priority"] == priority]

    section_label("Kanban")
    cols = st.columns(len(STATUSES))
    for col, status in zip(cols, STATUSES):
        with col:
            st.markdown(f"**{status}**")
            rows = filtered[filtered["status"] == status]
            if rows.empty:
                st.caption("Vide")
            for _, row in rows.iterrows():
                card(row["company"], f"{row['role']}\n{row['next_action'] or ''}", [row["field"], row["priority"], format_day(row["deadline"])])

    section_label("Liste detaillee")
    st.dataframe(filtered.drop(columns=["id", "created_at"], errors="ignore"), width="stretch", hide_index=True)
    with st.expander("Mettre a jour une candidature"):
        options = {f"{row['company']} - {row['role']}": int(row["id"]) for _, row in apps.iterrows()}
        if options:
            selected = st.selectbox("Candidature", list(options))
            new_status = st.selectbox("Nouveau statut", STATUSES)
            new_action = st.text_input("Nouvelle prochaine action")
            new_follow = st.date_input("Nouvelle date de relance", value=date.today() + timedelta(days=7))
            if st.button("Enregistrer la mise a jour", width="stretch"):
                run_sql("UPDATE applications SET status = ?, next_action = ?, follow_up_date = ? WHERE id = ?", (new_status, new_action, new_follow.isoformat(), options[selected]))
                st.success("Candidature mise a jour.")
                st.rerun()


def resources_page() -> None:
    hero("Bibliotheque", "Les liens utiles restent classes par usage, domaine finance et tags.", "Ressources")
    with st.expander("Nouvelle ressource", expanded=False):
        resource_form("main_resource")
    items = resources_df()
    query = st.text_input("Recherche bibliotheque")
    items = filter_rows(items, query)
    section_label("Ressources sauvegardees")
    cols = st.columns(3)
    for index, (_, row) in enumerate(items.iterrows()):
        with cols[index % 3]:
            card(row["title"], row["description"] or "", [row["category"], row["field"], row["tags"]])
            st.link_button("Ouvrir le lien", row["link"], width="stretch")


def calendar_page() -> None:
    hero("Calendrier", "Deadlines, entretiens, tests, relances et evenements importants au meme endroit.", "Planning")
    with st.expander("Nouvel evenement", expanded=False):
        event_form("main_event")
    evs = events_df()
    if evs.empty:
        st.info("Aucun evenement planifie.")
        return
    evs["date_affichee"] = evs["event_date"].apply(format_day)
    evs["etat"] = evs["done"].map({0: "A faire", 1: "Termine"})
    st.dataframe(evs[["date_affichee", "title", "event_type", "related_company", "priority", "etat", "notes"]], width="stretch", hide_index=True)


def goals_page() -> None:
    hero("Objectifs", "Transformer une ambition de carriere en etapes visibles et mesurables.", "Progression")
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
        run_sql("INSERT INTO goals (title, field, due_date, progress, status, next_step, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (title, field, due.isoformat(), progress, status, next_step, notes, datetime.utcnow().isoformat(timespec="seconds")))
        st.success("Objectif ajoute.")
        st.rerun()
    section_label("Objectifs en cours")
    for _, row in goals_df().iterrows():
        st.write(f"**{row['title']}**")
        st.progress(int(row["progress"]) / 100)
        st.caption(f"{row['status']} - {row['field'] or 'general'} - echeance {format_day(row['due_date'])} - {row['next_step'] or 'prochaine etape a definir'}")


def contacts_page() -> None:
    hero("Contacts", "Un mini-CRM simple pour alumni, recruteurs et professionnels associes aux candidatures.", "Network")
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
            associated = st.text_input("Candidature/entreprise associee")
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
    section_label("Carnet relationnel")
    st.dataframe(contacts_df().drop(columns=["id", "created_at"], errors="ignore"), width="stretch", hide_index=True)


def statistics_page() -> None:
    hero("Statistiques", "Des indicateurs utiles pour voir ou concentrer l'effort de recherche.", "Pilotage")
    apps, gls = applications_df(), goals_df()
    sent_base = max(len(apps[apps["status"] != "Entreprise cible"]), 1) if not apps.empty else 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total candidatures", len(apps))
    c2.metric("Taux entretien", f"{(apps['status'] == 'Entretien').sum() / sent_base:.0%}" if not apps.empty else "0%")
    c3.metric("Offres", int((apps["status"] == "Offre").sum()) if not apps.empty else 0)
    c4.metric("Actions a suivre", int(apps["follow_up_date"].notna().sum()) if not apps.empty else 0)
    left, right = st.columns(2)
    with left:
        section_label("Par statut")
        st.bar_chart(apps["status"].value_counts().reindex(STATUSES, fill_value=0) if not apps.empty else pd.Series(dtype=int))
    with right:
        section_label("Par domaine")
        st.bar_chart(apps["field"].value_counts() if not apps.empty else pd.Series(dtype=int))
    section_label("Progression objectifs")
    st.bar_chart(gls.set_index("title")["progress"] if not gls.empty else pd.Series(dtype=int))


def settings_page() -> None:
    hero("Parametres", "Export, donnees de demonstration et controle de deploiement Streamlit.", "Systeme")
    tables = {"applications": applications_df(), "resources": resources_df(), "events": events_df(), "goals": goals_df(), "contacts": contacts_df()}
    export = pd.concat([table.assign(table=name) for name, table in tables.items()], ignore_index=True, sort=False)
    st.download_button("Telecharger les donnees en CSV", export.to_csv(index=False).encode("utf-8"), f"mfc-export-{date.today().isoformat()}.csv", "text/csv", width="stretch")
    st.info("Compatible Streamlit Cloud: app.py, requirements.txt et .streamlit/config.toml.")
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
    page = nav()
    pages = {
        "Tableau de bord": dashboard_page,
        "Candidatures": applications_page,
        "Bibliotheque": resources_page,
        "Calendrier": calendar_page,
        "Objectifs": goals_page,
        "Contacts": contacts_page,
        "Statistiques": statistics_page,
        "Parametres": settings_page,
    }
    pages[page]()


if __name__ == "__main__":
    main()
