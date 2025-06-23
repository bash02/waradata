Django Utility Payment Gateway
This Django application powers a digital platform for making utility purchases (like airtime, data, and bill payments) and integrates with a secure payment gateway.

Prerequisites
Python (version 3.9 or higher recommended)

Pipenv (Python environment & dependency manager)

MySQL (or any configured database)

Getting Started
Ensure your Python version matches the one used in the project (update it locally if needed).

1. Clone the repository

git clone https://github.com/bash02/waradata.git
cd your-project

2. Set up virtual environment

pipenv install       
pipenv shell          

3. Configure environment variables
Create a .env file in the root directory:


DJANGO_SECRET_KEY=your-secret-key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password

4. Run database migrations

python manage.py migrate

5. Start the development server

python manage.py runserver
