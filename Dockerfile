FROM python:3.9-buster

# create user and group for all the X Window stuff
RUN addgroup --system xusers \
  && adduser \
      --home /home/xuser \
      --disabled-password \
      --shell /bin/bash \
      --gecos "user for running X Window stuff" \
      --ingroup xusers \
      --quiet \
      xuser

RUN echo 'deb https://notesalexp.org/tesseract-ocr-dev/buster/ buster main' >> /etc/apt/sources.list \
  && wget -O - https://notesalexp.org/debian/alexp_key.asc | apt-key add

# Install xvfb as X-Server and x11vnc as VNC-Server
RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb \
        xauth \
        x11vnc \
        x11-utils \
        x11-xserver-utils \
        firefox-esr \
        ipmitool \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# set up selenium
RUN curl --location https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux64.tar.gz -o /tmp/geckodriver.tgz \
  && cd /usr/local/bin/ \
  && tar zxf /tmp/geckodriver.tgz \
  && rm -f /tmp/geckodriver.tgz \
  && chmod +x /usr/local/bin/geckodriver

RUN mkdir -p /Xauthority && chown -R xuser:xusers /Xauthority
VOLUME /Xauthority

ENV DISPLAY :0.0
EXPOSE 5900
ENV VNC_PASSWORD 123456
ENV XFB_SCREEN 1960x1080x24
ENV XFB_SCREEN_DPI 150

COPY requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt

COPY app/ /app

VOLUME /db

COPY docker-entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

USER xuser

ENTRYPOINT ["/entrypoint.sh"]
