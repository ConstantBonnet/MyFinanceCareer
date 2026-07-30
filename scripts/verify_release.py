from __future__ import annotations

import os
import py_compile
import sqlite3
import subprocess
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
]
REQUIRED_TABLES = ["applications", "resources", "events", "goals", "contacts"]


def check(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAILED: {message}")
    print(f"OK: {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def git_ls_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return set(result.stdout.splitlines())


def main() -> None:
    for path in REQUIRED_FILES:
        check((ROOT / path).is_file(), f"{path} exists")

    requirements = read("requirements.txt")
    check("streamlit" in requirements, "requirements.txt includes Streamlit")
    check("pandas" in requirements, "requirements.txt includes Pandas")

    gitignore = read(".gitignore")
    check("mfc_data.sqlite3" in gitignore, "local SQLite database is ignored")
    check(".venv/" in gitignore, "local virtual environment is ignored")

    tracked_files = git_ls_files()
    check("mfc_data.sqlite3" not in tracked_files, "local SQLite database is not tracked")
    check(not any(path.startswith(".venv/") for path in tracked_files), "virtual environment is not tracked")

    with tempfile.TemporaryDirectory(prefix="mfc_pycache_") as pycache_dir:
        py_compile.compile(
            str(ROOT / "app.py"),
            cfile=str(Path(pycache_dir) / "app.pyc"),
            doraise=True,
        )
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

    print("Release verification passed.")


if __name__ == "__main__":
    main()
