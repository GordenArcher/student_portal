
---

# Contribution Guidelines

## Overview

Thank you for your interest in contributing to the **New Start Academy Student Portal**.
This project was developed as part of a semester course project to demonstrate full-stack web development with **Django** and **Django Templates**.

All contributions, whether large or small, are welcome — from improving documentation to refining models, templates, and business logic.

---

## Project Description

The **Student Portal** is designed for **New Start Academy** to manage academic activities digitally.
It allows:

* Admins to manage teachers, classes, and courses.
* Teachers to add students and upload their exam results.
* Students to view results for each semester or academic year.

---

## How to Contribute

### 1. Fork the Repository

Create your own copy of the repository:

```bash
git clone https://github.com/GordenArcher/student_portal.git
```

Then, navigate into the project folder:

```bash
cd student_portal
```

---

### 2. Create a New Branch

Always create a new branch for your work to keep `main` clean:

```bash
git checkout -b feature/your-feature-name
```

For example:

```bash
git checkout -b feature/add-result-export
```

---

### 3. Make Your Changes

Edit, refactor, or add features according to Django best practices.

Example contribution areas:

* Enhancing templates (HTML/CSS)
* Adding model relationships
* Improving validation or result calculation logic
* Writing or updating documentation
* Fixing bugs or UI issues

---

### 4. Test Your Changes

Before committing, ensure the app runs smoothly:

```bash
python manage.py runserver
```

Check the console for errors and verify that templates and data load correctly.

---

### 5. Commit and Push

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Added student promotion feature"
git push origin feature/add-result-export
```

---

### 6. Submit a Pull Request (PR)

Go to the main repository and submit a **Pull Request** from your branch to `main`.
Provide a brief description of:

* What changes you made
* Why they’re needed
* Any related issues they solve

---

## Code Standards

* Follow **PEP 8** for Python code style.
* Use **clear variable and function names**.
* Keep templates clean and readable.
* Comment sections of complex logic or queries.
* Avoid adding unnecessary dependencies.

---

## Contribution Example

Here’s an example of how contributions should be documented in your PR description:

```
### Summary
Added feature to calculate average student scores and assign grades automatically.

### Changes
- Updated Result model to include `total_score` and `grade`.
- Modified result upload view to auto-compute grades.
- Improved result template with total/grade display.

### Testing
- Created dummy student data.
- Verified grade calculation logic across multiple courses.
```

---

## Development Setup

Refer to the main [README.md](./README.md) for setup, installation, and usage instructions.

---

## Contributors

| Name                        | Role           | Institution          |
| --------------------------- | -------------- | -------------------- |
| **Gorden Archer**           | Lead Developer | Pentecost University |
| Open to Future Contributors | —              | —                    |

---

## License

This project is developed as an academic course project for **New Start Academy**.
All rights reserved © 2025.

---