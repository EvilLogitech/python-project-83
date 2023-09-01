import pytest
from page_analyzer.app import app as myapp


@pytest.fixture()
def app():
    testing_app = myapp
    testing_app.config['TESTING'] = True
    return testing_app


@pytest.fixture()
def client(app):
    return app.test_client()
