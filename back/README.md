# Real-Time ECG MI Predictor Backend

This directory contains the backend service for the Real-Time ECG MI Predictor project. The backend is built with Flask and MongoDB, providing RESTful APIs for user, device, report, alert management, ECG data processing, and real-time features.

---

## Tech Stack

- **Framework:** Flask (Python)
- **Database:** MongoDB (via `pymongo`)
- **Other:** Flask-CORS, JWT for authentication, Docker support

---

## Project Structure

```
/web/back/
│
├── app.py                # Main Flask application entry point
├── Dockerfile            # Docker container configuration
├── requirements.txt      # Python dependencies
├── utils.py              # ECG signal processing utilities
│
├── auth/                 # Authentication logic (JWT, decorators, routes)
├── controllers/          # Business logic for each resource
├── db/                   # Database connection and helpers
├── models/               # Data access layer (CRUD for each resource)
├── routes/               # API route definitions (Flask blueprints)
├── test/, tests/         # Test cases and data
└── ...
```

---

## Role-Based Access Control

The backend enforces strict role-based access control:

- **Admins** can create, update, and delete doctors. Only admins can list all doctors and all admins.
- **Doctors** can create, update, and delete their own patients. Only doctors can list their own patients (`/api/users/patients`).
- **Patients** cannot manage other users.
- All user management endpoints are protected by JWT authentication and role checks.

Attempting to perform an action outside your role will result in a 403 Forbidden error.

### 1. Application Entry Point

- **`app.py`**: Initializes Flask app, sets up CORS, and registers blueprints for modular routing. Exposes API endpoints for ECG data, prediction, and user/device/report/alert management.

### 2. Blueprints & Routing

- Modularized routes under `/routes` and `/auth/routes` for:
  - Users (`users_bp`)
  - Devices (`devices_bp`)
  - Reports (`reports_bp`)
  - Alerts (`alerts_bp`)
  - Real-time data (`realtime_bp`)
  - MongoDB stream (`mongo_stream_bp`)
  - Authentication (`auth_bp`)

### 3. Database Layer

- **`/db/mongodb.py`**: Handles MongoDB connection using environment variables. Ensures connection is established and database is usable.

### 4. Models

- **`/models/user_model.py`**: CRUD operations for users (admin, doctor, patient). Other models for devices, reports, and alerts exist.

### 5. Controllers

- **`/controllers/user_controller.py`**: Business logic for user operations, wraps model functions. Similar controllers for devices, reports, and alerts.

### 6. Utilities

- **`utils.py`**: Functions for ECG signal processing (RR intervals, heart rate, HRV).

### 7. API Endpoints (Example: Users)

- `POST /api/users` — Only admins can create doctors, only doctors can create patients.
- `GET /api/users/<user_id>` — Admins can view any user, doctors can only view their own patients.
- `PUT /api/users/<user_id>` — Only admins can update doctors, only doctors can update their own patients.
- `DELETE /api/users/<user_id>` — Only admins can delete doctors, only doctors can delete their own patients.
- `GET /api/users/doctors` — Only admins can list all doctors.
- `GET /api/users/admins` — Only admins can list all admins.
- `GET /api/users/patients` — Only doctors can list their own patients.
- Passwords are always hashed before storage.

### 8. Docker Support

- **`Dockerfile`**: For containerizing the backend service. Exposes port 5000.

### 9. Requirements

- **`requirements.txt`**: Lists all Python dependencies (Flask, pymongo, numpy, etc.).

### 10. Testing

- **`/tests`** and **`/test`**: Contain test scripts for API and utility functions.

---

## Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up environment variables:**
   - Create a `.env` file with MongoDB URI and database name.
3. **Run the server:**
   ```bash
   python app.py
   ```
4. **Docker:**
   - Build and run the container:
     ```bash
     docker build -t ecg-backend .
     docker run -p 5000:5000 ecg-backend
     ```

---

## Notes

- The backend is modular and follows best practices for Flask projects.
- MongoDB is used for persistent storage, with a clear separation between models, controllers, and routes.
- The project is ready for containerized deployment.
- There is a focus on ECG data processing and real-time features.

---

## Authors

- Saifeddine Rejeb

---

## License

---

## Weak Points & To-Do List

**1. Testing & Coverage**

- [ ] Add more unit and integration tests, especially for edge cases and error handling.
- [ ] Ensure all endpoints and business logic are covered by tests.
- [ ] Add automated test running (e.g., GitHub Actions, pytest).

**2. Error Handling & Validation**

- [ ] Improve error handling in all routes and controllers (return consistent error messages).
- [ ] Add input validation for all API endpoints (e.g., using Marshmallow or pydantic).
- [ ] Handle database connection failures gracefully.

**3. Security**

- [ ] Review and harden authentication (JWT expiration, refresh, blacklist, etc.).
- [ ] Sanitize all user inputs to prevent injection attacks.
- [ ] Ensure sensitive data (like passwords) is never returned in API responses.
- [ ] Add rate limiting and CORS restrictions for production.

**4. Code Quality & Organization**

- [ ] Remove commented-out and test code from production files (e.g., in `db/mongodb.py`).
- [ ] Add docstrings and comments for all public functions and classes.
- [ ] Refactor repeated code in routes/controllers (DRY principle).

**5. Documentation**

- [ ] Add API documentation (Swagger/OpenAPI or Postman collection).
- [ ] Document environment variables and configuration options.

**6. Features & Extensibility**

- [ ] Implement missing CRUD operations for all models (if any).
- [ ] Add pagination and filtering for list endpoints.
- [ ] Add logging (with log levels) for debugging and monitoring.

**7. Deployment & DevOps**

- [ ] Add production-ready settings (e.g., gunicorn for Flask, environment-based config).
- [ ] Add health check endpoint.
- [ ] Add Docker Compose for local development with MongoDB.

---

This project is licensed. See the main repository for details.
