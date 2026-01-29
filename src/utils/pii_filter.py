"""
PII (Personally Identifiable Information) filter for logging.

Prevents accidental logging of sensitive personal information in error messages and stack traces.
"""

import logging
import re


class PIIFilter(logging.Filter):
    """
    Logging filter to redact PII from log messages.
    
    Redacts:
    - Dominican Republic Cedula (ID): 000-0000000-0
    - Phone numbers: (809) 555-1234, 809-555-1234, 8095551234
    - Email addresses
    - Credit card numbers (basic pattern)
    """
    
    # Regex patterns for PII detection
    CEDULA_PATTERN = re.compile(r'\d{3}-\d{7}-\d')
    PHONE_PATTERN = re.compile(r'(\+?1?\s*)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}')
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to redact PII.
        
        Args:
            record: Log record to filter
            
        Returns:
            True (always allow the record, but with redacted content)
        """
        # Redact PII from message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._redact_pii(record.msg)
        
        # Redact PII from args
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._redact_pii(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self._redact_pii(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        
        return True
    
    def _redact_pii(self, text: str) -> str:
        """
        Redact PII patterns from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Text with PII redacted
        """
        # Redact Cedula (Dominican ID)
        text = self.CEDULA_PATTERN.sub('XXX-XXXXXXX-X', text)
        
        # Redact phone numbers
        text = self.PHONE_PATTERN.sub('[PHONE_REDACTED]', text)
        
        # Redact email addresses
        text = self.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', text)
        
        # Redact credit card numbers
        text = self.CREDIT_CARD_PATTERN.sub('[CARD_REDACTED]', text)
        
        return text
