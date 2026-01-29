"""
API endpoint tests for TransUnion PDF to JSON API.

Tests all API endpoints including health checks and PDF parsing.
"""

import os
import pytest
from io import BytesIO
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint returns healthy status."""
        response = test_client.get("/v1/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API information."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
        assert "/docs" in data["docs"]


class TestParseEndpoint:
    """Tests for the PDF parsing endpoint."""
    
    def test_parse_without_file(self, test_client):
        """Test parse endpoint without providing a file."""
        response = test_client.post("/v1/parse")
        
        # Should return 422 Unprocessable Entity (missing required field)
        assert response.status_code == 422
    
    def test_parse_with_invalid_file_type(self, test_client):
        """Test parse endpoint with non-PDF file."""
        files = {
            "file": ("test.jpg", b"fake image content", "image/jpeg")
        }
        response = test_client.post("/v1/parse", files=files)
        
        # Should return 400 Bad Request
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "pdf" in response.json()["detail"].lower()
    
    def test_parse_with_empty_file(self, test_client, sample_empty_file):
        """Test parse endpoint with empty PDF file."""
        files = {
            "file": ("empty.pdf", sample_empty_file, "application/pdf")
        }
        response = test_client.post("/v1/parse", files=files)
        
        # Should return 400 Bad Request or 500 depending on validation
        assert response.status_code in [400, 500]
        assert "detail" in response.json()
    
    def test_parse_with_invalid_pdf(self, test_client, sample_invalid_pdf):
        """Test parse endpoint with invalid PDF content."""
        files = {
            "file": ("invalid.pdf", sample_invalid_pdf, "application/pdf")
        }
        response = test_client.post("/v1/parse", files=files)
        
        # Should return 500 Internal Server Error (PDF parsing error)
        assert response.status_code == 500
        assert "detail" in response.json()
    
    @pytest.mark.skipif(
        not os.path.exists("tests/test_files/test_credit_report.pdf"),
        reason="Test PDF file not available"
    )
    def test_parse_with_valid_pdf(self, test_client, test_pdf_path):
        """Test parse endpoint with a valid credit report PDF."""
        with open(test_pdf_path, "rb") as f:
            files = {
                "file": ("credit_report.pdf", f, "application/pdf")
            }
            response = test_client.post("/v1/parse", files=files)
        
        # Should return 200 OK with parsed data
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "inquirer" in data
        assert "personal_data" in data
        assert "score" in data
        
        # Verify PII scrubbing was applied
        if "identification" in data["personal_data"]:
            id_value = data["personal_data"]["identification"]
            assert "X" in id_value or "*" in id_value  # Should be masked
    
    def test_parse_large_file(self, test_client):
        """Test parse endpoint with a large file."""
        # Create a 15MB file (larger than typical PDF)
        large_content = b"0" * (15 * 1024 * 1024)
        files = {
            "file": ("large.pdf", large_content, "application/pdf")
        }
        response = test_client.post("/v1/parse", files=files)
        
        # Should either reject (413) or handle it (400/500)
        assert response.status_code in [413, 400, 500]
    
    def test_parse_response_schema(self, test_client, sample_invalid_pdf):
        """Test that error responses have correct schema."""
        files = {
            "file": ("invalid.pdf", sample_invalid_pdf, "application/pdf")
        }
        response = test_client.post("/v1/parse", files=files)
        
        # All errors should have 'detail' field
        assert "detail" in response.json()
        assert isinstance(response.json()["detail"], str)


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""
    
    def test_swagger_docs_available(self, test_client):
        """Test that Swagger UI is accessible."""
        response = test_client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_available(self, test_client):
        """Test that ReDoc is accessible."""
        response = test_client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_openapi_schema_available(self, test_client):
        """Test that OpenAPI schema is accessible."""
        response = test_client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "TransUnion PDF to JSON API"
        assert schema["info"]["version"] == "1.0.0"


class TestConcurrentRequests:
    """Tests for concurrent API requests."""
    
    def test_concurrent_health_checks(self, test_client):
        """Test multiple concurrent health check requests."""
        import concurrent.futures
        
        def make_health_request():
            return test_client.get("/v1/health")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_health_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        assert all(r.json()["status"] == "healthy" for r in responses)
    
    @pytest.mark.skipif(
        not os.path.exists("tests/test_files/test_credit_report.pdf"),
        reason="Test PDF file not available"
    )
    def test_concurrent_parse_requests(self, test_client, test_pdf_path):
        """Test multiple concurrent parse requests."""
        import concurrent.futures
        
        def make_parse_request():
            with open(test_pdf_path, "rb") as f:
                files = {"file": ("credit_report.pdf", f, "application/pdf")}
                return test_client.post("/v1/parse", files=files)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_parse_request) for _ in range(3)]
            responses = [future.result() for future in futures]
        
        # All requests should complete (either success or expected error)
        assert all(r.status_code in [200, 400, 500] for r in responses)


class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_parse_with_malformed_request(self, test_client):
        """Test parse endpoint with malformed request."""
        # Send request with wrong field name
        response = test_client.post(
            "/v1/parse",
            files={"wrong_field": ("test.pdf", b"content", "application/pdf")}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_parse_with_multiple_files(self, test_client):
        """Test parse endpoint with multiple files (should only accept one)."""
        files = [
            ("file", ("test1.pdf", b"content1", "application/pdf")),
            ("file", ("test2.pdf", b"content2", "application/pdf"))
        ]
        response = test_client.post("/v1/parse", files=files)
        
        # Should process or reject appropriately
        assert response.status_code in [200, 400, 422, 500]
    
    def test_invalid_endpoint(self, test_client):
        """Test accessing non-existent endpoint."""
        response = test_client.get("/v1/nonexistent")
        
        assert response.status_code == 404
    
    def test_wrong_http_method(self, test_client):
        """Test using wrong HTTP method on parse endpoint."""
        response = test_client.get("/v1/parse")
        
        # Should return 405 Method Not Allowed
        assert response.status_code == 405
