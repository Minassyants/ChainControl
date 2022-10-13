FROM python:3.7

WORKDIR ./Autodom-app

COPY ./Autodom/requirements.txt ./Autodom/requirements.txt

COPY ./Autodom/serviceworker.js ./Autodom/serviceworker.js

COPY ./Autodom/manage.py ./Autodom/manage.py

RUN pip install -r Autodom/requirements.txt

COPY ./Autodom/pwa_webpush ./Autodom/pwa_webpush

COPY ./Autodom/Autodom ./Autodom/Autodom

COPY ./Autodom/ChainControl ./Autodom/ChainControl

WORKDIR Autodom



