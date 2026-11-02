from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = None

class UserResponse(ORMModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None = None
    role: str
    is_active: bool | None = None

class PetCreate(BaseModel):
    owner_id: int | None = None
    name: str = Field(min_length=1, max_length=255)
    species: str = Field(min_length=1, max_length=100)
    breed: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    weight_kg: float | None = Field(default=None, gt=0)
    image_url: str | None = None

class PetResponse(ORMModel):
    id: int
    owner_id: int
    name: str
    species: str
    breed: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    weight_kg: Decimal | None = None
    image_url: str | None = None
    created_at: datetime | None = None

class AppointmentCreate(BaseModel):
    clinic_id: int
    pet_id: int
    service_id: int | None = None
    vet_id: int | None = None
    appointment_date: date
    start_time: time
    reason: str | None = None

class AppointmentStatus(BaseModel):
    status: str

class AppointmentResponse(ORMModel):
    id: int
    clinic_id: int
    pet_id: int
    service_id: int | None = None
    vet_id: int | None = None
    appointment_date: date
    start_time: time
    reason: str | None = None
    status: str | None = None
    created_at: datetime | None = None

class VaccinationCreate(BaseModel):
    pet_id: int
    vaccine_name: str = Field(min_length=1, max_length=255)
    administered_date: date | None = None
    next_due_date: date | None = None
    notes: str | None = None

class VaccinationResponse(ORMModel):
    id: int
    pet_id: int
    vaccine_name: str
    administered_date: date | None = None
    next_due_date: date | None = None
    notes: str | None = None
    created_at: datetime | None = None

class VisitCreate(BaseModel):
    pet_id: int
    vet_id: int | None = None
    visit_date: datetime | None = None
    symptoms: str | None = None
    observations: str | None = None
    diagnosis: str | None = None
    treatment_notes: str | None = None
    follow_up_date: date | None = None

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
