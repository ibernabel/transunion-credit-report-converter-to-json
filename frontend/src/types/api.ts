export interface InquirerInfo {
    suscriptor: string;
    usuario: string;
    fecha_consulta: string;
    hora_consulta: string;
}

export interface PersonalPhones {
    casa?: string;
    trabajo?: string;
    celular?: string;
}

export interface PersonalInfo {
    cedula: string;
    nombres: string;
    apellidos: string;
    fecha_nacimiento: string;
    edad?: number;
    ocupacion?: string;
    lugar_nacimiento?: string;
    pasaporte?: string;
    estado_civil?: string;
    phones: PersonalPhones;
    direcciones: string[];
}

export interface CreditScore {
    score?: number;
    factors: string[];
}

export interface AccountSummary {
    subscriber: string;
    accounts_amount: number;
    account_type: string;
    credit_amount_dop: number;
    credit_amount_usd: number;
    current_balance_dop: number;
    current_balance_usd: number;
    current_overdue_dop: number;
    current_overdue_usd: number;
    utilization_percent_dop: number;
    utilization_percent_usd: number;
}

export interface AccountDetail {
    account_type: string;
    subscriber: string;
    status: string;
    update_date: string;
    opening_date: string;
    expiration_date?: string;
    currency: string;
    credit_limit: number;
    current_balance: number;
    balance_in_arrears: number;
    minimum_payment_installment: number;
    no_installments_modality: string;
    behavior_vector_last_12_months: (number | null)[];
}

export interface CreditReport {
    inquirer: InquirerInfo;
    personal_data: PersonalInfo;
    score?: CreditScore;
    summary_open_accounts: AccountSummary[];
    details_open_accounts: AccountDetail[];
}
