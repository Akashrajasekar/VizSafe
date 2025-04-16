from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from app.models.task import Task, TaskCreate, TaskUpdate

def register_routes(app, task_service):
    router = APIRouter(prefix="/api", tags=["tasks"])
    
    @router.get("/tasks", response_model=List[Dict[str, Any]])
    def get_tasks():
        tasks = task_service.get_all_tasks()
        return [task.to_dict() for task in tasks]
    
    @router.get("/tasks/{task_id}", response_model=Dict[str, Any])
    def get_task(task_id: int):
        task = task_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    
    @router.post("/tasks", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
    def create_task(task_data: dict):
        task = task_service.create_task(task_data)
        return task.to_dict()
    
    @router.put("/tasks/{task_id}", response_model=Dict[str, Any])
    def update_task(task_id: int, task_data: dict):
        task = task_service.update_task(task_id, task_data)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    
    @router.delete("/tasks/{task_id}", response_model=Dict[str, str])
    def delete_task(task_id: int):
        success = task_service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    
    # Include router in the app
    app.include_router(router)