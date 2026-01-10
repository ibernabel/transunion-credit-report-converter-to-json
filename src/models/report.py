from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class BaseReportModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

class InquirerInfo(BaseReportModel):
    subscriber: str = Field(..., alias="suscriptor")
    user: str = Field(..., alias="usuario")
    consultation_date: str = Field(..., alias="fecha_consulta")
    consultation_time: str = Field(..., alias="hora_consulta")

class PersonalPhones(BaseReportModel):
    home: Optional[str] = Field(None, alias="casa")
    work: Optional[str] = Field(None, alias="trabajo")
    mobile: Optional[str] = Field(None, alias="celular")

class PersonalInfo(BaseReportModel):
    identification: str = Field(..., alias="cedula")
    first_names: str = Field(..., alias="nombres")
    last_names: str = Field(..., alias="apellidos")
    birth_date: str = Field(..., alias="fecha_nacimiento")
    age: Optional[int] = Field(None, alias="edad")
    occupation: Optional[str] = Field(None, alias="ocupacion")
    birth_place: Optional[str] = Field(None, alias="lugar_nacimiento")
    passport: Optional[str] = Field(None, alias="pasaporte")
    marital_status: Optional[str] = Field(None, alias="estado_civil")
    phones: PersonalPhones = Field(default_factory=PersonalPhones)
    addresses: List[str] = Field(default_factory=list, alias="direcciones")

class CreditScore(BaseReportModel):
    score: Optional[int] = None
    factors: List[str] = Field(default_factory=list)

class AccountSummary(BaseReportModel):
    subscriber: str
    accounts_amount: int
    account_type: str
    credit_amount_dop: float
    credit_amount_usd: float
    current_balance_dop: float
    current_balance_usd: float
    current_overdue_dop: float
    current_overdue_usd: float
    utilization_percent_dop: float
    utilization_percent_usd: float

class AccountDetail(BaseReportModel):
    account_type: str
    subscriber: str
    status: str
    update_date: str
    opening_date: str
    expiration_date: Optional[str] = None
    currency: str
    credit_limit: float
    current_balance: float
    balance_in_arrears: float
    minimum_payment_installment: float
    no_installments_modality: str
    behavior_vector_last_12_months: List[Optional[int]] = Field(default_factory=list)

class CreditReport(BaseReportModel):
    inquirer: InquirerInfo
    personal_data: PersonalInfo
    score: Optional[CreditScore] = None
    summary_open_accounts: List[AccountSummary] = Field(default_factory=list)
    details_open_accounts: List[AccountDetail] = Field(default_factory=list)
