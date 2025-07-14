# SmartLot 🚗

SmartLot is a smart parking management web application built with **Flask** and **SQLite**.  
It helps admins manage parking lots, spots, reservations and provides a user-friendly portal for booking and releasing parking spots.

---

## 📁 Project Structure
SmartLot/
├── application
│ ├── config.py
│ ├── controllers.py
│ ├── database.py
│ ├── models.py
│ └── pycache
├── app.py
├── instance
│ └── db.sqlite3
├── pycache
│ ├── app.cpython-310.pyc
│ └── app.cpython-312.pyc
├── requirements.txt
├── static
│ ├── booking_bg.jpeg
│ ├── edit.jpeg
│ ├── editt.jpeg
│ ├── lot_revenue_chart.png
│ ├── parking-bg.jpeg
│ ├── parking_car_image.jpeg
│ ├── register.jpeg
│ ├── registerr.jpeg
│ ├── release.jpeg
│ ├── spot_status_chart.png
│ └── user_summary_pie.png
├── templates
│ ├── admin_add_lot.html
│ ├── admin_dashboard.html
│ ├── admin_delete_lot.html
│ ├── admin_edit_lot.html
│ ├── admin_profile_update.html
│ ├── admin_search_results.html
│ ├── admin_summary.html
│ ├── admin_users.html
│ ├── admin_view_profile.html
│ ├── admin_view_spots_details.html
│ ├── admin_view_spots.html
│ ├── admin_view_user_summary.html
│ ├── booking_dashboard.html
│ ├── footer.html
│ ├── header.html
│ ├── index.html
│ ├── layout.html
│ ├── login.html
│ ├── profile_update.html
│ ├── register.html
│ ├── release_dashboard.html
│ ├── search_results.html
│ ├── user_dashboard.html
│ ├── user_lot_dashboard.html
│ ├── user_summary.html
│ └── view_profile.html


---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite3
- **Frontend:** HTML, CSS, Jinja2 Templates
- **Charting:** Matplotlib (for generating charts)
- **Other:** Bootstrap (for responsive styling)

---

## ⚙️ Setup & Run

Follow these steps to run SmartLot locally:

1️⃣ **Create a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2️⃣ **Install dependencies**
```bash
pip install -r requirements.txt

3️⃣ **Freeze dependencies (optional)**
```bash
pip freeze > requirements.txt

4️⃣ **Run the app**
```bash
python3 app.py

👤 **Create Admin & User Accounts (Initial Setup)**
To create an admin and a sample user, open your Python shell:
```bash
python3

Then run:
from app import *
user1 = User(username="Admin123", email="admin@user.com", password="1234", address="XXXX", pincode=XXXX, phone_number=1234567890, type="admin")
db.session.add(user1)
db.session.commit()


✅ Done!
Now you can log in as the admin or a user, add parking lots, manage spots, and test all functionalities.

Feel free to customize this README with screenshots, deployment notes, or contributors!

**Happy Parking! 🚗✨**
