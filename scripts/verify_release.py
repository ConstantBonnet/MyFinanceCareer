from __future__ import annotations

import py_compile
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "app.py",
    "requirements.txt",
    "README.md",
    "DEPLOYMENT.md",
    ".streamlit/config.toml",
    "docs/PRODUCT_REFERENCE.md",
    "static/logo.png",
]
REQUIRED_TABLES = ["applications", "resources", "events", "goals", "contacts"]
REQUIRED_CONTACT_COLUMNS = {
    "profession_group",
    "seniority",
    "target_role",
    "status",
    "source",
    "contact_channel",
    "city",
    "priority",
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAILED: {message}")
    print(f"OK: {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    for path in REQUIRED_FILES:
        check((ROOT / path).is_file(), f"{path} exists")

    requirements = read("requirements.txt")
    check("streamlit" in requirements, "requirements.txt includes Streamlit")
    check("pandas" in requirements, "requirements.txt includes Pandas")
    check("openpyxl" in requirements, "requirements.txt includes OpenPyXL for Excel imports")

    gitignore = read(".gitignore")
    check("mfc_data.sqlite3" in gitignore, "local SQLite database is ignored")
    check(".DS_Store" in gitignore, "macOS metadata is ignored")

    with tempfile.TemporaryDirectory(prefix="mfc_pycache_") as pycache_dir:
        py_compile.compile(str(ROOT / "app.py"), cfile=str(Path(pycache_dir) / "app.pyc"), doraise=True)
        check(True, "app.py compiles")

    sys.path.insert(0, str(ROOT))
    import app

    with tempfile.TemporaryDirectory(prefix="mfc_release_") as tmpdir:
        app.DB_PATH = Path(tmpdir) / "mfc_test.sqlite3"
        app.init_db()
        app.seed_demo()
        with sqlite3.connect(app.DB_PATH) as conn:
            for table in REQUIRED_TABLES:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                check(count > 0, f"{table} demo data loads")
            contact_columns = {row[1] for row in conn.execute("PRAGMA table_info(contacts)").fetchall()}
            missing_columns = REQUIRED_CONTACT_COLUMNS - contact_columns
            check(not missing_columns, "contacts table includes network classification fields")
            profession_count = conn.execute("SELECT COUNT(DISTINCT profession_group) FROM contacts").fetchone()[0]
            check(profession_count >= 2, "network demo contacts are classified by profession")

    print("Release verification passed.")


if __name__ == "__main__":
    main()
