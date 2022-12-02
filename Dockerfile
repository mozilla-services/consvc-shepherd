FROM python:3.10.5-slim

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -U 'pip==21.3.1'

# install psycopg2 dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc libpq-dev python3-dev

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

RUN apt-get remove --yes gcc python3-dev && \
    apt-get -q --yes autoremove && \
    apt-get clean

COPY ./consvc_shepherd/ /app/consvc_shepherd/
COPY ./static/ /app/static/
COPY ./contile/ /app/contile/
COPY ./openidc/ /app/openidc/
COPY ./manage.py /app/
COPY ./version.json /app/
COPY ./bin/ /app/bin/

EXPOSE 8000

CMD ["python", "/app/manage.py", "runserver", "0.0.0.0:8000"]
