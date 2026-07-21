import pytest

from app.config import Settings


@pytest.mark.parametrize(
    "settings_parameters, expected_results",
    [
        (
            {
                "postgres_user": "x",
                "postgres_password": "x",
                "postgres_db": "x",
                "qdrant_service_http_port": "6333",
                "qdrant_service_grpc_port": "6334",
                "qdrant_service_api_key": "x",
                "qdrant_service_read_only_api_key": "x",
                "environment": "development",
            },
            {"is_dev": True, "is_prod": False, "is_staging": False},
        ),
        (
            {
                "postgres_user": "x",
                "postgres_password": "x",
                "postgres_db": "x",
                "qdrant_service_http_port": "6333",
                "qdrant_service_grpc_port": "6334",
                "qdrant_service_api_key": "x",
                "qdrant_service_read_only_api_key": "x",
                "environment": "staging",
            },
            {"is_dev": False, "is_prod": False, "is_staging": True},
        ),
        (
            {
                "postgres_user": "x",
                "postgres_password": "x",
                "postgres_db": "x",
                "qdrant_service_http_port": "6333",
                "qdrant_service_grpc_port": "6334",
                "qdrant_service_api_key": "x",
                "qdrant_service_read_only_api_key": "x",
                "environment": "production",
            },
            {"is_dev": False, "is_prod": True, "is_staging": False},
        ),
    ],
)
@pytest.mark.unit
def test_environemnt_flag_positive(settings_parameters, expected_results):
    s = Settings(**settings_parameters)
    assert s.is_dev == expected_results.get("is_dev")
    assert s.is_prod == expected_results.get("is_prod")
    assert s.is_staging == expected_results.get("is_staging")
