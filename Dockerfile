FROM python:3.10-slim

WORKDIR /usr/src/midas

COPY . /usr/src/midas

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
