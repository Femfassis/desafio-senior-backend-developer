FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY tests ./tests
COPY alembic.ini ./
COPY start_api.sh ./


RUN mkdir migrations
RUN mkdir migrations/versions
COPY migrations/env.py ./migrations
COPY migrations/script.py.mako ./migrations

EXPOSE 8000

CMD ["bash", "start_api.sh"]