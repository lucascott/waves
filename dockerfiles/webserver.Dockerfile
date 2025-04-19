FROM python:3.13-slim

WORKDIR /app

RUN pip install waitress

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD waitress-serve app:app
