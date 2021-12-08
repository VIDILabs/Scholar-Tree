# parent image
FROM python:2.7-alpine

# idk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# dependencies
COPY requirements.txt /
#RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install -r /requirements.txt

# copy & change workdir
COPY . /app
WORKDIR /app