# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.task import Task
from app.services.task_service import TaskService
from app import config

app = FastAPI(title="Task Manager API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize task service
task_service = TaskService()

# Import routes
from app.routes.tasks import register_routes
register_routes(app, task_service)