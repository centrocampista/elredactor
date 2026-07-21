from unittest.mock import patch
import uuid

import pytest

FAKE_MAX_FILE_SIZE = 100


@pytest.mark.parametrize(
    "file_configuration",
    [
        (
            {
                "filename": "test.pdf",
                "extension": ".pdf",
                "content_type": "application/pdf",
            }
        ),
        ({"filename": "test.txt", "extension": ".txt", "content_type": "text/plain"}),
        ({"filename": "test.md", "extension": ".md", "content_type": "text/markdown"}),
        (
            {
                "filename": "test.docx",
                "extension": ".docx",
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            }
        ),
    ],
)
@pytest.mark.integration
def test_upload_document(
    tmp_path,
    test_client,
    sample_pdf,
    sample_txt,
    sample_md,
    sample_docx,
    file_configuration,
):

    if file_configuration["extension"] == ".pdf":
        file_content = sample_pdf
    elif file_configuration["extension"] == ".txt":
        file_content = sample_txt
    elif file_configuration["extension"] == ".md":
        file_content = sample_md
    elif file_configuration["extension"] == ".docx":
        file_content = sample_docx

    with patch("app.api.v1.routers.documents.UPLOAD_DIR", tmp_path):
        response = test_client.post(
            "/v1/documents/upload",
            files={
                "file": (
                    file_configuration["filename"],
                    file_content,
                    file_configuration["content_type"],
                )
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == file_configuration["filename"]
    assert body["extension"] == file_configuration["extension"]
    assert body["status"] == "pending"
    assert uuid.UUID(body["document_id"])
    saved_file = tmp_path / f"{body['document_id']}{body['extension']}"

    assert saved_file.exists()
    assert saved_file.read_bytes() == file_content


@pytest.mark.integration
def test_upload_invalid_document(tmp_path, test_client):

    with patch("app.api.v1.routers.documents.UPLOAD_DIR", tmp_path):
        response = test_client.post(
            "v1/documents/upload",
            files={"file": ("test.mp3", b"audio content", "audio/mp3")},
        )

    assert response.status_code == 415


@pytest.mark.integration
def test_upload_too_large_document(tmp_path, test_client):
    with patch("app.api.v1.routers.documents.UPLOAD_DIR", tmp_path):
        with patch("app.api.v1.routers.documents.MAX_FILE_SIZE", FAKE_MAX_FILE_SIZE):
            response = test_client.post(
                "v1/documents/upload",
                files={
                    "file": (
                        "test.pdf",
                        b"x" * (FAKE_MAX_FILE_SIZE + 1),
                        "application/pdf",
                    )
                },
            )

    assert response.status_code == 413


@pytest.mark.integration
def test_upload_without_file(test_client):
    response = test_client.post("v1/documents/upload")
    assert response.status_code == 422


@pytest.mark.integration
def test_upload_documment_to_missing_dir(tmp_path, test_client, sample_pdf):
    missing_dir = tmp_path / "missing_dir"
    with patch("app.api.v1.routers.documents.UPLOAD_DIR", missing_dir):
        response = test_client.post(
            "v1/documents/upload",
            files={"file": ("test.pdf", sample_pdf, "application/pdf")},
        )

    assert response.status_code == 201
    assert missing_dir.exists()
    body = response.json()
    saved_file = missing_dir / f"{body['document_id']}{body['extension']}"
    assert saved_file.exists()
