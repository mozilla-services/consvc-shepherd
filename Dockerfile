ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS build

WORKDIR /tmp
# Pin Poetry to reduce image size
RUN pip install --no-cache-dir --quiet poetry

COPY ./pyproject.toml ./poetry.lock /tmp/
# Just need the requirements.txt from Poetry
RUN poetry export --no-interaction --without dev --output requirements.txt --without-hashes

FROM python:${PYTHON_VERSION}-slim

ENV PYTHONUNBUFFERED True

# Set app home
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . $APP_HOME

COPY --from=build /tmp/requirements.txt $APP_HOME/requirements.txt
# install psycopg2 dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc libpq-dev python3-dev

RUN pip install --no-cache-dir --quiet --upgrade -r requirements.txt

RUN apt-get remove --yes gcc python3-dev && \
    apt-get -q --yes autoremove && \
    apt-get clean

COPY ./consvc_shepherd/ /app/consvc_shepherd/
COPY ./static/ /app/static/
COPY ./contile/ /app/contile/
COPY ./openidc/ /app/openidc/
COPY ./schema/ /app/schema/
COPY ./manage.py /app/
COPY ./version.json /app/
COPY ./bin/ /app/bin/

EXPOSE 8000

CMD ["python", "/app/manage.py", "runserver", "0.0.0.0:8000"]
