FROM python:3.13-alpine

WORKDIR /app
COPY errbot.py requirements.txt PS4.csv PS5.csv /app/
RUN pip3 install -r requirements.txt

CMD [ "/usr/local/bin/python3", "/app/errbot.py" ]