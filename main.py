from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import patients_router, alerts_router, admin_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

# CORS – adjust origins when you know your Next.js URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later: restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}


# Include routers
app.include_router(patients_router)
app.include_router(alerts_router)
app.include_router(admin_router)