

python -m venv .venv

./.venv/Scripts/activate.ps1

pip install Pillow
pip install django-environ

python manage.py runmigrations

python manage.py migrate

python manage runserver
