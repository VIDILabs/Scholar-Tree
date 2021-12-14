# parent image
FROM python:2.7-alpine

# idk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# dependencies
COPY requirements.txt /code/
#RUN pip install --no-cache-dir -r /requirements.txt
RUN apk update
RUN apk add --virtual build-deps gcc python2-dev musl-dev
RUN apk add --no-cache mariadb-dev
RUN pip install -r requirements.txt
RUN apk del build-deps

# copy & change workdir
COPY . /code/