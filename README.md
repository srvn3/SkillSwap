# SkillSwap — Student Skill Exchange Platform

**A full-stack web application deployed on AWS EC2 that connects students to teach, learn, and exchange skills.**

## About the Project

SkillSwap is a student skill exchange platform designed to encourage collaborative learning.

Students can register, create profiles, share skills they can teach, discover skills offered by others, and send skill exchange requests.

For example, a student who knows Python can offer to teach it, while another student interested in learning Python can request a skill exchange.

## Features

- **User Registration:** Students can create an account.
- **User Login:** Secure login with password hashing and token-based authentication.
- **Dashboard:** Displays an overview of skills and swap requests.
- **Discover Skills:** Browse and search skills published by other students.
- **Add Skill:** Add skills to teach or skills to learn.
- **My Skills:** View and manage personal skills.
- **Swap Requests:** Send, receive, accept, or reject skill exchange requests.
- **My Profile:** View registered account information.
- **Logout:** Sign out of the application.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite |
| Web Server | Apache HTTP Server |
| Cloud Platform | Amazon Web Services (AWS) |
| Cloud Computing | Amazon EC2 |
| Operating System | Amazon Linux 2023 |
| API Communication | REST APIs, JSON |
| Backend Service | systemd |

## Project Structure

```text
SkillSwap/
├── frontend/
│   └── index.html
├── backend/
│   ├── main.py
│   └── requirements.txt
├── README.md
└── .gitignore
```

The frontend contains the user interface, styling, and JavaScript functionality.

The backend contains FastAPI endpoints, authentication, database operations, and skill exchange logic.

## System Architecture

```text
           User / Web Browser
                   |
                   v
            CLIENT AWS EC2
          Apache HTTP Server
         HTML + CSS + JavaScript
                   |
                   | REST API Requests
                   | Apache Reverse Proxy
                   v
            SERVER AWS EC2
              Python FastAPI
                   |
                   v
             SQLite Database
```

The project uses two AWS EC2 instances:

**Client EC2:** Hosts the frontend using Apache HTTP Server.

**Server EC2:** Runs the Python FastAPI backend and manages the SQLite database.

Apache forwards requests beginning with `/api/` to the backend EC2 instance through its private IP address.

## How SkillSwap Works

1. A student opens the SkillSwap website.
2. The student registers or logs in.
3. FastAPI authenticates the student using SQLite.
4. The dashboard displays the student's information.
5. The student adds skills they can teach or want to learn.
6. Other students discover available skills.
7. A student sends a skill swap request.
8. The receiver can accept or reject the request.
9. The request status is stored in the database.

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a student |
| POST | `/api/auth/login` | Log in |
| GET | `/api/profile/me` | View account profile |
| GET | `/api/skills` | Discover skills |
| GET | `/api/skills/mine` | View personal skills |
| POST | `/api/skills` | Add a skill |
| DELETE | `/api/skills/{sid}` | Delete a skill |
| POST | `/api/swaps` | Send a swap request |
| GET | `/api/swaps` | View swap requests |
| PATCH | `/api/swaps/{sid}?decision=accepted` | Accept a request |
| PATCH | `/api/swaps/{sid}?decision=rejected` | Reject a request |

## Database

SkillSwap uses SQLite to store application information.

The database contains four main tables:

| Table | Purpose |
|---|---|
| `users` | Stores student account information |
| `sessions` | Stores authentication sessions |
| `skills` | Stores offered and wanted skills |
| `swaps` | Stores skill exchange requests and their statuses |

The database file is generated automatically by the backend when it starts.

## Running the Project Locally

### Requirements

- Python 3.9 or newer
- pip
- A modern web browser

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/SkillSwap.git
cd SkillSwap
```

Replace `YOUR-USERNAME` with the GitHub account name.

### Step 2: Install backend dependencies

```bash
python -m pip install -r backend/requirements.txt
```

### Step 3: Start the backend

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

FastAPI runs at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### Step 4: Configure the frontend

The frontend makes API requests using `/api/` paths. It is designed to run behind Apache with reverse proxy configuration.

For full application functionality, configure Apache to serve `frontend/index.html` and forward `/api/` requests to the FastAPI backend.

Opening the HTML file directly without this configuration will not connect it to the backend.

## AWS Deployment

The application is deployed using two Amazon Linux EC2 instances.

- **Frontend instance:** Apache serves the web application.
- **Backend instance:** FastAPI runs on port 8000.
- **Reverse proxy:** Apache forwards API requests to the backend using its private IP.
- **Service management:** systemd manages the FastAPI backend process.
- **Database:** SQLite stores the application data.

This separates frontend hosting from backend processing.

## Testing

The application includes functionality for:

- Registration and login
- Adding and discovering skills
- Viewing and deleting personal skills
- Sending and viewing swap requests
- Accepting and rejecting requests
- Viewing account details
- Logging out
- Frontend-to-backend API communication

## Future Enhancements

- Skill recommendations
- Real-time chat between students
- Email notifications
- User ratings and reviews
- Improved skill matching
- Mobile application support

## Project Team

Developed as a student full-stack cloud computing project.

**Project:** SkillSwap — Student Skill Exchange Platform

**Platform:** AWS EC2

**Backend Framework:** FastAPI

**Database:** SQLite
