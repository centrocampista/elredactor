
from typing import NamedTuple
from unittest.mock import patch

import pytest

from tests.integration.conftest import SettingsMock

class ExpextedResponse(NamedTuple):
    status: str
    debug: bool | None
    environment: bool | None

@pytest.mark.parametrize(
    'case_setings, expected_response',
    [
        ( SettingsMock(environment='development',
            is_dev=True, is_staging=False, is_prod=False, debug=True),
            ExpextedResponse(status='ok', environment='development', debug=True)
            ),
        ( SettingsMock(environment='staging',
            is_dev=False, is_staging=True, is_prod=False, debug=False),
            ExpextedResponse(status='ok')
            ),
        ( SettingsMock(environment='production',
            is_dev=False, is_staging=False, is_prod=True, debug=False),
            ExpextedResponse(status='ok')
            ),
    ]
)
@pytest.mark.unit
async def test_health_positive(test_client, case_setings, expected_response):
    with patch('app.main.settings') as mock_settings: