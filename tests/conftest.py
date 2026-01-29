"""
Test configuration and fixtures for TransUnion PDF to JSON API.

Provides shared test fixtures and utilities for all tests.
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def test_client():
    """
    FastAPI test client fixture.
    
    Returns:
        TestClient: FastAPI test client for making API requests
    """
    return TestClient(app)


@pytest.fixture
def test_files_dir():
    """
    Test files directory path.
    
    Returns:
        Path: Path to the test files directory
    """
    return Path(__file__).parent / "test_files"


@pytest.fixture
def test_pdf_path(test_files_dir):
    """
    Path to a test PDF file.
    
    Returns:
        Path: Path to test PDF file (if it exists)
    """
    pdf_path = test_files_dir / "test_credit_report.pdf"
    return pdf_path if pdf_path.exists() else None


@pytest.fixture
def test_output_dir():
    """
    Temporary directory for test outputs.
    
    Creates a temporary directory before tests and cleans up after.
    
    Yields:
        Path: Path to temporary test output directory
    """
    test_dir = Path(__file__).parent / "test_output"
    test_dir.mkdir(exist_ok=True)
    
    yield test_dir
    
    # Clean up test files after tests
    if test_dir.exists():
        for file in test_dir.iterdir():
            if file.is_file():
                file.unlink()
        test_dir.rmdir()


@pytest.fixture
def sample_text_content():
    """
    Sample credit report text content for testing parser.
    
    Returns:
        str: Sample credit report text with TransUnion format
    """
    return """
    SUSCRIPTOR: BANCO POPULAR DOMINICANO
    USUARIO: TESTUSER123
    FECHA: 09/01/2026
    HORA: 17:50:00
    
    CEDULA: 001-1234567-8
    NOMBRES: JUAN PEDRO
    APELLIDOS: PEREZ MATOS
    FECHA NACIMIENTO: 01/01/1980
    EDAD: 46
    OCUPACION: INGENIERO DE SOFTWARE
    LUGAR NACIMIENTO: SANTO DOMINGO
    PASAPORTE: P0123456
    ESTADO CIVIL: CASADO
    
    TELEFONOS:
    CASA: 809-555-1234
    TRABAJO: 809-555-5678
    CELULAR: 829-555-9012
    
    DIRECCIONES:
    * CALLE PRIMERA #10, SECTOR LOS JARDINES, SANTO DOMINGO
    * AVE. INDEPENDENCIA #205, GAZCUE, SANTO DOMINGO
    
    PUNTUACION: 750
    
    FACTORES:
    * ALTO NIVEL DE CUMPLIMIENTO
    * MUCHAS CUENTAS ACTIVAS
    * BAJA UTILIZACION DE CREDITO
    
    RNC: 1-23-45678-9
    
    RESUMEN CUENTAS ABIERTAS:
    TIPO DE CREDITO: PRESTAMO PERSONAL
    CANTIDAD: 2
    BALANCE: DOP 150,000.00
    LIMITE: DOP 500,000.00
    
    DETALLE CUENTAS ABIERTAS:
    ENTIDAD: BANCO BHD LEON
    NUMERO CUENTA: *****1234
    TIPO: PRESTAMO PERSONAL
    MONEDA: DOP
    BALANCE: DOP 75,000.00
    FECHA APERTURA: 01/2024
    ESTADO: AL DIA
    """


@pytest.fixture
def sample_minimal_text():
    """
    Minimal credit report text for edge case testing.
    
    Returns:
        str: Minimal valid credit report text
    """
    return """
    SUSCRIPTOR: BANCO TEST
    USUARIO: TESTUSER
    FECHA: 01/01/2026
    HORA: 12:00:00
    CEDULA: 001-0000000-0
    NOMBRES: TEST
    APELLIDOS: USER
    PUNTUACION: 600
    """


@pytest.fixture
def mock_credit_report_data():
    """
    Mock credit report data for testing.
    
    Returns:
        dict: Sample credit report data structure
    """
    return {
        "inquirer": {
            "subscriber": "banco popular dominicano",
            "user": "testuser123",
            "consultation_date": "09/01/2026",
            "consultation_time": "17:50:00"
        },
        "personal_data": {
            "identification": "001-1234567-8",
            "first_names": "juan pedro",
            "last_names": "perez matos",
            "birth_date": "01/01/1980",
            "age": 46,
            "occupation": "ingeniero de software",
            "birth_place": "santo domingo",
            "passport": "p0123456",
            "marital_status": "casado",
            "phones": {
                "home": "809-555-1234",
                "work": "809-555-5678",
                "mobile": "829-555-9012"
            },
            "addresses": [
                "calle primera #10, sector los jardines, santo domingo",
                "ave. independencia #205, gazcue, santo domingo"
            ],
            "rnc": "1-23-45678-9"
        },
        "score": {
            "score": 750,
            "factors": [
                "alto nivel de cumplimiento",
                "muchas cuentas activas",
                "baja utilizacion de credito"
            ]
        }
    }


@pytest.fixture
def sample_invalid_pdf():
    """
    Create an invalid PDF file for testing error handling.
    
    Returns:
        bytes: Invalid PDF content
    """
    return b"This is not a valid PDF file"


@pytest.fixture
def sample_empty_file():
    """
    Create an empty file for testing error handling.
    
    Returns:
        bytes: Empty file content
    """
    return b""
