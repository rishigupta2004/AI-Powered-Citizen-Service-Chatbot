from pydantic import BaseModel
from typing import Optional

# Passport
class PassportKendra(BaseModel):
    name: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]

class PassportStatus(BaseModel):
    file_no: str
    status: str
    message: Optional[str]

# Aadhaar
class AadhaarEKYC(BaseModel):
    aadhaar: str
    verified: bool
    name: Optional[str]

# EPFO
class EPFOBalance(BaseModel):
    uan: str
    balance: float
    last_updated: Optional[str]

# PAN
class PANVerification(BaseModel):
    pan: str
    valid: bool
    name: Optional[str]

# Parivahan
class DLStatus(BaseModel):
    dl_no: str
    status: str
    holder_name: Optional[str]

# Common service/procedure schemas for validation tests
class ServiceSchema(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    ministry: Optional[str] = None

class ProcedureSchema(BaseModel):
    title: str
    description: Optional[str] = None
    procedure_type: Optional[str] = None
