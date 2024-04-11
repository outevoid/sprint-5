# Dockerfile

FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app /app

# Копируем init.sql внутрь контейнера
COPY init.sql /docker-entrypoint-initdb.d/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
