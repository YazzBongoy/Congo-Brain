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


def test_no_shared_repo_database_file_is_created(repo_database_baseline: dict[str, int | None]) -> None:
    # Only files *created by this session* are a violation. A root-level database that
    # predates the run (a developer ran the app locally) is irrelevant to isolation.
    for name, baseline_mtime_ns in repo_database_baseline.items():
        path = Path.cwd() / name
        if baseline_mtime_ns is None:
            assert not path.exists(), f"{name} was created in the working tree during the test run"
        else:
            assert path.exists(), f"{name} disappeared during the test run"
            assert path.stat().st_mtime_ns == baseline_mtime_ns, f"{name} was modified during the test run"
