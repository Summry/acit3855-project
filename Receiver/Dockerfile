FROM python:latest

LABEL maintainer="nfakhrurradi@my.bcit.ca"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

# RUN pip install 'connexion["flask"]'

COPY . /app/

CMD ["python3", "app.py"]
