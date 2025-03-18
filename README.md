# GameRent
GameRent is an e-commerce video game platform that allows users to flexibly purchase or rent digital titles. It offers rental services by the hour or day, allowing players to enjoy their favorite titles without having to purchase them outright.


## Features
- User authentication (registration and login)
- Game catalog with rental and purchase options
- Shopping cart functionality
- Shared game rentals with multiple users
- Payment system for shared rentals
- User library to manage purchased and rented games
- Admin panel for managing games
- Responsive design using Tailwind CSS

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.11+
- Node.js and npm
- A virtual environment (optional but recommended)

### Clone the Repository
```sh
git clone https://github.com/Sebastian-jimenez30/GameRent.git
cd GameShare
```

### Set Up Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Set Up the Database
```sh
python manage.py makemigrations
python manage.py migrate
```

### Create a Superuser (Admin Account)
```sh
python manage.py createsuperuser
```
Follow the prompts to set up an admin account.

## Setting Up Tailwind CSS
### Install Tailwind Dependencies
```sh
python manage.py tailwind install
```

### Build Tailwind CSS
```sh
python manage.py tailwind build
```

To enable automatic updates while developing:
```sh
python manage.py tailwind start
```

## Running the Project
```sh
python manage.py runserver
```
Access the project in your browser at:
```
http://127.0.0.1:8000/
```

## Directory Structure
```
GameShare/
│   manage.py
│   requirements.txt
│   README.md
├───apps
│   ├───games
│   ├───transactions
│   ├───users
├───theme
│   ├───static
│   ├───templates
├───static
├───templates
└───gameshare (Django core settings)
```

## Usage
### Access the Admin Panel
```
http://127.0.0.1:8000/admin/
```
Log in using the superuser credentials created earlier.

### Game Catalog
- Browse the available games
- Rent or purchase games
- Add games to the shopping cart

### Shared Rentals
- Select "Shared Rental" for a game
- Invite users to share the rental
- Each user must complete their payment for the game to be available

### User Library
- View purchased and rented games
- Download available games




