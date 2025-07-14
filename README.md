
---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite3
- **Frontend:** HTML, CSS, Jinja2 Templates
- **Charting:** Matplotlib (for generating charts)
- **Other:** Bootstrap (for responsive styling)

---

## ⚙️ Setup & Run

Follow these steps to run **SmartLot** locally:

```bash
# 1️⃣ Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ (Optional) Freeze dependencies
pip freeze > requirements.txt

# 4️⃣ Run the app
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
