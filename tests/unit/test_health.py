from unittest.mock import patch

import pytest

from app.api.v1.routers.health import health


@pytest.mark.parametrize(
    "environment, is_dev, is_staging, is_prod, debug, expected_response",
    [
        (
            "development",
            True,
            False,
            False,
            True,
            {"status": "ok", "environment": "development", "debug": True},
        ),
        ("staging", False, True, False, False, {"status": "ok"}),
        ("production", False, False, True, False, {"status": "ok"}),
    ],
)
@pytest.mark.unit
async def test_health_positive(
    environment, is_dev, is_staging, is_prod, debug, expected_response
):
    with patch("app.api.v1.routers.health.settings") as mock_settings:
        mock_settings.environment = environment
        mock_settings.is_dev = is_dev
        mock_settings.is_staging = is_staging
        mock_settings.is_prod = is_prod
        mock_settings.debug = debug
        response = await health()

        response_dict = response.model_dump(exclude_none=True)
        assert response_dict == expected_response
        assert response_dict["status"] == "ok"
        assert len(response_dict.keys()) == len(expected_response.keys())
        if is_dev:
            assert len(response_dict.keys()) > 1
        else:
            assert len(response_dict.keys()) == 1
