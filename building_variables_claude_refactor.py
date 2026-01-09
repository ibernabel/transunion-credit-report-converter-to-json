import pandas as pd
import json
import re


class CreditReportParser:
    def __init__(self, file_path):
        """
        Initialize the parser with the credit report file.

        :param file_path: Path to the credit report text file
        """
        with open(file_path, "r") as file:
            self.text = file.read()

        # Initialize parsed data containers
        self.parsed_data = {
            "inquirer": {},
            "personal_data": {},
            "score": None,
            "summary_open_accounts": [],
            "details_open_accounts": []
        }

    def extract_section(self, start_marker, end_marker=None):
        """
        Extract a section of text between start and end markers.

        :param start_marker: Starting text to find
        :param end_marker: Optional ending text to find
        :return: Extracted text section
        """
        start_index = self.text.find(start_marker)
        if start_index == -1:
            return None

        start_index += len(start_marker)

        if end_marker:
            end_index = self.text.find(end_marker, start_index)
            return self.text[start_index:end_index].strip() if end_index != -1 else self.text[start_index:].strip()

        return self.text[start_index:].strip()

    def parse_inquirer_info(self):
        """
        Extract inquirer information from the credit report.
        """
        markers = {
            "suscriptor": "suscriptor:",
            "usuario": "usuario:",
            "fecha": "fecha:",
            "hora": "hora:"
        }

        try:
            self.parsed_data['inquirer'] = {
                "suscriptor": self.extract_section("suscriptor:", "usuario:").strip(),
                "usuario": self.extract_section("usuario:", "fecha:").strip(),
                "fecha consulta": self.extract_section("fecha:", "hora:").strip(),
                "hora consulta": self.extract_section("hora:", "transunion").strip()
            }
        except Exception as e:
            print(f"Error parsing inquirer info: {e}")

    def parse_personal_data(self):
        """
        Extract personal data from the credit report.
        """
        personal_data_markers = [
            "cedula", "nombres", "apellidos", "fecha nacimiento", "edad",
            "ocupacion", "lugar nacimiento", "pasaporte", "estado civil",
            "telefonos", "direcciones"
        ]

        try:
            # Phones parsing
            phones = {
                "casa": self.extract_section("casa:", "trabajo:").strip(),
                "trabajo": self.extract_section("trabajo:", "celular:").strip(),
                "celular": self.extract_section("celular:", "direcciones").strip()
            }

            # Addresses parsing
            addresses_start = self.text.find("direcciones")
            addresses_end = self._find_next_section_index(addresses_start)
            addresses_raw = self.text[addresses_start:addresses_end].split(
                '* ')[1:]
            addresses = [addr.strip().replace('\n', ' ')
                         for addr in addresses_raw]

            self.parsed_data['personal_data'] = {
                "cedula": self.extract_section("cedula", "nombres").strip(),
                "nombres": self.extract_section("nombres", "apellidos").strip(),
                "apellidos": self.extract_section("apellidos", "fecha nacimiento").strip(),
                "fecha nacimiento": self.extract_section("fecha nacimiento", "edad").strip(),
                "edad": self.extract_section("edad", "ocupacion").strip(),
                "ocupacion": self.extract_section("ocupacion", "lugar nacimiento").strip(),
                "lugar nacimiento": self.extract_section("lugar nacimiento", "pasaporte").strip(),
                "pasaporte": self.extract_section("pasaporte", "estado civil").strip(),
                "estado civil": self.extract_section("estado civil", "telefonos").strip(),
                "telefonos": phones,
                "direcciones": addresses
            }
        except Exception as e:
            print(f"Error parsing personal data: {e}")

    def _find_next_section_index(self, start_index):
        """
        Find the index of the next section to define section boundaries.

        :param start_index: Starting index to search from
        :return: Index of the next section
        """
        sections = [
            "transunion creditvision score",
            "resumen de cuentas abiertas",
            "detalle de cuentas abiertas",
            "detalle de cuentas cerradas / inactivas",
            "indagaciones ultimos 6 meses"
        ]

        next_indices = [self.text.find(section, start_index)
                        for section in sections]
        valid_indices = [idx for idx in next_indices if idx != -1]

        return min(valid_indices) if valid_indices else len(self.text)

    def parse_credit_score(self):
        """
        Extract credit score and related information.
        """
        try:
            score_index = self.text.rfind("puntuacion")
            self.parsed_data['score'] = {
                "score": self.text[score_index + 10: score_index + 14].strip(),
                "factors": self._parse_score_factors()
            }
        except Exception as e:
            print(f"Error parsing credit score: {e}")

    def _parse_score_factors(self):
        """
        Parse credit score factors.

        :return: List of score factors
        """
        factors_index = self.text.find("factores")
        rnc_index = self.text.find("rnc")

        if factors_index == -1 or rnc_index == -1:
            return []

        factors_text = self.text[factors_index + 36: rnc_index - 1]
        return [factor.strip() for factor in factors_text.replace('* ', '').replace(') ', ')').split('\n') if factor.strip()]

    def parse_open_accounts_summary(self):
        """
        Parse summary of open accounts.
        """
        summary_index = self.text.find("resumen de cuentas abiertas")
        if summary_index == -1:
            return

        try:
            # Find the end of the summary section
            end_sections = [
                "leyenda comportamiento historico",
                "detalle de cuentas abiertas"
            ]
            end_indices = [self.text.find(section, summary_index)
                           for section in end_sections]
            end_indices = [idx for idx in end_indices if idx != -1]
            summary_end_index = min(
                end_indices) if end_indices else len(self.text)

            # Extract summary text
            summary_text = self.text[summary_index + 28: summary_end_index]
            summary_lines = summary_text.split('\n')

            # Find the data rows
            first_row_start = 17
            last_row_end = summary_lines.index("total general >>")

            # Process rows
            data_rows = [summary_lines[i:i+11]
                         for i in range(first_row_start, last_row_end, 11)]

            self.parsed_data['summary_open_accounts'] = [
                {
                    "subscriber": row[0],
                    "accounts_amount": row[1],
                    "account_type": row[2],
                    "credit_amount_dop": row[3],
                    "credit_amount_usd": row[4],
                    "current_balance_dop": row[5],
                    "current_balance_usd": row[6],
                    "current_overdue_dop": row[7],
                    "current_overdue_usd": row[8],
                    "utilization_percent_dop": row[9],
                    "utilization_percent_usd": row[10],
                }
                for row in data_rows
            ]
        except Exception as e:
            print(f"Error parsing open accounts summary: {e}")
      
    def parse_open_accounts_details(self):
        """
        Parse details of open accounts with comprehensive error handling.
        """
        details_index = self.text.find("detalle de cuentas abiertas")
        if details_index == -1:
            print("Warning: 'detalle de cuentas abiertas' section not found.")
            return
        
        try:
            # Find the end of the details section
            end_sections = [
                "detalle de cuentas cerradas / inactivas",
                "indagaciones ultimos 6 meses"
            ]
            end_indices = [self.text.find(section, details_index) for section in end_sections]
            end_indices = [idx for idx in end_indices if idx != -1]
            details_end_index = min(end_indices) if end_indices else len(self.text)
            
            # Extract details text
            details_text = self.text[details_index + 28 : details_end_index]
            details_lines = details_text.split('\n')
            
            # Find the data rows
            first_row_start = next((i for i, line in enumerate(details_lines) if ">>" in line), 26)
            last_row_marker = "totales generales rd$:"
            last_row_end = next((i for i, line in enumerate(details_lines[first_row_start:]) if last_row_marker in line), len(details_lines))
            
            details_rows = details_lines[first_row_start:first_row_start + last_row_end]
            
            # Process accounts details rows
            processed_rows = self._process_accounts_details_rows(details_rows)
            
            # Map processed rows to the desired dictionary format
            self.parsed_data['details_open_accounts'] = [
                {
                    "account_type": row[0],
                    "subscriber": row[1],
                    "status": row[2],
                    "update_date": row[3],
                    "opening_date": row[4],
                    "expiration_date": row[5],
                    "currency": row[6],
                    "credit_limit": row[7],
                    "current_balance": row[8],
                    "balance_in_arrears": row[9],
                    "minimum_payment_and_installment": row[10],
                    "no_of_installments_and_modality": row[11],
                    "behavior_vector_last_12_months": row[12] if len(row) > 12 else None,
                }
                for row in processed_rows
            ]
            
            #print(f"Processed {len(self.parsed_data['details_open_accounts'])} open accounts details")
        
        except Exception as e:
            print(f"Comprehensive error parsing open accounts details: {e}")
            import traceback
            traceback.print_exc()

    def _process_accounts_details_rows(self, details_rows):
        """
        Process the rows of account details, handling subscriber and account type 
        in a way similar to the legacy code.
        
        :param details_rows: List of raw details rows
        :return: Processed list of rows with subscribers
        """
        details_of_open_accounts_list_suscribers_rows = []
        current_sublist = []  # Initialize an empty sublist

        def process_table_details_account(current_sublist):
            """
            Process table details for a specific account/subscriber.
            
            :param current_sublist: Current sublist to process
            """
            # Extract and process subscriber information
            details_subscriber = current_sublist[0].split(">>")
            
            # Strip whitespace from subscriber elements
            details_subscriber = [s.strip() for s in details_subscriber]
            
            # Create sublists of 11 elements each (excluding the subscriber row)
            remaining_sublists = [current_sublist[i:i+11] for i in range(1, len(current_sublist), 11)]
            
            # Add subscriber to each sublist
            for element in remaining_sublists:
                # Combine subscriber info with row data
                full_row = details_subscriber + element
                
                # Handle behavior vector (assuming last element is the behavior vector)
                if len(full_row) >= 13:
                    # Convert behavior vector to list of integers
                    try:
                        behavior_vector = [int(char) if char.isdigit() else None 
                                          for char in full_row[12].replace(" ", "")]
                        full_row[12] = behavior_vector
                    except Exception:
                        # If conversion fails, keep original value
                        pass
                
                details_of_open_accounts_list_suscribers_rows.append(full_row)

        # Iterate through the rows
        for elemento in details_rows:
            if ">>" in elemento:
                # If we find ">>", save the current sublist and create a new one
                if current_sublist:
                    process_table_details_account(current_sublist)
                    current_sublist = []
            
            # Add elements to the current sublist
            current_sublist.append(elemento)

        # Process the last sublist
        if current_sublist:
            process_table_details_account(current_sublist)

        return details_of_open_accounts_list_suscribers_rows
      
    def parse(self):
        """
        Parse the entire credit report.
        """
        self.parse_inquirer_info()
        self.parse_personal_data()
        self.parse_credit_score()
        self.parse_open_accounts_summary()
        self.parse_open_accounts_details()
        
        return self.parsed_data

    def to_json(self, indent=2):
        """
        Convert parsed data to JSON.
        
        :param indent: Indentation for JSON formatting
        :return: JSON string of parsed data
        """
        return json.dumps(self.parsed_data, indent=indent, ensure_ascii=False)


def main():
    # Example usage
    parser = CreditReportParser("./output_text/idequel.txt")
    parsed_data = parser.parse()

    # Print or further process the parsed data
    print(parser.to_json())


if __name__ == "__main__":
    main()

