import pytest


@pytest.mark.integration
async def test_create_user(client_httpx):
    response = await client_httpx.post(
        "/v1/users",
        json={
            "first_name": "Jan",
            "last_name": "Kowalski",
            "email": "jan@example.com",
        },
    )
    assert response.status_code == 201
