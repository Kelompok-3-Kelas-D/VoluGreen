release: python manage.py migrate --noinput && python manage.py seed_initial_activities
web: python manage.py collectstatic --noinput --clear && python manage.py migrate --noinput && python manage.py seed_initial_activities && gunicorn volugreen.wsgi:application --bind 0.0.0.0:$PORT
