"""
Comprehensive unit tests for the ParserEngine.

Tests various edge cases, data formats, and error conditions to ensure
robust parsing of TransUnion credit reports.
"""

import pytest
from src.parser.engine import ParserEngine
from src.models.report import AccountDetail


class TestInquirerParsing:
    """Tests for inquirer information parsing."""

    def test_parse_inquirer_basic(self):
        """Test basic inquirer parsing."""
        text = """
        SUSCRIPTOR: BANCO POPULAR DOMINICANO
        USUARIO: JUAN PEREZ
        FECHA: 15/06/2024
        HORA: 14:30:00
        """
        parser = ParserEngine(text)
        inquirer = parser.parse_inquirer()

        assert inquirer.subscriber == "banco popular dominicano"
        assert inquirer.user == "juan perez"
        assert inquirer.consultation_date == "15/06/2024"
        assert inquirer.consultation_time == "14:30:00"

    def test_parse_inquirer_with_newlines(self):
        """Test inquirer parsing with extra newlines."""
        text = """
        SUSCRIPTOR: 
            BANCO BHD LEON
        USUARIO: 
            MARIA SANTOS
        FECHA: 
            01/01/2024
        HORA: 09:00 AM
        """
        parser = ParserEngine(text)
        inquirer = parser.parse_inquirer()

        assert inquirer.subscriber == "banco bhd leon"
        assert inquirer.user == "maria santos"

    def test_parse_inquirer_different_time_formats(self):
        """Test parsing different time formats."""
        test_cases = [
            ("14:30:00", "14:30:00"),
            ("09:15 AM", "09:15 am"),
            ("11:45 PM", "11:45 pm"),
            ("23:59", "23:59"),
        ]

        for time_input, expected in test_cases:
            text = f"HORA: {time_input}"
            parser = ParserEngine(text)
            inquirer = parser.parse_inquirer()
            assert inquirer.consultation_time == expected


class TestPersonalDataParsing:
    """Tests for personal data parsing."""

    def test_parse_personal_basic(self):
        """Test basic personal data parsing."""
        text = """
        CEDULA: 001-1234567-8
        NOMBRES: JUAN CARLOS
        APELLIDOS: PEREZ MATOS
        FECHA NACIMIENTO: 15/03/1985
        EDAD: 39
        OCUPACION: INGENIERO
        LUGAR NACIMIENTO: SANTO DOMINGO
        PASAPORTE: P1234567
        ESTADO CIVIL: CASADO
        CASA: 809-555-1234
        TRABAJO: 809-555-5678
        CELULAR: 829-555-9012
        """
        parser = ParserEngine(text)
        personal = parser.parse_personal_data()

        assert personal.identification == "001-1234567-8"
        assert personal.first_names == "juan carlos"
        assert personal.last_names == "perez matos"
        assert personal.birth_date == "15/03/1985"
        assert personal.age == 39
        assert personal.occupation == "ingeniero"
        assert personal.birth_place == "santo domingo"
        assert personal.passport == "p1234567"
        assert personal.marital_status == "casado"
        assert personal.phones.home == "809-555-1234"
        assert personal.phones.work == "809-555-5678"
        assert personal.phones.mobile == "829-555-9012"

    def test_parse_personal_missing_optional_fields(self):
        """Test parsing when optional fields are missing."""
        text = """
        CEDULA: 001-0000000-0
        NOMBRES: TEST
        APELLIDOS: USER
        FECHA NACIMIENTO: 01/01/2000
        """
        parser = ParserEngine(text)
        personal = parser.parse_personal_data()

        assert personal.identification == "001-0000000-0"
        assert personal.first_names == "test"
        assert personal.last_names == "user"
        # Optional fields should be None or empty
        assert personal.passport is None or personal.passport == ""

    def test_parse_phone_formats(self):
        """Test parsing different phone number formats."""
        test_cases = [
            "809-555-1234",
            "809 555 1234",
            "8095551234",
        ]

        for phone in test_cases:
            text = f"""
            CEDULA: 001-0000000-0
            NOMBRES: TEST
            APELLIDOS: USER
            FECHA NACIMIENTO: 01/01/2000
            CELULAR: {phone}
            """
            parser = ParserEngine(text)
            personal = parser.parse_personal_data()
            # Should parse successfully (exact format may vary)
            assert personal.phones.mobile is not None

    def test_parse_addresses_multiple(self):
        """Test parsing multiple addresses."""
        text = """
        CEDULA: 001-0000000-0
        NOMBRES: TEST
        APELLIDOS: USER
        FECHA NACIMIENTO: 01/01/2000
        DIRECCIONES:
        * CALLE PRIMERA #123, SECTOR NORTE, SANTO DOMINGO
        * AVE. INDEPENDENCIA #456, GAZCUE
        * CALLE TERCERA #789, ENSANCHE LUPERON
        """
        parser = ParserEngine(text)
        personal = parser.parse_personal_data()

        assert len(personal.addresses) == 3
        assert "calle primera" in personal.addresses[0].lower()
        assert "ave. independencia" in personal.addresses[1].lower()


