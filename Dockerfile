FROM python:3.8.0-alpine

WORKDIR /opt/panhit

RUN pip install --upgrade pip
COPY . /opt/panhit
RUN pip install -r /opt/panhit/requirements.txt