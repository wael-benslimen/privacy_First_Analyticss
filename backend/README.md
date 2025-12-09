# Backend - Django REST API

This directory contains the Django backend for the Privacy First Analytics application.

## Structure

```
backend/
├── api/              # Django app with models, views, serializers
├── config/           # Django project configuration
├── scripts/          # Utility scripts (e.g., create_user.py)
├── manage.py         # Django management script
└── requirements.txt  # Python dependencies
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```bash
   python scripts/create_user.py
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Quick Start

Use the startup script from the project root:
```bash
scripts\start_backend.bat
```

## API Endpoints

The API will be available at `http://localhost:8000/api/`

For detailed API documentation, refer to `api/urls.py` and `api/views.py`.

## Configuration

Environment-specific settings can be configured in `config/settings.py`.
