

python -m venv .venv

./.venv/Scripts/activate.ps1

pip install django Pillow dj-database-url psycopg2-binary django-environ requests azure-storage-blob 

python3 manage.py runmigrations

python3 manage.py migrate

python3 manage.py runserver
