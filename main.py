from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.patients import router as patients_router
from api.routes.alerts import router as alerts_router
from api.routes.admin import router as admin_router
from core.config import settings

app = FastAPI(title=settings.app_name)

# CORS – update origins when your Next.js app is live
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}


app.include_router(patients_router)
app.include_router(alerts_router)
app.include_router(admin_router)