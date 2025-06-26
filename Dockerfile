FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packageslo
  && apt-get install -y build-essential \
  # psycopg dependencies
  libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
WORKDIR /setup

RUN mkdir /app
WORKDIR /app
COPY . /app/
RUN pip install -r /app/requirements.txt 

# Create empty env-file to avoid warnings
RUN cp .env.example .env

# Run collectstatic
RUN python ./manage.py collectstatic --noinput

EXPOSE 8000

CMD ["./scripts/run_backend.sh"]
