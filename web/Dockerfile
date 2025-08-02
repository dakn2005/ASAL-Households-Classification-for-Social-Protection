FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install uvicorn "fastapi[standard]"

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "infer:app --reload"]