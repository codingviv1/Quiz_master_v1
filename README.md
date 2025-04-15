# Quiz Master V1

A multi-user quiz application built with Flask that allows administrators to create and manage quizzes, and users to attempt them.

## Features

- Admin and User roles
- Subject and Chapter management
- Quiz creation and management
- MCQ-based questions
- Score tracking
- User dashboard with performance charts
- RESTful API endpoints

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run the application:
```bash
python app.py
```

6. Access the application at `http://localhost:5000`

## Default Admin Credentials
- Username: admin@quizmaster.com
- Password: admin123

## Project Structure
```
quiz_master/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   └── templates/
├── config.py
├── init_db.py
└── app.py
``` 