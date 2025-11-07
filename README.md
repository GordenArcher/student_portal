
---

# New Start Academy – Student Portal

## Overview

The **New Start Academy Student Portal** is a Django-based web application designed to simplify and automate student result management for schools. It allows administrators and teachers to manage students, courses, and classes efficiently and securely.

Teachers can upload student exam scores for each course, and the system automatically computes totals and grades. The portal is built using **Django and Django Templates**, with a focus on simplicity, usability, and maintainability.

---

## Features

### Administrator

* Create and manage teacher accounts
* Assign classes and courses to teachers
* Oversee all academic data
* View and manage all results

### Teachers

* Log in with admin-provided credentials
* Access assigned classes and courses
* Add and manage students in their classes
* Upload and update student exam scores (3 scores per course)
* Automatically generate total scores and grades

### Students

* Each student has a unique ID generated upon registration
* Students can view their results for each semester/year
* Results include detailed breakdowns of individual and total scores

---

## Technology Stack

* **Backend:** Django (Python)
* **Frontend:** Django Templates, HTML, CSS, Bootstrap
* **Database:** SQLite (default) — can be switched to PostgreSQL or MySQL
* **Authentication:** Django’s built-in auth system with role-based access
* **Environment:** Python virtual environment (venv)

---

## Project Structure

```
student_portal/
│
├── student_portal/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/        # Authentication and role management (admin, teacher)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── templates/accounts/
│   └── admin.py
│
├── academics/       # Classes, courses, and student management
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/academics/
│   └── admin.py
│
├── results/         # Student results, grades, and reports
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/results/
│   └── admin.py
│
├── core/            # Dashboard, homepage, and shared pages
│   ├── views.py
│   ├── urls.py
│   ├── templates/core/
│   └── admin.py
│
├── templates/       # Shared templates (e.g., base.html, layout.html)
│
├── static/          # Static assets (CSS, JS, images)
│
└── manage.py
```

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/GordenArcher/student_portal.git
cd student_portal
```

### 2. Set Up Virtual Environment

```bash
python -m venv env
source env/bin/activate     # For macOS/Linux
env\Scripts\activate        # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Access the portal at:
**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## Application Flow

1. **Admin Login:**
   Admin logs in to the dashboard and creates teacher accounts, classes, and courses.

2. **Teacher Login:**
   Teachers log in with credentials provided by the admin and can:

   * Add students to their assigned classes.
   * Upload exam scores for each student (three per course).
   * View and manage results.

3. **Student Result View:**
   Students can view their results using their unique student ID or login details.

---

## Future Enhancements

* PDF result download functionality
* Bulk result upload via Excel file
* Result statistics and analytics for teachers
* Notification system for result updates
* Student and parent logins for direct result access

---

## License

This project is developed as part of a semester course project for **New Start Academy**.
All rights reserved © 2025.

---