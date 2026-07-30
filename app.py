from __future__ import annotations

import sqlite3
import html
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


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_sql(sql: str, values: tuple[Any, ...] = ()) -> None:
    with closing(connect()) as conn:
        conn.execute(sql, values)
        conn.commit()


def df(sql: str, values: tuple[Any, ...] = ()) -> pd.DataFrame:
    with closing(connect()) as conn:
        return pd.read_sql_query(sql, conn, params=values)


def init_db() -> None:
    with closing(connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL, role TEXT NOT NULL, field TEXT NOT NULL,
                location TEXT, contract_type TEXT, status TEXT NOT NULL, priority TEXT NOT NULL,
                deadline TEXT, sent_date TEXT, next_action TEXT, follow_up_date TEXT,
                offer_link TEXT, cv_link TEXT, cover_letter_link TEXT, contacts TEXT, notes TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, category TEXT NOT NULL, field TEXT, tags TEXT,
                link TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, event_type TEXT NOT NULL, event_date TEXT NOT NULL,
                related_company TEXT, priority TEXT NOT NULL, notes TEXT,
                done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, field TEXT, due_date TEXT, progress INTEGER NOT NULL,
                status TEXT NOT NULL, next_step TEXT, notes TEXT, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, company TEXT, role TEXT, relation_type TEXT, linkedin TEXT,
                email TEXT, last_interaction TEXT, next_follow_up TEXT,
                associated_company TEXT, notes TEXT, created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


def empty(table: str) -> bool:
    with closing(connect()) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


def seed_demo() -> None:
    if not empty("applications"):
        return
    today = date.today()
    now = datetime.utcnow().isoformat(timespec="seconds")
    applications = [
        ("Rothschild & Co", "M&A Intern - Paris", "Investment Banking", "Paris", "Stage", "Entretien", "Haute", 12, -8, "Preparer les questions techniques", 2, "Claire Martin"),
        ("Ardian", "Private Equity Analyst Intern", "Private Equity", "Paris", "Stage", "A preparer", "Haute", 7, None, "Adapter la lettre et trouver deux alumni", 1, ""),
        ("Amundi", "Portfolio Assistant", "Asset Management", "Paris", "Stage", "Envoyee", "Moyenne", 20, -3, "Relancer si pas de reponse", 6, ""),
        ("BNP Paribas CIB", "Global Markets Summer Intern", "Markets", "London", "Stage", "Tests", "Moyenne", 3, -5, "Finaliser test numerique", 0, ""),
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
                    contacts,
                    "Donnees de demonstration finance.",
                    now,
                )
                for company, role, field, location, contract, status, priority, deadline, sent, action, follow, contacts in applications
            ],
        )
        conn.executemany(
            "INSERT INTO resources (title, category, field, tags, link, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("CV Finance - version M&A", "CV", "Investment Banking", "cv, m&a, paris", "https://drive.google.com/", "Version orientee transaction.", now),
                ("400 questions techniques finance", "Preparation entretien", "Investment Banking", "valuation, accounting", "https://www.wallstreetprep.com/", "Support de revision entretien.", now),
                ("Liste alumni finance", "Site utile", "Financial Advisory", "networking, alumni", "https://www.linkedin.com/", "Base pour les prises de contact.", now),
            ],
        )
        conn.executemany(
            "INSERT INTO events (title, event_type, event_date, related_company, priority, notes, done, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Entretien Rothschild", "Entretien", (today + timedelta(days=3)).isoformat(), "Rothschild & Co", "Haute", "Reviser DCF et comparables.", 0, now),
                ("Relance Amundi", "Relance", (today + timedelta(days=6)).isoformat(), "Amundi", "Moyenne", "Message court et professionnel.", 0, now),
                ("Deadline Ardian", "Deadline", (today + timedelta(days=7)).isoformat(), "Ardian", "Haute", "Envoyer CV et lettre adaptee.", 0, now),
            ],
        )
        conn.executemany(
            "INSERT INTO goals (title, field, due_date, progress, status, next_step, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Obtenir un stage M&A a Paris", "Investment Banking", (today + timedelta(days=60)).isoformat(), 45, "En cours", "Envoyer 5 candidatures ciblees", "Priorite aux boutiques et banques.", now),
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


def parse_day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def fmt(value: Any) -> str:
    parsed = parse_day(value)
    return parsed.strftime("%d/%m/%Y") if parsed else "-"


