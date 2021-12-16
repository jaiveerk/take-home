FROM python:latest

ENV FLASK_DEBUG=0
ENV FLASK_APP=app.py

ADD app .
ADD requirements.txt .
RUN pip install requirements.txt

WORKDIR /app
CMD flask run