from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import health, auth, pets, appointments, patients, vaccinations, services, dashboard, assistant, analytics, clinics

app = FastAPI(
    title="AnimalCare AI API",
    description="Backend API for the AnimalCare AI veterinary clinic platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(pets.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(vaccinations.router, prefix="/api/v1")
app.include_router(services.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(assistant.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(clinics.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to AnimalCare AI API", "docs": "/docs", "version": "1.0.0"}
