FROM python:3.11-slim

WORKDIR /app

# requiremts.txt deb nomlangan faylni ko'chiramiz
COPY requiremts.txt .

RUN pip install --no-cache-dir -r requiremts.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
