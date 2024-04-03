FROM python:latest

LABEL maintainer="nfakhrurradi@my.bcit.ca"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app/

# RUN python3 create_database.py

CMD ["python3", "app.py"]
