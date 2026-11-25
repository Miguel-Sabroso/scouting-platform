import pytest
from pydantic import ValidationError

from core.settings import Settings

REQUIRED_ENV = {
    "POSTGRES_USER": "scouting",
    "POSTGRES_PASSWORD": "p@ss:word/1",
    "POSTGRES_DB": "scouting",
}


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for key in [*REQUIRED_ENV, "POSTGRES_HOST", "POSTGRES_PORT"]:
        monkeypatch.delenv(key, raising=False)
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    return monkeypatch


def load() -> Settings:
    # _env_file=None: tests must not depend on the developer's local .env.
    return Settings(_env_file=None)


def test_reads_environment_and_defaults(env: pytest.MonkeyPatch) -> None:
    settings = load()

    assert settings.postgres_user == "scouting"
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432


def test_port_is_parsed_as_int(env: pytest.MonkeyPatch) -> None:
    env.setenv("POSTGRES_PORT", "5433")

    assert load().postgres_port == 5433


def test_password_is_hidden_in_repr(env: pytest.MonkeyPatch) -> None:
    assert "p@ss:word/1" not in repr(load())


def test_database_url_escapes_special_characters(env: pytest.MonkeyPatch) -> None:
    assert load().database_url == "postgresql://scouting:p%40ss%3Aword%2F1@localhost:5432/scouting"


def test_missing_required_variable_fails(env: pytest.MonkeyPatch) -> None:
    env.delenv("POSTGRES_PASSWORD")

    with pytest.raises(ValidationError):
        load()