def setup_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":briefcase:", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background: #f6f8f7; }
        section[data-testid="stSidebar"] { background: #172026; }
        section[data-testid="stSidebar"] * { color: #f7fbfb; }
        .block-container { max-width: 1380px; padding-top: 1.5rem; }
        div[data-testid="stMetric"] {
            background: #fff; border: 1px solid #dce3e7; border-radius: 8px;
            padding: 14px 16px; box-shadow: 0 10px 24px rgba(23,32,38,.05);
        }
        .mfc-card {
            background: #fff; border: 1px solid #dce3e7; border-radius: 8px;
            padding: 14px 16px; margin-bottom: 10px; min-height: 120px;
        }
        .muted { color: #5d6b73; font-size: .92rem; white-space: pre-line; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def nav() -> str:
    st.sidebar.title("MFC")
    st.sidebar.caption("My Finance Career")
    page = st.sidebar.radio(
        "Navigation",
        ["Tableau de bord", "Candidatures", "Bibliotheque", "Calendrier", "Objectifs", "Contacts", "Statistiques", "Parametres"],
    )
    st.sidebar.divider()
    st.sidebar.caption("MVP Streamlit avec stockage SQLite local et documents sous forme de liens.")
    return page


def card(title: str, body: str, chips: list[Any] | None = None) -> None:
    chip_text = " | ".join(html.escape(str(item)) for item in chips or [] if item)
    safe_title = html.escape(str(title))
    safe_body = html.escape(str(body))
    st.markdown(
        f"<div class='mfc-card'><strong>{safe_title}</strong><div class='muted'>{safe_body}</div><div class='muted'>{chip_text}</div></div>",
        unsafe_allow_html=True,
    )


def applications() -> pd.DataFrame:
    return df("SELECT * FROM applications ORDER BY created_at DESC, id DESC")


def resources() -> pd.DataFrame:
    return df("SELECT * FROM resources ORDER BY created_at DESC, id DESC")


def events() -> pd.DataFrame:
    return df("SELECT * FROM events ORDER BY event_date ASC, id DESC")


def goals() -> pd.DataFrame:
    return df("SELECT * FROM goals ORDER BY due_date ASC, id DESC")


def contacts() -> pd.DataFrame:
    return df("SELECT * FROM contacts ORDER BY next_follow_up ASC, id DESC")


def application_form() -> None:
    with st.form("application_form", clear_on_submit=True):
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


def resource_form() -> None:
    with st.form("resource_form", clear_on_submit=True):
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


def event_form() -> None:
    with st.form("event_form", clear_on_submit=True):
        title = st.text_input("Titre")
        event_type = st.selectbox("Type", EVENT_TYPES)
        event_date = st.date_input("Date", value=date.today() + timedelta(days=7))
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
    st.title("My Finance Career")
    st.caption("Un centre de controle pour suivre candidatures, entretiens, ressources, contacts et objectifs sans se disperser.")
    apps, evs, gls = applications(), events(), goals()
    today = date.today()
    upcoming = evs[evs["event_date"].apply(lambda value: (parse_day(value) or date.min) >= today)] if not evs.empty else evs
    urgent = apps[apps["follow_up_date"].apply(lambda value: parse_day(value) is not None and parse_day(value) <= today + timedelta(days=3))] if not apps.empty else apps

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Candidatures", len(apps))
    c2.metric("Envoyees", int((apps["status"] == "Envoyee").sum()) if not apps.empty else 0)
    c3.metric("Entretiens", int((apps["status"] == "Entretien").sum()) if not apps.empty else 0)
    c4.metric("Echeances 14 jours", len(upcoming.head(14)))

    left, middle, right = st.columns([1.1, 1, 1])
    with left:
        st.subheader("A traiter maintenant")
        for _, row in urgent.head(4).iterrows():
            card(f"{row.company} - {row.role}", row.next_action or "Action a definir", [row.status, row.priority, fmt(row.follow_up_date)])
    with middle:
        st.subheader("Prochaines echeances")
        for _, row in upcoming.head(5).iterrows():
            card(row.title, row.notes or row.related_company or "", [row.event_type, fmt(row.event_date), row.priority])
    with right:
        st.subheader("Objectifs")
        for _, row in gls.head(4).iterrows():
            st.write(f"**{row.title}**")
            st.progress(int(row.progress) / 100)
            st.caption(f"{row.progress}% - {row.next_step or 'prochaine etape a definir'}")

    st.subheader("Raccourcis")
    a, b, c = st.columns(3)
    with a.expander("Ajouter une candidature"):
        application_form()
    with b.expander("Ajouter un evenement"):
        event_form()
    with c.expander("Ajouter une ressource"):
        resource_form()


def applications_page() -> None:
    st.title("Candidatures")
    st.caption("Pipeline Kanban et liste filtrable pour les stages et premiers emplois en finance.")
    application_form()
    st.divider()
    apps = applications()
    search, field_choice, priority_choice = st.columns([1.4, 1, 1])
    query = search.text_input("Recherche")
    field = field_choice.selectbox("Domaine", ["Tous"] + FIELDS)
    priority = priority_choice.selectbox("Priorite", ["Toutes"] + PRIORITIES)
    filtered = apps.copy()
    if query:
        filtered = filtered[filtered.apply(lambda row: query.lower() in " ".join(row.astype(str)).lower(), axis=1)]
    if field != "Tous":
        filtered = filtered[filtered["field"] == field]
    if priority != "Toutes":
        filtered = filtered[filtered["priority"] == priority]

    st.subheader("Vue Kanban")
    cols = st.columns(len(STATUSES))
    for col, status in zip(cols, STATUSES):
        with col:
            st.markdown(f"**{status}**")
            rows = filtered[filtered["status"] == status]
            st.caption("Vide" if rows.empty else "")
            for _, row in rows.iterrows():
                card(row.company, f"{row.role}\n{row.next_action or ''}", [row.field, row.priority, fmt(row.deadline)])

    st.subheader("Vue liste")
    st.dataframe(filtered.drop(columns=["id", "created_at"], errors="ignore"), width="stretch", hide_index=True)
    with st.expander("Mettre a jour une candidature"):
        options = {f"{row.company} - {row.role}": int(row.id) for _, row in apps.iterrows()}
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
    st.title("Bibliotheque")
    resource_form()
    st.divider()
    items = resources()
    query = st.text_input("Recherche bibliotheque")
    if query:
        items = items[items.apply(lambda row: query.lower() in " ".join(row.astype(str)).lower(), axis=1)]
    cols = st.columns(3)
    for index, (_, row) in enumerate(items.iterrows()):
        with cols[index % 3]:
            card(row.title, row.description or "", [row.category, row.field, row.tags])
            st.link_button("Ouvrir le lien", row.link, width="stretch")


def calendar_page() -> None:
    st.title("Calendrier")
    event_form()
    st.divider()
    evs = events()
    evs["date_affichee"] = evs["event_date"].apply(fmt)
    evs["etat"] = evs["done"].map({0: "A faire", 1: "Termine"})
    st.dataframe(evs[["date_affichee", "title", "event_type", "related_company", "priority", "etat", "notes"]], width="stretch", hide_index=True)


def goals_page() -> None:
    st.title("Objectifs")
    with st.form("goal_form", clear_on_submit=True):
        title = st.text_input("Objectif")
        field = st.selectbox("Domaine", [""] + FIELDS)
        due = st.date_input("Echeance", value=date.today() + timedelta(days=30))
        progress = st.slider("Progression", 0, 100, 10)
        status = st.selectbox("Statut", GOAL_STATUSES)
        next_step = st.text_input("Prochaine etape")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Ajouter l'objectif", width="stretch")
    if submitted and title:
        run_sql("INSERT INTO goals (title, field, due_date, progress, status, next_step, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (title, field, due.isoformat(), progress, status, next_step, notes, datetime.utcnow().isoformat(timespec="seconds")))
        st.success("Objectif ajoute.")
        st.rerun()
    for _, row in goals().iterrows():
        st.write(f"**{row.title}**")
        st.progress(int(row.progress) / 100)
        st.caption(f"{row.status} - {row.field or 'general'} - echeance {fmt(row.due_date)} - {row.next_step or 'prochaine etape a definir'}")


def contacts_page() -> None:
    st.title("Contacts")
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
    if submitted and name:
        run_sql(
            "INSERT INTO contacts (name, company, role, relation_type, linkedin, email, last_interaction, next_follow_up, associated_company, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, company, role, relation, linkedin, email, last.isoformat(), follow.isoformat(), associated, notes, datetime.utcnow().isoformat(timespec="seconds")),
        )
        st.success("Contact ajoute.")
        st.rerun()
    st.dataframe(contacts().drop(columns=["id", "created_at"], errors="ignore"), width="stretch", hide_index=True)


def statistics_page() -> None:
    st.title("Statistiques")
    apps, gls = applications(), goals()
    sent_base = max(len(apps[apps["status"] != "Entreprise cible"]), 1) if not apps.empty else 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total candidatures", len(apps))
    c2.metric("Taux entretien", f"{(apps['status'] == 'Entretien').sum() / sent_base:.0%}" if not apps.empty else "0%")
    c3.metric("Offres", int((apps["status"] == "Offre").sum()) if not apps.empty else 0)
    c4.metric("Actions a suivre", int(apps["follow_up_date"].notna().sum()) if not apps.empty else 0)
    left, right = st.columns(2)
    with left:
        st.subheader("Candidatures par statut")
        st.bar_chart(apps["status"].value_counts().reindex(STATUSES, fill_value=0) if not apps.empty else pd.Series(dtype=int))
    with right:
        st.subheader("Candidatures par domaine")
        st.bar_chart(apps["field"].value_counts() if not apps.empty else pd.Series(dtype=int))
    st.subheader("Progression des objectifs")
    st.bar_chart(gls.set_index("title")["progress"] if not gls.empty else pd.Series(dtype=int))


def settings_page() -> None:
    st.title("Parametres")
    tables = {"applications": applications(), "resources": resources(), "events": events(), "goals": goals(), "contacts": contacts()}
    export = pd.concat([table.assign(table=name) for name, table in tables.items()], ignore_index=True, sort=False)
    st.download_button("Telecharger les donnees en CSV", export.to_csv(index=False).encode("utf-8"), f"mfc-export-{date.today().isoformat()}.csv", "text/csv", width="stretch")
    st.info("Le projet est pret pour Streamlit Community Cloud avec app.py, requirements.txt et .streamlit/config.toml.")


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
