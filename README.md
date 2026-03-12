# CampConnect

CampConnect is a Django-based campus management system for four user roles:

- `HOD`
- `Staff`
- `Student`
- `Parent`

It manages user administration, attendance, results, leave workflows, feedback, and notifications in a single role-based application.

## Current Scope

CampConnect currently supports:

- HOD creation and management of staff, students, parents, courses, subjects, and sections
- single and bulk XLSX import for staff, students, parents, and semester results
- staff attendance marking and attendance updates
- student attendance viewing
- HOD semester result publishing
- staff unit and mid-term result submission
- parent linkage to students through `roll_number`
- notifications for staff, students, and parents
- dashboard summaries for each user type
- staff and student leave applications
- staff leave requests with substitute teacher selection
- HOD approval or rejection of staff and student leave requests
- student suspension by HOD

## Role Summary

### HOD

- manage staff, students, parents, courses, subjects, and sections
- create users individually or from XLSX
- suspend or reactivate students
- review attendance
- approve or reject leave requests
- send notifications to staff, students, and parents
- publish semester results manually in bulk or from XLSX

### Staff

- mark and update attendance
- submit unit and mid-term results
- send notifications to students
- apply for leave with a substitute teacher
- view notifications and leave history

### Student

- view attendance
- view unit/mid results
- view semester results grouped by semester name
- apply for leave
- submit feedback
- view notifications

### Parent

- view linked student summary
- receive attendance, result, and notification updates
- view notifications
- submit feedback

## Academic Structure

CampConnect uses this model:

- `Course`: degree course such as `CSE`, `EEE`, `ECE`
- `Subject`: subject under a course such as `AI`, `ML`, `DBMS`
- `Section`: class grouping such as `A`, `B`, `21CSE-A`

In code, the section model is still named `Session`, but the UI uses `Section`.

## Tech Stack

- Python
- Django
- SQLite by default
- HTML templates
- Bootstrap/AdminLTE-based assets
- jQuery
- Chart.js
- OpenPyXL for XLSX import/export samples
- WhiteNoise for static file serving

## Project Structure

```text
Campconnect/
|-- college_management_system/   Django settings, root URLs, WSGI/ASGI
|-- main_app/                    Models, views, forms, templates, migrations
|-- media/                       Uploaded media and sample XLSX files
|   `-- samples/                 Bulk import sample files
|-- db.sqlite3                   Default SQLite database
|-- manage.py                    Django management entry point
|-- requirements.txt             Python dependencies
|-- README.md
`-- PROJECT_DEEP_ANALYSIS.txt
```

## Main URLs

- `/` login page
- `/admin/home/` HOD dashboard
- `/staff/home/` staff dashboard
- `/student/home/` student dashboard
- `/parent/home/` parent dashboard

## Bulk Upload Formats

Sample files are stored in [`media/samples`](./media/samples).

### Staff

File: `staff_sample.xlsx`

Columns:

```text
first_name, last_name, address, email, gender, password, course_name
```

### Students

File: `students_sample.xlsx`

Columns:

```text
first_name, last_name, address, email, gender, password, roll_number, course_name, section_id(optional or section name)
```

### Parents

File: `parents_sample.xlsx`

Columns:

```text
first_name, last_name, address, email, gender, password, student_roll_number
```

Note: import students first, then parents using matching `student_roll_number`.

### Semester Results

File: `semester_results_sample.xlsx`

Columns:

```text
roll_number, subject_name, section_name, semester_name, internal_score, external_score
```

## Results Model

CampConnect currently supports three result types:

- `Unit Test`
- `Mid Term`
- `Semester Result`

Behavior:

- staff submit `Unit Test` and `Mid Term` results
- HOD publishes `Semester Result`
- semester results are shown on a separate student page and grouped by semester name

## Notifications

Notifications exist for:

- staff
- students
- parents

Dashboard behavior:

- recent notifications appear on the dashboard
- `Clear` removes them from the dashboard card only
- `View All` still keeps the full notification history

## Setup

### 1. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Create a superuser

```bash
python manage.py createsuperuser
```

### 5. Run the server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Important Notes

- This project uses a custom user model: `main_app.CustomUser`
- login uses email instead of username
- `db.sqlite3` is the default database
- sample XLSX files are included for the current import contract
- some features are implemented through `csrf_exempt` AJAX endpoints and should be hardened before production
- settings are currently development-oriented and not production-safe as-is

## Recent Functional Additions

- parent role integrated into login and dashboard flow
- parent-to-student link via student `roll_number`
- student suspension support
- semester result publishing and XLSX import
- grouped semester result display
- dashboard notification clear without deleting notification history
- staff leave request with substitute teacher
- bulk delete actions for manage pages

## Testing

There is only a small smoke-test set at the moment.

Run tests with:

```bash
python manage.py test
```

