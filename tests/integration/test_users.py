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


@pytest.mark.parametrize(
    "payload",
    [
        (
            {
                "first_name": "Jan",
                "last_name": "Kowalski",
            }
        ),
        (
            {
                "some_name": "Jan",
                "some_surname": "Kowalski",
            }
        ),
        ({}),
    ],
)
@pytest.mark.integration
async def test_create_user_invalid_payload(client_httpx, payload):
    response = await client_httpx.post("/v1/users", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        (
            {
                "first_name": "Jan",
                "last_name": "Kowalski",
                "email": "wrong=example.com",
            }
        ),
    ],
)
@pytest.mark.integration
async def test_create_user_invalid_email(client_httpx, payload):
    response = await client_httpx.post("/v1/users", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        (
            {
                "first_name": "Jan",
                "last_name": "Kowalski",
                "email": "jan@example.com",
            }
        ),
    ],
)
@pytest.mark.integration
async def test_create_user_duplicate_email(client_httpx, payload):
    response = await client_httpx.post("/v1/users", json=payload)

    assert response.status_code == 201
    response = await client_httpx.post("/v1/users", json=payload)
    assert response.status_code == 409

@pytest.mark.parametrize(
    "create_user_payload, update_user_payload",
    [
        (
            {
                "first_name": "Jan",
                "last_name": "Kowalski",
                "email": "jan@example.com",
            },
            {
                "first_name": "John",
                "last_name": "Kowalski",
                "email": "jan@example.com",
            },
        ),
        (
            {
                "first_name": "Jan",
                "last_name": "Kowalski",
                "email": "jan@example.com",
            },
            {
                "last_name": "Smith",
                "email": "jan@example.com",
            },
        ),
    ],
)
@pytest.mark.integration
async def test_update_user(client_httpx, create_user_payload, update_user_payload):
    first_name = update_user_payload['first_name'] if update_user_payload.get('first_name') is not None else create_user_payload['first_name']
    last_name = update_user_payload['last_name'] if update_user_payload.get('last_name') is not None else create_user_payload['last_name']
    response = await client_httpx.post("/v1/users", json=create_user_payload)
    assert response.status_code == 201
    response = await client_httpx.patch("/v1/users", json=update_user_payload)
    assert response.status_code == 200
    body = response.json()
    assert body['first_name'] == first_name
    assert body['last_name'] == last_name