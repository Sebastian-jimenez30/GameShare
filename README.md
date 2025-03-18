# GameRent
GameRent is an e-commerce video game platform that allows users to flexibly purchase or rent digital titles. It offers rental services by the hour or day, allowing players to enjoy their favorite titles without having to purchase them outright.


# GameRent 🎮

## 📌 Project Overview
GameRent is a Django-based web application that allows users to rent, purchase, and share video games. It includes user authentication, a game catalog, a shopping cart, and a library for managing purchased and rented games.

---

## 🚀 Installation & Setup
Follow these steps to set up and run the project locally.

### 1️⃣ Clone the Repository
```sh
git clone <REPO_URL>
cd GameRent
```

### 2️⃣ Create and Activate a Virtual Environment
It is recommended to use a virtual environment to avoid dependency conflicts.

#### 🔹 Windows
```sh
python -m venv venv
venv\Scripts\activate
```

#### 🔹 Mac/Linux
```sh
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
Run the following command to install all required Python packages:
```sh
pip install -r requirements.txt
```

### 4️⃣ Apply Database Migrations
```sh
python manage.py migrate
```

### 5️⃣ Install and Build Tailwind CSS
To apply the Tailwind CSS styles correctly, install the necessary dependencies:
```sh
python manage.py tailwind install
python manage.py tailwind build
```

### 6️⃣ Run the Development Server
```sh
python manage.py runserver
```
After running this command, visit **http://127.0.0.1:8000/** in your browser.

---

## 📌 Features
✅ **User Authentication:** Register, login, and manage user accounts.
✅ **Game Catalog:** Browse available games with rental, purchase, and shared rental options.
✅ **Shopping Cart:** Add games to the cart and complete the checkout process.
✅ **Game Library:** Manage purchased and rented games.
✅ **Shared Rentals:** Users can share game rentals and make payments.
✅ **Admin Panel:** Superusers can manage games, users, and transactions.

---

## 🎮 How to Use
### **User Registration & Login**
1. Register a new account at `/register/`.
2. Log in at `/login/`.

### **Managing Games**
- Browse the catalog at `/catalog/`.
- Click on a game to view details and choose between **renting**, **purchasing**, or **shared rental**.
- View your shopping cart at `/cart/` and proceed to checkout.
- Access your library of purchased and rented games at `/library/`.

---

## 👨‍💻 Admin Access
To create a superuser for the Django Admin Panel:
```sh
python manage.py createsuperuser
```
Follow the prompts to set up an admin account.

Log in at `/admin/` to manage games, users, and transactions.

---

## 🛠 Troubleshooting
If you encounter issues:
- Ensure the virtual environment is activated.
- Check that dependencies are installed (`pip install -r requirements.txt`).
- Make sure Tailwind is installed and built (`python manage.py tailwind install && python manage.py tailwind build`).
- If static files are not loading, run:
  ```sh
  python manage.py collectstatic
  ```
- Restart the server if needed (`python manage.py runserver`).

---

## 📄 License
This project is open-source under the MIT License.

---

## 📩 Contact
For any inquiries or contributions, feel free to reach out via email or submit a pull request!

Happy coding! 🎮🚀


