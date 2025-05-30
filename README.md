# CampConnect 🎓

  **CampConnect** is a full-fledged **College Management System** developed using Django. It’s designed to digitalize and centralize all key administrative and academic processes of an educational institution — offering distinct portals for HODs, Staff, Students, and Parents. This platform ensures transparency, improves academic efficiency, and enhances communication between all stakeholders.


### 🎯 Key Objectives

- 🏫 **Digitize college operations** like attendance, announcements, material sharing, and performance reporting.
- 👥 **Provide role-based interfaces** for different users (HOD, Staff, Student, Parent).
- 📊 **Ensure real-time tracking and visibility** of academic progress and student activities.
- 🔗 **Enhance connectivity** between college departments, faculty, students, and parents.

---

## 🧰 What Does It Manage?

CampConnect covers a wide range of college-level activities:

### 🧑‍🏫 Academic Management
- Course approvals by HOD
- Uploading and categorizing study materials
- Assignment distribution and submissions
- Performance monitoring

### 📅 Attendance Management
- Staff can mark daily attendance
- Students can view their attendance history
- Parents receive attendance alerts and summaries

### 🧾 Result & Progress Tracking
- Students can track academic performance
- Parents get simplified result summaries
- HOD and staff can analyze student trends

### 📢 Communication & Announcements
- Global and course-specific announcements
- Notice board for circulars and updates
- Parent-teacher communication channel

### 🧑‍💼 Staff & Department Management
- HOD can add/manage staff profiles
- Course allocations to staff
- Department-wise access and control

---

## 👥 Role-Based Access

| Role       | Capabilities                                                       |
|------------|--------------------------------------------------------------------|
| **HOD**    | Manage departments, approve staff uploads, monitor academics       |
| **Staff**  | Upload materials, post announcements, mark attendance              |
| **Student**| Access notes, view attendance, submit assignments                  |
| **Parent** | Monitor student progress, receive updates                          |

---

## 🛠️ Technologies Used

- **Backend**: Django 4.2 (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite (can scale to PostgreSQL)
- **Authentication**: Django’s User & Group system
- **AI Integration** *(optional/experimental)*: Google GenAI (for smart material suggestions, automated feedback, etc.)

---


## 📌 Project Structure

```
campconnect/
│
├── college_management_system/ # Project configuration and settings
├── main_app/ # Core app logic (views, models, templates)
├── media/ # Uploaded files and media content
├── db.sqlite3 # Default SQLite database
├── manage.py # Django CLI management tool
└── requirements.txt # Python dependencies

```

---



## 🚀 How to Run This Project

### 1. **Export / Fork the Repository**

You can either download the code as ZIP or fork it to your GitHub:

- To download:
  - Click the green **Code** button → **Download ZIP**
- To fork:
  - Click the **Fork** button at the top-right of the repository

---

### 2. **Clone the Repository**

  - git clone https://github.com/YourUsername/CampConnect.git
  - cd CampConnect

---

### 3. Create and Activate Virtual Environment (Optional but Recommended)

  - python -m venv venv
  - source venv/bin/activate      # Linux/macOS
  - venv\Scripts\activate         # Windows

---

### 4. Install Requirements

  - pip install -r requirements.txt

---

### 5. Run Migrations
  - python manage.py makemigrations
  - python manage.py migrate

---

### 6. Create Superuser (for HOD/Admin Access)

  - python manage.py createsuperuser

---

### 7. Run the Development Server

  - python manage.py runserver
  - Visit http://127.0.0.1:8000/ in your browser to use the system.

---



## 📸 UI Preview

  - Only a sample screenshot is shown below. There are more views available in the system.
Run the project locally to explore the full interface and features.


  ### Login Page
  ![image](https://github.com/user-attachments/assets/e993ce65-fb25-4431-bb81-660fce542c8c)
  
  ### HOD Dashboard
  ![image](https://github.com/user-attachments/assets/9b7e69d8-13a4-4e88-8675-66bf5d079a76)
  
  ### HOD Update Profile
  
  ![image](https://github.com/user-attachments/assets/077c1e84-45b2-48ac-b1e7-1d40088e4bb9)
  
  ### HOD Update Profile
  
  ![image](https://github.com/user-attachments/assets/0b9ea492-c8fb-4f42-988b-9a0dd58b08e1)
  
  ### Add Course
  
  ![image](https://github.com/user-attachments/assets/018e84a9-cc68-4640-a12c-733b8e4eff9e)
  
  ### Staff Creation  
  
  ![image](https://github.com/user-attachments/assets/0741ded4-0d6e-4b2a-b3a9-0e336d587667)
  
  ### Add Subject
  
  ![image](https://github.com/user-attachments/assets/871e6c03-059a-4b2c-9284-a01efdee49cf)
  
  ### Student Creation
  
  ![image](https://github.com/user-attachments/assets/b567cc78-f9aa-4831-acce-bf7d9b619b9e)
  
  ### Send Notifications (Staff)
  
  ![image](https://github.com/user-attachments/assets/c29baee0-967b-4ba2-9443-413492f0d93b)
  
  ### Send Notifications (Student)
  
  ![image](https://github.com/user-attachments/assets/8036e0f4-65fd-45f5-b6c5-d0a262457927)

  ### Staff Dashboard
  
  ![image](https://github.com/user-attachments/assets/336c1407-22b3-4c13-82eb-4af6bac371fe)


---


## 🔭 Future Scope

  ✅ Notification System (Email/SMS)
  
  ✅ Push Notifications using WebSockets
  
  ✅ Google GenAI for auto-suggestion of materials
  
  ✅ Assignment Plagiarism Checker
  
  ✅ Graph-based performance dashboards for students
  
  ✅ Mobile App Integration using React Native or Flutter
  
  ✅ Multilingual Support

