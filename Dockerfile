FROM python:3.9.16-slim

WORKDIR /app/

RUN pip3 install requests && apt update -y && apt install transmission-cli -y

COPY . .

CMD python3 main.py
