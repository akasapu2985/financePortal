from db.connection import build_connection_string


def test_build_connection_string_uses_expected_env_vars(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_HOST", "db.local")
    monkeypatch.setenv("POSTGRES_PORT", "5439")
    monkeypatch.setenv("POSTGRES_DB", "markets")
    monkeypatch.setenv("POSTGRES_USER", "finance")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss word")

    assert (
        build_connection_string()
        == "postgresql://finance:p%40ss+word@db.local:5439/markets"
    )
