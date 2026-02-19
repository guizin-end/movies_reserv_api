FROM python:3.14-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
COPY . .

COPY . .

RUN pip install poetry

RUN poetry lock
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]