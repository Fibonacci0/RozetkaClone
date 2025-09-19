

python -m venv .venv

./.venv/Scripts/activate.ps1

pip install Pillow dj-database-url psycopg2-binary


python manage.py runmigrations

python manage.py migrate

python manage runserver