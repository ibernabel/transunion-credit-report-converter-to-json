import pytest
from src.parser.engine import ParserEngine
from src.models.report import AccountDetail

def test_robust_account_parsing():
    # Simulate a wrapped layout:
    # 1. Subscriber name with a newline in the middle
    # 2. Extra spaces and different line breaks
    wrapped_text = """
    DETALLE DE CUENTAS ABIERTAS
    PRESTAMO PERSONALES >> BANCO
    POPULAR DOMINICANO
    vigente
    01/01/2023
    01/02/2023
    31/12/2025
    DOP
    100,000.00
    50,000.00
    0.00
    5,000.00
    12/36 MENSUAL
    111111111111
    totales generales rd$:
    """
    parser = ParserEngine(wrapped_text)
    details = parser.parse_account_details_v2()
    
    assert len(details) == 1
    acc = details[0]
    assert acc.account_type == "prestamo personales"
    assert acc.subscriber == "banco popular dominicano"
    assert acc.status == "vigente"
    assert acc.update_date == "01/01/2023"
    assert acc.credit_limit == 100000.0
    assert acc.current_balance == 50000.0
    assert acc.behavior_vector_last_12_months == [1,1,1,1,1,1,1,1,1,1,1,1]
