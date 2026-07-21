from unittest.mock import patch
import uuid

import pytest


@pytest.mark.integration
def test_upload_document_pdf(tmp_path, test_client, sample_pdf):
    with patch("app.api.v1.routers.documents.UPLOAD_DIR", tmp_path):
        response = test_client.post(
            "/v1/documents/upload",
            files={"file": ("test.pdf", sample_pdf, "application/pdf")},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "test.pdf"
    assert body["extension"] == ".pdf"
    assert body["status"] == "pending"
    assert uuid.UUID(body["document_id"])
    saved_file = tmp_path / f"{body['document_id']}{body['extension']}"

    assert saved_file.exists()
    assert saved_file.read_bytes() == sample_pdf
