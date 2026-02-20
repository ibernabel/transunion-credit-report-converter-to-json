# ADR 002: Legal Compliance & Risk Mitigation

## Status

Proposed (2026-02-20)

## Context

The project involves parsing PDF credit reports from TransUnion into structured JSON. Under Dominican Law (Ley 172-13) and contractual agreements with the credit bureau, several risks were identified:

1. **Data Integrity**: Inaccurate parsing could lead to legal liability.
2. **Trademark & Intellectual Property**: Using the "TransUnion" name in the project title and altering report formats without authorization poses legal risks.
3. **Data Security**: JSON format is more vulnerable to leakage than static PDFs if not properly handled.
4. **Principle of Purpose**: Storing data beyond the strict necessity of credit evaluation is prohibited.

## Decisions

1. **Project Rebranding**: Rename the project to **CreditGraph Parser** to remove direct trademark associations.
2. **Explicit Disclaimer**: Strengthen the disclaimer to emphasize independence and that it is for educational/private use.
3. **Security Standards**:
   - **Encryption**: JSON outputs should be encrypted at rest (AES-256) if stored.
   - **TLS 1.2+**: All data in transit must use secure channels.
   - **Minimal Logging**: Avoid logging PII; implement robust data masking (PII Filter) including Cedulas, Phones, and Account Numbers.
4. **Technical Mitigations**:
   - **In-Memory Transformation**: The parser operates entirely in memory (`BytesIO`). No temporary files are written to disk during the parsing lifecycle, minimizing the risk of data remnants.
   - **Sandboxing**: Treat PDF input as untrusted. Use Docker for process isolation with a non-root user (`appuser`).
   - **Audit Logs**: Maintain unalterable logs of who accessed the data and when.
   - **Storage Restriction (JSON)**: If JSON data MUST be stored, it must be encrypted using AES-256-GCM. Storage should be ephemeral by default, with an explicit "Right to be Forgotten" implementation.

## Consequences

- The project becomes more compliant with local regulations.
- Rebranding may require updating external links or integrations.
- Increased development scope for security features (Encryption/Auditing).
- The legal risk is mitigated but not eliminated; user compliance with Ley 172-13 remains their responsibility.
