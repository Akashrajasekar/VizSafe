# Demo Setup Full-Stack Application

A full-stack application with a React frontend and FastAPI backend for managing tasks.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or newer)
- [npm](https://www.npmjs.com/) 
- [Python](https://www.python.org/) (v3.8 or newer)

## Getting Started

Follow these instructions to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/Akashrajasekar/VizSafe.git
cd VizSafe
```

### 2. Set Up the Backend

#### Create and Activate a Virtual Environment

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
# For Windows
python -m venv hack
.\hack\Scripts\activate


```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Run the Backend Server

```bash
# Make sure you're in the backend directory
python run.py
```

The FastAPI backend will start on http://localhost:5000

You can access the API documentation at:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

### 3. Set Up the Frontend

#### Install Dependencies

```bash
# Open a new terminal window
# Navigate to the frontend directory from the project root
cd frontend

# Install dependencies
npm install

```

#### Run the Frontend Development Server

```bash
npm start

```

The React application will start on http://localhost:3000

### 4. Using the Application

1. Open your browser and navigate to http://localhost:3000
2. You'll see the home page with a welcome message
3. Click on "Go to Dashboard" to manage your tasks
4. On the dashboard, you can:
   - View existing tasks
   - Add new tasks
   - Mark tasks as complete/incomplete
   - Delete tasks

## Project Structure

```
my-fullstack-app/
├── frontend/                     # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── pages/                # Page components
│   │   ├── services/             # API services
│   │   ├── App.js                # Main App component
│   │   └── ...
│   └── package.json
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # Main FastAPI application
│   │   ├── config.py             # Configuration
│   │   ├── models/               # Data models
│   │   ├── routes/               # API routes
│   │   └── services/             # Business logic
│   ├── run.py                    # Entry point script
│   └── requirements.txt
└── README.md                     # This file
```

## API Endpoints

- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/{task_id}` - Get a specific task
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task

## Technologies Used

### Frontend
- React
- React Router
- CSS for styling

### Backend
- FastAPI
- Pydantic for data validation
- Uvicorn as the ASGI server

## Development Notes

- The backend currently uses in-memory storage for tasks. For a production application, you would want to integrate with a database.
- The frontend communicates with the backend via RESTful API calls.

# Frontend Development

- The frontend uses **React Router** for navigation between pages.
- API services are centralized in the `src/services/api.js` file.
- Styles are defined in `src/App.css`.

# Backend Development

The backend uses **FastAPI**, a modern, high-performance web framework for building APIs with Python.

## FastAPI Features

- **Automatic API documentation** with Swagger UI and ReDoc
- **Type hints** for better code safety and editor support
- **Pydantic** for data validation
- **Built on Starlette** for excellent performance

The backend uses a simple **in-memory storage** for tasks.  
*In a production application, you would replace this with a database (e.g., SQLite, PostgreSQL, MongoDB).*

## Application Architecture

The application follows a layered architecture:

- **Models:** Define data structures with Pydantic models
- **Services:** Implement business logic
- **Routes:** Handle HTTP requests and responses with automatic validation
