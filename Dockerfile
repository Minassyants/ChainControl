FROM python:3.7

WORKDIR ./Autodom-app

COPY ./Autodom/Autodom ./Autodom/Autodom

COPY ./Autodom/ChainControl ./Autodom/ChainControl

COPY ./Autodom/pwa_webpush ./Autodom/pwa_webpush

COPY ./Autodom/manage.py ./Autodom/manage.py

COPY ./Autodom/requirements.txt ./Autodom/requirements.txt

COPY ./Autodom/serviceworker.js ./Autodom/serviceworker.js

RUN pip install -r Autodom/requirements.txt

WORKDIR Autodom

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "-b 0.0.0.0:8000","Autodom.wsgi"]

