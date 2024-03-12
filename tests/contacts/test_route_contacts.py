from unittest.mock import MagicMock
from users.models import User


def test_create_contact(client, contact):
    with client as c:
        response = c.post(
            "/api/contacts",
            json=contact
        )
        data = response.json()
        assert data["contact"]["first_name"] == contact.get("first_name")
        assert "id" in data["contact"]