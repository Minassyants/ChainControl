FROM python:3.7

WORKDIR ./Autodom-app

COPY ./Autodom ./Autodom

RUN pip install -r Autodom/requirements.txt

WORKDIR Autodom

CMD ["gunicorn", "-b 0.0.0.0:8000","Autodom.wsgi"]

