release: python manage.py migrate --noinput
web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn volugreen.wsgi:application --bind 0.0.0.0:$PORT
