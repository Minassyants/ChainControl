FROM python:3.7

WORKDIR ./Autodom-app

COPY ./Autodom ./Autodom

RUN pip install -r Autodom/requirements.txt

WORKDIR Autodom

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "-b 0.0.0.0:8000","Autodom.wsgi"]

