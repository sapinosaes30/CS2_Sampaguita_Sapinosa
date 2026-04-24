# 🚀 MAX LEVEL WASTE MANAGEMENT SYSTEM

A professional-grade waste management application built with Python, Tkinter, and SQLite.

## 📁 Project Structure

```
waste_system/
├── db/                    # Database layer
│   ├── connection.py     # SQLite connection management
│   ├── init_db.py        # Database initialization
│   └── schema.sql        # Database schema
├── services/             # Business logic layer
│   ├── user_service.py   # User CRUD operations
│   └── pickup_service.py # Pickup CRUD operations
├── ui/                   # User interface layer
│   └── app.py           # Main Tkinter application
└── main.py              # Application entry point
```

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