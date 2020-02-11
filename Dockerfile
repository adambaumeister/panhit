FROM tiangolo/uwsgi-nginx:python3.7-alpine3.9

WORKDIR /app 

RUN apk add gcc musl-dev libffi-dev openssl-dev libsass g++ libstdc++ 
RUN pip install --upgrade pip
COPY . /app 
RUN pip install -r /app/requirements.txt
