# Waste Management System

A comprehensive Django-based waste management system with role-based access, REST API, and analytics dashboard.

## Features

- **Role-based Authentication**: Admin, Staff, and User roles
- **Waste Pickup Management**: Schedule, assign, and track pickups
- **REST API**: Full API for mobile apps and integrations
- **Analytics Dashboard**: Charts and statistics
- **Bootstrap UI**: Responsive, modern interface
- **PostgreSQL Ready**: Production database support

## Quick Start

### 1. Environment Setup

```bash
# Clone or download the project
cd waste_system

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` and login with your superuser credentials.

## Project Structure

```
waste_system/
├── core/              # Main app (pickups, waste types)
├── users/             # User management & authentication
├── dashboard/         # Analytics & dashboard
├── waste_management/  # Project settings
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── media/            # User uploads
└── db.sqlite3        # Database (development)
```

## User Roles

- **Admin**: Full system access, user management, analytics
- **Staff**: Pickup assignment, completion, limited admin access
- **User**: Schedule pickups, view own requests

## API Endpoints

- `GET/POST /api/pickups/` - Pickup management
- `GET/POST /api/waste-types/` - Waste type management
- `GET /api/users/` - User information
- `POST /api/pickups/{id}/assign/` - Assign pickup to staff
- `POST /api/pickups/{id}/complete/` - Mark pickup complete

## Deployment to Render

### 1. Prepare for Production

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# SECRET_KEY=your-production-secret
# DEBUG=False
# DATABASE_URL=your-postgresql-url
```

### 2. Create Render Services

1. **Web Service**:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn waste_management.wsgi`

2. **PostgreSQL Database**:
   - Create PostgreSQL instance
   - Copy connection URL to environment variables

### 3. Environment Variables

Add these to Render:

```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
```

### 4. Deploy

Push to GitHub and connect to Render. Your app will be live!

## Technologies Used

- **Backend**: Django 6.0, Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Bootstrap 5, Chart.js
- **Deployment**: Render (free tier)
- **Authentication**: Django Auth with custom user model

## Development

### Running Tests

```bash
python manage.py test
```

### Code Formatting

```bash
# Install black and isort
pip install black isort

# Format code
black .
isort .
```

### API Documentation

API endpoints are self-documenting. Visit `/api/` for browsable API.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## ✨ Features

- **Full CRUD Operations**: Complete Create, Read, Update, Delete for users and pickups
- **Relational Database**: SQLite with proper foreign key relationships
- **Modular Architecture**: Clean separation of concerns (DB, Services, UI)
- **Professional UI**: Modern Tkinter dashboard with navigation
- **Calendar System**: Interactive pickup scheduling calendar
- **Status Workflow**: Pickup status management (Pending → Driver Assigned → In Transit → Completed)
- **Data Validation**: Input validation and error handling

## 🚀 Getting Started

1. **Navigate to the project directory**:
   ```bash
   cd waste_system
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

## 🧠 Architecture Overview

### Database Layer (`db/`)
- `connection.py`: Manages SQLite connections with row factory
- `init_db.py`: Creates tables and initializes the database
- `schema.sql`: SQL schema definitions

### Service Layer (`services/`)
- `user_service.py`: User management (CRUD operations)
- `pickup_service.py`: Pickup management with status validation

### UI Layer (`ui/`)
- `app.py`: Main Tkinter application with dashboard and navigation

## 📊 Database Schema

### Users Table
- `user_id` (Primary Key)
- `name` (Required)
- `province`, `city`, `barangay`
- `house_id` (Unique)
- `address`

### Pickups Table
- `pickup_id` (Primary Key)
- `user_id` (Foreign Key → users)
- `date`, `time`
- `status` (Default: 'Pending')

## 🎯 Status Flow

Pickups follow this status progression:
1. **Pending** - Initial status
2. **Driver Assigned** - Driver has been assigned
3. **In Transit** - Pickup is underway
4. **Completed** - Pickup finished

## 🛠️ Development

The application uses:
- **Python 3.14+**
- **Tkinter** for GUI
- **SQLite** for data persistence
- **Modular architecture** for maintainability

## 📝 License

This project is open source and available under the MIT License.