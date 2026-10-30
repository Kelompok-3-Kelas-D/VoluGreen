release: python manage.py migrate --noinput && python manage.py create_superuser_auto
web: python manage.py collectstatic --noinput --clear && python manage.py migrate --noinput && python manage.py create_superuser_auto && gunicorn volugreen.wsgi:application --bind 0.0.0.0:$PORT
