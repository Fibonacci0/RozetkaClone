
python -m venv .venv

./.venv/Scripts/activate

pip install django
pip install pillow

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
