# Church Management System (ChMS)

A web-based application built with **Python** and **Django** to help churches efficiently manage **members**, **attendance**, **events**, **contributions**, and **communications**. The system features **admin dashboards**, **role-based access control**, and **data reporting tools** to streamline operations and enhance engagement.


## 🌐 Live Demo
[Repository Link](https://github.com/kiptoo-097/ChMS.git)

---

## ✨ Features

- 🧍 Member Registration & Management
- 📅 Event Scheduling & Tracking
- 📊 Attendance Monitoring
- 💸 Contribution Tracking (Tithes, Offerings, Donations)
- 📬 Communication Tools (Announcements, Emails)
- 🔐 Role-Based Access (Admin, Pastor, Member, etc.)
- 📈 Data Reporting & Analytics
- 🖼️ Media & Gallery Uploads
- 🔔 Notification System
- 🌙 Dark Mode Toggle (optional enhancement)
- 📱 Responsive UI for Mobile & Desktop

---

## 🚀 Technologies Used

- **Backend**: Python, Django
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap, optional JS libraries)
- **Database**: SQLite (default), PostgreSQL/MySQL (for production)
- **Others**: Django Admin, Crispy Forms, Django Messages

---



| Dashboard | Event Management | Member Profile |
|----------|------------------|----------------|
| ![Dashboard](screenshots/dashboard.png) | ![Events](screenshots/events.png) | ![Member](screenshots/member.png) |

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kiptoo-097/ChMS.git
cd ChMS
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
Visit: http://127.0.0.1:8000/ in your browser.

🧊 Future Improvements
SMS & WhatsApp integration

Event check-in QR codes

Financial reporting charts

Multi-church/branch support

RESTful API for mobile apps

