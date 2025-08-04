# FROM alpine:latest
# FROM python:3.12-alpine
 FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# RUN apk add python3 py3-pip

RUN python3 -m venv .venv

RUN . .venv/bin/activate && pip install uvicorn "fastapi[standard]"

RUN . .venv/bin/activate && pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "infer:app --reload"]