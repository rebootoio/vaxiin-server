import sys
import pathlib
import pytest

from app.config import configure_app
from app.helpers.db import get_test_db

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent) + '/app')

from app.vaxiin_server import create_app, create_db  # noqa: E402


@pytest.fixture()
def app():
    app = create_app()
    configure_app(app)
    app.config.update({
        "TESTING": True,
    })
    engine, session = get_test_db()
    create_db(app, engine, session)

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()
