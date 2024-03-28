FROM python:latest

LABEL maintainer="nfakhrurradi@my.bcit.ca"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app/

# CMD python3 create_tables_mysql.py && python3 app.py

CMD chmod +x start.sh && ./start.sh