class TestScoreParsing:
    """Tests for credit score parsing."""

    def test_parse_score_basic(self):
        """Test basic score parsing."""
        text = """
        PUNTUACION: 750
        FACTORES:
        * ALTO NIVEL DE CUMPLIMIENTO
        * MUCHAS CUENTAS ACTIVAS
        * BAJA UTILIZACION
        """
        parser = ParserEngine(text)
        score = parser.parse_score()

        assert score is not None
        assert score.score == 750
        assert len(score.factors) == 3
        assert "alto nivel de cumplimiento" in score.factors

    def test_parse_score_boundary_values(self):
        """Test parsing score boundary values."""
        test_cases = [300, 500, 750, 850, 900]

        for score_val in test_cases:
            text = f"PUNTUACION: {score_val}"
            parser = ParserEngine(text)
            score = parser.parse_score()
            assert score.score == score_val

    def test_parse_score_no_factors(self):
        """Test parsing score without factors."""
        text = "PUNTUACION: 600"
        parser = ParserEngine(text)
        score = parser.parse_score()

        assert score is not None
        assert score.score == 600
        assert score.factors == []


class TestAccountDetailsParsing:
    """Tests for account details parsing."""

    def test_parse_single_account(self):
        """Test parsing a single account."""
        text = """
        DETALLE DE CUENTAS ABIERTAS
        TARJETA CREDITO >> BANCO BHD LEON
        AL DIA
        06/2024
        12/2021
        DOP
        15,000.00
        7,500.00
        0.00
        500.00
        000000000000
        """
        parser = ParserEngine(text)
        details = parser.parse_account_details_v2()

        assert len(details) == 1
        account = details[0]
        assert account.account_type == "tarjeta credito"
        assert account.subscriber == "banco bhd leon"
        assert account.status == "al dia"
        assert account.credit_limit == 15000.0
        assert account.current_balance == 7500.0

    def test_parse_multiple_accounts(self):
        """Test parsing multiple accounts."""
        text = """
        DETALLE DE CUENTAS ABIERTAS
        TARJETA CREDITO >> BANCO BHD
        AL DIA
        06/2024
        12/2021
        DOP
        10,000.00
        5,000.00
        0.00
        0.00
        000000000000
        
        PRESTAMO PERSONAL >> BANCO POPULAR
        VIGENTE
        05/2024
        01/2023
        10/2026
        DOP
        200,000.00
        150,000.00
        0.00
        5,000.00
        12/36 MENSUAL
        000000000000
        """
        parser = ParserEngine(text)
        details = parser.parse_account_details_v2()

        assert len(details) >= 2
        assert details[0].account_type == "tarjeta credito"
        assert details[1].account_type == "prestamo personal"

    def test_parse_account_different_currencies(self):
        """Test parsing accounts in different currencies."""
        test_cases = [
            ("DOP", "DOP"),
            ("USD", "USD"),
            ("RD$", "DOP"),
            ("US$", "USD"),
        ]

        for currency_input, expected in test_cases:
            text = f"""
            DETALLE DE CUENTAS ABIERTAS
            TARJETA >> BANCO TEST
            AL DIA
            01/2024
            01/2023
            {currency_input}
            1,000.00
            500.00
            0.00
            0.00
            000000000000
            """
            parser = ParserEngine(text)
            details = parser.parse_account_details_v2()
            assert details[0].currency == expected

    def test_parse_account_status_variations(self):
        """Test parsing different account statuses."""
        statuses = [
            "AL DIA",
            "VIGENTE",
            "CANCELADA",
            "ATRASO",
            "PROCESO JUDICIAL",
        ]

        for status in statuses:
            text = f"""
            DETALLE DE CUENTAS ABIERTAS
            TARJETA >> BANCO TEST
            {status}
            01/2024
            01/2023
            DOP
            1000.00
            500.00
            0.00
            0.00
            000000000000
            """
            parser = ParserEngine(text)
            details = parser.parse_account_details_v2()
            assert details[0].status.lower() == status.lower()

    def test_parse_account_with_behavior_vector(self):
        """Test parsing account with payment behavior vector."""
        text = """
        DETALLE DE CUENTAS ABIERTAS
        TARJETA >> BANCO TEST
        AL DIA
        01/2024
        01/2023
        DOP
        10000.00
        5000.00
        0.00
        0.00
        001122334455
        """
        parser = ParserEngine(text)
        details = parser.parse_account_details_v2()

        assert len(details[0].behavior_vector_last_12_months) == 12
        assert details[0].behavior_vector_last_12_months[0] == 0
        assert details[0].behavior_vector_last_12_months[2] == 1


