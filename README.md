# 🚀 Interview Platform (Real-Time Code Editor & Whiteboard)

## 📌 Project Overview
This is a real-time **interview collaboration platform** built with **Django + Django Channels**.  
It includes:
- 📝 **Real-Time Code Editor** (via WebSockets)
- 🖌️ **Shared Whiteboard** (via WebSockets)
- 🔄 **WebSockets using Django Channels**
- 📡 **Redis for real-time communication**

---

## 🔧 Setup & Installation

### 🛠️ **1. Clone the Repository**

```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/interview-platform.git
cd interview-platform
```

### 📦 2. Set Up Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 🚀 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 🛠️ 4. Configure Environment Variables

Create a .env file:
```sh
DJANGO_SECRET_KEY="your-secret-key"
DEBUG=True
```

### 🔄 5. Run Migrations

```sh
python manage.py makemigrations
python manage.py migrate
```

### 🖥️ 6. Start Redis (Docker)

```sh
docker run -p 6379:6379 --name redis-container -d redis:latest
```

### 🚀 7. Run the Server

Using Django (For HTTP only)

```sh
python manage.py runserver
```

Using Daphne (For WebSockets)

```sh
daphne -b 0.0.0.0 -p 8000 interview_platform.asgi:application
```

### 🖥️ Usage

    Open http://127.0.0.1:8000/editor/ → Start real-time text editing
    Open http://127.0.0.1:8000/whiteboard/ → Start drawing in real-time
    Open in two browser windows and test real-time updates.

### 📌 Technologies Used

    Django 5.x → Web framework
    Django Channels → WebSockets support
    Redis → Real-time communication backend
    Daphne → ASGI server for WebSockets
    HTML + JavaScript → Frontend