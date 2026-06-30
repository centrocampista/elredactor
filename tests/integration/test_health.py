
from typing import Any, NamedTuple

import pytest

class ExpextedResponse(NamedTuple):
    status_code: int
    body: dict[str, Any]

@pytest.mark.parametrize(
    'expected_response',
    [
        ( ExpextedResponse(status_code=200, body={'status': 'ok'}))
    ]
)
@pytest.mark.integration
async def test_health_positive(test_client, test_settings, expected_response):
    if test_settings.environment == 'development':
        expected_response.body['environment'] = test_settings.environment
        expected_response.body['debug'] = test_settings.debug
    response = test_client.get("/health")
    assert response.status_code == expected_response.status_code
    assert response.json() == expected_response.body