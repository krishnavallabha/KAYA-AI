from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.api.endpoints import ingest, materials, schedule, alerts, actions
from backend.rag.router import router as rag_router
from backend.api.endpoints import schedule_planner


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(rag_router, prefix="/api/v1")
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["Ingest"])
app.include_router(materials.router, prefix=f"{settings.API_V1_STR}/materials", tags=["Materials"])
app.include_router(schedule.router, prefix=f"{settings.API_V1_STR}/schedule", tags=["Schedule"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_STR}/alerts", tags=["Alerts"])
app.include_router(actions.router, prefix=f"{settings.API_V1_STR}/actions", tags=["Actions"])
app.include_router(schedule_planner.router,prefix=settings.API_V1_STR,)


@app.get("/")
def root():
    return {
        "message": "Welcome to the FlowSense AI Backend API"
    }