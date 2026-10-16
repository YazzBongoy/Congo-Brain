"""Guardrail: the test suite must use a private, per-process database.

These tests encode the isolation contract fixed in MIAA-9. They fail if the suite is
ever pointed back at the shared, repo-relative ``test_congo_brain.db`` file that two
concurrent pytest processes used to race on.
"""

import os
from pathlib import Path


def test_database_url_points_at_a_private_per_process_file() -> None:
    database_url = os.environ["DATABASE_URL"]

    assert database_url.startswith("sqlite:///"), database_url
    database_path = Path(database_url.removeprefix("sqlite:///"))

    assert str(os.getpid()) in database_path.name, database_path
    assert database_path.parent != Path.cwd(), database_path


def test_no_shared_repo_database_file_is_created() -> None:
    # The application defaults to ``congo_brain.db`` and the old conftest used
    # ``test_congo_brain.db``; neither may be created in the working tree.
    assert not (Path.cwd() / "congo_brain.db").exists()
    assert not (Path.cwd() / "test_congo_brain.db").exists()
