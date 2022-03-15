FROM python:3.9-buster

RUN echo 'deb https://notesalexp.org/tesseract-ocr-dev/buster/ buster main' >> /etc/apt/sources.list \
  && wget -O - https://notesalexp.org/debian/alexp_key.asc | apt-key add

RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt

COPY app/ /app

VOLUME /db

ENTRYPOINT [ "python3" ]

CMD [ "/app/vaxiin-server.py" ]
