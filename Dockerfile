FROM python:3.11.10-slim-bookworm

RUN pip install poetry
COPY /pyproject.toml .
COPY /poetry.lock .
COPY ./f1data /f1data
RUN poetry install 
COPY . . 
CMD ["poetry", "run", "hypercorn", "f1data/main:app", "--bind", "::"]