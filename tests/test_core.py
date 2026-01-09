import pytest
from src.parser.engine import ParserEngine
from src.scrubber.service import PIIScrubber
from src.models.report import CreditReport, InquirerInfo, PersonalInfo, PersonalPhones

@pytest.fixture
def sample_text():
    return """
    suscriptor: BANCO POPULAR
    usuario: IDEQUEL
    fecha: 09/01/2026
    hora: 17:50:00
    cedula 001-1234567-8
    nombres JUAN PEREZ
    apellidos MATOS
    fecha nacimiento 01/01/1980
    edad 46
    ocupacion PROGRAMADOR
    lugar nacimiento SANTO DOMINGO
    pasaporte P0000000
    estado civil SOLTERO
    casa: 809-555-1234
    trabajo: 809-555-5678
    celular: 829-555-9012
    direcciones
    * CALLE 1, SD
    * CALLE 2, SDE
    puntuacion 750
    factores
    * ALTO CUMPLIMIENTO
    * MUCHAS CUENTAS
    rnc 1-23-45678-9
    """

def test_parser_engine_basic(sample_text):
    parser = ParserEngine(sample_text)
    inquirer = parser.parse_inquirer()
    assert inquirer.subscriber == "banco popular"
    assert inquirer.user == "idequel"
    assert inquirer.consultation_date == "09/01/2026"
    
    personal = parser.parse_personal_data()
    assert personal.identification == "001-1234567-8"
    assert personal.first_names == "juan perez"
    assert personal.phones.mobile == "829-555-9012"
    assert len(personal.addresses) == 2

    score = parser.parse_score()
    assert score is not None
    assert score.score == "750"
    assert "alto cumplimiento" in score.factors

def test_scrubber():
    # Create a mock report
    phones = PersonalPhones(mobile="829-555-9012")
    personal = PersonalInfo(
        identification="001-1234567-8",
        first_names="juan perez",
        last_names="matos",
        birth_date="01/01/1980",
        phones=phones,
        addresses=["calle 1, sd"]
    )
    report = CreditReport(
        inquirer=InquirerInfo(subscriber="bank", user="user", consultation_date="date", consultation_time="12:00:00"),
        personal_data=personal
    )
    
    scrubbed = PIIScrubber.scrub_report(report)
    
    assert scrubbed.personal_data.identification == "001-XXXXXXX-8"
    assert scrubbed.personal_data.first_names == "ju********"
    assert scrubbed.personal_data.phones.mobile == "829-********"
    assert scrubbed.personal_data.addresses[0] == "calle******"
