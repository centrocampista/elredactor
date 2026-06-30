from unittest.mock import patch

import pytest

from app.main import health

@pytest.mark.parametrize(
    'environment, is_dev, is_staging, is_prod, debug, expected_response', [
        ('development', True, False, False, True, 
         {'status': 'ok', 'environment': 'development', 'debug': True}
         ),
        ('staging', False, True, False, False, 
         {'status': 'ok'}),
        ('production', False, False, True, False, 
         {'status': 'ok'}),
    ]
)
@pytest.mark.unit
async def test_health_positive(environment, is_dev, is_staging, is_prod, debug, expected_response):
    with patch('app.main.settings') as mock_settings:
        mock_settings.environment = environment
        mock_settings.is_dev = is_dev
        mock_settings.is_staging = is_staging
        mock_settings.is_prod = is_prod
        mock_settings.debug = debug
        response = await health()
        assert response == expected_response
        assert response['status'] == 'ok'
        assert len(response.keys()) == len(expected_response.keys())
        if is_dev:
            assert len(response.keys()) > 1
        else:
            assert len(response.keys()) == 1
            