class TestDateParsing:
    """Tests for date parsing edge cases."""

    def test_parse_full_dates(self):
        """Test parsing full DD/MM/YYYY dates."""
        text = """
        DETALLE DE CUENTAS ABIERTAS
        PRESTAMO >> BANCO TEST
        AL DIA
        15/06/2024
        01/01/2020
        31/12/2025
        DOP
        100000.00
        50000.00
        0.00
        5000.00
        000000000000
        """
        parser = ParserEngine(text)
        details = parser.parse_account_details_v2()

        assert details[0].update_date == "15/06/2024"
        assert details[0].opening_date == "01/01/2020"
        assert details[0].expiration_date == "31/12/2025"

    def test_parse_partial_dates(self):
        """Test parsing MM/YYYY dates."""
        text = """
        DETALLE DE CUENTAS ABIERTAS
        TARJETA >> BANCO TEST
        AL DIA
        06/2024
        12/2021
        DOP
        10000.00
        5000.00
        0.00
        0.00
        000000000000
        """
        parser = ParserEngine(text)
        details = parser.parse_account_details_v2()

        assert details[0].update_date == "06/2024"
        assert details[0].opening_date == "12/2021"

    def test_parse_mixed_date_formats(self):
        """Test parsing mix of full and partial dates."""
        text = """
        DETALLE DE CUENTAS ABIERTAS
        PRESTAMO >> BANCO TEST
        AL DIA
        15/06/2024
        01/2020
        12/2025
        DOP
        100000.00
        50000.00
        0.00
        5000.00
        000000000000
        """
        parser = ParserEngine(text)
        details = parser.parse_account_details_v2()

        # Should parse all dates
        assert details[0].update_date is not None
        assert details[0].opening_date is not None


class TestMoneyParsing:
    """Tests for monetary value parsing."""

    def test_parse_money_with_commas(self):
        """Test parsing money values with thousand separators."""
        parser = ParserEngine("")

        test_cases = [
            ("1,000.00", 1000.0),
            ("10,000.50", 10000.5),
            ("100,000", 100000.0),
            ("1,000,000.00", 1000000.0),
        ]

        for input_val, expected in test_cases:
            result = parser._parse_money(input_val)
            assert result == expected

    def test_parse_money_without_commas(self):
        """Test parsing money values without separators."""
        parser = ParserEngine("")

        test_cases = [
            ("1000.00", 1000.0),
            ("500", 500.0),
            ("0.00", 0.0),
        ]

        for input_val, expected in test_cases:
            result = parser._parse_money(input_val)
            assert result == expected

    def test_parse_money_edge_cases(self):
        """Test edge cases in money parsing."""
        parser = ParserEngine("")

        assert parser._parse_money("0") == 0.0
        assert parser._parse_money("0.00") == 0.0
        assert parser._parse_money(None) == 0.0
        assert parser._parse_money("") == 0.0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_parse_empty_text(self):
        """Test parsing empty text."""
        parser = ParserEngine("")

        # Should not crash for inquirer (returns InquirerInfo with None values)
        inquirer = parser.parse_inquirer()
        assert inquirer is not None

        # Personal data will fail validation if required fields are missing
        # This is expected behavior - Pydantic enforces the schema
        with pytest.raises(Exception):  # ValidationError
            parser.parse_personal_data()

        # Score returns None if not found
        score = parser.parse_score()
        assert score is None

    def test_parse_malformed_data(self):
        """Test parsing with malformed/garbage data."""
        text = "XYZABC123!@#$%^&*()"
        parser = ParserEngine(text)

        # Should not crash
        score = parser.parse_score()
        details = parser.parse_account_details_v2()

        assert isinstance(details, list)
        assert score is None  # No valid score in garbage data

    def test_parse_unicode_characters(self):
        """Test parsing text with special characters."""
        text = """
        CEDULA: 001-1234567-8
        NOMBRES: JOSÉ MARÍA
        APELLIDOS: PÉREZ NÚÑEZ
        FECHA NACIMIENTO: 01/01/1990
        EDAD: 34
        OCUPACION: DISEÑADOR
        """
        parser = ParserEngine(text)
        personal = parser.parse_personal_data()

        # Should handle accented characters (converted to ASCII by unidecode)
        assert personal.first_names is not None
        assert personal.last_names is not None
        assert personal.occupation == "disenador"  # 'ñ' -> 'n'

    def test_parse_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        text = """
        CEDULA:     001-1234567-8
        
        NOMBRES:       JUAN    PEDRO
        
        APELLIDOS:      PEREZ
        
        FECHA NACIMIENTO: 01/01/1990
        
        EDAD: 35
        """
        parser = ParserEngine(text)
        personal = parser.parse_personal_data()

        assert personal.identification == "001-1234567-8"
        assert personal.first_names is not None
        assert personal.age == 35
