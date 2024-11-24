FROM python:3.11.10-slim-bookworm

RUN pip install poetry
COPY /pyproject.toml .
COPY /poetry.lock .
RUN poetry install 
COPY . . 
WORKDIR /f1data
CMD ["poetry", "run", "uvicorn", "main:app"]