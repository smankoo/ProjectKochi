# manage.py
import pytest
@manager.command
def test():
    """Runs the tests."""
    pytest.main(["-s", "tests"])