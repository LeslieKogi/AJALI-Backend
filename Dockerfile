FROM python:3.9
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5555

CMD ["gunicorn", "--bind", "0.0.0.0:5555", "app:app"]