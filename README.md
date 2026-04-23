# 📚 Library Management System

### 🚀 Advanced Full-Stack Python Project (Tkinter + MySQL)

---

## 🌟 Overview

A **production-style Library Management System** built with **Python (Tkinter GUI) and MySQL**, designed to handle real-world library operations with **secure authentication, role-based access, analytics dashboards, and messaging system**.

This project demonstrates **full-stack desktop application development**, including **UI, backend logic, database design, and security implementation**.

---

## 🎯 Key Highlights

* 🔐 Secure Authentication using **bcrypt hashing**
* 👥 Role-Based Access Control (**Super Admin / Admin / User**)
* 📚 Complete Book Management System
* 🔄 Issue & Return System with **Auto Fine Calculation**
* 📊 Interactive Dashboard using **Matplotlib**
* 💬 Real-time Messaging System (User ↔ Admin)
* 📤 Excel Export Feature
* 🧠 Clean Modular Architecture

---

## 🖼️ Application Preview

### 🔑 Login Interface

![Login](https://github.com/Ajeet2611/Multi-Role-Library-Management-System/blob/main/login%20window.png)

### 📊 Admin Dashboard

![Dashboard](https://github.com/Ajeet2611/Multi-Role-Library-Management-System/blob/main/Admin%20Dashboard.png)

---

## 🏗️ System Architecture

```text
User (GUI - Tkinter)
        ↓
Application Logic (Python Modules)
        ↓
Database Layer (MySQL)
        ↓
Data Storage (Tables & Relations)
```

---

## 🧠 Core Modules

### 🔐 Authentication Module (`auth.py`)

* Login validation (Users + Members)
* Password hashing (bcrypt)
* Role detection & routing

---

### 👨‍💼 Admin Module

* Book management (Add / Edit / Delete)
* Issue & Return system
* User management
* Excel export
* Messaging handling

---

### 👤 User Module

* View available books
* Check issued books & fines
* Send messages to admin
* Change password

---

### 💬 Messaging Module (`messaging.py`)

* User → Admin communication
* Admin → User reply system
* Message lifecycle tracking

---

### 📊 Dashboard Module (`dashboard_charts.py`)

* Pie chart (Active vs Inactive Users)
* Bar chart (Role distribution)

---

## 🗄️ Database Design

### 📌 Main Tables

* **Users** → Authentication & roles
* **Books** → Library inventory
* **Members** → User details
* **Transactions** → Issue/Return records
* **Messages** → Communication system
* **Institutions** → Multi-organization support

---

## ⚙️ Installation Guide

### 📌 Prerequisites

* Python 3.10+
* MySQL Server
* pip

---

### 🔧 Setup Steps

```bash
git clone https://github.com/Ajeet2611/Multi-Role-Library-Management-System.git
cd LibraryProject
```

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

```bash
pip install mysql-connector-python bcrypt pillow openpyxl matplotlib
```

---

### 🗄️ Database Setup

Update credentials in:

```bash
db.py
```

Then ensure database `library_db` and required tables exist.

---

## ▶️ Run Application

```bash
python gui_login.py
```

---

## 🔐 Security Features

* Password hashing using bcrypt
* Role-based access control
* Secure login validation
* Input validation mechanisms

---

## 📊 Features Breakdown

| Feature            | Description                          |
| ------------------ | ------------------------------------ |
| 🔐 Login System    | Secure login with role-based routing |
| 📚 Book Management | Add, edit, delete, track books       |
| 🔄 Issue/Return    | Fine calculation (₹5/day)            |
| 📊 Dashboard       | Data visualization with charts       |
| 💬 Messaging       | User-admin communication             |
| 📤 Export          | Excel export using openpyxl          |

---

## 📁 Project Structure

```text
LibraryProject/
├── assets/
├── admin_*.py
├── gui_*.py
├── db.py
├── auth.py
├── messaging.py
├── security.py
├── dashboard_charts.py
├── main.py
└── README.md
```

---

## 🚀 Future Roadmap

* 🌐 Web Version (Django / Flask)
* 📱 Mobile App (Flutter)
* ☁️ Cloud Database (Firebase / AWS)
* 🔔 Notification System (Email/SMS)
* 🔍 Advanced Search & Filters
* 📊 AI-based Book Recommendation

---

## 🎥 Demo (Optional)

👉  demo video link here
(YouTube / Drive)

---

## 🏆 Resume Value

This project showcases:

* Full-stack development skills
* GUI + Backend integration
* Database design & queries
* Security implementation
* Real-world problem solving

---

## 👨‍💻 Author

**Ajeet Prasad**
📧 [ajeetkumarbarh52@gmail.com](mailto:ajeetkumarbarh52@gmail.com)
🔗 www.linkedin.com/in/ajeet-prasad-dev

---

## 🤝 Contribution

Contributions are welcome!
Fork the repo and submit a pull request.

---

## ⭐ Support

If you found this useful:

* ⭐ Star the repo
* 🍴 Fork it
* 🔥 Share with others

---

## 📌 Final Note

This project is not just a college assignment —
it is a **complete real-world system design implementation** demonstrating practical development skills.

---
