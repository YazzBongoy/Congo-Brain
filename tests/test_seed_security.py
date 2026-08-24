"""Security gates for demo seed credentials."""

from unittest.mock import Mock

from congo_brain.data import seed


def test_demo_users_are_not_seeded_outside_development(monkeypatch) -> None:
    database = Mock()
    monkeypatch.setattr(seed, "ENVIRONMENT", "production")

    seed._seed_users(database)

    database.query.assert_not_called()
