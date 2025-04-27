![github-submission-banner](https://github.com/user-attachments/assets/a1493b84-e4e2-456e-a791-ce35ee2bcf2f)

# 🤖 Ai.ble 🔊📖

> Knowledge has never been more access_Ai_ble!

[Our App!](https://vizsafe-kbgjudorbna9couafvdsqd.streamlit.app/)
---

## 📌 Problem Statement
 
**Problem Statement 1 – Weave AI magic with Groq**

---

## 🎯 Objective

Our aim is to provide a one-stop-app for every accessibility user to harness the power of Multi-Modal AI to assist them in building their learning journey. No matter the disability, our solution curates a personalized and assitive course path for your educational needs. Just "say" the word, choose the number of topics and the difficulty level, and voila! Your very own learning plan will be displayed on our App, and spoken back to you!

---

## 🧠 Team & Approach

### Team Name:  
`The Resistance`

### Team Members:  
| Name                          | LinkedIn                                                                 | GitHub                                           |
|-------------------------------|--------------------------------------------------------------------------|--------------------------------------------------|
| 🐦‍⬛ Akash Rajasekar          | [LinkedIn](https://www.linkedin.com/in/akash-rajasekar/)               | [GitHub](https://github.com/Akashrajasekar)      |
| 🧚 Ilfa Shaheed Valiyallappil | [LinkedIn](https://www.linkedin.com/in/ilfa-shaheed-722250242/)         | [GitHub](https://github.com/ilfa2003)            |
| 🪄 Laya Shree Elango          | [LinkedIn](https://www.linkedin.com/in/laya-shree-elango/)              | [GitHub](https://github.com/Laya-Shree)          |
| 🎮 Karthik Vishal S. Ramkumar | [LinkedIn](https://www.linkedin.com/in/karthik-vishal-sr/)              | [GitHub](https://github.com/Karthik-Vishal03)    |


### Our Approach:  
- **Why this problem**: To design the ideal learning platform for accessibility users, and make the experience absolutely simple and learning focussed. 
- **Key challenges addressed**: _Voice-assisted learning_, _Simplified UI_, _Personalized Course-plan_ for every user.     
- **Pivots, brainstorms, breakthroughs**: We were able to efficiently manage our tokens by training our multi-modal AI system to recipropcate crisp and consise educational solutions!
  
---

## 🛠️ Tech Stack

### Core Technologies Used:
- Frontend: Streamlit
- Backend: Python
- APIs: Groq
- Hosting: Streamlit

### Sponsor Technologies Used (if any):
- [X] ✅ **Groq:** _Text, Speech-to-Text, Text-to-Speech models_  
- [ ] **Monad:** _Your blockchain implementation_  
- [ ] **Fluvio:** _Real-time data handling_  
- [ ] **Base:** _AgentKit / OnchainKit / Smart Wallet usage_  
- [ ] **Screenpipe:** _Screen-based analytics or workflows_  
- [ ] **Stellar:** _Payments, identity, or token usage_

---

## ✨ Key Features

Most important features of our project:

- ✅ Voice prompts to our AI assistant `Ai_ble`
- ✅ Customized options to choose the extent of the course plan (number of topics) and the difficulty level.
- ✅ Complete course charted in _text_by the AI, with proper formatting of details under every topic.
- ✅ Voice assisted reading of course content

![Image 1](https://github.com/Akashrajasekar/VizSafe/blob/master/Assets/Ai_ble_HomePage.jpg) <br>
![Image 2](https://github.com/Akashrajasekar/VizSafe/blob/master/Assets/Ai_ble_CourseGen.jpg) <br>
![Image 3](https://github.com/Akashrajasekar/VizSafe/blob/master/Assets/Ai_ble_Success.jpg) <br>
![Image 4](https://github.com/Akashrajasekar/VizSafe/blob/master/Assets/Ai_ble_Library.jpg)

---

## 📽️ Demo & Deliverables

- **Demo Video Link:** [Loom Link](https://www.loom.com/share/94f51049526c4b06b134970592a005e2?sid=84befc95-3960-4a40-881b-6bbda2437ca0)
- **Pitch Deck / PPT Link:** [PPT Link](https://docs.google.com/presentation/d/1zk2sTzOtVDeqdCsRSq4uy-j-FtPJiXJbFlb08atbmLk/edit?usp=sharing)

---

## ✅ Tasks & Bonus Checklist

- [X] ✅**All members of the team completed the mandatory task - Followed at least 2 of our social channels and filled the form** (Details in Participant Manual)  
- [X] ✅**All members of the team completed Bonus Task 1 - Sharing of Badges and filled the form (2 points)**  (Details in Participant Manual)
- [X] ✅**All members of the team completed Bonus Task 2 - Signing up for Sprint.dev and filled the form (3 points)**  (Details in Participant Manual)

---

## 🧑‍💻 How to Run the Project ‼️‼️‼️(change)

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or newer)
- [npm](https://www.npmjs.com/) 
- [Python](https://www.python.org/) (v3.8 or newer)

## Getting Started

Follow these instructions to get the application running on your local machine.

### 1. Clone the Repository
‼️[Make the dev as default]

```bash
‼️git clone -b dev https://github.com/Akashrajasekar/VizSafe.git
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
- **Routes:** Handle HTTP requests and responses with automatic validation ‼️‼️‼️

## 🧬 Future Scope

- 📈 ‼️‼️‼️
- 🛡️ ‼️‼️‼️
---

## 📎 Resources / Credits

- Groq API keys: https://console.groq.com/keys
- Groq documentation: https://console.groq.com/docs/overview
- Groq help videos: https://youtu.be/Ig7esRBhFPY

---

## 🏁 Final Words

Shout out to 🦖[Aaryan Sinha](https://github.com/AaryanTheLaughingGas)
---
