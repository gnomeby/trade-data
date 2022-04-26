FROM python:3.8-alpine3.14

RUN addgroup user1 && adduser --ingroup user1 -D -h /opt user1

WORKDIR /opt

USER user1

RUN python3 -m venv .venv

ENV PATH="/opt/.venv/bin:$PATH"

ADD --chown=user1 requirements.txt /opt
RUN pip3 install -r requirements.txt --no-cache-dir && rm -rf /var/cache/apk/*

ADD --chown=user1 data/.keep /opt/data/
ADD --chown=user1 static/* /opt/static/
ADD --chown=user1 templates/*.html /opt/templates/
ADD --chown=user1 utils/*.py /opt/utils/
ADD --chown=user1 *.py /opt/
ADD --chown=user1 *.sh /opt/
ADD --chown=user1 *.sql /opt/


ENV PYTHONIOENCODING=utf-8

RUN flask init-db

CMD [ "sh", "init_and_start.sh" ]

EXPOSE 8000
EXPOSE 8765
