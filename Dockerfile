FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "pyshop.wsgi:application"]
