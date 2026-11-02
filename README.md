# AnimalCare AI - FastAPI Backend

A modular FastAPI starter backend for the AnimalCare AI veterinary clinic platform.

## Current stage

- API routers and request schemas are created.
- Temporary in-memory mock data is included.
- CRUD and workflow endpoints are available for frontend integration.
- Neon PostgreSQL is **not connected yet**.
- Data resets when the API process restarts.
- Demo login and assistant responses are not production authentication or real LLM functionality.

## Requirements

- Python 3.10+
- pip

## Run on Windows PowerShell

Open PowerShell in this `backend` folder:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Open:
- API root: http://127.0.0.1:8000/
- Swagger docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health

## Demo login accounts

All demo accounts use password `demo123`:
- Owner: `owner@example.com`
- Vet: `vet@example.com`
- Admin: `admin@example.com`

The returned `DEMO_TOKEN_NOT_FOR_PRODUCTION` is a placeholder, not a secure JWT. Do not deploy this demo authentication publicly.

## API overview

| Area | Endpoint | Methods |
|---|---|---|
| Health | `/api/v1/health` | GET |
| Auth | `/api/v1/auth/login`, `/api/v1/auth/me` | POST, GET |
| Pets | `/api/v1/pets/` and `/api/v1/pets/{id}` | GET, POST, PUT, DELETE |
| Appointments | `/api/v1/appointments/` | GET, POST |
| Appointment status | `/api/v1/appointments/{id}/status?status=confirmed` | PATCH |
| Complete appointment | `/api/v1/appointments/{id}/complete` | POST |
| Patients | `/api/v1/patients/`, `/api/v1/patients/{id}` | GET |
| Patient history | `/api/v1/patients/{id}/history` | GET |
| Vaccinations | `/api/v1/vaccinations/` | GET, POST, PUT, DELETE |
| Services | `/api/v1/services/` | GET |
| Dashboard | `/api/v1/dashboard/clinic`, `/api/v1/dashboard/owner` | GET |
| Owner assistant | `/api/v1/assistant/owner-chat` | POST |
| Clinic assistant | `/api/v1/assistant/clinic-chat` | POST |
| Analytics | `/api/v1/analytics/overview` | GET |

## Example request bodies

### Add pet

```json
{
  "owner_id": 1,
  "name": "Rocky",
  "species": "Dog",
  "breed": "Labrador",
  "gender": "Male",
  "date_of_birth": "2024-02-12",
  "weight_kg": 12.5
}
```

### Book appointment

```json
{
  "clinic_id": 1,
  "pet_id": 1,
  "service_id": 1,
  "vet_id": 2,
  "appointment_date": "2026-11-10",
  "start_time": "11:30",
  "reason": "Routine check-up"
}
```

### Owner chat

```json
{
  "message": "How can I book an appointment?"
}
```

### Clinic chat

```json
{
  "message": "How many pending appointments?"
}
```

## Frontend integration

Angular should call this backend at `http://localhost:8000/api/v1`.
Keep database credentials in backend environment variables only. Never put the Neon connection string in Angular.

## Planned next stage: Neon PostgreSQL

1. Add SQLAlchemy models matching the existing Neon tables.
2. Add `DATABASE_URL` to local `.env` (never commit it).
3. Add database session/dependency and repositories.
4. Replace in-memory store access with database operations.
5. Add Alembic migrations and proper authentication/authorization.
6. Add tests before deploying.

## Important safety note

This is a development starter with synthetic demo data. It does not provide production-grade authentication, clinic tenant isolation, medical decision support, or audit logging. A veterinarian must review clinical information; the pet-care assistant is educational only.
