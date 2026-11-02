from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Identity, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Clinic(Base):
    __tablename__ = "clinics"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    opening_time: Mapped[time | None] = mapped_column(Time)
    closing_time: Mapped[time | None] = mapped_column(Time)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    members: Mapped[list["ClinicMember"]] = relationship(back_populates="clinic")
    services: Mapped[list["Service"]] = relationship(back_populates="clinic")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    memberships: Mapped[list["ClinicMember"]] = relationship(back_populates="user")
    pets: Mapped[list["Pet"]] = relationship(back_populates="owner", foreign_keys="Pet.owner_id")


class ClinicMember(Base):
    __tablename__ = "clinic_members"
    __table_args__ = (UniqueConstraint("clinic_id", "user_id"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    staff_role: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    clinic: Mapped[Clinic] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="memberships")


class Pet(Base):
    __tablename__ = "pets"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    species: Mapped[str] = mapped_column(String(100))
    breed: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[str | None] = mapped_column(String(50))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric)
    image_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    owner: Mapped[User] = relationship(back_populates="pets", foreign_keys=[owner_id])
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="pet")
    visits: Mapped[list["Visit"]] = relationship(back_populates="pet")
    vaccinations: Mapped[list["Vaccination"]] = relationship(back_populates="pet")


class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    duration_minutes: Mapped[int | None]
    price: Mapped[Decimal | None] = mapped_column(Numeric)
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default="true")
    clinic: Mapped[Clinic] = relationship(back_populates="services")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")


class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"))
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"))
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"))
    vet_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    appointment_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(50), server_default="pending")
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    pet: Mapped[Pet] = relationship(back_populates="appointments")
    service: Mapped[Service | None] = relationship(back_populates="appointments")
    visit: Mapped["Visit | None"] = relationship(back_populates="appointment", uselist=False)


class Visit(Base):
    __tablename__ = "visits"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"), unique=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"))
    vet_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    visit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    symptoms: Mapped[str | None] = mapped_column(Text)
    observations: Mapped[str | None] = mapped_column(Text)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    treatment_notes: Mapped[str | None] = mapped_column(Text)
    follow_up_date: Mapped[date | None] = mapped_column(Date)
    appointment: Mapped[Appointment | None] = relationship(back_populates="visit")
    pet: Mapped[Pet] = relationship(back_populates="visits")


class Vaccination(Base):
    __tablename__ = "vaccinations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"))
    vaccine_name: Mapped[str] = mapped_column(String(255))
    administered_date: Mapped[date | None] = mapped_column(Date)
    next_due_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    pet: Mapped[Pet] = relationship(back_populates="vaccinations")
