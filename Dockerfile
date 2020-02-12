FROM tiangolo/uwsgi-nginx:python3.7-alpine3.9

WORKDIR /app 

RUN apk add gcc musl-dev libffi-dev openssl-dev libsass g++ libstdc++ 
RUN pip install --upgrade pip
RUN mkdir -p /database/db
RUN mkdir -p /database/configdb
COPY . /app
COPY ssl.conf /etc/nginx/conf.d/ssl.conf
COPY /certs/nginx.crt /etc/ssl/certs/nginx.crt 
COPY /certs/nginx.key /etc/ssl/private/nginx.key
RUN pip install -r /app/requirements.txt
