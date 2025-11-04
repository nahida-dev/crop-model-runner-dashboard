import pathlib
import sys
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="client")
def client_fixture(monkeypatch):
    # Make repo root importable (…/model-runner/)
    ROOT = pathlib.Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    import backend.models.db_models  # Ensure tables registered

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    SQLModel.metadata.create_all(test_engine)

    import backend.db as db
    monkeypatch.setattr(db, "engine", test_engine, raising=True)

    from backend.main import app, get_current_user
    app.dependency_overrides[get_current_user] = lambda: "scientist@corteva.internal"

    return TestClient(app)
