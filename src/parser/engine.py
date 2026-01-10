import re
import fitz
import unidecode
import logging
from io import BytesIO
from typing import Optional, List, Dict, Any
from src.models.report import (
    CreditReport, InquirerInfo, PersonalInfo, PersonalPhones,
    CreditScore, AccountSummary, AccountDetail
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParserEngine:
    def __init__(self, text: str):
        self.text = text.lower()
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

    def extract_field(self, pattern: str, group: int = 1, dotall: bool = False, text_pool: Optional[str] = None) -> Optional[str]:
        source = text_pool if text_pool is not None else self.text
        flags = re.IGNORECASE | re.MULTILINE
        if dotall:
            flags |= re.DOTALL
        match = re.search(pattern, source, flags)
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
        score_val_str = self.extract_field(r"puntuacion\s*(\d+)")
        score_val = int(score_val_str) if score_val_str and score_val_str.isdigit() else None
        
        if score_val is None:
            return None
        
        factors_match = re.search(r"factores\s*(.*?)(?=\srnc|$)", self.text, re.DOTALL)
        factors = []
        if factors_match:
            factors = [f.strip() for f in factors_match.group(1).replace('*', '').split('\n') if f.strip()]
            
        return CreditScore(score=score_val, factors=factors)

    def _parse_money(self, value: Optional[str]) -> float:
        if not value:
            return 0.0
        try:
            return float(value.replace(',', '').replace('%', '').strip())
        except ValueError:
            return 0.0

    def parse_account_summaries(self) -> List[AccountSummary]:
        section_match = re.search(r"resumen de cuentas abiertas\s*(.*?)(?=\sleyenda|detalle|indagaciones|$)", self.text, re.DOTALL)
        if not section_match:
            return []
            
        lines = [l.strip() for l in section_match.group(1).split('\n') if l.strip()]
        summaries = []
        
        try:
            start_idx = 0
            for i, line in enumerate(lines):
                if "cuentas saldo" in line:
                    start_idx = i + 1
                    break
            
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if "total general >>" in line:
                    end_idx = i
                    break
            
            data_chunk = lines[start_idx:end_idx]
            # While the prompt asked to abandon line counting for details, summaries in Transunion 
            # are typically fixed-column tables. We'll keep it as is unless we find a better anchor 
            # for these specific rows.
            for i in range(0, len(data_chunk), 11):
                row = data_chunk[i:i+11]
                if len(row) < 11: break
                try:
                    summaries.append(AccountSummary(
                        subscriber=row[0],
                        accounts_amount=int(row[1]),
                        account_type=row[2],
                        credit_amount_dop=self._parse_money(row[3]),
                        credit_amount_usd=self._parse_money(row[4]),
                        current_balance_dop=self._parse_money(row[5]),
                        current_balance_usd=self._parse_money(row[6]),
                        current_overdue_dop=self._parse_money(row[7]),
                        current_overdue_usd=self._parse_money(row[8]),
                        utilization_percent_dop=self._parse_money(row[9]),
                        utilization_percent_usd=self._parse_money(row[10])
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse account summary row: {row}. Error: {e}")
        except Exception as e:
            logger.error(f"Error parsing account summaries section: {e}")
            
        return summaries

    def parse_account_details(self) -> List[AccountDetail]:
        section_match = re.search(r"detalle de cuentas abiertas\s*(.*?)(?=\sdetalle de cuentas cerradas|indagaciones|$)", self.text, re.DOTALL)
        if not section_match:
            return []
            
        section_text = section_match.group(1)
        # Anchor Parsing: Split by ">>"
        blocks = section_text.split(">>")
        # The first element is usually headers before the first ">>"
        blocks = blocks[1:]
        
        details = []
        for block in blocks:
            try:
                detail = self._parse_account_block(block)
                if detail:
                    details.append(detail)
            except Exception as e:
                logger.warning(f"Failed to parse account block: {block[:100]}... Error: {e}")
                
        return details

    def _parse_account_block(self, block: str) -> Optional[AccountDetail]:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            return None
            
        # The line containing the anchor ">>" (represented here as start of block)
        # usually is "AccountType >> Subscriber"
        # Since we split by ">>", the first line of 'block' is actually just the "Subscriber"
        # Wait, the split removes ">>". 
        # Example: "PRESTAMO PERSONALES >> BANCO POPULAR \n vigente ..."
        # block would be " BANCO POPULAR \n vigente ..."
        # So we need to reconstruct the Account Type from the previous block's tail or split differently.
        
        # Better split for "AccountType >> Subscriber":
        # Let's find all occurrences of "type >> sub" using regex
        pass

    def parse_account_details_v2(self) -> List[AccountDetail]:
        """Refactored version using pattern anchoring and block reconstruction."""
        section_match = re.search(r"detalle de cuentas abiertas\s*(.*?)(?=\sdetalle de cuentas cerradas|indagaciones|$)", self.text, re.DOTALL)
        if not section_match:
            return []
            
        section_text = section_match.group(1)
        
        # We find all "Type >> Sub" anchors. 
        # A more robust way: Find all instances of ">>" and the line containing it.
        # Then, everything between one ">>" line and the next is a block.
        
        # Find all start positions of Type >> Sub
        headers = list(re.finditer(r"([^\n>]+>>[^\n]+)", section_text))
        
        details = []
        for i in range(len(headers)):
            start_header = headers[i]
            # End is the start of the next header or end of section
            end_pos = headers[i+1].start() if i + 1 < len(headers) else len(section_text)
            
            header_line = start_header.group(1)
            # The remaining content starts right after the matched header line
            content = section_text[start_header.end():end_pos]
            
            try:
                parts = header_line.split(">>")
                acc_type = parts[0].strip()
                # The first part of subscriber is here, but it might wrap into 'content'
                initial_sub = parts[1].strip()
                
                # If content starts with more text before a status/date, it's wrapped subscriber
                # Status keywords list (extensible)
                status_kw = r"(vigente|cancelada|atraso|proceo judicial|reestructurado)"
                date_pat = r"\d{2}/\d{2}/\d{4}"
                
                # Match anything until we hit a status keyword or date at the start of a line
                wrap_match = re.search(rf"^(.*?)(?=\s*(?:{status_kw}|{date_pat}))", content, re.DOTALL | re.I)
                if wrap_match and wrap_match.group(1).strip():
                    subscriber = f"{initial_sub} {wrap_match.group(1).strip()}".replace('\n', ' ')
                    # Clean up double spaces
                    subscriber = " ".join(subscriber.split())
                    remaining_content = content[wrap_match.end():]
                else:
                    subscriber = initial_sub
                    remaining_content = content

                detail = self._extract_detail_from_content(acc_type, subscriber, remaining_content)
                if detail:
                    details.append(detail)
            except Exception as e:
                logger.warning(f"Failed to parse account block starting with {header_line}: {e}")
                
        return details

    def _extract_detail_from_content(self, acc_type: str, subscriber: str, content: str) -> Optional[AccountDetail]:
        # Sequence is critical: Extract and REMOVE to avoid double-matching
        
        # 1. Behavior Vector (usually 12+ digits/chars at the end)
        vector_match = re.search(r"([0-9x? \+]{12,})(?:\s+|$)", content, re.I)
        vector = []
        if vector_match:
            raw_v = vector_match.group(1).replace(" ", "")
            vector = [int(c) if c.isdigit() else None for c in raw_v]
            content = content[:vector_match.start()] + content[vector_match.end():]

        # 2. Dates (DD/MM/YYYY)
        dates = re.findall(r"(\d{2}/\d{2}/\d{4})", content)
        update_date = dates[0] if len(dates) > 0 else "n/a"
        opening_date = dates[1] if len(dates) > 1 else "n/a"
        expiration_date = dates[2] if len(dates) > 2 else None
        # Remove all dates to avoid picking them up as numbers
        content = re.sub(r"\d{2}/\d{2}/\d{4}", " ", content)

        # 3. Currency (DOP/USD)
        currency_match = re.search(r"\b(dop|usd)\b", content, re.I)
        currency = currency_match.group(1).upper() if currency_match else "DOP"
        content = re.sub(r"\b(dop|usd)\b", " ", content, flags=re.I)

        # 4. Modality (Usually looks like "12/36 MENSUAL" or similar)
        # Often contains a slash but not a full date
        modality_match = re.search(r"(\d+/\d+\s+[a-z]+|\b(mensual|quincenal|semanal|anual)\b)", content, re.I)
        modality = modality_match.group(1).strip() if modality_match else "n/a"
        if modality_match:
            content = content.replace(modality_match.group(0), " ")

        # 5. Status (Vigente, Cancelada, etc.)
        # Usually the first word or one of these keywords
        status_kw = ["vigente", "cancelada", "atraso", "proceso judicial", "reestructurado", "legal"]
        status = "unknown"
        for kw in status_kw:
            if kw in content.lower():
                status = kw
                content = content.replace(kw, " ")
                break

        # 6. Monetary Values (Numbers with commas/decimals)
        # We look for amounts like 100,000.00
        monetary_values = re.findall(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?|0\.00)", content)
        # Filter out stray single digits if we have better candidates
        monetary_values = [v for v in monetary_values if len(v.replace(',','').split('.')[0]) > 0]
        
        credit_limit = self._parse_money(monetary_values[0]) if len(monetary_values) > 0 else 0.0
        current_balance = self._parse_money(monetary_values[1]) if len(monetary_values) > 1 else 0.0
        balance_in_arrears = self._parse_money(monetary_values[2]) if len(monetary_values) > 2 else 0.0
        min_pmt = self._parse_money(monetary_values[3]) if len(monetary_values) > 3 else 0.0

        return AccountDetail(
            account_type=acc_type.lower(),
            subscriber=subscriber.lower(),
            status=status,
            update_date=update_date,
            opening_date=opening_date,
            expiration_date=expiration_date,
            currency=currency,
            credit_limit=credit_limit,
            current_balance=current_balance,
            balance_in_arrears=balance_in_arrears,
            minimum_payment_installment=min_pmt,
            no_installments_modality=modality.lower(),
            behavior_vector_last_12_months=vector
        )

    async def get_report(self) -> CreditReport:
        return CreditReport(
            inquirer=self.parse_inquirer(),
            personal_data=self.parse_personal_data(),
            score=self.parse_score(),
            summary_open_accounts=self.parse_account_summaries(),
            details_open_accounts=self.parse_account_details_v2()
        )
