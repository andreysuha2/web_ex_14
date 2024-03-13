def test_create_contact(client, contact):
    response = client.post(
        "/api/contacts",
        json=contact
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == contact.get("first_name")
    assert "id" in data

def test_list_contacts(client):
    response = client.get("/api/contacts")
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) == list
    assert len(data) == 1
    assert "id" in data[0]

def test_get_contact(client, contact):
    response = client.get("/api/contacts/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == contact.get("first_name")
    assert "id" in data

def test_get_contact_not_found(client):
    response = client.get("/api/contacts/2")
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Not found"

def test_put_contact(client, updated_contact):
    response = client.put("/api/contacts/1", json=updated_contact)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == updated_contact.get("first_name")
    assert data["last_name"] == updated_contact.get("last_name")
    assert data["additional_data"] == updated_contact.get("additional_data")
    assert "id" in data

def test_put_contact_not_found(client, updated_contact):
    response = client.put("/api/contacts/2", json=updated_contact)
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Not found"

def test_delete_contact(client, updated_contact):
    response = client.delete("/api/contacts/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == updated_contact.get("first_name")
    assert "id" in data

def test_delete_contact_not_found(client):
    response = client.delete("/api/contacts/1")
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Not found"

