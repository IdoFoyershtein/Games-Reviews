FROM python:3.11.8-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/python_files

EXPOSE 5000

CMD ["python3", "python-files/app.py"]