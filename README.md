# Household Services Application

A full-stack application for connecting customers with household service professionals. This platform facilitates service requests, professional management, and administrative oversight through a modern web interface.

## 📋 Features

### Customer Features

- Create an account and manage profile information
- Browse available services by category
- Find service professionals by location and service type
- Request services and track request status
- View service history and write reviews
- Receive monthly activity reports

### Professional Features

- Create a professional profile with service areas and types
- Accept or reject service requests
- Manage upcoming and past service appointments
- Track earnings and performance metrics
- Receive daily reminders for pending requests

### Admin Features

- Manage service categories and types
- Approve or block service professionals
- Export service data and generate reports
- View platform analytics and metrics
- Send notifications to users

## 🏗️ Architecture

### Backend (Flask)

- RESTful API built with Flask
- SQLite database with SQLAlchemy ORM
- JWT authentication for secure access
- Celery for background task processing (reminders, reports, exports)
- Redis for caching and Celery task management

### Frontend (HTML/CSS/JavaScript)

- Responsive design with modern UI components
- Client-side rendering for dynamic content
- Fetch API for asynchronous data loading
- Session-based authentication management

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for frontend development)
- Redis server (for Celery task queue)

### Installation and Setup

#### Backend Setup

1. Navigate to the backend directory:

   ```
   cd backend
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

5. Initialize the database:

   ```
   python populate_db.py
   ```

6. Start the Flask server:

   ```
   python app.py
   ```

7. The backend API will be available at `http://127.0.0.1:5000/`

#### Frontend Setup

1. Navigate to the frontend directory:

   ```
   cd frontend
   ```

2. Install dependencies (if you have package.json):

   ```
   npm install
   ```

3. Open the `index.html` file in your browser or use a local server:

   ```
   npx serve .
   ```

4. The frontend will be available at the provided URL (typically `http://localhost:3000`)

## 🔄 Background Tasks with Celery

The application uses Celery for handling background tasks:

### Starting Celery Worker

```
python start_celery_worker.py
```

### Starting Celery Beat (for scheduled tasks)

```
python start_celery_beat.py
```

### Available Background Tasks

- Daily reminders for professionals with pending requests
- Monthly activity reports for customers
- Asynchronous data exports for admin users

For detailed testing instructions, see the [Celery Testing Guide](backend/CELERY_TESTING_GUIDE.md).

## 📊 API Documentation

The API is documented using Swagger/OpenAPI. Access the documentation at `/apidocs` when the backend server is running.

### Authentication

- All API endpoints (except registration and login) require JWT authentication
- Token should be included in the `Authorization` header with the format: `Bearer <token>`

### Example API Endpoints

| Endpoint                                 | Method | Description                                |
| ---------------------------------------- | ------ | ------------------------------------------ |
| `/register`                              | POST   | Register a new user                        |
| `/login`                                 | POST   | Log in and obtain JWT token                |
| `/customer/profile`                      | GET    | Get customer profile information           |
| `/customer/professionals/<service_type>` | GET    | Find professionals by service type         |
| `/professional/requests`                 | GET    | Get service requests for a professional    |
| `/admin/service`                         | POST   | Create a new service                       |
| `/admin/export/<professional_id>`        | GET    | Export service requests for a professional |

## 🧪 Testing

### Backend Tests

To run the tests for individual components:

1. Test Celery reminders:

   ```
   python test_reminders.py
   ```

2. Test monthly reports:

   ```
   python test_reports.py
   ```

3. Test export functionality:
   ```
   python test_exports.py [professional_id]
   ```

### Frontend Testing

Open the application in your browser and ensure all features work correctly:

- User registration and login
- Service browsing and requesting
- Professional approval and service management
- Admin data exports and reporting

## 📁 Project Structure

### Backend Structure

```
backend/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models.py               # Database models
├── populate_db.py          # Database initialization script
├── requirements.txt        # Python dependencies
├── start_celery_beat.py    # Script to start Celery Beat scheduler
├── start_celery_worker.py  # Script to start Celery worker
├── test_exports.py         # Test script for export functionality
├── test_reminders.py       # Test script for reminders
├── test_reports.py         # Test script for reports
├── CELERY_TESTING_GUIDE.md # Guide for testing Celery tasks
├── routes/                 # API route definitions
│   ├── admin.py           # Admin-specific routes
│   ├── auth.py            # Authentication routes
│   ├── customer.py        # Customer-specific routes
│   ├── file.py            # File upload/download routes
│   └── professional.py    # Professional-specific routes
├── utils/                  # Utility functions
│   ├── celery_tasks.py    # Celery task definitions
│   ├── email.py           # Email sending utilities
│   ├── export_tasks.py    # Export functionality
│   └── helpers.py         # Helper functions
├── reports/                # Generated reports and exports
└── uploads/                # User-uploaded files
```

### Frontend Structure

```
frontend/
├── index.html              # Main HTML entry point
├── components/             # Reusable UI components
├── pages/                  # Page templates
├── static/                 # Static assets (images, CSS)
└── utils/                  # Utility JavaScript functions
```

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Celery](https://docs.celeryproject.org/) - Distributed task queue
- [Redis](https://redis.io/) - In-memory data structure store
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
