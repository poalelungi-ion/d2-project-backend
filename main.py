"""
SPA System Backend API

Application entry point. This module only wires the application together:
it creates the FastAPI instance, applies CORS, mounts the routers and seeds
the database on startup.

Endpoint definitions live in routers/, grouped by resource:
    routers/students.py   student roster, profiles and transcripts
    routers/courses.py    course catalogue and archiving
    routers/grades.py     exam results
    routers/upload.py     CSV/Excel ingestion (preview and confirm)
    routers/stats.py      dashboard KPIs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
import models
from database import engine, ensure_schema
from routers import courses, grades, stats, students, upload
from seed import seed_db

models.Base.metadata.create_all(bind=engine)
ensure_schema()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed demonstration data on startup, unless disabled or already present."""
    if config.SEED_ON_STARTUP:
        seed_db()
    yield


app = FastAPI(title="Study Progress Analysis API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router, tags=["students"])
app.include_router(courses.router, tags=["courses"])
app.include_router(upload.router, tags=["upload"])
app.include_router(stats.router, tags=["stats"])
app.include_router(grades.router, tags=["grades"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the SPA Backend API!"}
