import re
import fitz
import unidecode
from io import BytesIO
from typing import Optional, List, Dict, Any
from src.models.report import (
    CreditReport, InquirerInfo, PersonalInfo, PersonalPhones,
    CreditScore, AccountSummary, AccountDetail
)

class ParserEngine:
    def __init__(self, text: str):
        self.text = text.lower() # Already lowercase from extraction often, but ensuring here
        self.text = unidecode.unidecode(self.text)

    @classmethod
    async def from_pdf_bytes(cls, pdf_bytes: bytes) -> "ParserEngine":
        """In-memory PDF to text conversion."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return cls(text)

    def extract_field(self, pattern: str, group: int = 1, dotall: bool = False) -> Optional[str]:
        flags = re.IGNORECASE | re.MULTILINE
        if dotall:
            flags |= re.DOTALL
        match = re.search(pattern, self.text, flags)
        return match.group(group).strip() if match else None

    def parse_inquirer(self) -> InquirerInfo:
        return InquirerInfo(
            subscriber=self.extract_field(r"suscriptor:\s*(.*)"),
            user=self.extract_field(r"usuario:\s*(.*)"),
            consultation_date=self.extract_field(r"fecha:\s*(.*)"),
            consultation_time=self.extract_field(r"hora:\s*(\d{2}:\d{2}:\d{2})")
        )

    def parse_personal_data(self) -> PersonalInfo:
        phones = PersonalPhones(
            home=self.extract_field(r"casa:\s*(.*)"),
            work=self.extract_field(r"trabajo:\s*(.*)"),
            mobile=self.extract_field(r"celular:\s*(.*)")
        )
        
        # Addresses are star-separated in legacy
        addr_match = re.search(r"direcciones\s*(.*?)(?=\stransunion|resumen|detalle|indagaciones|puntuacion|$)", self.text, re.DOTALL)
        addresses = []
        if addr_match:
            raw_addr = addr_match.group(1).split('*')
            addresses = [a.strip().replace('\n', ' ') for a in raw_addr if a.strip()]

        return PersonalInfo(
            identification=self.extract_field(r"cedula\s+([^\s\n]+)"),
            first_names=self.extract_field(r"nombres\s+(.*)"),
            last_names=self.extract_field(r"apellidos\s+(.*)"),
            birth_date=self.extract_field(r"fecha nacimiento\s+(.*)"),
            age=int(self.extract_field(r"edad\s+(\d+)") or 0),
            occupation=self.extract_field(r"ocupacion\s+(.*)"),
            birth_place=self.extract_field(r"lugar nacimiento\s+(.*)"),
            passport=self.extract_field(r"pasaporte\s+(.*)"),
            marital_status=self.extract_field(r"estado civil\s+(.*)"),
            phones=phones,
            addresses=addresses
        )

    def parse_score(self) -> Optional[CreditScore]:
        score_val = self.extract_field(r"puntuacion\s*(\d+)")
        if not score_val:
            return None
        
        factors_match = re.search(r"factores\s*(.*?)(?=\srnc|$)", self.text, re.DOTALL)
        factors = []
        if factors_match:
            factors = [f.strip() for f in factors_match.group(1).replace('*', '').split('\n') if f.strip()]
            
        return CreditScore(score=score_val, factors=factors)

    def parse_account_summaries(self) -> List[AccountSummary]:
        # Legacy logic used indexing, let's try a regex approach or find the table section
        section_match = re.search(r"resumen de cuentas abiertas\s*(.*?)(?=\sleyenda|detalle|indagaciones|$)", self.text, re.DOTALL)
        if not section_match:
            return []
            
        lines = [l.strip() for l in section_match.group(1).split('\n') if l.strip()]
        # Skip headers (roughly first 17 items in legacy)
        # Better: find "total general >>" and work backwards or just match rows
        # Row pattern: Subscriber + 10 numeric/percent fields
        # This part is tricky with regex if layout varies. Keeping legacy logic spirit but more robust.
        
        summaries = []
        try:
            start_idx = 0
            for i, line in enumerate(lines):
                if "cuentas saldo" in line: # Header end hint
                    start_idx = i + 1
                    break
            
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if "total general >>" in line:
                    end_idx = i
                    break
            
            data_chunk = lines[start_idx:end_idx]
            for i in range(0, len(data_chunk), 11):
                row = data_chunk[i:i+11]
                if len(row) < 11: break
                summaries.append(AccountSummary(
                    subscriber=row[0],
                    accounts_amount=int(row[1]),
                    account_type=row[2],
                    credit_amount_dop=float(row[3].replace(',','')),
                    credit_amount_usd=float(row[4].replace(',','')),
                    current_balance_dop=float(row[5].replace(',','')),
                    current_balance_usd=float(row[6].replace(',','')),
                    current_overdue_dop=float(row[7].replace(',','')),
                    current_overdue_usd=float(row[8].replace(',','')),
                    utilization_percent_dop=float(row[9].replace('%','')),
                    utilization_percent_usd=float(row[10].replace('%',''))
                ))
        except Exception:
            pass # Robustness: return partial results if parsing fails mid-table
            
        return summaries

    def parse_account_details(self) -> List[AccountDetail]:
        section_match = re.search(r"detalle de cuentas abiertas\s*(.*?)(?=\sdetalle de cuentas cerradas|indagaciones|$)", self.text, re.DOTALL)
        if not section_match:
            return []
            
        lines = [l.strip() for l in section_match.group(1).split('\n') if l.strip()]
        
        details = []
        current_sub = None
        current_type = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if "total general rd$:" in line:
                break
            
            if ">>" in line:
                parts = line.split(">>")
                current_type = parts[0].strip()
                current_sub = parts[1].strip() if len(parts) > 1 else "Unknown"
                i += 1
                continue
            
            if current_sub and i + 10 < len(lines):
                row = lines[i:i+11]
                # Behavior vector usually space separated numbers
                vector_raw = row[10].replace(" ", "")
                vector = [int(c) if c.isdigit() else None for c in vector_raw]
                
                details.append(AccountDetail(
                    account_type=current_type,
                    subscriber=current_sub,
                    status=row[0],
                    update_date=row[1],
                    opening_date=row[2],
                    expiration_date=row[3],
                    currency=row[4],
                    credit_limit=float(row[5].replace(',','')),
                    current_balance=float(row[6].replace(',','')),
                    balance_in_arrears=float(row[7].replace(',','')),
                    minimum_payment_installment=float(row[8].replace(',','')),
                    no_installments_modality=row[9],
                    behavior_vector_last_12_months=vector
                ))
                i += 11
            else:
                i += 1
                
        return details

    async def get_report(self) -> CreditReport:
        return CreditReport(
            inquirer=self.parse_inquirer(),
            personal_data=self.parse_personal_data(),
            score=self.parse_score(),
            summary_open_accounts=self.parse_account_summaries(),
            details_open_accounts=self.parse_account_details()
        )
