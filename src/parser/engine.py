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
        if match:
            value = match.group(group)
            return value.strip() if value else ""
        return None

    def parse_inquirer(self) -> InquirerInfo:
        return InquirerInfo(
            subscriber=self.extract_field(r"suscriptor:\s*(.*)"),
            user=self.extract_field(r"usuario:[\s\n]+([^\n]+)"),
            consultation_date=self.extract_field(r"fecha:[\s\n]+(\d{2}/\d{2}/\d{4})"),
            consultation_time=self.extract_field(r"hora:[\s\n]+(\d{2}:\d{2}(?::\d{2})?\s*(?:am|pm)?)")
        )

    def parse_personal_data(self) -> PersonalInfo:
        phones = PersonalPhones(
            home=self.extract_field(r"casa:[\s\n]*(\d+[- ]\d+[- ]\d+)?"),
            work=self.extract_field(r"trabajo:[\s\n]*(\d+[- ]\d+[- ]\d+)?"),
            mobile=self.extract_field(r"celular:[\s\n]*(\d+[- ]\d+[- ]\d+)?")
        )
        
        addr_match = re.search(r"direcciones\s*(.*?)(?=\stransunion|resumen|detalle|indagaciones|puntuacion|$)", self.text, re.DOTALL)
        addresses = []
        if addr_match:
            # Split by bullet point or newline
            raw_addr = re.split(r"[\n\*]|•", addr_match.group(1))
            addresses = [a.strip() for a in raw_addr if a.strip() and len(a.strip()) > 5]

        # Robust extraction: match value until next known label
        labels = ["apellidos", "fecha nacimiento", "edad", "ocupacion", "lugar nacimiento", "pasaporte", "estado civil", "telefonos", "direcciones"]
        def get_val(label, next_labels):
            pattern = rf"{label}[\s\n]+(.*?)(?=\s*(?:{'|'.join(next_labels)}|$))"
            return self.extract_field(pattern, dotall=True)

        return PersonalInfo(
            identification=self.extract_field(r"cedula\s+#?([^\s\n]+)"),
            first_names=get_val("nombres", labels[0:]),
            last_names=get_val("apellidos", labels[1:]),
            birth_date=self.extract_field(r"fecha nacimiento[\s\n]+(\d{2}/\d{2}/\d{4})"),
            age=int(self.extract_field(r"edad[\s\n]+(\d+)") or 0),
            occupation=get_val("ocupacion", labels[4:]),
            birth_place=get_val("lugar nacimiento", labels[5:]),
            passport=get_val("pasaporte", labels[6:]),
            marital_status=get_val("estado civil", labels[7:]),
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
            # Data starts after the last occurrence of 'us$' in the header
            all_us_indices = [i for i, l in enumerate(lines) if l == "us$"]
            if not all_us_indices:
                return []
            
            start_idx = all_us_indices[-1] + 1
            
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if "total general" in line:
                    end_idx = i
                    break
            
            data_chunk = lines[start_idx:end_idx]
            
            for i in range(0, len(data_chunk), 11):
                row = data_chunk[i:i+11]
                if len(row) < 11: break
                
                # If the row is a subtotal, we skip it and DONT advance by a fixed 11
                # because the subtotal row itself might be shifted or shorter.
                # Actually, in Transunion the subtotal row IS 11 elements too.
                if "sub-total" in row[0].lower() or "total general" in row[0].lower():
                    continue

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
        section_match = re.search(r"detalle de cuentas abiertas\s*(.*?)(?=\sdetalle de cuentas cerradas|totales generales|indagaciones|$)", self.text, re.DOTALL)
        if not section_match:
            return []
            
        section_text = section_match.group(1)
        
        # We find all "Type >> Sub" anchors. 
        # Support both '>>' and '»', and handle cases where Type is missing (starts with »)
        headers = list(re.finditer(r"([^\n>»]*[>»]+[^\n]+)", section_text))
        
        details = []
        for i in range(len(headers)):
            start_header = headers[i]
            # End is the start of the next header or end of section
            end_pos = headers[i+1].start() if i + 1 < len(headers) else len(section_text)
            
            header_line = start_header.group(1)
            # The remaining content starts right after the matched header line
            content = section_text[start_header.end():end_pos]
            
            try:
                parts = re.split(r">>|»|>", header_line)
                parts = [p.strip() for p in parts if p.strip()]
                
                if len(parts) >= 2:
                    acc_type = parts[0]
                    initial_sub = parts[1]
                elif len(parts) == 1:
                    # Inherit from last known if possible, else unknown
                    acc_type = details[-1].account_type if details else "unknown"
                    initial_sub = parts[0]
                else:
                    acc_type = details[-1].account_type if details else "unknown"
                    initial_sub = "unknown"
                
                # A block might contain multiple records (RD$ and US$ variants)
                # We split the block content by the presence of a behavior vector, 
                # but we keep the vector as part of the sub-block.
                # Anchor: behavior vector is usually the end of a record.
                
                # Split content into parts where each part ends with a behavior vector
                vector_pat = r"([0-9x? \+]{11,}[0-9x? \+\-]{1,})"
                sub_records = []
                last_end = 0
                for v_match in re.finditer(vector_pat, content):
                    sub_records.append(content[last_end:v_match.end()])
                    last_end = v_match.end()
                
                # If there's content left after the last vector (shouldn't happen much in good blocks)
                if last_end < len(content) and len(content[last_end:].strip()) > 20:
                    sub_records.append(content[last_end:])

                if not sub_records:
                    # Fallback: maybe no vector found, try whole content
                    sub_records = [content]

                for record_content in sub_records:
                    # For the first record, we might have wrapped subscriber text
                    # For subsequent ones, we use the same header info
                    status_kw_pat = r"(al dia|vigente|cancelada|atraso|proceso judicial|reestructurado|legal)"
                    date_pat = r"\d{2}/\d{4}"
                    
                    wrap_match = re.search(rf"(.*?)(?=\s*(?:{status_kw_pat}|{date_pat}))", record_content, re.DOTALL | re.I)
                    
                    current_sub = initial_sub
                    current_acc_type = acc_type
                    
                    if wrap_match:
                        added_sub = wrap_match.group(1).strip()
                        if added_sub and len(added_sub) > 0:
                            # Is it really a subscriber wrap or just noise?
                            # If it's the first record in the block, it's likely a wrap.
                            # If it's the 2nd+, it might be noise before the status.
                            if record_content == sub_records[0]:
                                current_sub = f"{initial_sub} {added_sub}".strip().replace('\n', ' ')
                                current_sub = " ".join(current_sub.split())
                        
                        remaining_record = record_content[wrap_match.end():]
                    else:
                        remaining_record = record_content

                    detail = self._extract_detail_from_content(current_acc_type, current_sub, remaining_record)
                    if detail:
                        details.append(detail)
            except Exception as e:
                logger.warning(f"Failed to parse account block starting with {header_line}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                
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

        # 2. Dates (MM/YYYY)
        dates = re.findall(r"(\d{2}/\d{4})", content)
        update_date = dates[0] if len(dates) > 0 else "n/a"
        opening_date = dates[1] if len(dates) > 1 else "n/a"
        expiration_date = dates[2] if len(dates) > 2 else None
        # Remove all dates to avoid picking them up as numbers
        content = re.sub(r"\d{2}/\d{4}", " ", content)

        # 3. Currency (DOP/USD/RD$/US$)
        currency_match = re.search(r"(?:\b)(dop|usd|rd\$|us\$)", content, re.I)
        raw_currency = currency_match.group(1).upper() if currency_match else "DOP"
        currency = "USD" if "US" in raw_currency else "DOP"
        content = re.sub(r"(?:\b)(dop|usd|rd\$|us\$)", " ", content, flags=re.I)

        # 4. Modality (Usually looks like "12/36 MENSUAL" or similar)
        # Often contains a slash but not a full date
        modality_match = re.search(r"(\d+/\d+\s+[a-z]+|\b(mensual|quincenal|semanal|anual)\b)", content, re.I)
        modality = modality_match.group(1).strip() if modality_match else "n/a"
        if modality_match:
            content = content.replace(modality_match.group(0), " ")

        # 5. Status (Vigente, Cancelada, etc.)
        # Usually the first word or one of these keywords
        status_kw = ["al dia", "vigente", "cancelada", "atraso", "proceso judicial", "reestructurado", "legal"]
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
