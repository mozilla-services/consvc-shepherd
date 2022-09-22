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

COPY ./consvc_shepherd/ /app/consvc_shepherd/
COPY ./static/ /app/static/
COPY ./contile/ /app/contile/
COPY ./manage.py /app/
COPY ./bin/ /app/bin/
RUN chmod +x /app/bin/wait-for-it.sh

EXPOSE 8000

CMD ["python", "/app/manage.py", "runserver", "0.0.0.0:8000"]
