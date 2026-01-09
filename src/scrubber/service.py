import re
from typing import List
from src.models.report import CreditReport, PersonalInfo, PersonalPhones

class PIIScrubber:
    @staticmethod
    def mask_string(text: str, visible_chars: int = 2) -> str:
        if not text or len(text) <= visible_chars:
            return "*" * (len(text) if text else 5)
        return text[:visible_chars] + "*" * (len(text) - visible_chars)

    @staticmethod
    def mask_id(id_val: str) -> str:
        # Pattern for cedula 000-0000000-0 or passport
        if not id_val: return "*****"
        digits = re.sub(r"\D", "", id_val)
        if len(digits) >= 11: # Likley Cedula
             return f"{id_val[:3]}-XXXXXXX-{id_val[-1]}"
        return id_val[:2] + "X" * (len(id_val) - 2)

    @classmethod
    def scrub_report(cls, report: CreditReport) -> CreditReport:
        """Masks PII in the report. Returns a new instance (Pydantic model.copy() is shallow in V2 usually, use model_copy)."""
        new_report = report.model_copy(deep=True)
        
        p = new_report.personal_data
        p.identification = cls.mask_id(p.identification)
        p.first_names = cls.mask_string(p.first_names)
        p.last_names = cls.mask_string(p.last_names)
        p.passport = cls.mask_string(p.passport) if p.passport else None
        
        # Mask phones
        if p.phones:
            if p.phones.home: p.phones.home = cls.mask_string(p.phones.home, 4)
            if p.phones.work: p.phones.work = cls.mask_string(p.phones.work, 4)
            if p.phones.mobile: p.phones.mobile = cls.mask_string(p.phones.mobile, 4)
            
        # Mask addresses
        p.addresses = [cls.mask_string(addr, 5) for addr in p.addresses]
        
        return new_report
