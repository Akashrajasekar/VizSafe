from app.models.task import Task

class TaskService:
    def __init__(self):
        # In-memory storage for tasks (in a real app, you'd use a database)
        self.tasks = {}
        self.next_id = 1
        
        # Add some sample tasks
        sample_tasks = [
            {"title": "Complete project setup", "description": "Set up React and Flask project structure"},
            {"title": "Implement authentication", "description": "Add user login and registration"},
            {"title": "Add unit tests", "description": "Write tests for backend API"}
        ]
        
        for task_data in sample_tasks:
            self.create_task(task_data)
    
    def get_all_tasks(self):
        return list(self.tasks.values())
    
    def get_task_by_id(self, task_id):
        return self.tasks.get(task_id)
    
    def create_task(self, task_data):
        task = Task.from_dict(task_data, id=self.next_id)
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task
    
    def update_task(self, task_id, task_data):
        if task_id not in self.tasks:
            return None
        
        # Update existing task with new data
        current_task = self.tasks[task_id]
        updated_task = Task(
            id=task_id,
            title=task_data.get('title', current_task.title),
            description=task_data.get('description', current_task.description),
            completed=task_data.get('completed', current_task.completed)
        )
        
        self.tasks[task_id] = updated_task
        return updated_task
    
    def delete_task(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
