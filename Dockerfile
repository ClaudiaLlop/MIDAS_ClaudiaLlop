FROM python:3.10-slim

WORKDIR /usr/src/midas

COPY . /usr/src/midas

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]
